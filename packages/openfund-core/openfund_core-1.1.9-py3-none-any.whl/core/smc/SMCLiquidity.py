import logging
import pandas as pd
from decimal import Decimal
from core.smc.SMCStruct import SMCStruct


class SMCLiquidity(SMCStruct):
    EQUAL_HIGH_COL = "equal_high"
    EQUAL_LOW_COL = "equal_low"
    LIQU_HIGH_COL = "liqu_high"
    LIQU_LOW_COL = "liqu_low"
    EQUAL_HIGH_INDEX_KEY = "equal_high_index"
    EQUAL_LOW_INDEX_KEY = "equal_low_index"
    HAS_EQ_KEY = "has_EQ"
    LIQU_HIGH_DIFF_COL = "liqu_high_diff"
    LIQU_LOW_DIFF_COL = "liqu_low_diff"

    # 新增等高等低点识别相关常量
    EQUAL_POINTS_TIMESTAMP_COL = "equal_points_timestamp"
    EQUAL_POINTS_INDEX_COL = "equal_points_index"
    EQUAL_POINTS_PRICE_COL = "equal_points_price"
    EQUAL_POINTS_TYPE_COL = "equal_points_type"
    EXTREME_INDEX_COL = "extreme_index"
    EXTREME_VALUE_COL = "extreme_value"
    ATR_TOLERANCE_COL = "atr_tolerance"
    IS_EXTREME_COL = "is_extreme"
    HAS_EQUAL_POINTS_COL = "has_equal_points"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # 调试配置
        self.debug_enabled = False
        self.debug_level = "INFO"  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
        self.debug_info_cache = {}

    def _identify_liquidity_pivots(self, data, pivot_length=1):
        """
        识别流动性的高点和低点
        """

        df = data.copy()

        # 识别高点
        df[self.LIQU_HIGH_COL] = Decimal(0.0)
        for i in range(pivot_length, len(df) - pivot_length):
            if df[self.HIGH_COL].iloc[i] == max(
                df[self.HIGH_COL].iloc[i - pivot_length : i + pivot_length + 1]
            ):
                df.loc[df.index[i], self.LIQU_HIGH_COL] = df[self.HIGH_COL].iloc[i]
        # 识别低点
        df[self.LIQU_LOW_COL] = Decimal(0.0)
        for i in range(pivot_length, len(df) - pivot_length):
            if df[self.LOW_COL].iloc[i] == min(
                df[self.LOW_COL].iloc[i - pivot_length : i + pivot_length + 1]
            ):
                df.loc[df.index[i], self.LIQU_LOW_COL] = df[self.LOW_COL].iloc[i]

        return df

    def find_EQH_EQL(self, data, trend, end_idx=-1, atr_offset=0.1) -> dict:
        """_summary_
        识别等高等低流动性
        Args:
            data (_type_): _description_
            trend (_type_): _description_
            end_idx (int, optional): _description_. Defaults to -1.
            atr_offset (float, optional): _description_. Defaults to 0.1.

        Returns:
            dict: _description_
        """

        df = data.copy() if end_idx == -1 else data.copy().iloc[: end_idx + 1]

        check_columns = [self.LIQU_HIGH_COL, self.LIQU_LOW_COL]

        try:
            self.check_columns(df, check_columns)
        except ValueError as e:
            # self.logger.warning(f"DataFrame must contain columns {check_columns} : {str(e)}")
            df = self._identify_liquidity_pivots(df)

        df = df[(df[self.LIQU_HIGH_COL] > 0) | (df[self.LIQU_LOW_COL] > 0)]
        # 初始化结果列
        df[self.EQUAL_HIGH_COL] = 0
        df[self.EQUAL_LOW_COL] = 0
        atr_df = self.calculate_atr(df)
        df[self.ATR_COL] = atr_df[self.ATR_COL]
        # 跟踪前一个高点和低点
        previous_high = None
        previous_high_index = None
        previous_high_pos = -1
        previous_low = None
        previous_low_index = None
        previous_low_pos = -1
        for i in range(len(df) - 1, -1, -1):
            offset = self.toDecimal(
                self.toDecimal(df[self.ATR_COL].iloc[i]) * self.toDecimal(atr_offset)
            )

            if trend == self.BULLISH_TREND:
                current_high = df[self.LIQU_HIGH_COL].iloc[i]
                if current_high == 0:
                    continue

                if previous_high is None:
                    previous_high = current_high
                    previous_high_index = df.index[i]
                    previous_high_pos = i
                    continue

                max_val = max(current_high, previous_high)
                min_val = min(current_high, previous_high)

                if abs(max_val - min_val) <= offset:  # EQH|EQL
                    df.loc[df.index[i], self.EQUAL_HIGH_COL] = previous_high_index
                    df.loc[df.index[previous_high_pos], self.EQUAL_HIGH_COL] = (
                        previous_high_index
                    )

                else:
                    # 倒序遍历，等高线被高点破坏，则更新等高点位置
                    if current_high > previous_high:
                        previous_high = current_high
                        previous_high_index = df.index[i]
                        previous_high_pos = i

            else:
                current_low = df[self.LIQU_LOW_COL].iloc[i]
                if current_low == 0:
                    continue

                # current_low = df[self.EQUAL_LOW_COL].iloc[i]
                if previous_low is None:
                    previous_low = current_low
                    previous_low_index = df.index[i]
                    previous_low_pos = i
                    continue

                max_val = max(current_low, previous_low)
                min_val = min(current_low, previous_low)

                if abs(max_val - min_val) <= offset:  # EQH|EQL
                    df.loc[df.index[i], self.EQUAL_LOW_COL] = previous_low_index
                    df.loc[df.index[previous_low_pos], self.EQUAL_LOW_COL] = (
                        previous_low_index
                    )

                else:
                    # 倒序遍历，等高线被高点破坏，则更新等高点位置
                    if current_low < previous_low:
                        previous_low = current_low
                        previous_low_index = df.index[i]
                        previous_low_pos = i

        # 筛选有效结构且在prd范围内的数据
        last_EQ = {}
        if trend == self.BULLISH_TREND:
            mask = df[self.EQUAL_HIGH_COL] > 0
            valid_EQH_df = df[mask]
            if not valid_EQH_df.empty:
                last_EQ[self.HAS_EQ_KEY] = True
                last_EQ[self.EQUAL_HIGH_COL] = valid_EQH_df.iloc[-1][self.LIQU_HIGH_COL]
                last_EQ[self.EQUAL_HIGH_INDEX_KEY] = valid_EQH_df.iloc[-1][
                    self.EQUAL_HIGH_COL
                ]
                last_EQ[self.TIMESTAMP_COL] = valid_EQH_df.iloc[-1][self.TIMESTAMP_COL]
        else:
            mask = df[self.EQUAL_LOW_COL] > 0
            valid_EQL_df = df[mask]
            if not valid_EQL_df.empty:
                last_EQ[self.HAS_EQ_KEY] = True
                last_EQ[self.EQUAL_LOW_COL] = valid_EQL_df.iloc[-1][self.LIQU_LOW_COL]
                last_EQ[self.EQUAL_LOW_INDEX_KEY] = valid_EQL_df.iloc[-1][
                    self.EQUAL_LOW_COL
                ]
                last_EQ[self.TIMESTAMP_COL] = valid_EQL_df.iloc[-1][self.TIMESTAMP_COL]

        return last_EQ

    def identify_dynamic_trendlines(
        self, data, trend, start_idx=-1, end_idx=-1, ratio=0.8
    ) -> tuple:
        """
        识别动态趋势线或隧道
        Args:
            data (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """

        df = (
            data.copy()
            if start_idx == -1 or end_idx == -1
            else data.copy().iloc[start_idx - 1 : end_idx + 2]
        )  # 考虑poivt值，前后各增加一个

        check_columns = [self.LIQU_HIGH_COL]

        try:
            self.check_columns(df, check_columns)
        except ValueError as e:
            self.logger.warning(
                f"DataFrame must contain columns {check_columns} : {str(e)}"
            )
            df = self._identify_liquidity_pivots(df)
        diff_ratio = 0.0
        if trend == self.BEARISH_TREND:
            # 判断Bearish趋势是高点不断升高,
            liqu_bear_df = df[df[self.LIQU_HIGH_COL] > 0]
            liqu_bear_df[self.LIQU_HIGH_DIFF_COL] = liqu_bear_df[
                self.LIQU_HIGH_COL
            ].diff()
            # self.logger.info(f"dynamic_trendlines:\n {liqu_bear_df[[self.TIMESTAMP_COL,self.LIQU_HIGH_COL,self.LIQU_HIGH_DIFF_COL]]}")
            diff_ratio = self.toDecimal(
                liqu_bear_df[self.LIQU_HIGH_DIFF_COL].dropna().lt(0).mean(), 2
            )
            if diff_ratio >= ratio:
                return diff_ratio, True
        else:
            # Bullish趋势是低点不断降低
            liqu_bullish_df = df[df[self.LIQU_LOW_COL] > 0]
            liqu_bullish_df[self.LIQU_LOW_DIFF_COL] = liqu_bullish_df[
                self.LIQU_LOW_COL
            ].diff()
            # self.logger.info(f"dynamic_trendlines:\n {liqu_bullish_df[[self.TIMESTAMP_COL,self.LIQU_LOW_COL,self.LIQU_LOW_DIFF_COL]]}")
            diff_ratio = self.toDecimal(
                liqu_bullish_df[self.LIQU_LOW_DIFF_COL].dropna().gt(0).mean(), 2
            )
            if diff_ratio >= ratio:
                return diff_ratio, True

        return diff_ratio, False

    def find_extreme_point_in_range(self, data, point_type="high"):
        """在当前K线范围内找到极值点（最高点或最低点）

        Args:
            data: 价格数据DataFrame
            point_type: 'high' 或 'low'

        Returns:
            (extreme_index, extreme_value) 极值点索引和值

        Raises:
            ValueError: 当输入数据无效时
        """
        # 输入验证
        if data.empty:
            self.logger.warning("输入数据为空，无法找到极值点")
            return None, None

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        # 验证必需的列存在
        required_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
        if required_col not in data.columns:
            raise ValueError(f"DataFrame必须包含列: {required_col}")

        try:
            if point_type == "high":
                extreme_index = data[self.HIGH_COL].idxmax()
                extreme_value = data[self.HIGH_COL].loc[extreme_index]
            else:  # point_type == 'low'
                extreme_index = data[self.LOW_COL].idxmin()
                extreme_value = data[self.LOW_COL].loc[extreme_index]

            # 验证找到的极值点是有效的
            if pd.isna(extreme_value):
                self.logger.warning(f"找到的{point_type}极值点包含NaN值")
                return None, None

            self.logger.debug(
                f"找到{point_type}极值点: 索引={extreme_index}, 值={extreme_value}"
            )
            return extreme_index, extreme_value

        except Exception as e:
            self.logger.error(f"查找极值点时发生错误: {str(e)}")
            return None, None

    def is_swing_point(self, data, index, point_type="high", lookback=1):
        """验证某个点是否为有效的swing point

        Args:
            data: 价格数据DataFrame
            index: 要验证的点的索引
            point_type: 'high' 或 'low'
            lookback: 左右两边需要比较的K线数量

        Returns:
            bool: 如果是有效的swing point返回True，否则返回False
        """
        result, _ = self.is_swing_point_enhanced(data, index, point_type, lookback)
        return result

    def is_swing_point_enhanced(self, data, index, point_type="high", lookback=1):
        """增强版swing point验证，提供详细的验证失败原因

        Args:
            data: 价格数据DataFrame
            index: 要验证的点的索引
            point_type: 'high' 或 'low'
            lookback: 左右两边需要比较的K线数量

        Returns:
            tuple: (is_valid, validation_info)
                - is_valid: bool, 是否为有效的swing point
                - validation_info: dict, 详细的验证信息
        """
        validation_info = {
            "is_valid": False,
            "index": index,
            "point_type": point_type,
            "lookback": lookback,
            "current_value": None,
            "position": None,
            "boundary_check": {"passed": False, "reason": ""},
            "left_neighbors": [],
            "right_neighbors": [],
            "validation_failures": [],
            "error_message": None,
        }

        try:
            # 边界检查和基本验证
            if data.empty:
                validation_info["boundary_check"]["reason"] = "输入数据为空"
                return False, validation_info

            if point_type not in ["high", "low"]:
                validation_info["boundary_check"][
                    "reason"
                ] = f"无效的point_type: {point_type}"
                return False, validation_info

            if index not in data.index:
                validation_info["boundary_check"][
                    "reason"
                ] = f"索引 {index} 不在数据范围内"
                return False, validation_info

            # 检查价格列是否存在
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
            if price_col not in data.columns:
                validation_info["boundary_check"][
                    "reason"
                ] = f"DataFrame缺少必需的列: {price_col}"
                return False, validation_info

            # 获取索引在DataFrame中的位置
            try:
                position = data.index.get_loc(index)
                validation_info["position"] = position
            except KeyError:
                validation_info["boundary_check"][
                    "reason"
                ] = f"无法获取索引 {index} 的位置"
                return False, validation_info

            # 检查是否有足够的数据进行比较
            if position < lookback:
                validation_info["boundary_check"][
                    "reason"
                ] = f"左边数据不足，位置={position}, 需要lookback={lookback}"
                return False, validation_info

            if position >= len(data) - lookback:
                validation_info["boundary_check"][
                    "reason"
                ] = f"右边数据不足，位置={position}, 数据长度={len(data)}, 需要lookback={lookback}"
                return False, validation_info

            validation_info["boundary_check"]["passed"] = True

            current_value = data[price_col].loc[index]
            validation_info["current_value"] = current_value

            if pd.isna(current_value):
                validation_info["validation_failures"].append("当前值为NaN")
                return False, validation_info

            # 检查左边的邻居
            for i in range(1, lookback + 1):
                left_index = data.index[position - i]
                left_value = data[price_col].loc[left_index]

                neighbor_info = {
                    "index": left_index,
                    "value": left_value,
                    "distance": i,
                    "is_nan": pd.isna(left_value),
                    "comparison_result": None,
                    "passes_check": None,
                }

                if pd.isna(left_value):
                    neighbor_info["comparison_result"] = "跳过NaN值"
                    neighbor_info["passes_check"] = True  # NaN值不影响验证
                else:
                    if point_type == "high":
                        # 对于swing high，当前点应该比左边的点高
                        passes = current_value >= left_value
                        neighbor_info["comparison_result"] = (
                            f"当前值{current_value} {'≥' if passes else '<'} 左邻居{left_value}"
                        )
                        neighbor_info["passes_check"] = passes
                        if not passes:
                            validation_info["validation_failures"].append(
                                f"左邻居检查失败: 当前值{current_value} < 左邻居{left_value} (距离={i})"
                            )
                    else:  # point_type == 'low'
                        # 对于swing low，当前点应该比左边的点低
                        passes = current_value <= left_value
                        neighbor_info["comparison_result"] = (
                            f"当前值{current_value} {'≤' if passes else '>'} 左邻居{left_value}"
                        )
                        neighbor_info["passes_check"] = passes
                        if not passes:
                            validation_info["validation_failures"].append(
                                f"左邻居检查失败: 当前值{current_value} > 左邻居{left_value} (距离={i})"
                            )

                validation_info["left_neighbors"].append(neighbor_info)

            # 检查右边的邻居
            for i in range(1, lookback + 1):
                if position + i >= len(data):
                    break

                right_index = data.index[position + i]
                right_value = data[price_col].loc[right_index]

                neighbor_info = {
                    "index": right_index,
                    "value": right_value,
                    "distance": i,
                    "is_nan": pd.isna(right_value),
                    "comparison_result": None,
                    "passes_check": None,
                }

                if pd.isna(right_value):
                    neighbor_info["comparison_result"] = "跳过NaN值"
                    neighbor_info["passes_check"] = True  # NaN值不影响验证
                else:
                    if point_type == "high":
                        # 对于swing high，当前点应该比右边的点高
                        passes = current_value >= right_value
                        neighbor_info["comparison_result"] = (
                            f"当前值{current_value} {'≥' if passes else '<'} 右邻居{right_value}"
                        )
                        neighbor_info["passes_check"] = passes
                        if not passes:
                            validation_info["validation_failures"].append(
                                f"右邻居检查失败: 当前值{current_value} < 右邻居{right_value} (距离={i})"
                            )
                    else:  # point_type == 'low'
                        # 对于swing low，当前点应该比右边的点低
                        passes = current_value <= right_value
                        neighbor_info["comparison_result"] = (
                            f"当前值{current_value} {'≤' if passes else '>'} 右邻居{right_value}"
                        )
                        neighbor_info["passes_check"] = passes
                        if not passes:
                            validation_info["validation_failures"].append(
                                f"右邻居检查失败: 当前值{current_value} > 右邻居{right_value} (距离={i})"
                            )

                validation_info["right_neighbors"].append(neighbor_info)

            # 判断最终结果
            is_valid = len(validation_info["validation_failures"]) == 0
            validation_info["is_valid"] = is_valid

            return is_valid, validation_info

        except Exception as e:
            error_msg = f"验证swing point时发生错误: {str(e)}"
            validation_info["error_message"] = error_msg
            self.logger.error(error_msg)
            return False, validation_info

    def find_extreme_point_in_range_with_swing_validation(
        self, data, point_type="high", lookback=1
    ):
        """在当前K线范围内找到有效的swing point极值点

        Args:
            data: 价格数据DataFrame
            point_type: 'high' 或 'low'
            lookback: swing point验证的lookback周期

        Returns:
            (extreme_index, extreme_value) 极值点索引和值，如果没有有效的swing point则返回None
        """
        # 输入验证
        if data.empty:
            self.logger.warning("输入数据为空，无法找到极值点")
            return None, None

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        # 验证必需的列存在
        required_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
        if required_col not in data.columns:
            raise ValueError(f"DataFrame必须包含列: {required_col}")

        try:
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

            # 找到所有可能的极值点（排除边界点，因为它们无法验证swing point）
            valid_range = (
                data.iloc[lookback:-lookback]
                if len(data) > 2 * lookback
                else pd.DataFrame()
            )

            if valid_range.empty:
                self.logger.warning(
                    f"数据量不足以进行swing point验证，需要至少 {2 * lookback + 1} 个数据点"
                )
                return None, None

            # 在有效范围内找到极值
            if point_type == "high":
                extreme_index = valid_range[price_col].idxmax()
                extreme_value = valid_range[price_col].loc[extreme_index]
            else:
                extreme_index = valid_range[price_col].idxmin()
                extreme_value = valid_range[price_col].loc[extreme_index]

            # 验证是否为有效的swing point
            if self.is_swing_point(data, extreme_index, point_type, lookback):
                self.logger.debug(
                    f"找到有效的{point_type} swing point: 索引={extreme_index}, 值={extreme_value}"
                )
                return extreme_index, extreme_value
            else:
                self.logger.debug(
                    f"找到的{point_type}极值点不是有效的swing point: 索引={extreme_index}"
                )
                return None, None

        except Exception as e:
            self.logger.error(f"查找swing point极值点时发生错误: {str(e)}")
            return None, None

    def find_next_swing_point_in_range(self, data, point_type="high", lookback=1):
        """在当前范围内找到极值swing point（最高点或最低点）

        Args:
            data: 价格数据DataFrame
            point_type: 'high' 或 'low'
            lookback: swing point验证的lookback周期

        Returns:
            (swing_index, swing_value) 极值swing point的索引和值
        """
        # 输入验证
        if data.empty:
            return None, None

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

        if price_col not in data.columns:
            raise ValueError(f"DataFrame必须包含列: {price_col}")

        try:
            # 首先收集所有有效的swing points
            valid_swing_points = []

            for i in range(lookback, len(data) - lookback):
                current_index = data.index[i]

                # 验证是否为swing point
                if self.is_swing_point(data, current_index, point_type, lookback):
                    current_value = data[price_col].loc[current_index]
                    valid_swing_points.append((current_index, current_value))

            if not valid_swing_points:
                self.logger.debug(f"在范围内未找到{point_type} swing point")
                return None, None

            # 从所有有效的swing points中找到极值点
            if point_type == "high":
                # 找最高点
                extreme_index, extreme_value = max(
                    valid_swing_points, key=lambda x: x[1]
                )
            else:  # point_type == "low"
                # 找最低点
                extreme_index, extreme_value = min(
                    valid_swing_points, key=lambda x: x[1]
                )

            self.logger.debug(
                f"找到极值{point_type} swing point: 索引={extreme_index}, 值={extreme_value}，从{len(valid_swing_points)}个候选点中选出"
            )
            return extreme_index, extreme_value

        except Exception as e:
            self.logger.error(f"查找极值swing point时发生错误: {str(e)}")
            return None, None

    def check_equal_points_from_extreme(
        self,
        data,
        extreme_index,
        extreme_value,
        atr_value,
        atr_offset,
        point_type="high",
        min_distance=2,
        lookback=1,
    ):
        """从极值点向前搜索等点（只考虑有效的swing points）

        Args:
            data: 价格数据DataFrame
            extreme_index: 极值点索引
            extreme_value: 极值点价格值
            atr_value: ATR值
            atr_offset: ATR偏移量
            point_type: 'high' 或 'low'
            min_distance: 最小间隔距离，相邻节点不算等点（默认为2，即至少间隔1个节点）
            lookback: swing point验证的lookback周期

        Returns:
            符合条件的等点列表，每个元素包含index, value, timestamp

        Raises:
            ValueError: 当输入参数无效时
        """
        # 输入验证
        if data.empty:
            self.logger.warning("输入数据为空，无法搜索等点")
            return []

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        if extreme_index not in data.index:
            raise ValueError(f"极值点索引 {extreme_index} 不在数据范围内")

        if min_distance < 1:
            raise ValueError("min_distance必须大于等于1")

        # 计算容差
        try:
            tolerance = self.calculate_atr_tolerance(atr_value, atr_offset)
        except ValueError as e:
            self.logger.error(f"计算容差失败: {str(e)}")
            return []

        equal_points = []
        price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

        # 验证价格列存在
        if price_col not in data.columns:
            raise ValueError(f"DataFrame必须包含列: {price_col}")

        try:
            # 获取极值点在DataFrame中的位置
            extreme_position = data.index.get_loc(extreme_index)

            # 从极值点索引向前搜索（按需求从最大值索引向前寻找）
            # 但要排除相邻的节点（距离小于min_distance的节点）
            for i in range(extreme_position):
                current_index = data.index[i]
                current_value = data[price_col].loc[current_index]

                # 跳过NaN值
                if pd.isna(current_value):
                    continue

                # 验证该点是否为有效的swing point
                if not self.is_swing_point(data, current_index, point_type, lookback):
                    self.logger.debug(f"跳过非swing point: 索引={current_index}")
                    continue

                # 检查距离约束：相邻节点不算等点
                distance = extreme_position - i
                if distance < min_distance:
                    self.logger.debug(
                        f"跳过相邻节点: 索引={current_index}, 距离={distance} < {min_distance}"
                    )
                    continue

                # 检查是否在容差范围内
                price_diff = abs(
                    self.toDecimal(current_value) - self.toDecimal(extreme_value)
                )
                if price_diff <= tolerance:
                    # 检查中间是否有更极端的点（关键的SMC规则）
                    if self._has_intermediate_more_extreme_point_simple(
                        data, current_index, extreme_index, point_type
                    ):
                        self.logger.debug(
                            f"跳过等点候选: 索引={current_index}，因为中间有更极端的点"
                        )
                        continue

                    equal_point = {
                        "index": current_index,
                        "value": current_value,
                        "timestamp": (
                            data[self.TIMESTAMP_COL].loc[current_index]
                            if self.TIMESTAMP_COL in data.columns
                            else None
                        ),
                        "price_diff": price_diff,
                        "tolerance_used": tolerance,
                        "distance_from_extreme": distance,
                    }
                    equal_points.append(equal_point)

            self.logger.debug(
                f"找到 {len(equal_points)} 个{point_type}等点（仅swing points），极值点索引: {extreme_index}，排除了相邻节点（最小距离: {min_distance}）"
            )

        except Exception as e:
            self.logger.error(f"搜索等点时发生错误: {str(e)}")
            return []

        return equal_points

    def _has_intermediate_more_extreme_point_simple(
        self, data, first_extreme_index, second_extreme_index, point_type
    ):
        """检查两个极值点之间是否有更极端的点（简化版，用于单点检查）

        Args:
            data: 价格数据DataFrame
            first_extreme_index: 第一个极值点索引（较早的）
            second_extreme_index: 第二个极值点索引（较晚的）
            point_type: 'high' 或 'low'

        Returns:
            bool: 如果中间有更极端的点返回True，否则返回False
        """
        try:
            # 获取两个极值点的位置
            first_position = data.index.get_loc(first_extreme_index)
            second_position = data.index.get_loc(second_extreme_index)

            # 确保first在second之前
            if first_position >= second_position:
                first_position, second_position = second_position, first_position
                first_extreme_index, second_extreme_index = (
                    second_extreme_index,
                    first_extreme_index,
                )

            # 获取两个极值点的价格
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
            first_value = data[price_col].loc[first_extreme_index]
            second_value = data[price_col].loc[second_extreme_index]

            # 计算等点的参考值（两个点的最极端值）
            if point_type == "high":
                reference_value = max(first_value, second_value)
            else:
                reference_value = min(first_value, second_value)

            # 检查中间区域的所有点
            intermediate_data = data.iloc[first_position + 1 : second_position]

            for idx, row in intermediate_data.iterrows():
                intermediate_value = row[price_col]

                if pd.isna(intermediate_value):
                    continue

                # 检查中间点是否更极端
                violation_detected = False
                if point_type == "high":
                    # 对于高点，如果中间有更高的点，则破坏等高点关系
                    if intermediate_value > reference_value:
                        violation_detected = True
                else:  # point_type == 'low'
                    # 对于低点，如果中间有更低的点，则破坏等低点关系
                    if intermediate_value < reference_value:
                        violation_detected = True

                if violation_detected:
                    self.logger.debug(
                        f"发现中间违规点破坏了索引{first_extreme_index}({first_value})和{second_extreme_index}({second_value})的等{point_type}点关系: "
                        f"中间点索引={idx}, 值={intermediate_value}"
                    )
                    return True

            return False

        except Exception as e:
            self.logger.error(f"检查中间极值点时发生错误: {str(e)}")
            return True  # 出错时保守地返回True，避免错误识别

    def check_equal_points_from_all_extremes(
        self,
        data,
        all_extreme_points,
        current_extreme_index,
        current_extreme_value,
        atr_value,
        atr_offset,
        point_type="high",
        min_distance=2,
        lookback=1,
    ):
        """从所有已知极值点中搜索等点（只考虑有效的swing points）

        Args:
            data: 价格数据DataFrame
            all_extreme_points: 所有已找到的极值点列表
            current_extreme_index: 当前极值点索引
            current_extreme_value: 当前极值点价格值
            atr_value: ATR值
            atr_offset: ATR偏移量
            point_type: 'high' 或 'low'
            min_distance: 最小间隔距离，相邻节点不算等点
            lookback: swing point验证的lookback周期

        Returns:
            符合条件的等点列表
        """
        # 输入验证
        if data.empty:
            self.logger.warning("输入数据为空，无法搜索等点")
            return []

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        if current_extreme_index not in data.index:
            raise ValueError(f"当前极值点索引 {current_extreme_index} 不在数据范围内")

        # 计算容差
        try:
            tolerance = self.calculate_atr_tolerance(atr_value, atr_offset)
        except ValueError as e:
            self.logger.error(f"计算容差失败: {str(e)}")
            return []

        equal_points = []
        price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

        # 验证价格列存在
        if price_col not in data.columns:
            raise ValueError(f"DataFrame必须包含列: {price_col}")

        try:
            # 获取当前极值点在DataFrame中的位置
            current_position = data.index.get_loc(current_extreme_index)

            # 从所有已知极值点中搜索等点
            for extreme_point in all_extreme_points:
                candidate_index = extreme_point["index"]
                candidate_value = extreme_point["value"]

                # 跳过当前极值点自己
                if candidate_index == current_extreme_index:
                    continue

                # 获取候选点的位置
                candidate_position = data.index.get_loc(candidate_index)

                # 检查距离约束：相邻节点不算等点
                distance = abs(current_position - candidate_position)
                if distance < min_distance:
                    self.logger.debug(
                        f"跳过相邻节点: 索引={candidate_index}, 距离={distance} < {min_distance}"
                    )
                    continue

                # 验证该点是否为有效的swing point
                if not self.is_swing_point(data, candidate_index, point_type, lookback):
                    self.logger.debug(f"跳过非swing point: 索引={candidate_index}")
                    continue

                # 检查是否在容差范围内
                price_diff = abs(
                    self.toDecimal(candidate_value)
                    - self.toDecimal(current_extreme_value)
                )
                if price_diff <= tolerance:
                    # 检查平衡约束
                    if not self.check_balance_constraint(
                        data, candidate_index, current_extreme_index, point_type
                    ):
                        self.logger.debug(
                            f"跳过等点候选: 索引={candidate_index}，因为违反平衡约束"
                        )
                        continue

                    equal_point = {
                        "index": candidate_index,
                        "value": candidate_value,
                        "timestamp": (
                            data[self.TIMESTAMP_COL].loc[candidate_index]
                            if self.TIMESTAMP_COL in data.columns
                            else None
                        ),
                        "price_diff": price_diff,
                        "tolerance_used": tolerance,
                        "distance_from_extreme": distance,
                    }
                    equal_points.append(equal_point)

            self.logger.debug(
                f"从{len(all_extreme_points)}个极值点中找到 {len(equal_points)} 个{point_type}等点"
            )

        except Exception as e:
            self.logger.error(f"搜索等点时发生错误: {str(e)}")
            return []

        return equal_points

    def check_balance_constraint(self, data, point1_index, point2_index, point_type):
        """检查两个候选等点之间是否存在被平衡的点

        Args:
            data: 价格数据DataFrame
            point1_index: 第一个候选点索引
            point2_index: 第二个候选点索引
            point_type: 'high' 或 'low'

        Returns:
            True如果没有平衡约束违反，False如果存在平衡约束违反
        """
        try:
            # 输入验证
            if data.empty:
                self.logger.warning("输入数据为空，无法检查平衡约束")
                return False

            if point_type not in ["high", "low"]:
                raise ValueError("point_type必须是'high'或'low'")

            if point1_index not in data.index or point2_index not in data.index:
                raise ValueError("候选点索引不在数据范围内")

            # 确保point1_index < point2_index（按时间顺序）
            pos1 = data.index.get_loc(point1_index)
            pos2 = data.index.get_loc(point2_index)

            start_pos = min(pos1, pos2)
            end_pos = max(pos1, pos2)
            start_idx = data.index[start_pos]
            end_idx = data.index[end_pos]

            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

            # 检查中间区域的所有点
            for i in range(start_pos + 1, end_pos):
                current_index = data.index[i]
                current_value = data[price_col].loc[current_index]

                if pd.isna(current_value):
                    continue

                # 检查当前点是否被后续点平衡
                for j in range(i + 1, len(data)):
                    future_index = data.index[j]
                    future_value = data[price_col].loc[future_index]

                    if pd.isna(future_value):
                        continue

                    if point_type == "high":
                        # 检查是否存在高点被后续更高点平衡
                        if future_value > current_value:
                            self.logger.debug(
                                f"发现平衡约束违反: 高点{current_index}({current_value})被{future_index}({future_value})平衡"
                            )
                            return False
                    else:  # point_type == 'low'
                        # 检查是否存在低点被后续更低点平衡
                        if future_value < current_value:
                            self.logger.debug(
                                f"发现平衡约束违反: 低点{current_index}({current_value})被{future_index}({future_value})平衡"
                            )
                            return False

            return True  # 没有发现平衡约束违反

        except Exception as e:
            self.logger.error(f"检查平衡约束时发生错误: {str(e)}")
            return False  # 出错时保守地返回False

    def create_equal_points_dataframe(self, equal_points_data, extreme_point_info=None):
        """创建标准的等高等低点DataFrame输出格式

        Args:
            equal_points_data: 等点数据列表，每个元素包含index, value, timestamp等信息
            extreme_point_info: 极值点信息字典，包含extreme_index, extreme_value等

        Returns:
            pd.DataFrame: 包含所有必需列的DataFrame
        """
        try:
            # 定义DataFrame的标准列结构
            columns = [
                self.TIMESTAMP_COL,  # timestamp: K线时间信息
                self.EQUAL_POINTS_INDEX_COL,  # index: 索引位置
                self.EQUAL_POINTS_PRICE_COL,  # price_value: 实际价格值
                self.EQUAL_POINTS_TYPE_COL,  # point_type: 'equal_high' 或 'equal_low'
                self.EXTREME_INDEX_COL,  # extreme_index: 对应的极值点索引
                self.EXTREME_VALUE_COL,  # extreme_value: 对应的极值点价格
                self.ATR_TOLERANCE_COL,  # atr_tolerance: 使用的ATR容差值
                self.IS_EXTREME_COL,  # is_extreme: 是否为极值点
                self.HAS_EQUAL_POINTS_COL,  # has_equal_points: 是否存在等点
            ]

            # 如果没有等点数据，返回空DataFrame但保持列结构
            if not equal_points_data:
                empty_df = pd.DataFrame(columns=columns)
                # 设置正确的数据类型
                empty_df[self.TIMESTAMP_COL] = pd.to_datetime(
                    empty_df[self.TIMESTAMP_COL]
                )
                empty_df[self.EQUAL_POINTS_INDEX_COL] = empty_df[
                    self.EQUAL_POINTS_INDEX_COL
                ].astype("Int64")
                empty_df[self.EQUAL_POINTS_PRICE_COL] = empty_df[
                    self.EQUAL_POINTS_PRICE_COL
                ].astype("float64")
                empty_df[self.EQUAL_POINTS_TYPE_COL] = empty_df[
                    self.EQUAL_POINTS_TYPE_COL
                ].astype("string")
                empty_df[self.EXTREME_INDEX_COL] = empty_df[
                    self.EXTREME_INDEX_COL
                ].astype("Int64")
                empty_df[self.EXTREME_VALUE_COL] = empty_df[
                    self.EXTREME_VALUE_COL
                ].astype("float64")
                empty_df[self.ATR_TOLERANCE_COL] = empty_df[
                    self.ATR_TOLERANCE_COL
                ].astype("float64")
                empty_df[self.IS_EXTREME_COL] = empty_df[self.IS_EXTREME_COL].astype(
                    "boolean"
                )
                empty_df[self.HAS_EQUAL_POINTS_COL] = empty_df[
                    self.HAS_EQUAL_POINTS_COL
                ].astype("boolean")

                self.logger.debug("创建空的等点DataFrame，保持标准列结构")
                return empty_df

            # 构建DataFrame数据
            df_data = []

            for point_data in equal_points_data:
                # 判断是否有等点：优先使用传入的值，否则根据点类型判断
                if "has_equal_points" in point_data:
                    has_equal_points = point_data.get("has_equal_points")
                else:
                    has_equal_points = point_data.get("point_type", "").startswith(
                        "equal_"
                    )

                row = {
                    self.TIMESTAMP_COL: point_data.get("timestamp"),
                    self.EQUAL_POINTS_INDEX_COL: point_data.get("index"),
                    self.EQUAL_POINTS_PRICE_COL: float(point_data.get("value", 0)),
                    self.EQUAL_POINTS_TYPE_COL: point_data.get("point_type", ""),
                    self.EXTREME_INDEX_COL: (
                        extreme_point_info.get("extreme_index")
                        if extreme_point_info
                        else None
                    ),
                    self.EXTREME_VALUE_COL: (
                        float(extreme_point_info.get("extreme_value", 0))
                        if extreme_point_info
                        else None
                    ),
                    self.ATR_TOLERANCE_COL: float(point_data.get("tolerance_used", 0)),
                    self.IS_EXTREME_COL: point_data.get("is_extreme", False),
                    self.HAS_EQUAL_POINTS_COL: has_equal_points,
                }
                df_data.append(row)

            # 创建DataFrame
            result_df = pd.DataFrame(df_data, columns=columns)

            # 设置正确的数据类型
            result_df[self.TIMESTAMP_COL] = pd.to_datetime(
                result_df[self.TIMESTAMP_COL]
            )
            result_df[self.EQUAL_POINTS_INDEX_COL] = result_df[
                self.EQUAL_POINTS_INDEX_COL
            ].astype("Int64")
            result_df[self.EQUAL_POINTS_PRICE_COL] = result_df[
                self.EQUAL_POINTS_PRICE_COL
            ].astype("float64")
            result_df[self.EQUAL_POINTS_TYPE_COL] = result_df[
                self.EQUAL_POINTS_TYPE_COL
            ].astype("string")
            result_df[self.EXTREME_INDEX_COL] = result_df[
                self.EXTREME_INDEX_COL
            ].astype("Int64")
            result_df[self.EXTREME_VALUE_COL] = result_df[
                self.EXTREME_VALUE_COL
            ].astype("float64")
            result_df[self.ATR_TOLERANCE_COL] = result_df[
                self.ATR_TOLERANCE_COL
            ].astype("float64")
            result_df[self.IS_EXTREME_COL] = result_df[self.IS_EXTREME_COL].astype(
                "boolean"
            )
            result_df[self.HAS_EQUAL_POINTS_COL] = result_df[
                self.HAS_EQUAL_POINTS_COL
            ].astype("boolean")

            # 按时间顺序排序
            if not result_df.empty and self.TIMESTAMP_COL in result_df.columns:
                result_df = result_df.sort_values(by=self.TIMESTAMP_COL).reset_index(
                    drop=True
                )

            self.logger.debug(f"成功创建等点DataFrame，包含 {len(result_df)} 行数据")
            return result_df

        except Exception as e:
            self.logger.error(f"创建等点DataFrame时发生错误: {str(e)}")
            # 返回空DataFrame但保持列结构
            empty_df = pd.DataFrame(columns=columns)
            return empty_df

    def convert_internal_data_to_dataframe(self, internal_results):
        """将内部数据结构转换为DataFrame格式

        Args:
            internal_results: 内部结果数据，包含extreme_points和equal_points信息

        Returns:
            pd.DataFrame: 标准格式的DataFrame
        """
        try:
            if not internal_results:
                self.logger.warning("内部结果数据为空")
                return self.create_equal_points_dataframe([])

            all_dataframes = []

            # 处理每个极值点及其等点
            for result in internal_results:
                extreme_info = result.get("extreme_point", {})
                equal_points = result.get("equal_points", [])
                point_type = result.get("point_type", "")

                # 为每个等点添加类型信息
                for point in equal_points:
                    point["point_type"] = f"equal_{point_type}"
                    point["is_extreme"] = False

                # 如果有等点，创建DataFrame
                if equal_points:
                    df = self.create_equal_points_dataframe(equal_points, extreme_info)
                    if not df.empty:
                        all_dataframes.append(df)

                # 如果极值点本身也需要包含在结果中
                if extreme_info and result.get("include_extreme_in_result", False):
                    # 判断该极值点是否有等点
                    has_equal_points_for_extreme = len(equal_points) > 0

                    extreme_point_data = [
                        {
                            "index": extreme_info.get("extreme_index"),
                            "value": extreme_info.get("extreme_value"),
                            "timestamp": extreme_info.get("timestamp"),
                            "point_type": f"extreme_{point_type}",
                            "tolerance_used": extreme_info.get("atr_tolerance", 0),
                            "is_extreme": True,
                            "has_equal_points": has_equal_points_for_extreme,
                        }
                    ]
                    extreme_df = self.create_equal_points_dataframe(
                        extreme_point_data, extreme_info
                    )
                    if not extreme_df.empty:
                        all_dataframes.append(extreme_df)

            # 合并所有DataFrame
            if all_dataframes:
                final_df = pd.concat(all_dataframes, ignore_index=True)
                # 按时间顺序排序
                if self.TIMESTAMP_COL in final_df.columns:
                    final_df = final_df.sort_values(by=self.TIMESTAMP_COL).reset_index(
                        drop=True
                    )

                self.logger.debug(
                    f"成功转换内部数据为DataFrame，总共 {len(final_df)} 行"
                )
                return final_df
            else:
                self.logger.debug("没有有效的等点数据，返回空DataFrame")
                return self.create_equal_points_dataframe([])

        except Exception as e:
            self.logger.error(f"转换内部数据为DataFrame时发生错误: {str(e)}")
            return self.create_equal_points_dataframe([])

    def handle_empty_results(self, point_type=""):
        """处理空结果情况，返回具有正确列结构的空DataFrame

        Args:
            point_type: 点类型，用于日志记录

        Returns:
            pd.DataFrame: 空的但具有正确列结构的DataFrame
        """
        self.logger.info(f"未找到{point_type}等点，返回空结果")
        return self.create_equal_points_dataframe([])

    def handle_no_extreme_point_found(self, point_type=""):
        """处理无法识别极值点的情况

        Args:
            point_type: 点类型，用于日志记录

        Returns:
            dict: 包含错误信息的字典
        """
        error_info = {
            "error": True,
            "message": f"无法识别{point_type}极值点",
            "point_type": point_type,
            "has_equal_points": False,
            "extreme_point_found": False,
        }

        self.logger.warning(f"无法识别{point_type}极值点")
        return error_info

    def validate_and_maintain_time_order(self, df):
        """验证并维护DataFrame的时间顺序

        Args:
            df: 输入的DataFrame

        Returns:
            pd.DataFrame: 按时间排序的DataFrame
        """
        try:
            if df.empty:
                return df

            # 检查是否有时间戳列
            if self.TIMESTAMP_COL not in df.columns:
                self.logger.warning("DataFrame缺少时间戳列，无法进行时间排序")
                return df

            # 检查时间戳列是否有有效数据
            valid_timestamps = df[self.TIMESTAMP_COL].notna()
            if not valid_timestamps.any():
                self.logger.warning("所有时间戳都为空，无法进行时间排序")
                return df

            # 按时间戳排序
            sorted_df = df.sort_values(by=self.TIMESTAMP_COL).reset_index(drop=True)

            # 验证排序结果
            if len(sorted_df) != len(df):
                self.logger.warning("排序后数据行数发生变化")

            self.logger.debug(f"成功按时间排序DataFrame，共 {len(sorted_df)} 行")
            return sorted_df

        except Exception as e:
            self.logger.error(f"维护时间顺序时发生错误: {str(e)}")
            return df  # 返回原始DataFrame

    def create_no_match_indication(self, point_type="", search_info=None):
        """创建明确的无匹配指示

        Args:
            point_type: 搜索的点类型
            search_info: 搜索相关信息

        Returns:
            dict: 包含无匹配指示的字典
        """
        indication = {
            "has_equal_points": False,
            "point_type": point_type,
            "search_completed": True,
            "message": f"未找到{point_type}等点",
            "search_info": search_info or {},
            "result_dataframe": self.create_equal_points_dataframe([]),
        }

        self.logger.info(f"创建无匹配指示: {point_type}")
        return indication

    def validate_dataframe_structure(self, df):
        """验证DataFrame结构是否符合要求

        Args:
            df: 要验证的DataFrame

        Returns:
            tuple: (is_valid, validation_info)
        """
        validation_info = {
            "is_valid": False,
            "missing_columns": [],
            "incorrect_dtypes": [],
            "row_count": len(df) if df is not None else 0,
            "has_data": False,
            "time_ordered": False,
        }

        try:
            if df is None:
                validation_info["error"] = "DataFrame为None"
                return False, validation_info

            # 检查必需的列
            required_columns = [
                self.TIMESTAMP_COL,
                self.EQUAL_POINTS_INDEX_COL,
                self.EQUAL_POINTS_PRICE_COL,
                self.EQUAL_POINTS_TYPE_COL,
                self.EXTREME_INDEX_COL,
                self.EXTREME_VALUE_COL,
                self.ATR_TOLERANCE_COL,
                self.IS_EXTREME_COL,
                self.HAS_EQUAL_POINTS_COL,
            ]

            for col in required_columns:
                if col not in df.columns:
                    validation_info["missing_columns"].append(col)

            # 检查数据类型（仅在有数据时检查）
            if not df.empty:
                validation_info["has_data"] = True

                # 检查时间戳列的数据类型
                if self.TIMESTAMP_COL in df.columns:
                    if not pd.api.types.is_datetime64_any_dtype(df[self.TIMESTAMP_COL]):
                        validation_info["incorrect_dtypes"].append(
                            f"{self.TIMESTAMP_COL}: 应为datetime类型"
                        )

                # 检查数值列的数据类型
                numeric_columns = [
                    self.EQUAL_POINTS_PRICE_COL,
                    self.EXTREME_VALUE_COL,
                    self.ATR_TOLERANCE_COL,
                ]

                for col in numeric_columns:
                    if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                        validation_info["incorrect_dtypes"].append(
                            f"{col}: 应为数值类型"
                        )

                # 检查时间顺序
                if self.TIMESTAMP_COL in df.columns and len(df) > 1:
                    timestamps = df[self.TIMESTAMP_COL].dropna()
                    if len(timestamps) > 1:
                        validation_info["time_ordered"] = (
                            timestamps.is_monotonic_increasing
                        )

            # 判断整体有效性
            validation_info["is_valid"] = (
                len(validation_info["missing_columns"]) == 0
                and len(validation_info["incorrect_dtypes"]) == 0
            )

            return validation_info["is_valid"], validation_info

        except Exception as e:
            validation_info["error"] = f"验证过程中发生错误: {str(e)}"
            self.logger.error(f"验证DataFrame结构时发生错误: {str(e)}")
            return False, validation_info

    def validate_input_data(self, data, atr_offset=None):
        """全面的输入数据验证

        Args:
            data: 输入的DataFrame
            atr_offset: ATR偏移量参数（可选）

        Returns:
            tuple: (is_valid, validation_result)
                - is_valid: bool, 数据是否有效
                - validation_result: dict, 详细的验证结果
        """
        validation_result = {
            "is_valid": False,
            "data_structure": {"valid": False, "issues": []},
            "required_columns": {"valid": False, "missing": [], "present": []},
            "data_types": {"valid": False, "issues": []},
            "data_quality": {"valid": False, "issues": []},
            "atr_offset_validation": {"valid": True, "issues": []},
            "row_count": 0,
            "recommendations": [],
        }

        try:
            # 1. 基本数据结构验证
            if data is None:
                validation_result["data_structure"]["issues"].append("输入数据为None")
                return False, validation_result

            if not isinstance(data, pd.DataFrame):
                validation_result["data_structure"]["issues"].append(
                    f"输入数据类型错误，期望DataFrame，实际为{type(data)}"
                )
                return False, validation_result

            if data.empty:
                validation_result["data_structure"]["issues"].append(
                    "输入DataFrame为空"
                )
                return False, validation_result

            validation_result["row_count"] = len(data)
            validation_result["data_structure"]["valid"] = True

            # 2. 必需列验证
            required_columns = [
                self.HIGH_COL,
                self.LOW_COL,
                self.ATR_COL,
                self.TIMESTAMP_COL,
            ]
            missing_columns = []
            present_columns = []

            for col in required_columns:
                if col in data.columns:
                    present_columns.append(col)
                else:
                    missing_columns.append(col)

            validation_result["required_columns"]["missing"] = missing_columns
            validation_result["required_columns"]["present"] = present_columns
            validation_result["required_columns"]["valid"] = len(missing_columns) == 0

            if missing_columns:
                validation_result["required_columns"]["issues"] = [
                    f"缺少必需列: {', '.join(missing_columns)}"
                ]

            # 3. 数据类型验证
            dtype_issues = []

            # 验证价格列（high, low）
            for price_col in [self.HIGH_COL, self.LOW_COL]:
                if price_col in data.columns:
                    if not pd.api.types.is_numeric_dtype(data[price_col]):
                        dtype_issues.append(
                            f"{price_col}列应为数值类型，当前为{data[price_col].dtype}"
                        )

            # 验证ATR列
            if self.ATR_COL in data.columns:
                if not pd.api.types.is_numeric_dtype(data[self.ATR_COL]):
                    dtype_issues.append(
                        f"{self.ATR_COL}列应为数值类型，当前为{data[self.ATR_COL].dtype}"
                    )

            # 验证时间戳列
            if self.TIMESTAMP_COL in data.columns:
                if not pd.api.types.is_datetime64_any_dtype(data[self.TIMESTAMP_COL]):
                    # 尝试转换为datetime
                    try:
                        pd.to_datetime(data[self.TIMESTAMP_COL])
                        validation_result["recommendations"].append(
                            f"建议将{self.TIMESTAMP_COL}列转换为datetime类型"
                        )
                    except:
                        dtype_issues.append(
                            f"{self.TIMESTAMP_COL}列无法转换为datetime类型"
                        )

            validation_result["data_types"]["issues"] = dtype_issues
            validation_result["data_types"]["valid"] = len(dtype_issues) == 0

            # 4. 数据质量验证
            quality_issues = []

            # 检查缺失值
            for col in [self.HIGH_COL, self.LOW_COL, self.ATR_COL]:
                if col in data.columns:
                    null_count = data[col].isnull().sum()
                    if null_count > 0:
                        null_percentage = (null_count / len(data)) * 100
                        quality_issues.append(
                            f"{col}列有{null_count}个缺失值 ({null_percentage:.1f}%)"
                        )

            # 检查ATR值的有效性
            if self.ATR_COL in data.columns:
                atr_data = data[self.ATR_COL].dropna()
                if len(atr_data) > 0:
                    # 检查负值或零值
                    invalid_atr = (atr_data <= 0).sum()
                    if invalid_atr > 0:
                        quality_issues.append(f"ATR列有{invalid_atr}个无效值（≤0）")

                    # 检查异常值
                    if len(atr_data) > 1:
                        atr_mean = atr_data.mean()
                        atr_std = atr_data.std()
                        outliers = ((atr_data - atr_mean).abs() > 3 * atr_std).sum()
                        if outliers > 0:
                            validation_result["recommendations"].append(
                                f"ATR列有{outliers}个可能的异常值"
                            )

            # 检查价格数据的逻辑性
            if self.HIGH_COL in data.columns and self.LOW_COL in data.columns:
                invalid_price_logic = (data[self.HIGH_COL] < data[self.LOW_COL]).sum()
                if invalid_price_logic > 0:
                    quality_issues.append(
                        f"有{invalid_price_logic}行数据的最高价低于最低价"
                    )

            validation_result["data_quality"]["issues"] = quality_issues
            validation_result["data_quality"]["valid"] = len(quality_issues) == 0

            # 5. ATR偏移量参数验证
            if atr_offset is not None:
                atr_offset_issues = []

                if not isinstance(atr_offset, (int, float, Decimal)):
                    atr_offset_issues.append(
                        f"atr_offset应为数值类型，当前为{type(atr_offset)}"
                    )
                elif atr_offset <= 0:
                    atr_offset_issues.append("atr_offset应大于0")
                elif atr_offset > 1.0:
                    validation_result["recommendations"].append(
                        "atr_offset大于1.0可能导致容差过大"
                    )
                elif atr_offset < 0.01:
                    validation_result["recommendations"].append(
                        "atr_offset小于0.01可能导致容差过小"
                    )

                validation_result["atr_offset_validation"]["issues"] = atr_offset_issues
                validation_result["atr_offset_validation"]["valid"] = (
                    len(atr_offset_issues) == 0
                )

            # 6. 整体有效性判断
            validation_result["is_valid"] = (
                validation_result["data_structure"]["valid"]
                and validation_result["required_columns"]["valid"]
                and validation_result["data_types"]["valid"]
                and validation_result["data_quality"]["valid"]
                and validation_result["atr_offset_validation"]["valid"]
            )

            # 7. 生成建议
            if validation_result["row_count"] < 10:
                validation_result["recommendations"].append(
                    "数据量较少，可能影响分析结果的可靠性"
                )

            if not validation_result["is_valid"]:
                validation_result["recommendations"].append("请修复上述验证问题后重试")

            return validation_result["is_valid"], validation_result

        except Exception as e:
            validation_result["error"] = f"验证过程中发生异常: {str(e)}"
            self.logger.error(f"输入数据验证时发生错误: {str(e)}")
            return False, validation_result

    def validate_atr_offset_parameter(self, atr_offset):
        """验证ATR偏移量参数

        Args:
            atr_offset: ATR偏移量参数

        Returns:
            tuple: (is_valid, message)
        """
        try:
            if atr_offset is None:
                return False, "atr_offset参数不能为None"

            if not isinstance(atr_offset, (int, float, Decimal)):
                return False, f"atr_offset必须为数值类型，当前为{type(atr_offset)}"

            if atr_offset <= 0:
                return False, "atr_offset必须大于0"

            if atr_offset > 1.0:
                self.logger.warning(f"atr_offset值较大({atr_offset})，可能导致容差过宽")

            if atr_offset < 0.01:
                self.logger.warning(f"atr_offset值较小({atr_offset})，可能导致容差过窄")

            return True, "atr_offset参数有效"

        except Exception as e:
            return False, f"验证atr_offset时发生错误: {str(e)}"

    def handle_missing_or_invalid_data(self, data, column_name):
        """处理缺失或无效数据

        Args:
            data: DataFrame数据
            column_name: 列名

        Returns:
            pd.Series: 处理后的数据
        """
        try:
            if column_name not in data.columns:
                self.logger.error(f"列 {column_name} 不存在")
                return pd.Series(dtype="float64")

            column_data = data[column_name].copy()

            # 处理缺失值
            null_count = column_data.isnull().sum()
            if null_count > 0:
                self.logger.warning(f"列 {column_name} 有 {null_count} 个缺失值")

                # 对于价格数据，可以使用前向填充
                if column_name in [
                    self.HIGH_COL,
                    self.LOW_COL,
                    self.CLOSE_COL,
                    self.OPEN_COL,
                ]:
                    column_data = column_data.fillna(method="ffill")
                    remaining_nulls = column_data.isnull().sum()
                    if remaining_nulls > 0:
                        # 如果还有缺失值，使用后向填充
                        column_data = column_data.fillna(method="bfill")

                # 对于ATR数据，可以使用均值填充
                elif column_name == self.ATR_COL:
                    mean_value = column_data.mean()
                    if not pd.isna(mean_value):
                        column_data = column_data.fillna(mean_value)

            # 处理无效值（如负数ATR）
            if column_name == self.ATR_COL:
                invalid_count = (column_data <= 0).sum()
                if invalid_count > 0:
                    self.logger.warning(
                        f"ATR列有 {invalid_count} 个无效值（≤0），将使用均值替换"
                    )
                    valid_mean = column_data[column_data > 0].mean()
                    if not pd.isna(valid_mean):
                        column_data[column_data <= 0] = valid_mean

            return column_data

        except Exception as e:
            self.logger.error(
                f"处理列 {column_name} 的缺失或无效数据时发生错误: {str(e)}"
            )
            return pd.Series(dtype="float64")

    def handle_extreme_point_not_found_error(self, point_type, data_info=None):
        """处理无法识别极值点的错误情况

        Args:
            point_type: 点类型 ('high' 或 'low')
            data_info: 数据相关信息

        Returns:
            dict: 错误处理结果
        """
        error_result = {
            "success": False,
            "error_type": "extreme_point_not_found",
            "point_type": point_type,
            "message": f"无法识别{point_type}极值点",
            "data_info": data_info or {},
            "suggested_actions": [],
            "fallback_result": self.create_equal_points_dataframe([]),
        }

        # 根据数据情况提供建议
        if data_info:
            if data_info.get("row_count", 0) < 3:
                error_result["suggested_actions"].append(
                    "增加数据量，至少需要3个数据点"
                )

            if data_info.get("has_null_values", False):
                error_result["suggested_actions"].append("清理数据中的缺失值")

            if data_info.get("all_values_equal", False):
                error_result["suggested_actions"].append("检查数据是否包含价格变化")

        self.logger.warning(f"极值点识别失败: {error_result['message']}")
        return error_result

    def handle_atr_calculation_failure(self, atr_value, fallback_value=None):
        """处理ATR计算失败和无效值的情况

        Args:
            atr_value: 原始ATR值
            fallback_value: 备用值

        Returns:
            tuple: (processed_atr_value, warning_message)
        """
        try:
            # 检查ATR值是否有效
            if pd.isna(atr_value):
                warning_msg = "ATR值为NaN"
                if fallback_value is not None and fallback_value > 0:
                    self.logger.warning(f"{warning_msg}，使用备用值: {fallback_value}")
                    return fallback_value, warning_msg
                else:
                    # 使用默认的小值作为备用
                    default_atr = 0.001
                    self.logger.warning(f"{warning_msg}，使用默认值: {default_atr}")
                    return default_atr, warning_msg

            if atr_value <= 0:
                warning_msg = f"ATR值无效 ({atr_value} ≤ 0)"
                if fallback_value is not None and fallback_value > 0:
                    self.logger.warning(f"{warning_msg}，使用备用值: {fallback_value}")
                    return fallback_value, warning_msg
                else:
                    # 使用绝对值或默认值
                    processed_value = abs(atr_value) if atr_value != 0 else 0.001
                    self.logger.warning(
                        f"{warning_msg}，使用处理后的值: {processed_value}"
                    )
                    return processed_value, warning_msg

            # ATR值有效
            return atr_value, None

        except Exception as e:
            error_msg = f"处理ATR值时发生错误: {str(e)}"
            self.logger.error(error_msg)
            default_atr = 0.001
            return default_atr, error_msg

    def calculate_atr_tolerance(self, atr_value, atr_offset):
        """计算ATR容差，包含错误处理

        Args:
            atr_value: ATR值
            atr_offset: ATR偏移量

        Returns:
            Decimal: 计算得到的容差值

        Raises:
            ValueError: 当参数无效时
        """
        try:
            # 处理ATR值
            processed_atr, atr_warning = self.handle_atr_calculation_failure(atr_value)
            if atr_warning:
                self.logger.warning(f"ATR处理警告: {atr_warning}")

            # 验证atr_offset
            is_valid, offset_message = self.validate_atr_offset_parameter(atr_offset)
            if not is_valid:
                raise ValueError(f"ATR偏移量无效: {offset_message}")

            # 计算容差
            tolerance = self.toDecimal(processed_atr * atr_offset)

            # 验证计算结果
            if tolerance <= 0:
                raise ValueError(f"计算得到的容差值无效: {tolerance}")

            self.logger.debug(
                f"计算ATR容差: ATR={processed_atr}, 偏移量={atr_offset}, 容差={tolerance}"
            )
            return tolerance

        except Exception as e:
            error_msg = f"计算ATR容差时发生错误: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def setup_debug_logging(self, enable_debug=True, log_level="INFO"):
        """设置调试日志记录

        Args:
            enable_debug: 是否启用调试模式
            log_level: 日志级别
        """
        try:
            self.debug_enabled = enable_debug
            self.debug_level = log_level.upper()

            # 设置日志级别
            if self.debug_enabled:
                if self.debug_level == "DEBUG":
                    self.logger.setLevel(logging.DEBUG)
                elif self.debug_level == "INFO":
                    self.logger.setLevel(logging.INFO)
                elif self.debug_level == "WARNING":
                    self.logger.setLevel(logging.WARNING)
                elif self.debug_level == "ERROR":
                    self.logger.setLevel(logging.ERROR)

                self.logger.info(f"调试模式已启用，日志级别: {self.debug_level}")
            else:
                self.logger.setLevel(logging.WARNING)
                self.logger.info("调试模式已禁用")

        except Exception as e:
            print(f"设置调试日志时发生错误: {str(e)}")

    def log_operation_info(self, operation_name, **kwargs):
        """记录操作信息用于调试和监控

        Args:
            operation_name: 操作名称
            **kwargs: 其他信息
        """
        try:
            if self.debug_enabled:
                info_msg = f"操作: {operation_name}"
                if kwargs:
                    details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
                    info_msg += f" - {details}"

                self.logger.info(info_msg)

                # 缓存调试信息
                if operation_name not in self.debug_info_cache:
                    self.debug_info_cache[operation_name] = []

                self.debug_info_cache[operation_name].append(
                    {"timestamp": pd.Timestamp.now(), "details": kwargs}
                )

        except Exception as e:
            self.logger.error(f"记录操作信息时发生错误: {str(e)}")

    def handle_recursive_search_error(self, error, search_context=None):
        """处理递归搜索过程中的错误

        Args:
            error: 异常对象
            search_context: 搜索上下文信息

        Returns:
            dict: 错误处理结果
        """
        error_result = {
            "success": False,
            "error_type": "recursive_search_error",
            "error_message": str(error),
            "search_context": search_context or {},
            "partial_results": [],
            "recovery_attempted": False,
            "fallback_result": self.create_equal_points_dataframe([]),
        }

        try:
            # 尝试从搜索上下文中恢复部分结果
            if search_context and "partial_results" in search_context:
                partial_results = search_context["partial_results"]
                if partial_results:
                    error_result["partial_results"] = partial_results
                    error_result["recovery_attempted"] = True

                    # 尝试创建部分结果的DataFrame
                    try:
                        partial_df = self.convert_internal_data_to_dataframe(
                            partial_results
                        )
                        error_result["fallback_result"] = partial_df
                        self.logger.warning(
                            f"递归搜索出错，但恢复了 {len(partial_results)} 个部分结果"
                        )
                    except Exception as recovery_error:
                        self.logger.error(
                            f"恢复部分结果时也发生错误: {str(recovery_error)}"
                        )

            self.logger.error(f"递归搜索错误: {str(error)}")
            return error_result

        except Exception as handle_error:
            self.logger.error(f"处理递归搜索错误时发生异常: {str(handle_error)}")
            return error_result

    def _has_intermediate_more_extreme_point(
        self,
        data,
        all_extreme_points,
        first_extreme_index,
        second_extreme_index,
        point_type,
    ):
        """检查两个极值点之间是否有更极端的点（优化版）

        Args:
            data: 价格数据DataFrame
            all_extreme_points: 所有极值点列表
            first_extreme_index: 第一个极值点索引（较早的）
            second_extreme_index: 第二个极值点索引（较晚的）
            point_type: 'high' 或 'low'

        Returns:
            bool: 如果中间有更极端的点返回True，否则返回False
        """
        try:
            # 获取两个极值点的位置
            first_position = data.index.get_loc(first_extreme_index)
            second_position = data.index.get_loc(second_extreme_index)

            # 确保first在second之前
            if first_position >= second_position:
                return False

            # 获取两个极值点的价格
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
            first_value = data[price_col].loc[first_extreme_index]
            second_value = data[price_col].loc[second_extreme_index]

            # 计算等点的参考值（两个点的最极端值）
            if point_type == "high":
                reference_value = max(first_value, second_value)
            else:
                reference_value = min(first_value, second_value)

            # 检查所有极值点中的中间点
            intermediate_violations = []

            for extreme_point in all_extreme_points:
                extreme_index = extreme_point["index"]
                extreme_position = data.index.get_loc(extreme_index)

                # 跳过不在中间的点
                if (
                    extreme_position <= first_position
                    or extreme_position >= second_position
                ):
                    continue

                # 获取中间点的价格
                intermediate_value = extreme_point["value"]

                # 检查中间点是否更极端
                violation_detected = False
                if point_type == "high":
                    # 对于高点，如果中间有更高的点，则破坏等高点关系
                    if intermediate_value > reference_value:
                        violation_detected = True
                else:  # point_type == 'low'
                    # 对于低点，如果中间有更低的点，则破坏等低点关系
                    if intermediate_value < reference_value:
                        violation_detected = True

                if violation_detected:
                    intermediate_violations.append(
                        {
                            "index": extreme_index,
                            "value": intermediate_value,
                            "position": extreme_position,
                        }
                    )

            # 记录详细的违规信息
            if intermediate_violations:
                self.logger.debug(
                    f"发现{len(intermediate_violations)}个中间违规点破坏了索引{first_extreme_index}({first_value})和{second_extreme_index}({second_value})的等{point_type}点关系"
                )
                for violation in intermediate_violations:
                    self.logger.debug(
                        f"  违规点: 索引={violation['index']}, 值={violation['value']}"
                    )
                return True

            return False

        except Exception as e:
            self.logger.error(f"检查中间极值点时发生错误: {str(e)}")
            return True  # 出错时保守地返回True，避免错误识别

    def check_intermediate_violation_comprehensive(
        self, data, point1_index, point2_index, point_type, tolerance=None
    ):
        """全面检查两点间的中间违规情况

        Args:
            data: 价格数据DataFrame
            point1_index: 第一个点的索引
            point2_index: 第二个点的索引
            point_type: 'high' 或 'low'
            tolerance: 可选的容差值，用于更精确的违规检测

        Returns:
            dict: 包含详细违规分析的字典
        """
        try:
            # 获取位置信息
            pos1 = data.index.get_loc(point1_index)
            pos2 = data.index.get_loc(point2_index)

            # 确保正确的顺序
            if pos1 > pos2:
                pos1, pos2 = pos2, pos1
                point1_index, point2_index = point2_index, point1_index

            # 获取价格信息
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL
            value1 = data[price_col].loc[point1_index]
            value2 = data[price_col].loc[point2_index]

            # 计算参考值
            if point_type == "high":
                reference_value = max(value1, value2)
            else:
                reference_value = min(value1, value2)

            # 如果提供了容差，调整参考值
            if tolerance is not None:
                if point_type == "high":
                    reference_value += tolerance  # 高点容差向上
                else:
                    reference_value -= tolerance  # 低点容差向下

            # 检查中间区域的所有点
            violations = []
            intermediate_data = data.iloc[pos1 + 1 : pos2]

            for i, (idx, row) in enumerate(intermediate_data.iterrows()):
                intermediate_value = row[price_col]

                if pd.isna(intermediate_value):
                    continue

                violation_detected = False
                if point_type == "high":
                    violation_detected = intermediate_value > reference_value
                else:
                    violation_detected = intermediate_value < reference_value

                if violation_detected:
                    violations.append(
                        {
                            "index": idx,
                            "value": intermediate_value,
                            "position": pos1 + 1 + i,
                            "difference_from_reference": abs(
                                intermediate_value - reference_value
                            ),
                        }
                    )

            return {
                "has_violations": len(violations) > 0,
                "violation_count": len(violations),
                "violations": violations,
                "reference_value": reference_value,
                "tolerance_used": tolerance,
                "point1": {"index": point1_index, "value": value1, "position": pos1},
                "point2": {"index": point2_index, "value": value2, "position": pos2},
                "intermediate_range": {
                    "start": pos1 + 1,
                    "end": pos2 - 1,
                    "count": len(intermediate_data),
                },
            }

        except Exception as e:
            self.logger.error(f"检查中间违规时发生错误: {str(e)}")
            return {"has_violations": True, "error": str(e)}  # 出错时保守处理

    def calculate_dynamic_atr_tolerance(
        self, data, candidate_points, point_type, base_atr_offset=0.1
    ):
        """动态计算ATR容差，基于候选点的价格分布

        Args:
            data: 价格数据DataFrame
            candidate_points: 候选点列表，每个元素包含index和value
            point_type: 'high' 或 'low'
            base_atr_offset: 基础ATR偏移量

        Returns:
            dict: 包含动态容差计算结果的字典
        """
        if not candidate_points or len(candidate_points) < 2:
            return {
                "dynamic_tolerance": None,
                "base_tolerance": None,
                "adjustment_factor": 1.0,
                "price_differences": [],
                "recommendation": f"候选点不足，使用基础偏移量 {base_atr_offset}",
            }

        try:
            # 计算所有候选点之间的价格差异
            price_differences = []
            values = [point["value"] for point in candidate_points]

            for i in range(len(values)):
                for j in range(i + 1, len(values)):
                    diff = abs(float(values[i]) - float(values[j]))
                    price_differences.append(diff)

            if not price_differences:
                return {
                    "dynamic_tolerance": None,
                    "base_tolerance": None,
                    "adjustment_factor": 1.0,
                    "price_differences": [],
                    "recommendation": "无法计算价格差异",
                }

            # 获取ATR值（使用第一个候选点的ATR）
            first_point_index = candidate_points[0]["index"]
            atr_value = data[self.ATR_COL].loc[first_point_index]

            if pd.isna(atr_value) or atr_value <= 0:
                return {
                    "dynamic_tolerance": None,
                    "base_tolerance": None,
                    "adjustment_factor": 1.0,
                    "price_differences": price_differences,
                    "recommendation": f"ATR值无效: {atr_value}",
                }

            # 计算基础容差
            base_tolerance = self.calculate_atr_tolerance(atr_value, base_atr_offset)

            # 分析价格差异分布
            max_diff = max(price_differences)
            min_diff = min(price_differences)
            avg_diff = sum(price_differences) / len(price_differences)

            # 计算调整因子
            # 如果最大价格差异超过基础容差，需要调整
            if max_diff > float(base_tolerance):
                # 计算需要的最小偏移量
                required_offset = max_diff / float(atr_value)
                adjustment_factor = (required_offset / base_atr_offset) * 1.1  # 10%缓冲
            else:
                adjustment_factor = 1.0

            # 计算动态容差
            dynamic_atr_offset = base_atr_offset * adjustment_factor
            dynamic_atr_offset = max(0.01, min(1.0, dynamic_atr_offset))  # 限制范围
            dynamic_tolerance = self.calculate_atr_tolerance(
                atr_value, dynamic_atr_offset
            )

            # 生成建议
            if adjustment_factor > 1.1:
                recommendation = f"建议增加ATR偏移量至 {dynamic_atr_offset:.3f} 以覆盖最大价格差异 {max_diff:.6f}"
            elif adjustment_factor < 0.9:
                recommendation = f"当前偏移量 {base_atr_offset} 已足够，可考虑降至 {dynamic_atr_offset:.3f}"
            else:
                recommendation = f"当前偏移量 {base_atr_offset} 适合"

            return {
                "dynamic_tolerance": dynamic_tolerance,
                "base_tolerance": base_tolerance,
                "dynamic_atr_offset": dynamic_atr_offset,
                "adjustment_factor": adjustment_factor,
                "price_differences": price_differences,
                "price_stats": {
                    "max": max_diff,
                    "min": min_diff,
                    "avg": avg_diff,
                    "count": len(price_differences),
                },
                "atr_value": float(atr_value),
                "recommendation": recommendation,
            }

        except Exception as e:
            self.logger.error(f"计算动态ATR容差时发生错误: {str(e)}")
            return {
                "dynamic_tolerance": None,
                "base_tolerance": None,
                "adjustment_factor": 1.0,
                "price_differences": [],
                "error": str(e),
                "recommendation": f"计算失败，使用基础偏移量 {base_atr_offset}",
            }

    def _validate_input_data(self, data, atr_offset):
        """验证输入数据的完整性和有效性

        Args:
            data: 输入的DataFrame
            atr_offset: ATR偏移量参数

        Raises:
            ValueError: 当数据验证失败时
        """
        if data.empty:
            raise ValueError("输入数据不能为空")

        required_columns = [self.HIGH_COL, self.LOW_COL, self.TIMESTAMP_COL]
        self.check_columns(data, required_columns)

        # 验证ATR偏移量范围
        if not (0.01 <= atr_offset <= 1.0):
            raise ValueError("atr_offset必须在0.01到1.0之间")

        # 验证数据类型
        for col in [self.HIGH_COL, self.LOW_COL]:
            if not pd.api.types.is_numeric_dtype(data[col]):
                raise ValueError(f"列 {col} 必须是数值类型")

    def calculate_atr_tolerance(self, atr_value, atr_offset):
        """计算基于ATR的容差值（优化版）

        Args:
            atr_value: ATR值
            atr_offset: ATR偏移量

        Returns:
            计算得到的容差值

        Raises:
            ValueError: 当ATR值无效时
        """
        # 验证ATR值
        if pd.isna(atr_value) or atr_value <= 0:
            raise ValueError(f"ATR值必须是正数，当前值: {atr_value}")

        # 验证atr_offset
        if not (0.01 <= atr_offset <= 1.0):
            raise ValueError(f"atr_offset必须在0.01到1.0之间，当前值: {atr_offset}")

        # 使用高精度计算，确保小价差能被正确处理
        tolerance = self.toDecimal(float(atr_value) * float(atr_offset))

        # 确保最小容差，防止极小的ATR值导致容差为0
        min_tolerance = self.toDecimal(0.000001)  # 1e-6的最小容差
        if tolerance < min_tolerance:
            self.logger.warning(
                f"计算的容差{tolerance}过小，使用最小容差{min_tolerance}"
            )
            tolerance = min_tolerance

        self.logger.debug(
            f"计算ATR容差: ATR={atr_value}, offset={atr_offset}, tolerance={tolerance}"
        )

        return tolerance

    def suggest_atr_offset(
        self,
        data,
        target_points=None,
        point_type="high",
        current_atr_offset=0.1,
        buffer_ratio=1.2,
    ):
        """智能建议ATR偏移量，基于价格差异智能建议偏移量

        Args:
            data: 价格数据DataFrame，必须包含ATR列
            target_points: 目标点索引列表，如果为None则自动寻找候选点
            point_type: 点类型 ('high' 或 'low')
            current_atr_offset: 当前使用的ATR偏移量
            buffer_ratio: 缓冲比例，默认1.2（20%缓冲）

        Returns:
            dict: 包含建议偏移量和分析信息的字典
        """
        try:
            # 输入验证
            if data.empty:
                return {
                    "suggested_offset": None,
                    "error": "输入数据为空",
                    "analysis": {},
                    "warnings": [],
                    "recommendations": [],
                }

            if point_type not in ["high", "low"]:
                return {
                    "suggested_offset": None,
                    "error": f"无效的point_type: {point_type}",
                    "analysis": {},
                    "warnings": [],
                    "recommendations": [],
                }

            # 验证参数范围
            if not (0.01 <= current_atr_offset <= 1.0):
                return {
                    "suggested_offset": None,
                    "error": f"current_atr_offset必须在0.01到1.0之间，当前值: {current_atr_offset}",
                    "analysis": {},
                    "warnings": [],
                    "recommendations": [],
                }

            if buffer_ratio < 1.0:
                return {
                    "suggested_offset": None,
                    "error": f"buffer_ratio必须大于等于1.0，当前值: {buffer_ratio}",
                    "analysis": {},
                    "warnings": [],
                    "recommendations": [],
                }

            # 确保数据包含ATR列
            df = self.ensure_atr_column(data)

            # 如果没有提供目标点，自动寻找候选点
            if target_points is None:
                target_points = self._find_candidate_points_for_analysis(df, point_type)

            if not target_points or len(target_points) < 2:
                return {
                    "suggested_offset": current_atr_offset,
                    "error": None,
                    "analysis": {
                        "candidate_points_count": (
                            len(target_points) if target_points else 0
                        ),
                        "reason": "候选点不足，无法进行价格差异分析",
                    },
                    "warnings": ["候选点数量不足，建议使用默认偏移量"],
                    "recommendations": [f"当前偏移量 {current_atr_offset} 可能适用"],
                }

            # 验证目标点在数据中存在
            valid_points = []
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

            for point_idx in target_points:
                if point_idx in df.index and not pd.isna(df[price_col].loc[point_idx]):
                    valid_points.append(point_idx)

            if len(valid_points) < 2:
                return {
                    "suggested_offset": current_atr_offset,
                    "error": None,
                    "analysis": {
                        "valid_points_count": len(valid_points),
                        "reason": "有效候选点不足",
                    },
                    "warnings": ["有效候选点数量不足"],
                    "recommendations": [f"当前偏移量 {current_atr_offset} 可能适用"],
                }

            # 计算价格差异
            price_differences = []
            point_values = []
            atr_values = []

            for point_idx in valid_points:
                price_value = df[price_col].loc[point_idx]
                atr_value = df[self.ATR_COL].loc[point_idx]

                if not pd.isna(atr_value) and atr_value > 0:
                    point_values.append(float(price_value))
                    atr_values.append(float(atr_value))

            if len(point_values) < 2:
                return {
                    "suggested_offset": current_atr_offset,
                    "error": None,
                    "analysis": {
                        "valid_atr_points_count": len(point_values),
                        "reason": "有效ATR值不足",
                    },
                    "warnings": ["有效ATR值数量不足"],
                    "recommendations": [f"当前偏移量 {current_atr_offset} 可能适用"],
                }

            # 计算所有点之间的价格差异
            for i in range(len(point_values)):
                for j in range(i + 1, len(point_values)):
                    diff = abs(point_values[i] - point_values[j])
                    price_differences.append(diff)

            # 使用平均ATR值进行计算
            avg_atr = sum(atr_values) / len(atr_values)
            max_price_diff = max(price_differences)
            min_price_diff = min(price_differences)
            avg_price_diff = sum(price_differences) / len(price_differences)

            # 计算当前偏移量的容差
            current_tolerance = avg_atr * current_atr_offset

            # 计算最小所需偏移量
            min_required_offset = max_price_diff / avg_atr

            # 添加缓冲
            suggested_offset = min_required_offset * buffer_ratio

            # 限制在合理范围内
            suggested_offset = max(0.01, min(1.0, suggested_offset))

            # 分析当前偏移量的充足性
            sufficient_for_max = current_tolerance >= max_price_diff
            sufficient_for_avg = current_tolerance >= avg_price_diff
            coverage_ratio = (
                current_tolerance / max_price_diff
                if max_price_diff > 0
                else float("inf")
            )

            # 生成警告和建议
            warnings = []
            recommendations = []

            if not sufficient_for_max:
                warnings.append(
                    f"当前ATR偏移量 {current_atr_offset} 不足以覆盖最大价格差异 {max_price_diff:.6f}"
                )
                recommendations.append(
                    f"建议使用ATR偏移量 {suggested_offset:.3f} 以覆盖所有价格差异"
                )
            elif coverage_ratio > 2.0:
                recommendations.append(
                    f"当前偏移量可能过大，可考虑降至 {min_required_offset * 1.1:.3f}"
                )
            else:
                recommendations.append(f"当前偏移量 {current_atr_offset} 适合当前数据")

            # 测试常用偏移量的效果
            common_offsets = [0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
            offset_analysis = []

            for offset in common_offsets:
                tolerance = avg_atr * offset
                covers_max = tolerance >= max_price_diff
                covers_avg = tolerance >= avg_price_diff
                covered_diffs = sum(
                    1 for diff in price_differences if tolerance >= diff
                )
                coverage_percentage = (covered_diffs / len(price_differences)) * 100

                offset_analysis.append(
                    {
                        "offset": offset,
                        "tolerance": tolerance,
                        "covers_max_diff": covers_max,
                        "covers_avg_diff": covers_avg,
                        "coverage_percentage": coverage_percentage,
                        "covered_differences": covered_diffs,
                        "total_differences": len(price_differences),
                    }
                )

            # 构建详细分析
            analysis = {
                "input_data": {
                    "target_points_count": len(target_points),
                    "valid_points_count": len(valid_points),
                    "point_type": point_type,
                    "current_atr_offset": current_atr_offset,
                    "buffer_ratio": buffer_ratio,
                },
                "atr_analysis": {
                    "avg_atr_value": avg_atr,
                    "atr_values_range": {
                        "min": min(atr_values),
                        "max": max(atr_values),
                    },
                    "current_tolerance": current_tolerance,
                },
                "price_difference_analysis": {
                    "price_differences": price_differences,
                    "max_difference": max_price_diff,
                    "min_difference": min_price_diff,
                    "avg_difference": avg_price_diff,
                    "difference_count": len(price_differences),
                },
                "offset_calculation": {
                    "min_required_offset": min_required_offset,
                    "suggested_offset": suggested_offset,
                    "buffer_applied": buffer_ratio,
                    "tolerance_with_suggested": avg_atr * suggested_offset,
                },
                "current_offset_assessment": {
                    "sufficient_for_max": sufficient_for_max,
                    "sufficient_for_avg": sufficient_for_avg,
                    "coverage_ratio": coverage_ratio,
                    "covered_differences": sum(
                        1 for diff in price_differences if current_tolerance >= diff
                    ),
                },
                "offset_comparison": offset_analysis,
            }

            self.logger.debug(
                f"ATR偏移量建议分析完成: 建议={suggested_offset:.3f}, 当前={current_atr_offset}, 最小需要={min_required_offset:.3f}"
            )

            return {
                "suggested_offset": suggested_offset,
                "error": None,
                "analysis": analysis,
                "warnings": warnings,
                "recommendations": recommendations,
            }

        except Exception as e:
            error_msg = f"计算ATR偏移量建议时发生错误: {str(e)}"
            self.logger.error(error_msg)
            return {
                "suggested_offset": None,
                "error": error_msg,
                "analysis": {},
                "warnings": [error_msg],
                "recommendations": [],
            }

    def _find_candidate_points_for_analysis(
        self, data, point_type="high", max_points=10
    ):
        """寻找用于ATR偏移量分析的候选点

        Args:
            data: 价格数据DataFrame
            point_type: 点类型 ('high' 或 'low')
            max_points: 最大候选点数量

        Returns:
            候选点索引列表
        """
        try:
            price_col = self.HIGH_COL if point_type == "high" else self.LOW_COL

            if price_col not in data.columns:
                self.logger.warning(f"数据中缺少列: {price_col}")
                return []

            # 寻找swing points作为候选点
            candidate_points = []

            # 从数据中间部分开始搜索，避免边界问题
            lookback = 1
            start_idx = lookback
            end_idx = len(data) - lookback

            for i in range(start_idx, min(end_idx, start_idx + max_points)):
                current_index = data.index[i]
                if self.is_swing_point(data, current_index, point_type, lookback):
                    candidate_points.append(current_index)

            return candidate_points[:max_points]

        except Exception as e:
            self.logger.error(f"寻找候选点时发生错误: {str(e)}")
            return []

    def check_atr_offset_sufficiency(self, atr_value, atr_offset, price_differences):
        """检查ATR偏移量是否足够处理给定的价格差异列表

        Args:
            atr_value: ATR值
            atr_offset: 当前ATR偏移量
            price_differences: 价格差异列表

        Returns:
            dict: 包含充足性分析的字典
        """
        if not price_differences:
            return {
                "sufficient": True,
                "max_difference": 0,
                "current_tolerance": 0,
                "coverage_ratio": float("inf"),
                "recommendations": [],
            }

        current_tolerance = self.toDecimal(atr_value) * self.toDecimal(atr_offset)
        max_difference = max(price_differences)
        sufficient = current_tolerance >= max_difference
        coverage_ratio = (
            current_tolerance / max_difference if max_difference > 0 else float("inf")
        )

        recommendations = []
        if not sufficient:
            suggestion = self.suggest_atr_offset(atr_value, max_difference)
            if suggestion["suggested_offset"]:
                recommendations.append(
                    f"建议使用ATR偏移量 {suggestion['suggested_offset']:.3f}"
                )

        # 分析每个价格差异
        difference_analysis = []
        for diff in price_differences:
            covered = current_tolerance >= diff
            difference_analysis.append(
                {
                    "difference": diff,
                    "covered": covered,
                    "required_offset": (
                        diff / float(atr_value) if atr_value > 0 else float("inf")
                    ),
                }
            )

        return {
            "sufficient": sufficient,
            "max_difference": max_difference,
            "current_tolerance": current_tolerance,
            "coverage_ratio": coverage_ratio,
            "recommendations": recommendations,
            "difference_analysis": difference_analysis,
            "covered_count": sum(
                1 for analysis in difference_analysis if analysis["covered"]
            ),
            "total_count": len(difference_analysis),
        }

    def ensure_atr_column(self, data):
        """确保DataFrame包含ATR列，如果不存在则计算

        Args:
            data: 输入的DataFrame

        Returns:
            包含ATR列的DataFrame
        """
        df = data.copy()

        if self.ATR_COL not in df.columns:
            self.logger.info("ATR列不存在，正在计算ATR值")
            try:
                # 使用基类的ATR计算方法
                df = self.calculate_atr(df)
            except Exception as e:
                self.logger.error(f"计算ATR时发生错误: {str(e)}")
                raise ValueError(f"无法计算ATR: {str(e)}")

        # 验证ATR列的有效性
        if df[self.ATR_COL].isna().all():
            raise ValueError("ATR列包含全部NaN值")

        return df

    def collect_point_information(
        self,
        data,
        extreme_index,
        extreme_value,
        equal_points,
        point_type,
        atr_tolerance,
    ):
        """收集点的全面信息

        Args:
            data: 原始数据DataFrame
            extreme_index: 极值点索引
            extreme_value: 极值点价格值
            equal_points: 等点列表
            point_type: 点类型 ('high' 或 'low')
            atr_tolerance: 使用的ATR容差

        Returns:
            包含详细信息的字典列表
        """
        collected_points = []

        # 添加极值点信息
        extreme_point_info = {
            self.EQUAL_POINTS_TIMESTAMP_COL: (
                data[self.TIMESTAMP_COL].loc[extreme_index]
                if self.TIMESTAMP_COL in data.columns
                else None
            ),
            self.EQUAL_POINTS_INDEX_COL: extreme_index,
            self.EQUAL_POINTS_PRICE_COL: extreme_value,
            self.EQUAL_POINTS_TYPE_COL: f"extreme_{point_type}",
            self.EXTREME_INDEX_COL: extreme_index,
            self.EXTREME_VALUE_COL: extreme_value,
            self.ATR_TOLERANCE_COL: atr_tolerance,
            self.IS_EXTREME_COL: True,
            self.HAS_EQUAL_POINTS_COL: len(equal_points) > 0,
        }
        collected_points.append(extreme_point_info)

        # 添加等点信息
        for equal_point in equal_points:
            equal_point_info = {
                self.EQUAL_POINTS_TIMESTAMP_COL: equal_point["timestamp"],
                self.EQUAL_POINTS_INDEX_COL: equal_point["index"],
                self.EQUAL_POINTS_PRICE_COL: equal_point["value"],
                self.EQUAL_POINTS_TYPE_COL: f"equal_{point_type}",
                self.EXTREME_INDEX_COL: extreme_index,
                self.EXTREME_VALUE_COL: extreme_value,
                self.ATR_TOLERANCE_COL: atr_tolerance,
                self.IS_EXTREME_COL: False,
                self.HAS_EQUAL_POINTS_COL: True,
            }
            collected_points.append(equal_point_info)

        # 按时间顺序排序
        collected_points.sort(
            key=lambda x: (
                x[self.EQUAL_POINTS_TIMESTAMP_COL]
                if x[self.EQUAL_POINTS_TIMESTAMP_COL] is not None
                else pd.Timestamp.min
            )
        )

        self.logger.debug(
            f"收集了 {len(collected_points)} 个点的信息（包括1个极值点和{len(equal_points)}个等点）"
        )

        return collected_points

    def create_result_dataframe(self, collected_points, debug=False):
        """创建结果DataFrame

        Args:
            collected_points: 收集的点信息列表
            debug: 是否包含调试信息列

        Returns:
            格式化的结果DataFrame
        """
        # 基础列结构
        base_columns = [
            self.EQUAL_POINTS_TIMESTAMP_COL,
            self.EQUAL_POINTS_INDEX_COL,
            self.EQUAL_POINTS_PRICE_COL,
            self.EQUAL_POINTS_TYPE_COL,
            self.EXTREME_INDEX_COL,
            self.EXTREME_VALUE_COL,
            self.ATR_TOLERANCE_COL,
            self.IS_EXTREME_COL,
            self.HAS_EQUAL_POINTS_COL,
        ]

        # 如果启用调试模式，添加调试列
        debug_columns = []
        if debug:
            debug_columns = [
                "is_swing_point",
                "atr_value",
                "debug_atr_tolerance",  # 重命名以避免与基础列冲突
                "price_difference",
                "intermediate_violation",
                "debug_info",
            ]

        all_columns = base_columns + debug_columns

        if not collected_points:
            # 返回空DataFrame但保持正确的列结构
            empty_df = pd.DataFrame(columns=all_columns)
            self.logger.info(
                f"未找到等点，返回空DataFrame{'（包含调试列）' if debug else ''}"
            )
            return empty_df

        # 创建DataFrame
        result_df = pd.DataFrame(collected_points)

        # 设置正确的数据类型
        result_df[self.EQUAL_POINTS_PRICE_COL] = result_df[
            self.EQUAL_POINTS_PRICE_COL
        ].astype(float)
        result_df[self.EXTREME_VALUE_COL] = result_df[self.EXTREME_VALUE_COL].astype(
            float
        )
        result_df[self.ATR_TOLERANCE_COL] = result_df[self.ATR_TOLERANCE_COL].astype(
            float
        )
        result_df[self.IS_EXTREME_COL] = result_df[self.IS_EXTREME_COL].astype(bool)
        result_df[self.HAS_EQUAL_POINTS_COL] = result_df[
            self.HAS_EQUAL_POINTS_COL
        ].astype(bool)

        # 如果有时间戳列，确保是datetime类型
        if self.EQUAL_POINTS_TIMESTAMP_COL in result_df.columns:
            result_df[self.EQUAL_POINTS_TIMESTAMP_COL] = pd.to_datetime(
                result_df[self.EQUAL_POINTS_TIMESTAMP_COL]
            )

        self.logger.info(
            f"创建结果DataFrame，包含 {len(result_df)} 行数据{'（包含调试列）' if debug else ''}"
        )

        return result_df

    def recursive_extreme_search(
        self,
        data,
        start_index=0,
        point_type="high",
        atr_offset=0.1,
        max_depth=10,
        min_distance=2,
        debug=False,
    ):
        """递归搜索后续极值点并判断等点

        Args:
            data: 价格数据DataFrame
            start_index: 开始搜索的索引位置（在DataFrame中的位置，不是索引值）
            point_type: 'high' 或 'low'
            atr_offset: ATR偏移量
            max_depth: 最大递归深度，防止无限递归
            min_distance: 最小间隔距离，相邻节点不算等点
            debug: 是否启用调试模式

        Returns:
            包含所有识别出的极值点和等点信息的DataFrame

        Raises:
            ValueError: 当输入参数无效时
        """
        # 输入验证
        self._validate_input_data(data, atr_offset)

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        if max_depth <= 0:
            raise ValueError("max_depth必须大于0")

        # 确保数据包含ATR列
        df = self.ensure_atr_column(data)

        all_collected_points = []
        all_extreme_points = []  # 跟踪所有找到的极值点
        current_start = start_index
        depth = 0

        self.logger.info(f"开始递归搜索{point_type}极值点，起始位置: {current_start}")

        if debug:
            self.logger.info(f"调试模式已启用，将收集详细的搜索过程信息")

        search_end_position = len(df)  # 初始搜索结束位置

        while depth < max_depth and current_start < search_end_position:
            # 获取当前搜索范围的数据（从current_start到search_end_position）
            search_data = df.iloc[current_start:search_end_position]

            if (
                search_data.empty or len(search_data) < 3
            ):  # 需要至少3个点来验证swing point
                self.logger.debug(f"搜索数据不足，递归结束，深度: {depth}")
                break

            # 在当前范围内找到有效的swing point极值点
            extreme_index, extreme_value = (
                self.find_extreme_point_in_range_with_swing_validation(
                    search_data, point_type, lookback=1
                )
            )

            if extreme_index is None or extreme_value is None:
                self.logger.debug(f"未找到{point_type}极值点，递归结束，深度: {depth}")
                break

            # 获取ATR值
            atr_value = df[self.ATR_COL].loc[extreme_index]
            if pd.isna(atr_value) or atr_value <= 0:
                self.logger.warning(f"极值点 {extreme_index} 的ATR值无效: {atr_value}")
                # 尝试使用附近的ATR值
                atr_value = self._get_valid_atr_value(df, extreme_index)
                if atr_value is None:
                    break

            # 将当前极值点添加到极值点列表
            current_extreme_point = {
                "index": extreme_index,
                "value": extreme_value,
                "timestamp": (
                    df[self.TIMESTAMP_COL].loc[extreme_index]
                    if self.TIMESTAMP_COL in df.columns
                    else None
                ),
            }
            all_extreme_points.append(current_extreme_point)

            # 从所有已知极值点中搜索等点
            equal_points = self.check_equal_points_from_all_extremes(
                df,
                all_extreme_points,
                extreme_index,
                extreme_value,
                atr_value,
                atr_offset,
                point_type,
                min_distance,
                lookback=1,
            )

            # 计算容差
            tolerance = self.calculate_atr_tolerance(atr_value, atr_offset)

            # 收集点信息
            points_info = self.collect_point_information(
                df, extreme_index, extreme_value, equal_points, point_type, tolerance
            )

            all_collected_points.extend(points_info)

            # 更新下一次搜索的范围
            # 找到极值点在原始DataFrame中的位置
            extreme_position_in_original = df.index.get_loc(extreme_index)

            # 关键修复：下一次搜索应该在当前极值点之前的范围内进行
            # 这样才能找到所有可能的等高点
            search_end_position = extreme_position_in_original

            if (
                search_end_position <= current_start + 2
            ):  # 需要至少3个点来验证swing point
                self.logger.debug(
                    f"搜索范围太小（{current_start} 到 {search_end_position}），无法继续搜索"
                )
                break

            depth += 1
            self.logger.debug(
                f"完成第 {depth} 层递归，找到极值点: {extreme_index}，等点数量: {len(equal_points)}"
            )

        self.logger.info(
            f"递归搜索完成，总深度: {depth}，总点数: {len(all_collected_points)}"
        )

        # 创建结果DataFrame
        result_df = self.create_result_dataframe(all_collected_points)

        return result_df

    def _get_valid_atr_value(self, data, target_index, search_range=5):
        """获取有效的ATR值

        Args:
            data: 数据DataFrame
            target_index: 目标索引
            search_range: 搜索范围

        Returns:
            有效的ATR值或None
        """
        try:
            target_position = data.index.get_loc(target_index)

            # 在目标位置附近搜索有效的ATR值
            for offset in range(1, search_range + 1):
                # 向前搜索
                if target_position - offset >= 0:
                    atr_val = data[self.ATR_COL].iloc[target_position - offset]
                    if not pd.isna(atr_val) and atr_val > 0:
                        self.logger.debug(
                            f"使用位置 {target_position - offset} 的ATR值: {atr_val}"
                        )
                        return atr_val

                # 向后搜索
                if target_position + offset < len(data):
                    atr_val = data[self.ATR_COL].iloc[target_position + offset]
                    if not pd.isna(atr_val) and atr_val > 0:
                        self.logger.debug(
                            f"使用位置 {target_position + offset} 的ATR值: {atr_val}"
                        )
                        return atr_val

        except Exception as e:
            self.logger.error(f"获取有效ATR值时发生错误: {str(e)}")

        return None

    def identify_equal_points_in_range(
        self,
        data,
        atr_offset=0.1,
        end_idx=-1,
        point_type=None,
        max_depth=10,
        min_distance=2,
        debug=False,
    ):
        """在当前K线范围内识别极值点并判断是否存在等点（增强版主要集成方法）

        Args:
            data: 包含OHLC和ATR数据的DataFrame
            atr_offset: ATR偏移量用于容差计算
            end_idx (int, optional): _description_. Defaults to -1.
            point_type: 指定搜索类型 ('high', 'low', 或 None 表示两者都搜索)
            max_depth: 最大递归深度
            min_distance: 最小间隔距离，相邻节点不算等点（默认为2，即至少间隔1个节点）
            debug: 是否启用详细调试信息输出和收集

        Returns:
            包含等点信息的DataFrame，如果debug=True则包含额外的调试信息列

        Raises:
            ValueError: 当输入参数无效时
        """

        df_data = data if end_idx == -1 else data.copy().iloc[: end_idx + 1]

        # 设置调试模式
        original_debug_enabled = self.debug_enabled
        if debug:
            self.debug_enabled = True
            self.debug_info_cache = {}
            self.logger.info("启用调试模式，将收集详细的等点识别信息")

        try:
            # 输入验证
            self._validate_input_data(df_data, atr_offset)

            if point_type is not None and point_type not in [
                self.HIGH_COL,
                self.LOW_COL,
            ]:
                raise ValueError("point_type必须是'high'、'low'或None")

            # 确保数据包含ATR列
            df = self.ensure_atr_column(df_data)

            # 如果启用调试模式，收集初始分析信息
            if debug:
                debug_info = self.collect_debug_info(df, atr_offset, point_type)
                self.debug_info_cache["initial_analysis"] = debug_info

            all_results = []

            # 根据point_type决定搜索类型
            search_types = [point_type] if point_type else [self.HIGH_COL, self.LOW_COL]

            for search_type in search_types:
                self.logger.info(f"开始识别{search_type}等点")

                try:
                    # 执行递归搜索
                    result_df = self.recursive_extreme_search(
                        df,
                        start_index=0,
                        point_type=search_type,
                        atr_offset=atr_offset,
                        max_depth=max_depth,
                        min_distance=min_distance,
                        debug=debug,
                    )

                    if not result_df.empty:
                        all_results.append(result_df)

                except Exception as e:
                    self.logger.error(f"识别{search_type}等点时发生错误: {str(e)}")
                    if debug:
                        self.debug_info_cache[f"{search_type}_error"] = str(e)
                    continue

            # 合并所有结果
            if all_results:
                combined_result = pd.concat(all_results, ignore_index=True)
                # 按时间戳排序
                if self.EQUAL_POINTS_TIMESTAMP_COL in combined_result.columns:
                    combined_result = combined_result.sort_values(
                        self.EQUAL_POINTS_TIMESTAMP_COL
                    )
                    combined_result = combined_result.reset_index(drop=True)

                # 如果启用调试模式，添加调试信息列
                if debug:
                    combined_result = self._add_debug_columns(
                        combined_result, df, atr_offset
                    )

                self.logger.info(f"识别完成，总共找到 {len(combined_result)} 个点")
                return combined_result
            else:
                # 返回空DataFrame但保持正确的列结构
                empty_result = self.create_result_dataframe([], debug=debug)
                self.logger.info("未找到任何等点")
                return empty_result

        finally:
            # 恢复原始调试设置
            self.debug_enabled = original_debug_enabled

    def collect_debug_info(self, data, atr_offset, point_type=None):
        """收集详细的调试信息

        Args:
            data: 价格数据DataFrame
            atr_offset: ATR偏移量
            point_type: 点类型 ('high', 'low', 或 None)

        Returns:
            包含调试信息的字典
        """
        debug_info = {
            "data_summary": {
                "total_rows": len(data),
                "date_range": {
                    "start": (
                        data[self.TIMESTAMP_COL].min()
                        if self.TIMESTAMP_COL in data.columns
                        else None
                    ),
                    "end": (
                        data[self.TIMESTAMP_COL].max()
                        if self.TIMESTAMP_COL in data.columns
                        else None
                    ),
                },
                "price_range": {
                    "high_min": (
                        data[self.HIGH_COL].min()
                        if self.HIGH_COL in data.columns
                        else None
                    ),
                    "high_max": (
                        data[self.HIGH_COL].max()
                        if self.HIGH_COL in data.columns
                        else None
                    ),
                    "low_min": (
                        data[self.LOW_COL].min()
                        if self.LOW_COL in data.columns
                        else None
                    ),
                    "low_max": (
                        data[self.LOW_COL].max()
                        if self.LOW_COL in data.columns
                        else None
                    ),
                },
            },
            "atr_analysis": {
                "atr_offset": atr_offset,
                "atr_stats": {
                    "mean": (
                        data[self.ATR_COL].mean()
                        if self.ATR_COL in data.columns
                        else None
                    ),
                    "min": (
                        data[self.ATR_COL].min()
                        if self.ATR_COL in data.columns
                        else None
                    ),
                    "max": (
                        data[self.ATR_COL].max()
                        if self.ATR_COL in data.columns
                        else None
                    ),
                    "std": (
                        data[self.ATR_COL].std()
                        if self.ATR_COL in data.columns
                        else None
                    ),
                },
            },
            "search_config": {
                "point_type": point_type,
                "search_types": (
                    [point_type] if point_type else [self.HIGH_COL, self.LOW_COL]
                ),
            },
        }

        # 如果指定了点类型，进行ATR偏移量建议分析
        if point_type:
            try:
                suggestion_result = self.suggest_atr_offset(
                    data, point_type=point_type, current_atr_offset=atr_offset
                )
                debug_info["atr_offset_suggestion"] = suggestion_result
            except Exception as e:
                debug_info["atr_offset_suggestion"] = {"error": str(e)}

        return debug_info

    def _add_debug_columns(self, result_df, original_data, atr_offset):
        """为结果DataFrame添加调试信息列

        Args:
            result_df: 原始结果DataFrame
            original_data: 原始价格数据
            atr_offset: ATR偏移量

        Returns:
            增强了调试信息的DataFrame
        """
        if result_df.empty:
            return result_df

        # 添加调试列
        debug_columns = {
            "is_swing_point": [],
            "atr_value": [],
            "debug_atr_tolerance": [],  # 重命名以避免与基础列冲突
            "price_difference": [],
            "intermediate_violation": [],
            "debug_info": [],
        }

        for idx, row in result_df.iterrows():
            point_index = row[self.EQUAL_POINTS_INDEX_COL]
            point_type = (
                "high"
                if row[self.EQUAL_POINTS_TYPE_COL] in ["equal_high", "extreme_high"]
                else "low"
            )

            # 验证是否为swing point
            is_swing, swing_info = self.is_swing_point_enhanced(
                original_data, point_index, point_type
            )
            debug_columns["is_swing_point"].append(is_swing)

            # 获取ATR值和容差
            if (
                point_index in original_data.index
                and self.ATR_COL in original_data.columns
            ):
                atr_val = original_data[self.ATR_COL].loc[point_index]
                tolerance = (
                    self.calculate_atr_tolerance(atr_val, atr_offset)
                    if not pd.isna(atr_val)
                    else None
                )
                # 转换为float以确保数值类型
                tolerance = float(tolerance) if tolerance is not None else None
            else:
                atr_val = None
                tolerance = None

            debug_columns["atr_value"].append(atr_val)
            debug_columns["debug_atr_tolerance"].append(tolerance)

            # 计算与极值点的价格差异
            if not row[self.IS_EXTREME_COL]:  # 如果不是极值点
                extreme_value = row[self.EXTREME_VALUE_COL]
                current_value = row[self.EQUAL_POINTS_PRICE_COL]
                price_diff = abs(float(current_value) - float(extreme_value))
            else:
                price_diff = 0.0

            debug_columns["price_difference"].append(price_diff)

            # 检查中间违规（简化版）
            debug_columns["intermediate_violation"].append(False)  # 可以后续增强

            # 构建详细调试信息
            atr_str = (
                f"{atr_val:.6f}"
                if atr_val is not None and not pd.isna(atr_val)
                else "N/A"
            )
            tolerance_str = (
                f"{tolerance:.6f}"
                if tolerance is not None and not pd.isna(tolerance)
                else "N/A"
            )
            debug_info_str = f"swing_valid={is_swing}, atr={atr_str}, tolerance={tolerance_str}, price_diff={price_diff:.6f}"
            debug_columns["debug_info"].append(debug_info_str)

        # 添加调试列到DataFrame
        for col_name, col_data in debug_columns.items():
            result_df[col_name] = col_data

        return result_df

    def get_equal_points_summary(self, result_df):
        """获取等点识别结果的摘要信息

        Args:
            result_df: identify_equal_points_in_range方法返回的结果DataFrame

        Returns:
            包含摘要信息的字典
        """
        if result_df.empty:
            return {
                "total_points": 0,
                "extreme_points": 0,
                "equal_high_points": 0,
                "equal_low_points": 0,
                "has_equal_points": False,
            }

        summary = {
            "total_points": len(result_df),
            "extreme_points": len(result_df[result_df[self.IS_EXTREME_COL] == True]),
            "equal_high_points": len(
                result_df[result_df[self.EQUAL_POINTS_TYPE_COL] == "equal_high"]
            ),
            "equal_low_points": len(
                result_df[result_df[self.EQUAL_POINTS_TYPE_COL] == "equal_low"]
            ),
            "has_equal_points": len(result_df[result_df[self.IS_EXTREME_COL] == False])
            > 0,
        }

        # 添加时间范围信息
        if (
            self.EQUAL_POINTS_TIMESTAMP_COL in result_df.columns
            and not result_df[self.EQUAL_POINTS_TIMESTAMP_COL].isna().all()
        ):
            summary["time_range"] = {
                "start": result_df[self.EQUAL_POINTS_TIMESTAMP_COL].min(),
                "end": result_df[self.EQUAL_POINTS_TIMESTAMP_COL].max(),
            }

        return summary

    def recursive_extreme_search(
        self,
        data,
        start_index,
        point_type="high",
        atr_offset=0.1,
        max_recursion_depth=10,
    ):
        """递归搜索后续极值点并判断等点

        Args:
            data: 价格数据DataFrame
            start_index: 开始搜索的索引位置
            point_type: 'high' 或 'low'
            atr_offset: ATR偏移量
            max_recursion_depth: 最大递归深度，防止无限递归

        Returns:
            包含所有识别出的极值点和等点信息的DataFrame
        """
        self.logger.debug(
            f"recursive_extreme_search - 开始递归搜索，起始索引: {start_index}, 类型: {point_type}"
        )

        # 输入验证
        if data.empty:
            self.logger.warning("recursive_extreme_search - 输入数据为空")
            return pd.DataFrame()

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        if start_index not in data.index:
            self.logger.warning(
                f"recursive_extreme_search - 起始索引 {start_index} 不在数据范围内"
            )
            return pd.DataFrame()

        if max_recursion_depth <= 0:
            self.logger.debug("recursive_extreme_search - 达到最大递归深度，停止搜索")
            return pd.DataFrame()

        try:
            # 获取起始位置在DataFrame中的位置
            start_position = data.index.get_loc(start_index)

            # 从起始位置向后搜索（索引变大的方向）
            remaining_data = data.iloc[start_position + 1 :]  # 从下一个位置开始

            self.logger.debug(
                f"recursive_extreme_search - 搜索范围: 从位置 {start_position + 1} 到 {len(data) - 1}，共 {len(remaining_data)} 个数据点"
            )

            if remaining_data.empty:
                self.logger.debug(
                    "recursive_extreme_search - 没有更多数据可搜索，递归结束"
                )
                return pd.DataFrame()

            # 在剩余数据中找到下一个极值点（使用swing point验证）
            next_extreme_index, next_extreme_value = (
                self.find_next_swing_point_in_range(
                    remaining_data, point_type=point_type, lookback=1
                )
            )

            if next_extreme_index is None:
                self.logger.debug(
                    f"recursive_extreme_search - 在剩余数据中未找到{point_type} swing point，递归结束"
                )
                return pd.DataFrame()

            self.logger.debug(
                f"recursive_extreme_search - 找到下一个{point_type}极值点: 索引={next_extreme_index}, 值={next_extreme_value}"
            )

            # 获取ATR值用于容差计算
            if self.ATR_COL not in data.columns:
                # 如果没有ATR列，计算ATR
                atr_data = self.calculate_atr(data)
                data = data.copy()
                data[self.ATR_COL] = atr_data[self.ATR_COL]

            atr_value = data[self.ATR_COL].loc[next_extreme_index]

            # 对新找到的极值点执行等点判断
            # 这里我们需要在整个数据集中搜索等点，而不仅仅是在剩余数据中
            equal_points = self.check_equal_points_from_extreme(
                data=data,
                extreme_index=next_extreme_index,
                extreme_value=next_extreme_value,
                atr_value=atr_value,
                atr_offset=atr_offset,
                point_type=point_type,
                min_distance=2,
                lookback=1,
            )

            # 构建当前结果
            current_results = []

            # 添加极值点本身
            extreme_point_data = {
                self.EQUAL_POINTS_TIMESTAMP_COL: (
                    data[self.TIMESTAMP_COL].loc[next_extreme_index]
                    if self.TIMESTAMP_COL in data.columns
                    else None
                ),
                self.EQUAL_POINTS_INDEX_COL: next_extreme_index,
                self.EQUAL_POINTS_PRICE_COL: next_extreme_value,
                self.EQUAL_POINTS_TYPE_COL: f"equal_{point_type}",
                self.EXTREME_INDEX_COL: next_extreme_index,
                self.EXTREME_VALUE_COL: next_extreme_value,
                self.ATR_TOLERANCE_COL: self.calculate_atr_tolerance(
                    atr_value, atr_offset
                ),
                self.IS_EXTREME_COL: True,
                self.HAS_EQUAL_POINTS_COL: len(equal_points) > 0,
            }
            current_results.append(extreme_point_data)

            # 添加找到的等点
            for equal_point in equal_points:
                equal_point_data = {
                    self.EQUAL_POINTS_TIMESTAMP_COL: equal_point.get("timestamp"),
                    self.EQUAL_POINTS_INDEX_COL: equal_point["index"],
                    self.EQUAL_POINTS_PRICE_COL: equal_point["value"],
                    self.EQUAL_POINTS_TYPE_COL: f"equal_{point_type}",
                    self.EXTREME_INDEX_COL: next_extreme_index,
                    self.EXTREME_VALUE_COL: next_extreme_value,
                    self.ATR_TOLERANCE_COL: equal_point.get("tolerance_used"),
                    self.IS_EXTREME_COL: False,
                    self.HAS_EQUAL_POINTS_COL: True,
                }
                current_results.append(equal_point_data)

            # 创建当前结果的DataFrame
            current_df = pd.DataFrame(current_results)

            # 递归搜索下一个极值点
            next_results_df = self.recursive_extreme_search(
                data=data,
                start_index=next_extreme_index,
                point_type=point_type,
                atr_offset=atr_offset,
                max_recursion_depth=max_recursion_depth - 1,
            )

            # 合并结果
            if not next_results_df.empty:
                combined_df = pd.concat(
                    [current_df, next_results_df], ignore_index=True
                )
            else:
                combined_df = current_df

            self.logger.debug(
                f"recursive_extreme_search - 递归搜索完成，总共找到 {len(combined_df)} 个点"
            )
            return combined_df

        except Exception as e:
            self.logger.error(
                f"recursive_extreme_search - 递归搜索时发生错误: {str(e)}"
            )
            return pd.DataFrame()

    def identify_equal_points_in_range(self, data, atr_offset=0.1, point_type="high"):
        """在当前K线范围内识别极值点并判断是否存在等点，然后递归搜索后续极值点

        Args:
            data: 包含OHLC和ATR数据的DataFrame
            atr_offset: ATR偏移量用于容差计算
            point_type: 'high' 或 'low'

        Returns:
            包含等点信息的DataFrame
        """
        self.logger.debug(
            f"identify_equal_points_in_range - 开始识别等点，类型: {point_type}"
        )

        # 输入验证
        if data.empty:
            self.logger.warning("identify_equal_points_in_range - 输入数据为空")
            return pd.DataFrame()

        if point_type not in ["high", "low"]:
            raise ValueError("point_type必须是'high'或'low'")

        # 验证必需的列存在
        required_cols = [self.HIGH_COL, self.LOW_COL, self.TIMESTAMP_COL]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"DataFrame必须包含列: {missing_cols}")

        try:
            # 计算ATR（如果不存在）
            if self.ATR_COL not in data.columns:
                atr_data = self.calculate_atr(data)
                data = data.copy()
                data[self.ATR_COL] = atr_data[self.ATR_COL]

            # 第一步：在当前范围内找到极值点
            extreme_index, extreme_value = (
                self.find_extreme_point_in_range_with_swing_validation(
                    data, point_type=point_type, lookback=1
                )
            )

            if extreme_index is None:
                self.logger.debug(
                    f"identify_equal_points_in_range - 在当前范围内未找到有效的{point_type}极值点"
                )
                return pd.DataFrame()

            self.logger.debug(
                f"identify_equal_points_in_range - 找到初始{point_type}极值点: 索引={extreme_index}, 值={extreme_value}"
            )

            # 获取ATR值
            atr_value = data[self.ATR_COL].loc[extreme_index]

            # 第二步：从极值点向前搜索等点
            equal_points = self.check_equal_points_from_extreme(
                data=data,
                extreme_index=extreme_index,
                extreme_value=extreme_value,
                atr_value=atr_value,
                atr_offset=atr_offset,
                point_type=point_type,
                min_distance=2,
                lookback=1,
            )

            # 构建初始结果
            initial_results = []

            # 添加初始极值点
            extreme_point_data = {
                self.EQUAL_POINTS_TIMESTAMP_COL: data[self.TIMESTAMP_COL].loc[
                    extreme_index
                ],
                self.EQUAL_POINTS_INDEX_COL: extreme_index,
                self.EQUAL_POINTS_PRICE_COL: extreme_value,
                self.EQUAL_POINTS_TYPE_COL: f"equal_{point_type}",
                self.EXTREME_INDEX_COL: extreme_index,
                self.EXTREME_VALUE_COL: extreme_value,
                self.ATR_TOLERANCE_COL: self.calculate_atr_tolerance(
                    atr_value, atr_offset
                ),
                self.IS_EXTREME_COL: True,
                self.HAS_EQUAL_POINTS_COL: len(equal_points) > 0,
            }
            initial_results.append(extreme_point_data)

            # 添加找到的等点
            for equal_point in equal_points:
                equal_point_data = {
                    self.EQUAL_POINTS_TIMESTAMP_COL: equal_point.get("timestamp"),
                    self.EQUAL_POINTS_INDEX_COL: equal_point["index"],
                    self.EQUAL_POINTS_PRICE_COL: equal_point["value"],
                    self.EQUAL_POINTS_TYPE_COL: f"equal_{point_type}",
                    self.EXTREME_INDEX_COL: extreme_index,
                    self.EXTREME_VALUE_COL: extreme_value,
                    self.ATR_TOLERANCE_COL: equal_point.get("tolerance_used"),
                    self.IS_EXTREME_COL: False,
                    self.HAS_EQUAL_POINTS_COL: True,
                }
                initial_results.append(equal_point_data)

            # 创建初始结果DataFrame
            initial_df = pd.DataFrame(initial_results)

            # 第三步：递归搜索后续极值点
            recursive_results_df = self.recursive_extreme_search(
                data=data,
                start_index=extreme_index,
                point_type=point_type,
                atr_offset=atr_offset,
                max_recursion_depth=10,
            )

            # 合并所有结果
            if not recursive_results_df.empty:
                final_df = pd.concat(
                    [initial_df, recursive_results_df], ignore_index=True
                )
            else:
                final_df = initial_df

            # 按时间戳排序
            if self.EQUAL_POINTS_TIMESTAMP_COL in final_df.columns:
                final_df = final_df.sort_values(
                    self.EQUAL_POINTS_TIMESTAMP_COL
                ).reset_index(drop=True)

            self.logger.debug(
                f"identify_equal_points_in_range - 完成等点识别，总共找到 {len(final_df)} 个点"
            )
            return final_df

        except Exception as e:
            self.logger.error(
                f"identify_equal_points_in_range - 识别等点时发生错误: {str(e)}"
            )
            return pd.DataFrame()

    def recursive_extreme_search(
        self, data, start_index, point_type="high", atr_offset=0.1, max_depth=10
    ):
        """递归搜索后续极值点并判断等点

        Args:
            data: 价格数据DataFrame
            start_index: 开始搜索的索引位置
            point_type: 'high' 或 'low'
            atr_offset: ATR偏移量
            max_depth: 最大递归深度，防止无限递归

        Returns:
            包含所有识别出的极值点和等点信息的DataFrame
        """
        try:
            # 输入验证
            is_valid, validation_result = self.validate_input_data(data, atr_offset)
            if not is_valid:
                # 如果只是缺少ATR列，尝试自动计算
                if (
                    validation_result.get("required_columns", {}).get("missing")
                    == ["atr"]
                    and len(
                        validation_result.get("required_columns", {}).get("present", [])
                    )
                    >= 3
                ):
                    self.logger.info("递归搜索：缺少ATR列，自动计算ATR...")
                    try:
                        data = self.calculate_atr(data)
                        # 重新验证
                        is_valid, validation_result = self.validate_input_data(
                            data, atr_offset
                        )
                        if not is_valid:
                            self.logger.error(
                                f"递归搜索：计算ATR后数据验证仍失败: {validation_result}"
                            )
                            return self.handle_empty_results(point_type)
                    except Exception as atr_error:
                        self.logger.error(
                            f"递归搜索：自动计算ATR失败: {str(atr_error)}"
                        )
                        return self.handle_empty_results(point_type)
                else:
                    self.logger.error(f"递归搜索输入数据验证失败: {validation_result}")
                    return self.handle_empty_results(point_type)

            if point_type not in ["high", "low"]:
                raise ValueError("point_type必须是'high'或'low'")

            if start_index not in data.index:
                raise ValueError(f"起始索引 {start_index} 不在数据范围内")

            if max_depth <= 0:
                self.logger.warning("达到最大递归深度，停止搜索")
                return self.handle_empty_results(point_type)

            self.log_operation_info(
                "recursive_extreme_search",
                start_index=start_index,
                point_type=point_type,
                max_depth=max_depth,
            )

            # 获取起始位置
            start_position = data.index.get_loc(start_index)

            # 从起始位置向后搜索的数据
            search_data = data.iloc[start_position:]

            if len(search_data) < 3:  # 需要足够的数据进行swing point验证
                self.logger.debug("搜索数据不足，结束递归")
                return self.handle_empty_results(point_type)

            # 在搜索范围内找到下一个极值swing point
            extreme_index, extreme_value = self.find_next_swing_point_in_range(
                search_data, point_type, lookback=1
            )

            if extreme_index is None:
                self.logger.debug("未找到下一个极值点，结束递归")
                return self.handle_empty_results(point_type)

            # 对找到的极值点进行等点分析
            atr_value = data[self.ATR_COL].loc[extreme_index]
            processed_atr, _ = self.handle_atr_calculation_failure(atr_value)

            # 搜索等点
            equal_points = self.check_equal_points_from_extreme(
                data,
                extreme_index,
                extreme_value,
                processed_atr,
                atr_offset,
                point_type,
                min_distance=2,
                lookback=1,
            )

            # 构建当前结果
            current_results = []

            # 添加极值点信息
            extreme_point_info = {
                "extreme_index": extreme_index,
                "extreme_value": extreme_value,
                "timestamp": (
                    data[self.TIMESTAMP_COL].loc[extreme_index]
                    if self.TIMESTAMP_COL in data.columns
                    else None
                ),
                "atr_tolerance": self.toDecimal(processed_atr)
                * self.toDecimal(atr_offset),
            }

            # 为等点添加类型信息
            for point in equal_points:
                point["point_type"] = f"equal_{point_type}"
                point["is_extreme"] = False

            current_result = {
                "extreme_point": extreme_point_info,
                "equal_points": equal_points,
                "point_type": point_type,
                "search_depth": max_depth,
                "include_extreme_in_result": True,  # 标记要在结果中包含极值点
            }
            current_results.append(current_result)

            # 递归搜索下一个极值点
            if max_depth > 1:
                try:
                    # 从当前极值点位置继续搜索
                    next_results_df = self.recursive_extreme_search(
                        data, extreme_index, point_type, atr_offset, max_depth - 1
                    )

                    # 如果递归返回了结果，合并到当前结果中
                    if not next_results_df.empty:
                        # 先转换当前结果为DataFrame
                        current_df = self.convert_internal_data_to_dataframe(
                            current_results
                        )

                        # 合并两个DataFrame
                        if not current_df.empty:
                            combined_df = pd.concat(
                                [current_df, next_results_df], ignore_index=True
                            )
                            # 按时间戳排序
                            if self.TIMESTAMP_COL in combined_df.columns:
                                combined_df = combined_df.sort_values(
                                    by=self.TIMESTAMP_COL
                                ).reset_index(drop=True)

                            self.logger.debug(
                                f"递归搜索完成，合并结果共 {len(combined_df)} 行"
                            )
                            return combined_df
                        else:
                            return next_results_df

                except Exception as recursive_error:
                    self.logger.warning(f"递归搜索出错: {str(recursive_error)}")
                    # 继续使用当前结果

            # 转换为DataFrame格式
            result_df = self.convert_internal_data_to_dataframe(current_results)

            self.logger.debug(f"递归搜索完成，找到 {len(current_results)} 个极值点")
            return result_df

        except Exception as e:
            error_context = {
                "start_index": start_index,
                "point_type": point_type,
                "max_depth": max_depth,
                "data_size": len(data) if data is not None else 0,
            }
            error_result = self.handle_recursive_search_error(e, error_context)
            self.logger.error(f"递归搜索发生错误: {str(e)}")
            return error_result["fallback_result"]

    def identify_equal_points_in_range(
        self, data, atr_offset=0.1, end_idx=-1, point_type="high", max_search_depth=10
    ):  # noqa: F811
        """在当前K线范围内识别极值点并递归搜索后续极值点以判断是否存在等点

        Args:
            data: 包含OHLC和ATR数据的DataFrame
            atr_offset: ATR偏移量用于容差计算
            point_type: 'high' 或 'low'
            max_search_depth: 最大搜索深度，控制递归搜索的极值点数量

        Returns:
            包含所有极值点和等点信息的DataFrame
        """

        data = data if end_idx == -1 else data.copy().iloc[: end_idx + 1]

        try:
            # 输入验证
            is_valid, validation_result = self.validate_input_data(data, atr_offset)
            if not is_valid:
                # 如果只是缺少ATR列，尝试自动计算
                if (
                    validation_result.get("required_columns", {}).get("missing")
                    == ["atr"]
                    and len(
                        validation_result.get("required_columns", {}).get("present", [])
                    )
                    >= 3
                ):
                    self.logger.info("缺少ATR列，自动计算ATR...")
                    try:
                        data = self.calculate_atr(data)
                        # 重新验证
                        is_valid, validation_result = self.validate_input_data(
                            data, atr_offset
                        )
                        if not is_valid:
                            self.logger.error(
                                f"计算ATR后数据验证仍失败: {validation_result}"
                            )
                            return self.handle_empty_results(point_type)
                    except Exception as atr_error:
                        self.logger.error(f"自动计算ATR失败: {str(atr_error)}")
                        return self.handle_empty_results(point_type)
                else:
                    self.logger.error(f"输入数据验证失败: {validation_result}")
                    return self.handle_empty_results(point_type)

            self.log_operation_info(
                "identify_equal_points_in_range",
                point_type=point_type,
                atr_offset=atr_offset,
                data_size=len(data),
                max_search_depth=max_search_depth,
            )

            # 使用递归搜索来找到所有极值点和等点
            result_df = self.recursive_extreme_search(
                data, data.index[0], point_type, atr_offset, max_search_depth
            )

            if not result_df.empty:
                unique_extremes = result_df[self.EXTREME_INDEX_COL].dropna().nunique()
                total_points = len(result_df)
                self.logger.info(
                    f"成功识别 {unique_extremes} 个{point_type}极值点，总共 {total_points} 个点（包含等点）"
                )
            else:
                self.logger.info(f"未找到{point_type}极值点或等点")

            return result_df

        except Exception as e:
            self.logger.error(f"识别等点时发生错误: {str(e)}")
            return self.handle_empty_results(point_type)
