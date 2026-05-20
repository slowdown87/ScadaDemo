"""
Conductivity Anomaly Detector
电导率异常检测器
"""

from typing import Dict, List, Any, Tuple
import logging

import numpy as np

from .isolation_forest_detector import IsolationForestDetector

logger = logging.getLogger(__name__)


class ConductivityDetector(IsolationForestDetector):
    """电导率传感器异常检测器"""

    CONDUCTIVITY_MIN = 0.0
    CONDUCTIVITY_MAX = 500.0
    WATER_NORMAL_MIN = 1.0
    WATER_NORMAL_MAX = 50.0
    ALKALI_NORMAL_MIN = 30.0
    ALKALI_NORMAL_MAX = 80.0
    ACID_NORMAL_MIN = 20.0
    ACID_NORMAL_MAX = 60.0
    RINSE_NORMAL_MAX = 50.0

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        zone_id: int = 1
    ):
        """
        初始化电导率检测器

        Args:
            sensor_id: 传感器ID（如 CD-101）
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
        return ["conductivity", "conductivity_rate", "phase"]

    def _get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return ["conductivity", "conductivity_rate", "phase_code"]

    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取特征正常范围"""
        return {
            "conductivity": (self.CONDUCTIVITY_MIN, self.CONDUCTIVITY_MAX),
            "conductivity_rate": (-100.0, 100.0),
            "phase_code": (0, 5),
        }

    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {
            "conductivity": 0.7,
            "conductivity_rate": 0.2,
            "phase_code": 0.1,
        }

    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """提取电导率特征"""
        phase = data.get("phase", "idle")
        phase_code = self._phase_to_code(phase)

        return np.array([
            data.get("conductivity", 5.0),
            data.get("conductivity_rate", 0.0),
            phase_code,
        ])

    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """验证电导率数据"""
        warnings = []

        if "conductivity" not in data:
            return False, ["缺少电导率数据"]

        cd = data["conductivity"]

        if cd < self.CONDUCTIVITY_MIN or cd > self.CONDUCTIVITY_MAX:
            return False, [f"电导率 {cd} mS/cm 超出物理范围"]

        rate = data.get("conductivity_rate", 0.0)
        if abs(rate) > 200.0:
            warnings.append(f"电导率变化率 {rate} mS/cm/s 异常")

        return len(warnings) == 0, warnings

    def _phase_to_code(self, phase: str) -> float:
        """将阶段名称转换为数值编码"""
        phase_map = {
            "idle": 0,
            "pre_rinse": 1,
            "main": 2,
            "alkali": 3,
            "acid": 4,
            "rinse": 5,
        }
        return float(phase_map.get(phase.lower(), 0))

    def _generate_message(
        self,
        is_anomaly: bool,
        score: float,
        contribution: Dict[str, float]
    ) -> str:
        """生成电导率异常消息"""
        if not is_anomaly:
            return f"{self.sensor_id} 电导率正常: {score:.1f} mS/cm"

        cd = contribution.get("conductivity", 0)

        if cd > 50.0:
            return f"{self.sensor_id} 电导率严重异常: {cd:.1f} mS/cm (score={score:.3f})"
        elif cd > 20.0:
            return f"{self.sensor_id} 电导率轻微异常: {cd:.1f} mS/cm (score={score:.3f})"
        else:
            return f"{self.sensor_id} 电导率变化异常 (score={score:.3f})"

    def check_cip_phase_compliance(
        self,
        conductivity: float,
        phase: str
    ) -> Tuple[bool, str]:
        """
        检查CIP阶段电导率合规性

        Args:
            conductivity: 当前电导率
            phase: CIP阶段

        Returns:
            (是否合规, 提示消息)
        """
        if phase == "pre_rinse":
            if conductivity <= self.RINSE_NORMAL_MAX:
                return True, "预冲洗电导率合规"
            else:
                return False, f"预冲洗电导率 {conductivity} mS/cm 超过阈值 {self.RINSE_NORMAL_MAX} mS/cm"

        elif phase == "alkali":
            if self.ALKALI_NORMAL_MIN <= conductivity <= self.ALKALI_NORMAL_MAX:
                return True, "碱液电导率合规"
            else:
                return False, f"碱液电导率 {conductivity} mS/cm 不在 [{self.ALKALI_NORMAL_MIN}, {self.ALKALI_NORMAL_MAX}] mS/cm 范围内"

        elif phase == "acid":
            if self.ACID_NORMAL_MIN <= conductivity <= self.ACID_NORMAL_MAX:
                return True, "酸液电导率合规"
            else:
                return False, f"酸液电导率 {conductivity} mS/cm 不在 [{self.ACID_NORMAL_MIN}, {self.ACID_NORMAL_MAX}] mS/cm 范围内"

        elif phase == "rinse":
            if conductivity <= self.RINSE_NORMAL_MAX:
                return True, "最终冲洗电导率合规"
            else:
                return False, f"最终冲洗电导率 {conductivity} mS/cm 超过阈值 {self.RINSE_NORMAL_MAX} mS/cm"

        return True, "阶段电导率正常"

    def check_rinse_endpoint(
        self,
        conductivity_history: List[float],
        threshold: float = None
    ) -> Tuple[bool, float]:
        """
        检查冲洗终点

        Args:
            conductivity_history: 电导率历史数据
            threshold: 阈值（默认使用RINSE_NORMAL_MAX）

        Returns:
            (是否达标, 当前电导率)
        """
        threshold = threshold or self.RINSE_NORMAL_MAX

        if not conductivity_history:
            return False, 0.0

        current = conductivity_history[-1]
        return current <= threshold, current

    def get_normal_range(self, phase: str) -> Tuple[float, float]:
        """获取指定阶段的正常电导率范围"""
        if phase == "pre_rinse":
            return (self.CONDUCTIVITY_MIN, self.RINSE_NORMAL_MAX)
        elif phase == "alkali":
            return (self.ALKALI_NORMAL_MIN, self.ALKALI_NORMAL_MAX)
        elif phase == "acid":
            return (self.ACID_NORMAL_MIN, self.ACID_NORMAL_MAX)
        elif phase == "rinse":
            return (self.CONDUCTIVITY_MIN, self.RINSE_NORMAL_MAX)
        return (self.CONDUCTIVITY_MIN, self.CONDUCTIVITY_MAX)
