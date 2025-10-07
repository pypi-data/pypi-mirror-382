# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import traceback


@dataclass
class AdaptiveTargetConfig:
    """自适应目标位配置"""

    enabled: bool = True
    max_price_deviation_percent: float = 5.0
    min_profit_percent: float = 2.0
    min_profit_ratio: float = 1.5
    search_step_percent: float = 0.5
    technical_priority_weight: float = 0.7
    liquidity_priority_weight: float = 0.3


@dataclass
class AdaptiveTargetResult:
    """自适应目标位搜索结果"""

    success: bool
    new_target_price: Optional[float] = None
    original_target_price: Optional[float] = None
    adjustment_reason: str = ""
    technical_score: float = 0.0
    profit_percent: float = 0.0
    profit_ratio: float = 0.0
    search_attempts: int = 0


class AdaptiveTargetError(Exception):
    """自适应目标位相关异常基类"""

    pass


class NoValidTargetFoundError(AdaptiveTargetError):
    """未找到有效目标位异常"""

    pass


class ConfigurationError(AdaptiveTargetError):
    """配置错误异常"""

    pass


class AdaptiveTargetFinder:
    """
    自适应目标位查找器
    当价格距离原始目标位过远时，智能搜索满足条件的替代目标位
    """

    def __init__(self, strategy_maker, config: Dict):
        """
        初始化自适应目标位查找器

        Args:
            strategy_maker: 策略制造器实例
            config: 配置字典
        """
        self.strategy_maker = strategy_maker
        self.logger = strategy_maker.logger

        # 解析配置
        adaptive_config = config.get("adaptive_target", {})
        self.config = AdaptiveTargetConfig(
            enabled=adaptive_config.get("enabled", True),
            max_price_deviation_percent=adaptive_config.get(
                "max_price_deviation_percent", 5.0
            ),
            min_profit_percent=adaptive_config.get("min_profit_percent", 2.0),
            min_profit_ratio=adaptive_config.get("min_profit_ratio", 1.5),
            search_step_percent=adaptive_config.get("search_step_percent", 0.5),
            technical_priority_weight=adaptive_config.get(
                "technical_priority_weight", 0.7
            ),
            liquidity_priority_weight=adaptive_config.get(
                "liquidity_priority_weight", 0.3
            ),
        )

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """验证配置参数的有效性"""
        if (
            self.config.max_price_deviation_percent <= 0
            or self.config.max_price_deviation_percent > 20
        ):
            raise ConfigurationError("max_price_deviation_percent必须在0-20之间")

        if self.config.min_profit_percent <= 0 or self.config.min_profit_percent > 10:
            raise ConfigurationError("min_profit_percent必须在0-10之间")

        if self.config.min_profit_ratio <= 1.0 or self.config.min_profit_ratio > 5.0:
            raise ConfigurationError("min_profit_ratio必须在1.0-5.0之间")

        if (
            self.config.search_step_percent <= 0
            or self.config.search_step_percent > 2.0
        ):
            raise ConfigurationError("search_step_percent必须在0-2.0之间")

        weight_sum = (
            self.config.technical_priority_weight
            + self.config.liquidity_priority_weight
        )
        if abs(weight_sum - 1.0) > 0.01:
            raise ConfigurationError("技术分析权重和流动性权重之和必须等于1.0")

    def find_adaptive_target(
        self,
        symbol: str,
        current_price: float,
        original_target: float,
        side: str,
        htf_result,
        atf_result,
        precision: int,
    ) -> AdaptiveTargetResult:
        """
        寻找自适应目标位

        Args:
            symbol: 交易对符号
            current_price: 当前市场价格
            original_target: 原始目标位
            side: 交易方向 (buy/sell)
            htf_result: HTF分析结果
            atf_result: ATF分析结果
            precision: 价格精度

        Returns:
            AdaptiveTargetResult: 搜索结果
        """
        if not self.config.enabled:
            return AdaptiveTargetResult(
                success=False,
                original_target_price=original_target,
                adjustment_reason="自适应目标位功能已禁用",
            )

        try:
            import time

            start_time = time.time()

            self.logger.info(
                f"{symbol} : 3.2.1. 启动自适应目标位搜索，原始目标={original_target:.{precision}f}"
            )

            # 计算搜索范围
            search_range = self._calculate_search_range(current_price, side)
            self.logger.debug(
                f"{symbol} : 3.2.1.1. 搜索范围: {search_range[0]:.{precision}f} - {search_range[1]:.{precision}f}"
            )

            # 生成候选目标位
            candidates = self._generate_candidates(current_price, side, search_range)
            self.logger.debug(f"{symbol} : 3.2.1.2. 生成{len(candidates)}个候选目标位")

            # 搜索最佳目标位
            best_target = self._search_best_target(
                symbol,
                candidates,
                current_price,
                side,
                htf_result,
                atf_result,
                precision,
            )

            # 记录搜索性能
            search_time = time.time() - start_time
            self.logger.debug(f"{symbol} : 3.2.1.3. 搜索耗时: {search_time:.3f}秒")

            if best_target:
                self.logger.info(
                    f"{symbol} : 3.2.3. 找到新目标位={best_target['price']:.{precision}f}，"
                    f"利润空间={best_target['profit_percent']:.2f}%"
                )

                return AdaptiveTargetResult(
                    success=True,
                    new_target_price=best_target["price"],
                    original_target_price=original_target,
                    adjustment_reason=best_target["reason"],
                    technical_score=best_target["technical_score"],
                    profit_percent=best_target["profit_percent"],
                    profit_ratio=best_target["profit_ratio"],
                    search_attempts=len(candidates),
                )
            else:
                self.logger.info(f"{symbol} : 3.2.4. 未找到满足条件的替代目标位")
                return AdaptiveTargetResult(
                    success=False,
                    original_target_price=original_target,
                    adjustment_reason="未找到满足条件的替代目标位",
                    search_attempts=len(candidates),
                )

        except Exception as e:
            error_msg = f"自适应目标位搜索异常: {str(e)}"
            self.logger.error(f"{symbol} : {error_msg}\n{traceback.format_exc()}")
            return AdaptiveTargetResult(
                success=False,
                original_target_price=original_target,
                adjustment_reason=error_msg,
            )

    def _calculate_search_range(
        self, current_price: float, side: str
    ) -> Tuple[float, float]:
        """
        计算搜索范围

        Args:
            current_price: 当前价格
            side: 交易方向

        Returns:
            Tuple[float, float]: (最小价格, 最大价格)
        """
        deviation = current_price * self.config.max_price_deviation_percent / 100

        if side == self.strategy_maker.BUY_SIDE:
            # 多头：搜索当前价格上方的目标位
            min_price = current_price
            max_price = current_price + deviation
        else:
            # 空头：搜索当前价格下方的目标位
            min_price = current_price - deviation
            max_price = current_price

        return min_price, max_price

    def _generate_candidates(
        self, current_price: float, side: str, search_range: Tuple[float, float]
    ) -> List[float]:
        """
        生成候选目标位列表

        Args:
            current_price: 当前价格
            side: 交易方向
            search_range: 搜索范围

        Returns:
            List[float]: 候选价格列表
        """
        min_price, max_price = search_range
        step = current_price * self.config.search_step_percent / 100

        candidates = []
        price = min_price

        while price <= max_price:
            # 确保候选价格与当前价格有足够的距离
            if side == self.strategy_maker.BUY_SIDE and price > current_price:
                candidates.append(price)
            elif side == self.strategy_maker.SELL_SIDE and price < current_price:
                candidates.append(price)

            price += step

        return candidates

    def _search_best_target(
        self,
        symbol: str,
        candidates: List[float],
        current_price: float,
        side: str,
        htf_result,
        atf_result,
        precision: int,
    ) -> Optional[Dict]:
        """
        搜索最佳目标位

        Args:
            symbol: 交易对符号
            candidates: 候选价格列表
            current_price: 当前价格
            side: 交易方向
            htf_result: HTF分析结果
            atf_result: ATF分析结果
            precision: 价格精度

        Returns:
            Optional[Dict]: 最佳目标位信息或None
        """
        best_target = None
        best_score = 0.0

        for i, candidate in enumerate(candidates):
            self.logger.debug(
                f"{symbol} : 3.2.2. 评估候选目标位[{i+1}/{len(candidates)}]={candidate:.{precision}f}"
            )

            # 基础验证：利润空间和盈亏比
            if not self._validate_basic_requirements(current_price, candidate, side):
                self.logger.debug(
                    f"{symbol} : 3.2.2.1. 候选位{candidate:.{precision}f}未通过基础验证"
                )
                continue

            # 计算技术分析评分
            technical_score = self._calculate_technical_score(
                symbol, candidate, side, htf_result, atf_result
            )

            # 计算综合评分
            profit_percent = abs(candidate - current_price) / current_price * 100
            profit_ratio = self._calculate_profit_ratio(current_price, candidate, side)

            # 综合评分 = 技术评分 * 权重 + 利润评分 * 权重
            profit_score = min(profit_percent / 10.0, 1.0)  # 标准化到0-1
            total_score = (
                technical_score * self.config.technical_priority_weight
                + profit_score * self.config.liquidity_priority_weight
            )

            self.logger.debug(
                f"{symbol} : 3.2.2.2. 候选位{candidate:.{precision}f} - "
                f"技术评分:{technical_score:.2f}, 利润评分:{profit_score:.2f}, "
                f"综合评分:{total_score:.2f}"
            )

            if total_score > best_score:
                best_score = total_score
                best_target = {
                    "price": candidate,
                    "technical_score": technical_score,
                    "profit_percent": profit_percent,
                    "profit_ratio": profit_ratio,
                    "total_score": total_score,
                    "reason": f"技术评分{technical_score:.2f}，利润空间{profit_percent:.2f}%",
                }
                self.logger.debug(
                    f"{symbol} : 3.2.2.3. 更新最佳候选位: {candidate:.{precision}f}"
                )

        return best_target

    def _validate_basic_requirements(
        self, current_price: float, target_price: float, side: str
    ) -> bool:
        """
        验证基础要求：最小利润空间和盈亏比

        Args:
            current_price: 当前价格
            target_price: 目标价格
            side: 交易方向

        Returns:
            bool: 是否满足基础要求
        """
        # 检查利润空间
        profit_percent = abs(target_price - current_price) / current_price * 100
        if profit_percent < self.config.min_profit_percent:
            return False

        # 检查盈亏比
        profit_ratio = self._calculate_profit_ratio(current_price, target_price, side)
        if profit_ratio < self.config.min_profit_ratio:
            return False

        return True

    def _calculate_profit_ratio(
        self, current_price: float, target_price: float, side: str
    ) -> float:
        """
        计算盈亏比

        Args:
            current_price: 当前价格
            target_price: 目标价格
            side: 交易方向

        Returns:
            float: 盈亏比
        """
        profit_distance = abs(target_price - current_price)
        # 简化计算：假设止损距离为利润距离的1/盈亏比
        stop_loss_distance = profit_distance / self.config.min_profit_ratio

        return profit_distance / stop_loss_distance if stop_loss_distance > 0 else 0.0

    def _calculate_technical_score(
        self, symbol: str, candidate_price: float, side: str, htf_result, atf_result
    ) -> float:
        """
        计算技术分析评分

        Args:
            symbol: 交易对符号
            candidate_price: 候选价格
            side: 交易方向
            htf_result: HTF分析结果
            atf_result: ATF分析结果

        Returns:
            float: 技术分析评分 (0-1)
        """
        try:
            # 如果有技术分析集成器，使用更精确的评分
            if (
                hasattr(self.strategy_maker, "technical_analysis_integrator")
                and self.strategy_maker.technical_analysis_integrator
            ):

                # 获取技术关键位
                technical_levels = self.strategy_maker.technical_analysis_integrator.find_technical_levels(
                    symbol=symbol,
                    current_price=candidate_price,
                    side=side,
                    search_range_percent=self.config.max_price_deviation_percent,
                    htf_result=htf_result,
                    atf_result=atf_result,
                )

                # 使用技术分析集成器评估评分
                return self.strategy_maker.technical_analysis_integrator.evaluate_target_technical_score(
                    target_price=candidate_price,
                    technical_levels=technical_levels,
                    side=side,
                )

            # 回退到基础实现
            score = 0.5  # 基础评分

            if side == self.strategy_maker.BUY_SIDE:
                # 多头：检查与阻力位的距离
                resistance_price = htf_result.resistance_price
                if resistance_price:
                    distance_percent = (
                        abs(candidate_price - resistance_price) / resistance_price * 100
                    )
                    # 距离阻力位越近，评分越高
                    if distance_percent < 1.0:
                        score += 0.4
                    elif distance_percent < 2.0:
                        score += 0.2
            else:
                # 空头：检查与支撑位的距离
                support_price = htf_result.support_price
                if support_price:
                    distance_percent = (
                        abs(candidate_price - support_price) / support_price * 100
                    )
                    # 距离支撑位越近，评分越高
                    if distance_percent < 1.0:
                        score += 0.4
                    elif distance_percent < 2.0:
                        score += 0.2

            return min(score, 1.0)

        except Exception as e:
            self.logger.debug(f"{symbol} : 技术分析评分计算异常: {e}")
            return 0.5
