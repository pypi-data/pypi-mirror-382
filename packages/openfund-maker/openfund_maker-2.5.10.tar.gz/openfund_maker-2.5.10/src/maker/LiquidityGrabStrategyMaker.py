# -*- coding: utf-8 -*-
import traceback
import pandas as pd
from datetime import datetime, timedelta
from typing import override
from cachetools import TTLCache
from core.smc.TF import TF
from maker.StrategyMaker import StrategyMaker
from maker.AdaptiveTargetFinder import AdaptiveTargetFinder
from maker.TargetValidationEngine import TargetValidationEngine
from maker.TechnicalAnalysisIntegrator import TechnicalAnalysisIntegrator


class LiquidityGrabStrategyMaker(StrategyMaker):
    """
    流动性抓取形态策略Maker端
    基于Smart Money Concepts的流动性抓取策略，核心逻辑是识别市场中因"等低等高流动性"聚集形成的潜在转折点
    """

    def __init__(
        self, config, platform_config, common_config, logger=None, exchangeKey="okx"
    ):
        super().__init__(config, platform_config, common_config, logger, exchangeKey)
        self.logger = logger
        cache_ttl = common_config.get("cache_ttl", 60)

        # 缓存系统
        self.htf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl * 60))
        self.atf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl * 60))
        self.liquidity_cache = TTLCache(maxsize=100, ttl=600)  # 流动性缓存，10分钟TTL

        # 首次触及追踪器
        self.first_touch_tracker = {}

        # 流动性强度追踪
        self.liquidity_strength = {}

        # 初始化自适应目标位组件
        try:
            self.adaptive_target_finder = AdaptiveTargetFinder(self, config)
            self.target_validation_engine = TargetValidationEngine(
                config.get("liquidity_grab_strategy", {})
            )
            self.technical_analysis_integrator = TechnicalAnalysisIntegrator(self)
            self.logger.info("自适应目标位组件初始化成功")
        except Exception as e:
            self.logger.warning(f"自适应目标位组件初始化失败: {e}")
            # 回退到无自适应功能模式
            self.adaptive_target_finder = None
            self.target_validation_engine = None
            self.technical_analysis_integrator = None
            # 发送通知
            self.send_feishu_notification(
                "系统", f"自适应目标位功能初始化失败，回退到基础模式: {e}"
            )

    @override
    def reset_all_cache(self, symbol):
        """重置所有缓存"""
        super().reset_all_cache(symbol)
        self.htf_cache.pop(symbol, None)
        self.atf_cache.pop(symbol, None)
        self.liquidity_cache.pop(symbol, None)
        self.first_touch_tracker.pop(symbol, None)
        self.liquidity_strength.pop(symbol, None)

    @override
    def process_pair(self, symbol, pair_config):
        """
        流动性抓取策略核心处理逻辑
        HTF定方向→ATF找机会→LTF抓时机
        """
        self.logger.info("-" * 60)

        try:
            # 检查是否有持仓
            if self.fetch_position(symbol=symbol):
                self.reset_all_cache(symbol)
                self.logger.info(f"{symbol} : 有持仓合约，不进行下单。")
                return

            precision = self.get_precision_length(symbol)
            liquidity_strategy = pair_config.get("liquidity_grab_strategy", {})

            # 获取策略配置
            htf = str(pair_config.get("htf", "4h"))
            atf = str(pair_config.get("atf", "15m"))
            ltf = str(pair_config.get("ltf", "1m"))
            open_body_break = bool(pair_config.get("open_body_break", True))

            self.logger.info(
                f"{symbol} : 流动性抓取策略 {htf}|{atf}|{ltf} open_body_break={open_body_break}"
            )

            market_price = self.get_market_price(symbol=symbol)

            # Step 1: HTF确认趋势与核心支撑/阻力位
            htf_result = self._analyze_htf_trend_and_levels(
                symbol, htf, open_body_break, liquidity_strategy, precision
            )
            if not htf_result:
                return

            # Step 2: ATF识别等高等低流动性聚集区
            atf_result = self._analyze_atf_liquidity_zones(
                symbol, atf, htf_result, open_body_break, liquidity_strategy, precision
            )
            if not atf_result:
                return

            # Step 3: LTF精准入场时机
            ltf_result = self._analyze_ltf_entry_timing(
                symbol,
                ltf,
                htf_result,
                atf_result,
                open_body_break,
                market_price,
                precision,
            )
            if not ltf_result:
                return

            # Step 4: 验证首次触及条件
            if not self._validate_first_touch_condition(
                symbol,
                atf_result.confluence_result["target_level"],
                atf_result.confluence_result["equal_points_type"],
                liquidity_strategy,
            ):
                self.logger.info(f"{symbol} : 不满足首次触及条件，等待...")
                return

            # Step 5: 执行下单
            self._execute_liquidity_grab_order(
                symbol, ltf_result, atf_result, market_price, pair_config, precision
            )

        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(f"{error_message}\n{traceback.format_exc()}")
            traceback.print_exc()
            self.send_feishu_notification(symbol, error_message)
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        finally:
            self.logger.info("=" * 60 + "\n")

    def _analyze_htf_trend_and_levels(
        self, symbol, htf, open_body_break, strategy, precision
    ):
        """Step 1: HTF确认趋势与核心支撑/阻力位"""
        step = "1"
        htf_cache_key = f"{symbol}_{htf}"

        if htf_cache_key not in self.htf_cache:
            # HTF数据分析
            htf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=htf)
            htf_struct = self.build_struct(
                symbol=symbol, data=htf_df, is_struct_body_break=open_body_break
            )
            htf_latest_struct = self.get_latest_struct(
                symbol=symbol, data=htf_struct, is_struct_body_break=open_body_break
            )

            if htf_latest_struct is None:
                self.logger.info(f"{symbol} : {step}. HTF {htf} 未形成结构，等待...")
                return None

            htf_trend = htf_latest_struct[self.STRUCT_DIRECTION_COL]
            htf_side = (
                self.BUY_SIDE if htf_trend == self.BULLISH_TREND else self.SELL_SIDE
            )

            self.logger.info(f"{symbol} : {step}.1. HTF {htf} 趋势方向: {htf_trend}")

            # 1.2 识别关键支撑阻力位
            range_of_the_ob = float(strategy.get("range_of_the_ob", 0.6))
            htf_OBs_df = self.find_OBs(
                symbol=symbol,
                struct=htf_struct,
                is_struct_body_break=open_body_break,
                atr_multiplier=range_of_the_ob,
            )
            htf_support_resistance = self.get_support_resistance_from_OBs(
                symbol=symbol, obs_df=htf_OBs_df, struct_df=htf_struct
            )

            if htf_support_resistance is None:
                self.logger.info(
                    f"{symbol} : {step}.2. HTF {htf} 未找到支撑位和阻力位。"
                )
                return None

            htf_support_price = htf_support_resistance.get(self.SUPPORT_PRICE_KEY)
            htf_resistance_price = htf_support_resistance.get(self.RESISTANCE_PRICE_KEY)
            htf_support_OB = htf_support_resistance.get(self.SUPPORT_OB_KEY)
            htf_resistance_OB = htf_support_resistance.get(self.RESISTANCE_OB_KEY)

            self.logger.info(
                f"{symbol} : {step}.2. HTF {htf} 支撑位={htf_support_price:.{precision}f}, 阻力位={htf_resistance_price:.{precision}f}"
            )

            # 1.3 检查利润空间
            min_profit_percent = self.toDecimal(strategy.get("min_profit_percent", 4))
            profit_percent = self.toDecimal(
                abs(
                    (htf_resistance_price - htf_support_price) / htf_support_price * 100
                )
            )

            if profit_percent < min_profit_percent:
                self.logger.info(
                    f"{symbol} : {step}.3. HTF {htf} 利润空间{profit_percent:.2f}% < {min_profit_percent}%，等待..."
                )
                return None

            # 构建HTF缓存
            tf_HTF = TF(TF.HTF, htf, htf_side, htf_trend)
            tf_HTF.resistance_price = htf_resistance_price
            tf_HTF.support_price = htf_support_price
            tf_HTF.struct = htf_latest_struct
            tf_HTF.support_OB = htf_support_OB
            tf_HTF.resistance_OB = htf_resistance_OB

            self.htf_cache[htf_cache_key] = tf_HTF
            self.logger.info(f"{symbol} : {step}.4. HTF {htf} 缓存构建成功")

        return self.htf_cache[htf_cache_key]

    def _analyze_atf_liquidity_zones(
        self, symbol, atf, htf_result, open_body_break, strategy, precision
    ):
        """Step 2: ATF识别等高等低流动性聚集区"""
        step = "2"
        atf_cache_key = f"{symbol}_{atf}"

        if atf_cache_key not in self.atf_cache:
            # 获取ATF数据
            htf_support_timestamp = (
                htf_result.support_OB.get(self.TIMESTAMP_COL)
                if htf_result.support_OB
                else None
            )
            htf_resistance_timestamp = (
                htf_result.resistance_OB.get(self.TIMESTAMP_COL)
                if htf_result.resistance_OB
                else None
            )

            if htf_support_timestamp and htf_resistance_timestamp:
                min_timestamp = min(htf_support_timestamp, htf_resistance_timestamp)
                atf_start_timestamp = (
                    pd.Timestamp(min_timestamp) - pd.Timedelta(atf)
                ).strftime("%Y-%m-%d %H:%M:%S+08:00")
                atf_df = self.get_historical_klines_df(
                    symbol=symbol, tf=atf, after=atf_start_timestamp
                )
            else:
                atf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=atf)

            atf_struct = self.build_struct(
                symbol=symbol, data=atf_df, is_struct_body_break=open_body_break
            )
            atf_latest_struct = self.get_latest_struct(
                symbol=symbol, data=atf_struct, is_struct_body_break=open_body_break
            )

            if atf_latest_struct is None:
                self.logger.info(f"{symbol} : {step}.1. ATF {atf} 未形成结构，等待...")
                return None

            atf_trend = atf_latest_struct[self.STRUCT_DIRECTION_COL]
            atf_side = (
                self.BUY_SIDE if atf_trend == self.BULLISH_TREND else self.SELL_SIDE
            )

            # 2.1 优先识别等高等低流动性
            liquidity_result = self._identify_equal_highs_lows_liquidity(
                symbol, atf_df, atf_trend, strategy
            )
            if not liquidity_result:
                self.logger.info(
                    f"{symbol} : {step}.1. ATF {atf} 未找到有效的等高等低流动性"
                )
                return None

            self.logger.info(
                f"{symbol} : {step}.1.1 ATF {atf} 发现{liquidity_result[self.EQUAL_POINTS_TYPE_COL]}流动性，价格={liquidity_result[self.EQUAL_POINTS_PRICE_COL]}"
            )

            # 2.2 验证ATF与HTF趋势一致性
            enable_check_htf_side = bool(strategy.get("enable_check_htf_side", True))
            if enable_check_htf_side:
                if htf_result.side != atf_side:
                    self.logger.info(
                        f"{symbol} : {step}.2. ATF {atf} 趋势{atf_side} 与 HTF 趋势{htf_result.side} 不一致，等待..."
                    )
                    return None
                self.logger.info(
                    f"{symbol} : {step}.2. ATF {atf} 趋势{atf_side} 与 HTF 趋势一致"
                )

            # 2.3 验证支撑/阻力位与流动性的配合
            confluence_result = self._validate_support_resistance_confluence(
                symbol, htf_result, liquidity_result, atf_side, precision, strategy
            )
            if not confluence_result:
                return None

            # 构建ATF缓存
            tf_ATF = TF(TF.ATF, atf, atf_side, atf_trend)
            tf_ATF.struct = atf_latest_struct
            tf_ATF.liquidity_result = liquidity_result
            tf_ATF.confluence_result = confluence_result

            self.atf_cache[atf_cache_key] = tf_ATF
            self.logger.info(f"{symbol} : {step}.3. ATF {atf} 流动性分析完成")

        return self.atf_cache[atf_cache_key]

    def _identify_equal_highs_lows_liquidity(
        self, symbol, data, trend, strategy
    ) -> dict:
        """识别等高等低流动性"""
        atr_offset = self.toDecimal(strategy.get("liquidity_atr_offset", 0.1))

        # 使用SMCLiquidity查找等高等低
        df_equal_liquidity = self.find_EQH_EQL(
            symbol=symbol, data=data, trend=trend, atr_offset=atr_offset
        )
        # 找到流动性
        mask = df_equal_liquidity[self.HAS_EQUAL_POINTS_COL]
        if len(df_equal_liquidity[mask]) == 0:
            self.logger.info(f"{symbol} : 未找到等高等低流动性，继续等待...")
            return None
        else:
            # 打印等高等低流动性的关键信息用于调试
            debug_columns = [
                self.TIMESTAMP_COL,
                self.EQUAL_POINTS_PRICE_COL,
                self.EQUAL_POINTS_TYPE_COL,
                self.EXTREME_VALUE_COL,
                self.ATR_TOLERANCE_COL,
                self.HAS_EQUAL_POINTS_COL,
            ]
            self.logger.debug(
                f"df_equal_liquidity=\n{df_equal_liquidity[debug_columns].to_string()}"
            )

        return self._get_equal_liquidity(df_equal_liquidity, trend)

    def _get_equal_liquidity(self, df_equal_liquidity, trend):
        # 筛选有等高点的行
        df_with_equal_points = df_equal_liquidity[
            df_equal_liquidity[self.HAS_EQUAL_POINTS_COL]
        ]

        if df_with_equal_points.empty:
            return None

        # 根据趋势选择最高/最低价格的行
        if trend == self.BULLISH_TREND:
            target_row = df_with_equal_points.loc[
                df_with_equal_points[self.EQUAL_POINTS_PRICE_COL].idxmax()
            ]
        else:
            target_row = df_with_equal_points.loc[
                df_with_equal_points[self.EQUAL_POINTS_PRICE_COL].idxmin()
            ]

        return {
            self.TIMESTAMP_COL: target_row[self.TIMESTAMP_COL],
            self.EQUAL_POINTS_PRICE_COL: target_row[self.EQUAL_POINTS_PRICE_COL],
            self.EQUAL_POINTS_TYPE_COL: target_row[self.EQUAL_POINTS_TYPE_COL],
            "trend": trend,
            "equal_liquidity": target_row,
        }

    def _validate_support_resistance_confluence(
        self, symbol, htf_result, liquidity_result, atf_side, precision, strategy
    ):
        """验证支撑/阻力位与流动性的配合"""
        step = "2.3"

        if atf_side == self.BUY_SIDE:
            # 多头：需要支撑位+等高流动性配合
            support_price = htf_result.support_price
            liquidity_price = liquidity_result[self.EQUAL_POINTS_PRICE_COL]

            if liquidity_result[self.EQUAL_POINTS_TYPE_COL] != self.EQUAL_HIGH_TYPE:
                self.logger.info(
                    f"{symbol} : {step}. 多头需要等高流动性，但找到的是{liquidity_result[self.EQUAL_POINTS_TYPE_COL]}"
                )
                return None

            target_level = support_price
            tp_target = liquidity_price
            equal_points_type = self.SUPPORT_TYPE

            self.logger.info(
                f"{symbol} : {step}. 多头机会: 支撑位={support_price:.{precision}f}, 等高流动性={liquidity_price:.{precision}f}"
            )

        else:
            # 空头：需要阻力位+等低流动性配合
            resistance_price = htf_result.resistance_price
            liquidity_price = liquidity_result[self.EQUAL_POINTS_PRICE_COL]

            if liquidity_result[self.EQUAL_POINTS_TYPE_COL] != self.EQUAL_LOW_TYPE:
                self.logger.info(
                    f"{symbol} : {step}. 空头需要等低流动性，但找到的是{liquidity_result[self.EQUAL_POINTS_TYPE_COL]}"
                )
                return None

            target_level = resistance_price
            tp_target = liquidity_price
            equal_points_type = self.RESISTANCE_TYPE

            self.logger.info(
                f"{symbol} : {step}. 空头机会: 阻力位={resistance_price:.{precision}f}, 等低流动性={liquidity_price:.{precision}f}"
            )

        # 验证盈亏比
        min_profit_ratio = self.toDecimal(strategy.get("min_profit_ratio", 1.5))
        profit_distance = abs(self.toDecimal(tp_target) - self.toDecimal(target_level))
        entry_distance = profit_distance / min_profit_ratio  # 估算最大入场偏移

        if profit_distance < entry_distance * min_profit_ratio:
            self.logger.info(
                f"{symbol} : {step}. 盈亏比不足{min_profit_ratio}, 利润距离={profit_distance:.{precision}f}"
            )
            return None

        return {
            "target_level": target_level,
            "tp_target": tp_target,
            "equal_points_type": equal_points_type,
            "side": atf_side,
            "profit_distance": profit_distance,
        }

    def _analyze_ltf_entry_timing(
        self,
        symbol,
        ltf,
        htf_result,
        atf_result,
        open_body_break,
        market_price,
        precision,
    ):
        """Step 3: LTF精准入场时机"""
        step = "3"

        # 获取LTF数据
        ltf_df = self.get_historical_klines_df(symbol=symbol, tf=ltf)
        ltf_struct = self.build_struct(
            symbol=symbol, data=ltf_df, is_struct_body_break=open_body_break
        )
        ltf_latest_struct = self.get_latest_struct(
            symbol=symbol, data=ltf_struct, is_struct_body_break=open_body_break
        )

        if ltf_latest_struct is None:
            self.logger.info(f"{symbol} : {step}.1. LTF {ltf} 未形成结构，等待...")
            return None

        ltf_trend = ltf_latest_struct[self.STRUCT_DIRECTION_COL]
        ltf_side = self.BUY_SIDE if ltf_trend == self.BULLISH_TREND else self.SELL_SIDE

        self.logger.info(f"{symbol} : {step}.1. LTF {ltf} 趋势: {ltf_trend}")

        # 3.1 检查价格是否接近目标位置
        target_level = self.toDecimal(atf_result.confluence_result["target_level"])
        market_price = self.toDecimal(market_price)
        tolerance_pct = self.toDecimal(0.5)  # 0.5%容差
        price_diff_pct = abs(market_price - target_level) / target_level * 100

        if price_diff_pct > tolerance_pct:
            self.logger.info(
                f"{symbol} : {step}.2. 当前价格{market_price:.{precision}f}距离目标位{target_level:.{precision}f}太远({price_diff_pct:.2f}%)"
            )

            # 尝试自适应目标位搜索
            if self.adaptive_target_finder:
                try:
                    adaptive_result = self.adaptive_target_finder.find_adaptive_target(
                        symbol=symbol,
                        current_price=float(market_price),
                        original_target=float(target_level),
                        side=atf_result.confluence_result["side"],
                        htf_result=htf_result,
                        atf_result=atf_result,
                        precision=precision,
                    )

                    if adaptive_result.success:
                        # 更新目标位
                        new_target_level = self.toDecimal(
                            adaptive_result.new_target_price
                        )
                        atf_result.confluence_result["target_level"] = new_target_level
                        atf_result.confluence_result["adaptive_adjustment"] = True
                        atf_result.confluence_result["adjustment_reason"] = (
                            adaptive_result.adjustment_reason
                        )

                        self.logger.info(
                            f"{symbol} : {step}.2.1. 自适应目标位调整成功: "
                            f"{float(target_level):.{precision}f} -> {adaptive_result.new_target_price:.{precision}f}"
                        )

                        # 更新target_level为新的目标位
                        target_level = new_target_level
                        price_diff_pct = (
                            abs(market_price - target_level) / target_level * 100
                        )
                    else:
                        self.logger.info(
                            f"{symbol} : {step}.2.2. 自适应目标位搜索失败: {adaptive_result.adjustment_reason}"
                        )
                        return None

                except Exception as e:
                    self.logger.error(
                        f"{symbol} : {step}.2.3. 自适应目标位搜索异常: {e}"
                    )
                    # 发送异常通知
                    self.send_feishu_notification(symbol, f"自适应目标位搜索异常: {e}")
                    # 回退到等待模式
                    return None
            else:
                self.logger.info(
                    f"{symbol} : {step}.2.4. 自适应目标位功能不可用，回退到等待模式"
                )
                return None

        # 3.2 检查LTF结构反转信号
        expected_side = atf_result.confluence_result["side"]
        if ltf_side != expected_side:
            self.logger.info(
                f"{symbol} : {step}.3. LTF结构{ltf_side}与预期方向{expected_side}不符，等待..."
            )
            return None

        # 3.3 寻找PDArray入场点
        ltf_PDArrays_df = self.find_PDArrays(
            symbol=symbol,
            struct=ltf_struct,
            side=ltf_side,
            is_struct_body_break=open_body_break,
        )
        if len(ltf_PDArrays_df) == 0:
            self.logger.info(f"{symbol} : {step}.4. LTF {ltf} 未找到PDArray，等待...")
            return None

        # 选择最新的PDArray
        ltf_latest_PDArray = ltf_PDArrays_df.iloc[-1]

        # 检查当前价格是否在PDArray范围内
        if not (
            ltf_latest_PDArray[self.PD_LOW_COL]
            <= market_price
            <= ltf_latest_PDArray[self.PD_HIGH_COL]
        ):
            self.logger.info(
                f"{symbol} : {step}.5. 当前价格{market_price:.{precision}f}不在PDArray范围内"
            )
            return None

        self.logger.info(f"{symbol} : {step}.6. LTF {ltf} 入场条件满足")

        return {
            "ltf_side": ltf_side,
            "ltf_trend": ltf_trend,
            "ltf_struct": ltf_latest_struct,
            "entry_pdarray": ltf_latest_PDArray,
            "entry_price": ltf_latest_PDArray[self.PD_MID_COL],
        }

    def _validate_first_touch_condition(
        self, symbol, target_level, equal_points_type, strategy
    ):
        """验证首次触及条件"""
        max_candle_interval = int(strategy.get("max_candle_interval", 200))

        if symbol not in self.first_touch_tracker:
            self.first_touch_tracker[symbol] = {}

        level_key = f"{equal_points_type}_{target_level}"
        touch_history = self.first_touch_tracker[symbol]

        if level_key in touch_history:
            last_touch_time = touch_history[level_key]
            # FIXME:如果距离上次触及超过200个K线，可以重置
            if (
                datetime.now() - last_touch_time
            ).total_seconds() > 15 * max_candle_interval:
                del touch_history[level_key]
            else:
                return False

        # 标记为已触及
        touch_history[level_key] = datetime.now()
        return True

    def _execute_liquidity_grab_order(
        self, symbol, ltf_result, atf_result, market_price, pair_config, precision
    ):
        """执行流动性抓取下单"""
        step = "4"

        entry_price = self.toDecimal(ltf_result["entry_price"])
        order_side = ltf_result["ltf_side"]

        # 检查价格变化
        latest_order_price = self.toDecimal(self.place_order_prices.get(symbol, 0))
        if entry_price == latest_order_price:
            self.logger.info(
                f"{symbol} : {step}. 下单价格{entry_price:.{precision}f}未变化，跳过"
            )
            return

        # 取消现有订单并下新单
        self.cancel_all_orders(symbol=symbol)
        self.place_order(
            symbol=symbol, price=entry_price, side=order_side, pair_config=pair_config
        )
        self.place_order_prices[symbol] = entry_price

        self.logger.info(
            f"{symbol} : {step}. 流动性抓取{order_side}单已下，价格={entry_price:.{precision}f}"
        )
