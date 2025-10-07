# -*- coding: utf-8 -*-
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pandas as pd


@dataclass
class TechnicalLevel:
    """技术分析关键位"""

    price: float
    level_type: str  # 'support', 'resistance', 'liquidity', 'structure'
    strength: float  # 强度评分 0-1
    source: str  # 来源说明
    confidence: float  # 置信度 0-1


class TechnicalAnalysisIntegrator:
    """
    技术分析集成器
    集成现有SMC技术分析能力，为目标位搜索提供技术支持
    """

    def __init__(self, strategy_maker):
        """
        初始化技术分析集成器

        Args:
            strategy_maker: 策略制造器实例
        """
        self.strategy_maker = strategy_maker
        self.logger = strategy_maker.logger

    def find_technical_levels(
        self,
        symbol: str,
        current_price: float,
        side: str,
        search_range_percent: float,
        htf_result,
        atf_result,
    ) -> List[TechnicalLevel]:
        """
        寻找技术分析关键位

        Args:
            symbol: 交易对符号
            current_price: 当前价格
            side: 交易方向
            search_range_percent: 搜索范围百分比
            htf_result: HTF分析结果
            atf_result: ATF分析结果

        Returns:
            List[TechnicalLevel]: 技术关键位列表，按优先级排序
        """
        technical_levels = []

        try:
            # 1. 从HTF结果中提取支撑阻力位
            htf_levels = self._extract_htf_levels(
                htf_result, current_price, search_range_percent
            )
            technical_levels.extend(htf_levels)

            # 2. 从ATF结果中提取流动性聚集区
            atf_levels = self._extract_atf_levels(
                atf_result, current_price, search_range_percent
            )
            technical_levels.extend(atf_levels)

            # 3. 识别结构性关键位
            structure_levels = self._identify_structure_levels(
                symbol, current_price, side, search_range_percent
            )
            technical_levels.extend(structure_levels)

            # 4. 按优先级排序
            technical_levels = self._sort_by_priority(technical_levels, side)

            self.logger.debug(f"{symbol} : 找到{len(technical_levels)}个技术关键位")

        except Exception as e:
            self.logger.error(f"{symbol} : 技术分析关键位识别异常: {e}")

        return technical_levels

    def _extract_htf_levels(
        self, htf_result, current_price: float, search_range_percent: float
    ) -> List[TechnicalLevel]:
        """
        从HTF结果中提取支撑阻力位

        Args:
            htf_result: HTF分析结果
            current_price: 当前价格
            search_range_percent: 搜索范围百分比

        Returns:
            List[TechnicalLevel]: HTF技术位列表
        """
        levels = []
        search_range = current_price * search_range_percent / 100

        try:
            # 支撑位
            if hasattr(htf_result, "support_price") and htf_result.support_price:
                support_price = float(htf_result.support_price)
                if abs(support_price - current_price) <= search_range:
                    levels.append(
                        TechnicalLevel(
                            price=support_price,
                            level_type="support",
                            strength=0.8,  # HTF支撑位强度较高
                            source="HTF支撑位",
                            confidence=0.9,
                        )
                    )

            # 阻力位
            if hasattr(htf_result, "resistance_price") and htf_result.resistance_price:
                resistance_price = float(htf_result.resistance_price)
                if abs(resistance_price - current_price) <= search_range:
                    levels.append(
                        TechnicalLevel(
                            price=resistance_price,
                            level_type="resistance",
                            strength=0.8,  # HTF阻力位强度较高
                            source="HTF阻力位",
                            confidence=0.9,
                        )
                    )

        except Exception as e:
            self.logger.debug(f"HTF关键位提取异常: {e}")

        return levels

    def _extract_atf_levels(
        self, atf_result, current_price: float, search_range_percent: float
    ) -> List[TechnicalLevel]:
        """
        从ATF结果中提取流动性聚集区

        Args:
            atf_result: ATF分析结果
            current_price: 当前价格
            search_range_percent: 搜索范围百分比

        Returns:
            List[TechnicalLevel]: ATF技术位列表
        """
        levels = []
        search_range = current_price * search_range_percent / 100

        try:
            # 流动性聚集区
            if hasattr(atf_result, "liquidity_result") and atf_result.liquidity_result:
                liquidity_price = float(
                    atf_result.liquidity_result.get(
                        self.strategy_maker.EQUAL_POINTS_PRICE_COL, 0
                    )
                )
                liquidity_type = atf_result.liquidity_result.get(
                    self.strategy_maker.EQUAL_POINTS_TYPE_COL, ""
                )

                if (
                    liquidity_price > 0
                    and abs(liquidity_price - current_price) <= search_range
                ):
                    levels.append(
                        TechnicalLevel(
                            price=liquidity_price,
                            level_type="liquidity",
                            strength=0.7,  # 流动性聚集区强度中等
                            source=f"ATF流动性聚集区({liquidity_type})",
                            confidence=0.8,
                        )
                    )

        except Exception as e:
            self.logger.debug(f"ATF流动性位提取异常: {e}")

        return levels

    def _identify_structure_levels(
        self, symbol: str, current_price: float, side: str, search_range_percent: float
    ) -> List[TechnicalLevel]:
        """
        识别结构性关键位

        Args:
            symbol: 交易对符号
            current_price: 当前价格
            side: 交易方向
            search_range_percent: 搜索范围百分比

        Returns:
            List[TechnicalLevel]: 结构性关键位列表
        """
        levels = []

        try:
            # 获取最近的K线数据进行结构分析
            df = self.strategy_maker.get_historical_klines_df(
                symbol=symbol, tf="15m", limit=100
            )
            if df is None or len(df) < 20:
                return levels

            # 识别近期高低点
            recent_levels = self._find_recent_highs_lows(
                df, current_price, search_range_percent
            )
            levels.extend(recent_levels)

            # 识别成交量确认的关键位
            volume_levels = self._find_volume_confirmed_levels(
                df, current_price, search_range_percent
            )
            levels.extend(volume_levels)

        except Exception as e:
            self.logger.debug(f"结构性关键位识别异常: {e}")

        return levels

    def _find_recent_highs_lows(
        self, df: pd.DataFrame, current_price: float, search_range_percent: float
    ) -> List[TechnicalLevel]:
        """
        寻找近期高低点

        Args:
            df: K线数据
            current_price: 当前价格
            search_range_percent: 搜索范围百分比

        Returns:
            List[TechnicalLevel]: 近期高低点列表
        """
        levels = []
        search_range = current_price * search_range_percent / 100

        try:
            # 寻找局部高点
            for i in range(2, len(df) - 2):
                high = df.iloc[i][self.strategy_maker.HIGH_COL]
                if (
                    df.iloc[i - 2][self.strategy_maker.HIGH_COL] < high
                    and df.iloc[i - 1][self.strategy_maker.HIGH_COL] < high
                    and df.iloc[i + 1][self.strategy_maker.HIGH_COL] < high
                    and df.iloc[i + 2][self.strategy_maker.HIGH_COL] < high
                ):

                    if abs(high - current_price) <= search_range:
                        levels.append(
                            TechnicalLevel(
                                price=high,
                                level_type="resistance",
                                strength=0.6,
                                source="近期高点",
                                confidence=0.7,
                            )
                        )

            # 寻找局部低点
            for i in range(2, len(df) - 2):
                low = df.iloc[i][self.strategy_maker.LOW_COL]
                if (
                    df.iloc[i - 2][self.strategy_maker.LOW_COL] > low
                    and df.iloc[i - 1][self.strategy_maker.LOW_COL] > low
                    and df.iloc[i + 1][self.strategy_maker.LOW_COL] > low
                    and df.iloc[i + 2][self.strategy_maker.LOW_COL] > low
                ):

                    if abs(low - current_price) <= search_range:
                        levels.append(
                            TechnicalLevel(
                                price=low,
                                level_type="support",
                                strength=0.6,
                                source="近期低点",
                                confidence=0.7,
                            )
                        )

        except Exception as e:
            self.logger.debug(f"近期高低点识别异常: {e}")

        return levels

    def _find_volume_confirmed_levels(
        self, df: pd.DataFrame, current_price: float, search_range_percent: float
    ) -> List[TechnicalLevel]:
        """
        寻找成交量确认的关键位

        Args:
            df: K线数据
            current_price: 当前价格
            search_range_percent: 搜索范围百分比

        Returns:
            List[TechnicalLevel]: 成交量确认的关键位列表
        """
        levels = []
        search_range = current_price * search_range_percent / 100

        try:
            # 计算平均成交量
            avg_volume = df[self.strategy_maker.VOLUME_COL].mean()

            # 寻找高成交量的价格区域
            for i, row in df.iterrows():
                if (
                    row[self.strategy_maker.VOLUME_COL] > avg_volume * 1.5
                ):  # 成交量超过平均值1.5倍
                    price_level = (
                        row[self.strategy_maker.HIGH_COL]
                        + row[self.strategy_maker.LOW_COL]
                    ) / 2

                    if abs(price_level - current_price) <= search_range:
                        levels.append(
                            TechnicalLevel(
                                price=price_level,
                                level_type="structure",
                                strength=0.5,
                                source="高成交量确认",
                                confidence=0.6,
                            )
                        )

        except Exception as e:
            self.logger.debug(f"成交量确认关键位识别异常: {e}")

        return levels

    def _sort_by_priority(
        self, levels: List[TechnicalLevel], side: str
    ) -> List[TechnicalLevel]:
        """
        按优先级排序技术关键位

        Args:
            levels: 技术关键位列表
            side: 交易方向

        Returns:
            List[TechnicalLevel]: 排序后的技术关键位列表
        """
        # 计算综合优先级评分
        for level in levels:
            priority_score = level.strength * level.confidence

            # 根据交易方向调整优先级
            if side == self.strategy_maker.BUY_SIDE:
                # 多头优先考虑阻力位和流动性聚集区
                if level.level_type in ["resistance", "liquidity"]:
                    priority_score *= 1.2
            else:
                # 空头优先考虑支撑位和流动性聚集区
                if level.level_type in ["support", "liquidity"]:
                    priority_score *= 1.2

            level.priority_score = priority_score

        # 按优先级评分降序排序
        return sorted(
            levels, key=lambda x: getattr(x, "priority_score", 0), reverse=True
        )

    def evaluate_target_technical_score(
        self, target_price: float, technical_levels: List[TechnicalLevel], side: str
    ) -> float:
        """
        评估目标位的技术分析评分

        Args:
            target_price: 目标价格
            technical_levels: 技术关键位列表
            side: 交易方向

        Returns:
            float: 技术分析评分 (0-1)
        """
        if not technical_levels:
            return 0.5  # 无技术位信息时返回中性评分

        best_score = 0.0

        for level in technical_levels:
            # 计算价格距离
            distance_percent = abs(target_price - level.price) / level.price * 100

            # 距离越近，评分越高
            if distance_percent < 0.5:
                distance_score = 1.0
            elif distance_percent < 1.0:
                distance_score = 0.8
            elif distance_percent < 2.0:
                distance_score = 0.6
            else:
                distance_score = 0.3

            # 综合评分 = 距离评分 * 技术位强度 * 置信度
            total_score = distance_score * level.strength * level.confidence

            # 根据交易方向和技术位类型调整评分
            if side == self.strategy_maker.BUY_SIDE and level.level_type in [
                "resistance",
                "liquidity",
            ]:
                total_score *= 1.1
            elif side == self.strategy_maker.SELL_SIDE and level.level_type in [
                "support",
                "liquidity",
            ]:
                total_score *= 1.1

            best_score = max(best_score, total_score)

        return min(best_score, 1.0)
