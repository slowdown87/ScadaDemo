"""
Temperature Anomaly Detector
温度异常检测器
"""

from typing import Dict, List, Any, Tuple
import logging

import numpy as np

from .isolation_forest_detector import IsolationForestDetector

logger = logging.getLogger(__name__)


class TemperatureDetector(IsolationForestDetector):
    """温度传感器异常检测器"""

    TEMPERATURE_MIN = -10.0
    TEMPERATURE_MAX = 150.0
    CIP_NORMAL_MIN = 20.0
    CIP_NORMAL_MAX = 85.0
    CIP_HIGH_MIN = 85.0
    CIP_HIGH_MAX = 95.0
    RINSE_NORMAL_MIN = 15.0
    RINSE_NORMAL_MAX = 40.0

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        zone_id: int = 1
    ):
        """
        初始化温度检测器

        Args:
            sensor_id: 传感器ID（如 TT-101）
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
        return ["temperature", "temperature_rate", "zone_id"]

    def _get_feature_names(self) -> List[str]:
        """获取特征名称"""
        return ["temperature", "temperature_rate", "zone_id"]

    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取特征正常范围"""
        return {
            "temperature": (self.TEMPERATURE_MIN, self.TEMPERATURE_MAX),
            "temperature_rate": (-5.0, 5.0),
            "zone_id": (1, 5),
        }

    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {
            "temperature": 0.6,
            "temperature_rate": 0.25,
            "zone_id": 0.15,
        }

    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """提取温度特征"""
        return np.array([
            data.get("temperature", 25.0),
            data.get("temperature_rate", 0.0),
            data.get("zone_id", self.zone_id),
        ])

    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """验证温度数据"""
        warnings = []

        if "temperature" not in data:
            return False, ["缺少温度数据"]

        temp = data["temperature"]

        if temp < self.TEMPERATURE_MIN or temp > self.TEMPERATURE_MAX:
            return False, [f"温度 {temp}°C 超出物理范围"]

        rate = data.get("temperature_rate", 0.0)
        if abs(rate) > 10.0:
            warnings.append(f"温度变化率 {rate}°C/s 异常")

        if temp < -10 or temp > 150:
            warnings.append(f"温度 {temp}°C 超出安全范围")

        return len(warnings) == 0, warnings

    def _generate_message(
        self,
        is_anomaly: bool,
        score: float,
        contribution: Dict[str, float]
    ) -> str:
        """生成温度异常消息"""
        if not is_anomaly:
            return f"{self.sensor_id} 温度正常: {score:.1f}°C"

        temp = contribution.get("temperature", 0)
        rate = contribution.get("temperature_rate", 0)

        if temp > rate:
            severity = "严重" if temp > 5.0 else "轻微"
            return f"{self.sensor_id} 温度{severity}异常: {temp:.1f}°C (score={score:.3f})"
        else:
            return f"{self.sensor_id} 温度变化率异常: {rate:.2f}°C/s (score={score:.3f})"

    def check_cip_phase_compliance(
        self,
        temperature: float,
        phase: str
    ) -> Tuple[bool, str]:
        """
        检查CIP阶段温度合规性

        Args:
            temperature: 当前温度
            phase: CIP阶段 (pre_rinse/main/alkali/acid/rinse)

        Returns:
            (是否合规, 提示消息)
        """
        if phase == "pre_rinse":
            if self.RINSE_NORMAL_MIN <= temperature <= self.RINSE_NORMAL_MAX:
                return True, "预冲洗温度合规"
            else:
                return False, f"预冲洗温度 {temperature}°C 不在 [{self.RINSE_NORMAL_MIN}, {self.RINSE_NORMAL_MAX}]°C 范围内"

        elif phase == "main":
            if self.CIP_HIGH_MIN <= temperature <= self.CIP_HIGH_MAX:
                return True, "主清洗温度合规"
            else:
                return False, f"主清洗温度 {temperature}°C 不在 [{self.CIP_HIGH_MIN}, {self.CIP_HIGH_MAX}]°C 范围内"

        elif phase in ["alkali", "acid"]:
            if self.CIP_NORMAL_MIN <= temperature <= self.CIP_NORMAL_MAX:
                return True, "化学清洗温度合规"
            else:
                return False, f"化学清洗温度 {temperature}°C 不在 [{self.CIP_NORMAL_MIN}, {self.CIP_NORMAL_MAX}]°C 范围内"

        elif phase == "rinse":
            if self.RINSE_NORMAL_MIN <= temperature <= self.RINSE_NORMAL_MAX:
                return True, "最终冲洗温度合规"
            else:
                return False, f"最终冲洗温度 {temperature}°C 不在 [{self.RINSE_NORMAL_MIN}, {self.RINSE_NORMAL_MAX}]°C 范围内"

        return True, "阶段温度正常"

    def get_normal_range(self, phase: str) -> Tuple[float, float]:
        """获取指定阶段的正常温度范围"""
        if phase == "pre_rinse":
            return (self.RINSE_NORMAL_MIN, self.RINSE_NORMAL_MAX)
        elif phase == "main":
            return (self.CIP_HIGH_MIN, self.CIP_HIGH_MAX)
        elif phase in ["alkali", "acid"]:
            return (self.CIP_NORMAL_MIN, self.CIP_NORMAL_MAX)
        elif phase == "rinse":
            return (self.RINSE_NORMAL_MIN, self.RINSE_NORMAL_MAX)
        return (self.TEMPERATURE_MIN, self.TEMPERATURE_MAX)
