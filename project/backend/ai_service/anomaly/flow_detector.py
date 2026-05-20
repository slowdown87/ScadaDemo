"""
Flow Anomaly Detector
流量异常检测器
"""

from typing import Dict, List, Any, Tuple
import logging

import numpy as np

from .isolation_forest_detector import IsolationForestDetector

logger = logging.getLogger(__name__)


class FlowDetector(IsolationForestDetector):
    """流量传感器异常检测器"""

    FLOW_MIN = 0.0
    FLOW_MAX = 10000.0
    FLOW_NORMAL_MIN = 500.0
    FLOW_NORMAL_MAX = 3000.0
    FLOW_LOW_MIN = 100.0
    FLOW_LOW_MAX = 500.0

    PRESSURE_MIN = -1.0
    PRESSURE_MAX = 10.0

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        zone_id: int = 1
    ):
        """
        初始化流量检测器

        Args:
            sensor_id: 传感器ID（如 FT-101）
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
        return ["flow_rate", "flow_rate_rate", "pressure"]

    def _get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return ["flow_rate", "flow_rate_rate", "pressure"]

    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取特征正常范围"""
        return {
            "flow_rate": (self.FLOW_MIN, self.FLOW_MAX),
            "flow_rate_rate": (-500.0, 500.0),
            "pressure": (self.PRESSURE_MIN, self.PRESSURE_MAX),
        }

    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {
            "flow_rate": 0.5,
            "flow_rate_rate": 0.3,
            "pressure": 0.2,
        }

    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """提取流量特征"""
        return np.array([
            data.get("flow_rate", 0.0),
            data.get("flow_rate_rate", 0.0),
            data.get("pressure", 1.0),
        ])

    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """验证流量数据"""
        warnings = []

        if "flow_rate" not in data:
            return False, ["缺少流量数据"]

        flow = data["flow_rate"]

        if flow < self.FLOW_MIN or flow > self.FLOW_MAX:
            return False, [f"流量 {flow} L/h 超出物理范围"]

        rate = data.get("flow_rate_rate", 0.0)
        if abs(rate) > 1000.0:
            warnings.append(f"流量变化率 {rate} L/h/s 异常")

        pressure = data.get("pressure", 1.0)
        if pressure < self.PRESSURE_MIN or pressure > self.PRESSURE_MAX:
            warnings.append(f"压力 {pressure} bar 超出正常范围")

        return len(warnings) == 0, warnings

    def _generate_message(
        self,
        is_anomaly: bool,
        score: float,
        contribution: Dict[str, float]
    ) -> str:
        """生成流量异常消息"""
        if not is_anomaly:
            return f"{self.sensor_id} 流量正常: {score:.1f} L/h"

        flow = contribution.get("flow_rate", 0)
        rate = contribution.get("flow_rate_rate", 0)
        pressure = contribution.get("pressure", 0)

        if flow > rate and flow > pressure:
            if flow > 5000.0:
                return f"{self.sensor_id} 流量严重超高: {flow:.1f} L/h (score={score:.3f})"
            elif flow > 3000.0:
                return f"{self.sensor_id} 流量偏高: {flow:.1f} L/h (score={score:.3f})"
            else:
                return f"{self.sensor_id} 流量偏低: {flow:.1f} L/h (score={score:.3f})"
        elif rate > pressure:
            return f"{self.sensor_id} 流量变化异常: {rate:.1f} L/h/s (score={score:.3f})"
        else:
            return f"{self.sensor_id} 压力异常: {pressure:.2f} bar (score={score:.3f})"

    def check_flow_rate_compliance(
        self,
        flow_rate: float,
        phase: str
    ) -> Tuple[bool, str]:
        """
        检查流量合规性

        Args:
            flow_rate: 当前流量
            phase: CIP阶段

        Returns:
            (是否合规, 提示消息)
        """
        if phase in ["pre_rinse", "main", "alkali", "acid", "rinse"]:
            if self.FLOW_NORMAL_MIN <= flow_rate <= self.FLOW_NORMAL_MAX:
                return True, f"{phase}阶段流量合规"
            elif flow_rate < self.FLOW_NORMAL_MIN:
                return False, f"{phase}阶段流量过低: {flow_rate} L/h < {self.FLOW_NORMAL_MIN} L/h"
            else:
                return False, f"{phase}阶段流量过高: {flow_rate} L/h > {self.FLOW_NORMAL_MAX} L/h"

        return True, "流量正常"

    def check_no_flow(self, flow_rate: float, duration_seconds: float) -> Tuple[bool, str]:
        """
        检查无流量告警

        Args:
            flow_rate: 当前流量
            duration_seconds: 持续时间

        Returns:
            (是否无流量, 提示消息)
        """
        if flow_rate < self.FLOW_LOW_MIN:
            if duration_seconds > 60:
                return True, f"无流量告警持续 {duration_seconds:.0f} 秒"
            return True, f"检测到无流量状态"
        return False, "流量正常"

    def check_flow_stability(
        self,
        flow_history: List[float],
        cv_threshold: float = 0.15
    ) -> Tuple[bool, float]:
        """
        检查流量稳定性（变异系数）

        Args:
            flow_history: 流量历史数据
            cv_threshold: 变异系数阈值

        Returns:
            (是否稳定, 当前变异系数)
        """
        if len(flow_history) < 10:
            return True, 0.0

        mean = np.mean(flow_history)
        std = np.std(flow_history)
        cv = std / mean if mean > 0 else 0.0

        return cv <= cv_threshold, cv

    def get_normal_range(self, phase: str = None) -> Tuple[float, float]:
        """获取正常流量范围"""
        return (self.FLOW_NORMAL_MIN, self.FLOW_NORMAL_MAX)
