"""
Base Anomaly Detector
异常检测器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """异常检测结果"""
    is_anomaly: bool
    anomaly_score: float
    confidence: float
    feature_contribution: Dict[str, float]
    timestamp: datetime
    sensor_id: str
    message: str


class BaseAnomalyDetector(ABC):
    """异常检测器基类"""

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        threshold: Optional[float] = None
    ):
        """
        初始化异常检测器

        Args:
            sensor_id: 传感器ID
            contamination: 污染率（异常比例估计）
            threshold: 自定义阈值（覆盖自动计算）
        """
        self.sensor_id = sensor_id
        self.contamination = contamination
        self.threshold = threshold
        self._is_trained = False
        self._feature_names: List[str] = []
        self._training_stats: Dict[str, Any] = {}

    @abstractmethod
    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        验证输入数据

        Args:
            data: 输入数据字典

        Returns:
            (是否有效, 警告信息列表)
        """
        pass

    @abstractmethod
    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """
        提取特征向量

        Args:
            data: 输入数据字典

        Returns:
            特征向量
        """
        pass

    @abstractmethod
    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取各特征的正常范围"""
        pass

    @abstractmethod
    def _get_feature_weights(self) -> Dict[str, float]:
        """获取各特征的权重"""
        pass

    def train(self, historical_data: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        训练模型

        Args:
            historical_data: 历史数据列表

        Returns:
            训练统计信息
        """
        if len(historical_data) < 50:
            raise ValueError(f"训练数据不足，需要至少50条记录，当前{len(historical_data)}条")

        valid_data = []
        for data in historical_data:
            is_valid, warnings = self._validate_data(data)
            if is_valid:
                valid_data.append(data)
            else:
                logger.debug(f"跳过无效数据: {warnings}")

        if len(valid_data) < 50:
            raise ValueError(f"有效训练数据不足，需要至少50条，当前{len(valid_data)}条")

        features = np.array([self._extract_features(d) for d in valid_data])
        self._feature_names = [f"feature_{i}" for i in range(features.shape[1])]

        self._training_stats = {
            "sample_count": len(valid_data),
            "feature_count": features.shape[1],
            "feature_means": np.mean(features, axis=0).tolist(),
            "feature_stds": np.std(features, axis=0).tolist(),
            "feature_mins": np.min(features, axis=0).tolist(),
            "feature_maxs": np.max(features, axis=0).tolist(),
            "training_time": datetime.now().isoformat(),
        }

        self._is_trained = True
        logger.info(f"{self.sensor_id} 异常检测器训练完成，样本数: {len(valid_data)}")

        return self._training_stats

    def detect(self, data: Dict[str, float]) -> AnomalyResult:
        """
        执行异常检测

        Args:
            data: 输入数据

        Returns:
            异常检测结果
        """
        if not self._is_trained:
            raise RuntimeError("模型尚未训练，请先调用train()方法")

        is_valid, warnings = self._validate_data(data)
        if not is_valid:
            return AnomalyResult(
                is_anomaly=True,
                anomaly_score=1.0,
                confidence=0.9,
                feature_contribution={},
                timestamp=datetime.now(),
                sensor_id=self.sensor_id,
                message=f"数据验证失败: {', '.join(warnings)}"
            )

        features = self._extract_features(data)
        anomaly_score = self._calculate_anomaly_score(features)
        is_anomaly, confidence, feature_contribution = self._interpret_score(anomaly_score, features)

        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=float(anomaly_score),
            confidence=confidence,
            feature_contribution=feature_contribution,
            timestamp=datetime.now(),
            sensor_id=self.sensor_id,
            message=self._generate_message(is_anomaly, anomaly_score, feature_contribution)
        )

    @abstractmethod
    def _calculate_anomaly_score(self, features: np.ndarray) -> float:
        """计算异常分数"""
        pass

    def _interpret_score(
        self,
        score: float,
        features: np.ndarray
    ) -> Tuple[bool, float, Dict[str, float]]:
        """
        解释异常分数

        Args:
            score: 异常分数
            features: 特征向量

        Returns:
            (是否异常, 置信度, 各特征贡献)
        """
        threshold = self.threshold or self._calculate_threshold()
        is_anomaly = score > threshold

        distance_from_threshold = abs(score - threshold)
        max_possible_distance = 1.0 - threshold
        confidence = min(distance_from_threshold / max_possible_distance * 0.5 + 0.5, 1.0)

        feature_contribution = {}
        if self._feature_names and len(features) == len(self._feature_names):
            feature_weights = self._get_feature_weights()
            total_weight = sum(feature_weights.values()) or 1.0
            for i, name in enumerate(self._feature_names):
                weight = feature_weights.get(name, 1.0)
                contribution = abs(features[i] - self._training_stats["feature_means"][i]) * weight
                feature_contribution[name] = float(contribution / total_weight)

        return is_anomaly, confidence, feature_contribution

    def _calculate_threshold(self) -> float:
        """根据污染率计算阈值"""
        return 1.0 - self.contamination

    def _generate_message(
        self,
        is_anomaly: bool,
        score: float,
        contribution: Dict[str, float]
    ) -> str:
        """生成异常消息"""
        if not is_anomaly:
            return f"{self.sensor_id} 检测正常 (score={score:.3f})"

        top_features = sorted(contribution.items(), key=lambda x: x[1], reverse=True)[:3]
        feature_str = ", ".join([f"{k}={v:.3f}" for k, v in top_features])

        return f"{self.sensor_id} 检测到异常 (score={score:.3f}), 主要贡献: {feature_str}"

    def get_training_stats(self) -> Dict[str, Any]:
        """获取训练统计信息"""
        return self._training_stats.copy()

    def is_trained(self) -> bool:
        """检查是否已训练"""
        return self._is_trained
