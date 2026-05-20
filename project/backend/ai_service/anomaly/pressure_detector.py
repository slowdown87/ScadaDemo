"""
Pressure Anomaly Detector
压力异常检测器
"""

from typing import Dict, List, Any, Tuple
import logging

import numpy as np

from .isolation_forest_detector import IsolationForestDetector

logger = logging.getLogger(__name__)


class PressureDetector(IsolationForestDetector):
    """压力传感器异常检测器"""

    PRESSURE_MIN = -1.0
    PRESSURE_MAX = 10.0
    PRESSURE_NORMAL_MIN = 0.5
    PRESSURE_NORMAL_MAX = 4.0
    PRESSURE_LOW_MIN = 0.0
    PRESSURE_LOW_MAX = 0.5
    PRESSURE_HIGH_MIN = 4.0
    PRESSURE_HIGH_MAX = 6.0
    PRESSURE_CRITICAL_MAX = 8.0

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        zone_id: int = 1
    ):
        """
        初始化压力检测器

        Args:
            sensor_id: 传感器ID（如 PT-101）
            contamination: 污染率
            zone_id: 清洗区ID
        """
        super().__init__(
            sensor_id=sensor_id,
            contamination=contamination,
            n_estimators=100,
            threshold=0.85
        )
        self.zone_id = zone_id

    def _get_required_fields(self) -> List[str]:
        """获取必需字段"""
        return ["pressure", "pressure_rate", "flow_rate"]

    def _get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return ["pressure", "pressure_rate", "flow_rate"]

    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取特征正常范围"""
        return {
            "pressure": (self.PRESSURE_MIN, self.PRESSURE_MAX),
            "pressure_rate": (-1.0, 1.0),
            "flow_rate": (0.0, 5000.0),
        }

    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {
            "pressure": 0.6,
            "pressure_rate": 0.25,
            "flow_rate": 0.15,
        }

    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """提取压力特征"""
        return np.array([
            data.get("pressure", 1.0),
            data.get("pressure_rate", 0.0),
            data.get("flow_rate", 1000.0),
        ])

    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """验证压力数据"""
        warnings = []

        if "pressure" not in data:
            return False, ["缺少压力数据"]

        pressure = data["pressure"]

        if pressure < self.PRESSURE_MIN or pressure > self.PRESSURE_MAX:
            return False, [f"压力 {pressure} bar 超出物理范围"]

        rate = data.get("pressure_rate", 0.0)
        if abs(rate) > 2.0:
            warnings.append(f"压力变化率 {rate} bar/s 异常")

        if pressure > self.PRESSURE_CRITICAL_MAX:
            warnings.append(f"压力 {pressure} bar 超过安全临界值 {self.PRESSURE_CRITICAL_MAX} bar")

        return len(warnings) == 0, warnings

    def _generate_message(
        self,
        is_anomaly: bool,
        score: float,
        contribution: Dict[str, float]
    ) -> str:
        """生成压力异常消息"""
        if not is_anomaly:
            return f"{self.sensor_id} 压力正常: {score:.2f} bar"

        pressure = contribution.get("pressure", 0)

        if pressure > self.PRESSURE_CRITICAL_MAX:
            return f"{self.sensor_id} 压力严重超高: {pressure:.2f} bar ⚠️紧急! (score={score:.3f})"
        elif pressure > self.PRESSURE_HIGH_MAX:
            return f"{self.sensor_id} 压力超高: {pressure:.2f} bar (score={score:.3f})"
        elif pressure < self.PRESSURE_LOW_MIN:
            return f"{self.sensor_id} 压力过低: {pressure:.2f} bar (score={score:.3f})"
        else:
            return f"{self.sensor_id} 压力异常: {pressure:.2f} bar (score={score:.3f})"

    def check_pressure_compliance(
        self,
        pressure: float,
        phase: str
    ) -> Tuple[bool, str]:
        """
        检查压力合规性

        Args:
            pressure: 当前压力
            phase: CIP阶段

        Returns:
            (是否合规, 提示消息)
        """
        if pressure < self.PRESSURE_NORMAL_MIN:
            return False, f"压力过低: {pressure:.2f} bar < {self.PRESSURE_NORMAL_MIN} bar"
        elif pressure > self.PRESSURE_HIGH_MAX:
            return False, f"压力过高: {pressure:.2f} bar > {self.PRESSURE_HIGH_MAX} bar"

        return True, "压力正常"

    def check_pressure_drop(
        self,
        pressure_history: List[float],
        drop_threshold: float = 0.5,
        time_window: int = 10
    ) -> Tuple[bool, float]:
        """
        检查压力骤降

        Args:
            pressure_history: 压力历史数据
            drop_threshold: 压降阈值
            time_window: 时间窗口大小

        Returns:
            (是否压降, 压降值)
        """
        if len(pressure_history) < time_window:
            return False, 0.0

        recent = pressure_history[-time_window:]
        initial = recent[0]
        current = recent[-1]
        drop = initial - current

        return drop > drop_threshold, drop

    def check_pressure_spike(
        self,
        pressure_history: List[float],
        spike_threshold: float = 1.0
    ) -> Tuple[bool, float]:
        """
        检查压力骤升

        Args:
            pressure_history: 压力历史数据
            spike_threshold: 突升阈值

        Returns:
            (是否突升, 突升值)
        """
        if len(pressure_history) < 2:
            return False, 0.0

        mean = np.mean(pressure_history[:-1])
        current = pressure_history[-1]
        spike = current - mean

        return spike > spike_threshold, spike

    def check_blockage_risk(
        self,
        pressure: float,
        flow_rate: float
    ) -> Tuple[bool, str]:
        """
        检查堵塞风险

        Args:
            pressure: 当前压力
            flow_rate: 当前流量

        Returns:
            (是否存在风险, 提示消息)
        """
        if flow_rate < 500.0 and pressure > 3.0:
            return True, f"堵塞风险：低流量 {flow_rate:.0f} L/h + 高压力 {pressure:.2f} bar"
        elif flow_rate < 200.0 and pressure > 2.5:
            return True, f"高堵塞风险：极低流量 {flow_rate:.0f} L/h + 高压力 {pressure:.2f} bar"

        return False, "无堵塞风险"

    def get_normal_range(self, phase: str = None) -> Tuple[float, float]:
        """获取正常压力范围"""
        return (self.PRESSURE_NORMAL_MIN, self.PRESSURE_NORMAL_MAX)
