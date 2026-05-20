"""
Ensemble Anomaly Detector
集成异常检测器 - 综合多个检测器结果
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio

from .base_detector import AnomalyResult
from .temperature_detector import TemperatureDetector
from .conductivity_detector import ConductivityDetector
from .flow_detector import FlowDetector
from .pressure_detector import PressureDetector

logger = logging.getLogger(__name__)


@dataclass
class EnsembleResult:
    """集成检测结果"""
    is_anomaly: bool
    overall_score: float
    confidence: float
    detector_results: Dict[str, AnomalyResult]
    alarm_level: str
    timestamp: datetime
    message: str
    recommended_action: str


@dataclass
class AlarmRule:
    """告警规则"""
    name: str
    condition: Callable[[Dict[str, AnomalyResult]], bool]
    level: str
    message: str
    action: str


class EnsembleAnomalyDetector:
    """集成异常检测器"""

    ALARM_LEVEL_NORMAL = "normal"
    ALARM_LEVEL_WARNING = "warning"
    ALARM_LEVEL_ERROR = "error"
    ALARM_LEVEL_CRITICAL = "critical"

    def __init__(self, zone_id: int = 1):
        """
        初始化集成检测器

        Args:
            zone_id: 清洗区ID
        """
        self.zone_id = zone_id

        self._temperature_detector: Optional[TemperatureDetector] = None
        self._conductivity_detector: Optional[ConductivityDetector] = None
        self._flow_detector: Optional[FlowDetector] = None
        self._pressure_detector: Optional[PressureDetector] = None

        self._alarm_rules: List[AlarmRule] = []
        self._is_initialized = False

        self._init_alarm_rules()

    def _init_alarm_rules(self):
        """初始化告警规则"""
        self._alarm_rules = [
            AlarmRule(
                name="multi_sensor_anomaly",
                condition=lambda r: sum(1 for det in r.values() if det.is_anomaly) >= 2,
                level=self.ALARM_LEVEL_ERROR,
                message="多个传感器检测到异常",
                action="检查设备状态和连接"
            ),
            AlarmRule(
                name="temperature_and_flow",
                condition=lambda r: (
                    r.get("temperature", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).is_anomaly and
                    r.get("flow", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).is_anomaly
                ),
                level=self.ALARM_LEVEL_CRITICAL,
                message="温度和流量同时异常",
                action="立即检查换热器和泵组"
            ),
            AlarmRule(
                name="high_score_anomaly",
                condition=lambda r: any(d.anomaly_score > 0.9 for d in r.values()),
                level=self.ALARM_LEVEL_ERROR,
                message="检测到高置信度异常",
                action="人工介入检查"
            ),
            AlarmRule(
                name="temperature_spike",
                condition=lambda r: (
                    r.get("temperature", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).anomaly_score > 0.8 and
                    "严重" in r.get("temperature", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).message
                ),
                level=self.ALARM_LEVEL_CRITICAL,
                message="温度严重超高",
                action="立即停止加热并检查"
            ),
            AlarmRule(
                name="pressure_high",
                condition=lambda r: (
                    r.get("pressure", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).anomaly_score > 0.8 and
                    "超高" in r.get("pressure", AnomalyResult(False, 0, 0, {}, datetime.now(), "", "")).message
                ),
                level=self.ALARM_LEVEL_CRITICAL,
                message="压力严重超高",
                action="立即泄压并检查安全阀"
            ),
        ]

    def initialize(self, historical_data: Dict[str, List[Dict[str, float]]]):
        """
        初始化并训练所有检测器

        Args:
            historical_data: 历史数据字典
                {
                    "temperature": [...],
                    "conductivity": [...],
                    "flow": [...],
                    "pressure": [...]
                }
        """
        logger.info(f"初始化区域 {self.zone_id} 集成异常检测器")

        self._temperature_detector = TemperatureDetector(
            sensor_id=f"TT-Z{self.zone_id}",
            zone_id=self.zone_id
        )
        if "temperature" in historical_data:
            self._temperature_detector.train(historical_data["temperature"])

        self._conductivity_detector = ConductivityDetector(
            sensor_id=f"CD-Z{self.zone_id}",
            zone_id=self.zone_id
        )
        if "conductivity" in historical_data:
            self._conductivity_detector.train(historical_data["conductivity"])

        self._flow_detector = FlowDetector(
            sensor_id=f"FT-Z{self.zone_id}",
            zone_id=self.zone_id
        )
        if "flow" in historical_data:
            self._flow_detector.train(historical_data["flow"])

        self._pressure_detector = PressureDetector(
            sensor_id=f"PT-Z{self.zone_id}",
            zone_id=self.zone_id
        )
        if "pressure" in historical_data:
            self._pressure_detector.train(historical_data["pressure"])

        self._is_initialized = True
        logger.info(f"区域 {self.zone_id} 集成检测器初始化完成")

    def detect(
        self,
        temperature: Optional[float] = None,
        conductivity: Optional[float] = None,
        flow_rate: Optional[float] = None,
        pressure: Optional[float] = None,
        temperature_rate: float = 0.0,
        conductivity_rate: float = 0.0,
        flow_rate_rate: float = 0.0,
        pressure_rate: float = 0.0,
        phase: str = "idle"
    ) -> EnsembleResult:
        """
        执行集成异常检测

        Args:
            temperature: 温度值
            conductivity: 电导率值
            flow_rate: 流量值
            pressure: 压力值
            *_rate: 对应变化率
            phase: CIP阶段

        Returns:
            集成检测结果
        """
        if not self._is_initialized:
            raise RuntimeError("检测器尚未初始化，请先调用initialize()方法")

        detector_results: Dict[str, AnomalyResult] = {}

        if temperature is not None and self._temperature_detector:
            data = {
                "temperature": temperature,
                "temperature_rate": temperature_rate,
                "zone_id": self.zone_id
            }
            result = self._temperature_detector.detect(data)
            detector_results["temperature"] = result

        if conductivity is not None and self._conductivity_detector:
            data = {
                "conductivity": conductivity,
                "conductivity_rate": conductivity_rate,
                "phase": phase
            }
            result = self._conductivity_detector.detect(data)
            detector_results["conductivity"] = result

        if flow_rate is not None and self._flow_detector:
            data = {
                "flow_rate": flow_rate,
                "flow_rate_rate": flow_rate_rate,
                "pressure": pressure or 1.0
            }
            result = self._flow_detector.detect(data)
            detector_results["flow"] = result

        if pressure is not None and self._pressure_detector:
            data = {
                "pressure": pressure,
                "pressure_rate": pressure_rate,
                "flow_rate": flow_rate or 1000.0
            }
            result = self._pressure_detector.detect(data)
            detector_results["pressure"] = result

        alarm_level, recommended_action = self._evaluate_alarm_rules(detector_results)

        anomaly_count = sum(1 for r in detector_results.values() if r.is_anomaly)
        total_score = sum(r.anomaly_score for r in detector_results.values())
        overall_score = total_score / len(detector_results) if detector_results else 0.0
        is_anomaly = anomaly_count > 0

        confidence = self._calculate_confidence(detector_results, alarm_level)

        message = self._generate_message(detector_results, alarm_level)

        return EnsembleResult(
            is_anomaly=is_anomaly,
            overall_score=overall_score,
            confidence=confidence,
            detector_results=detector_results,
            alarm_level=alarm_level,
            timestamp=datetime.now(),
            message=message,
            recommended_action=recommended_action
        )

    def _evaluate_alarm_rules(
        self,
        results: Dict[str, AnomalyResult]
    ) -> tuple:
        """评估告警规则"""
        highest_level = self.ALARM_LEVEL_NORMAL
        action = "继续监控"

        for rule in self._alarm_rules:
            if rule.condition(results):
                level_order = {
                    self.ALARM_LEVEL_NORMAL: 0,
                    self.ALARM_LEVEL_WARNING: 1,
                    self.ALARM_LEVEL_ERROR: 2,
                    self.ALARM_LEVEL_CRITICAL: 3,
                }

                if level_order.get(rule.level, 0) > level_order.get(highest_level, 0):
                    highest_level = rule.level
                    action = rule.action

        return highest_level, action

    def _calculate_confidence(
        self,
        results: Dict[str, AnomalyResult],
        alarm_level: str
    ) -> float:
        """计算置信度"""
        if not results:
            return 0.0

        avg_score = sum(r.anomaly_score for r in results.values()) / len(results)
        avg_confidence = sum(r.confidence for r in results.values()) / len(results)

        level_bonus = {
            self.ALARM_LEVEL_NORMAL: 0.0,
            self.ALARM_LEVEL_WARNING: 0.1,
            self.ALARM_LEVEL_ERROR: 0.2,
            self.ALARM_LEVEL_CRITICAL: 0.3,
        }

        return min(avg_confidence * 0.7 + avg_score * 0.3 + level_bonus.get(alarm_level, 0), 1.0)

    def _generate_message(
        self,
        results: Dict[str, AnomalyResult],
        alarm_level: str
    ) -> str:
        """生成综合消息"""
        if alarm_level == self.ALARM_LEVEL_NORMAL:
            return f"Zone {self.zone_id} 所有参数正常"

        anomalies = [r.message for r in results.values() if r.is_anomaly]
        return f"Zone {self.zone_id} 检测到{len(anomalies)}项异常: {'; '.join(anomalies[:2])}"

    def add_alarm_rule(self, rule: AlarmRule):
        """添加自定义告警规则"""
        self._alarm_rules.append(rule)

    def get_detector_status(self) -> Dict[str, bool]:
        """获取各检测器状态"""
        return {
            "temperature": self._temperature_detector.is_trained() if self._temperature_detector else False,
            "conductivity": self._conductivity_detector.is_trained() if self._conductivity_detector else False,
            "flow": self._flow_detector.is_trained() if self._flow_detector else False,
            "pressure": self._pressure_detector.is_trained() if self._pressure_detector else False,
        }

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._is_initialized
