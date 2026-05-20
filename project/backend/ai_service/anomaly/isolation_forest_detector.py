"""
Isolation Forest Detector
基于Isolation Forest算法的异常检测器
"""

from typing import Dict, List, Any, Tuple, Optional
import logging

import numpy as np
from sklearn.ensemble import IsolationForest as SKIsolationForest

from .base_detector import BaseAnomalyDetector, AnomalyResult

logger = logging.getLogger(__name__)


class IsolationForestDetector(BaseAnomalyDetector):
    """Isolation Forest 异常检测器"""

    def __init__(
        self,
        sensor_id: str,
        contamination: float = 0.1,
        n_estimators: int = 100,
        max_samples: str = "auto",
        random_state: int = 42,
        threshold: Optional[float] = None
    ):
        """
        初始化 Isolation Forest 检测器

        Args:
            sensor_id: 传感器ID
            contamination: 污染率（异常比例）
            n_estimators: 树的数量
            max_samples: 采样数量
            random_state: 随机种子
            threshold: 自定义阈值
        """
        super().__init__(sensor_id, contamination, threshold)

        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state

        self._model: Optional[SKIsolationForest] = None

    def _validate_data(self, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """验证输入数据"""
        warnings = []

        if not data:
            return False, ["数据为空"]

        required_fields = self._get_required_fields()
        for field in required_fields:
            if field not in data:
                warnings.append(f"缺少必需字段: {field}")

        feature_ranges = self._get_feature_ranges()
        for feature, (min_val, max_val) in feature_ranges.items():
            if feature in data:
                value = data[feature]
                if value < min_val or value > max_val:
                    warnings.append(f"{feature}={value} 超出范围 [{min_val}, {max_val}]")

        return len(warnings) == 0, warnings

    def _extract_features(self, data: Dict[str, float]) -> np.ndarray:
        """提取特征向量"""
        features = []

        for feature_name in self._get_feature_names():
            value = data.get(feature_name, 0.0)
            features.append(value)

        return np.array(features)

    def _get_required_fields(self) -> List[str]:
        """获取必需的数据字段"""
        return self._get_feature_names()

    def _get_feature_names(self) -> List[str]:
        """获取特征名称列表"""
        return ["value"]

    def _get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """获取特征正常范围"""
        return {}

    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {"value": 1.0}

    def train(self, historical_data: List[Dict[str, float]]) -> Dict[str, Any]:
        """训练 Isolation Forest 模型"""
        if len(historical_data) < 50:
            raise ValueError(f"训练数据不足，需要至少50条记录，当前{len(historical_data)}条")

        feature_names = self._get_feature_names()
        features = []

        for data in historical_data:
            is_valid, warnings = self._validate_data(data)
            if is_valid:
                feature_vector = [data.get(f, 0.0) for f in feature_names]
                features.append(feature_vector)

        if len(features) < 50:
            raise ValueError(f"有效训练数据不足，需要至少50条，当前{len(features)}条")

        X = np.array(features)
        self._feature_names = feature_names

        self._model = SKIsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples if self.max_samples != "auto" else X.shape[0],
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )

        self._model.fit(X)

        scores = self._model.score_samples(X)
        self._training_stats = {
            "sample_count": len(features),
            "feature_count": len(feature_names),
            "score_mean": float(np.mean(scores)),
            "score_std": float(np.std(scores)),
            "score_min": float(np.min(scores)),
            "score_max": float(np.max(scores)),
            "score_percentile_1": float(np.percentile(scores, 1)),
            "score_percentile_5": float(np.percentile(scores, 5)),
            "score_percentile_10": float(np.percentile(scores, 10)),
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "training_time": self._model.training_time if hasattr(self._model, 'training_time') else None,
        }

        self._is_trained = True
        logger.info(f"{self.sensor_id} Isolation Forest 训练完成，样本数: {len(features)}")

        return self._training_stats

    def _calculate_anomaly_score(self, features: np.ndarray) -> float:
        """计算异常分数"""
        if self._model is None:
            raise RuntimeError("模型尚未训练")

        score = self._model.score_samples(features.reshape(1, -1))[0]

        normalized_score = (score - self._training_stats["score_min"]) / (
            self._training_stats["score_max"] - self._training_stats["score_min"] + 1e-10
        )

        return max(0.0, min(1.0, normalized_score))

    def _interpret_score(
        self,
        score: float,
        features: np.ndarray
    ) -> Tuple[bool, float, Dict[str, float]]:
        """解释异常分数"""
        threshold = self.threshold or 0.8
        is_anomaly = score > threshold

        distance = abs(score - threshold)
        confidence = min(distance / (1 - threshold) * 0.5 + 0.5, 1.0)

        feature_contribution = {}
        if self._feature_names:
            means = self._training_stats.get("score_mean", 0)
            for i, name in enumerate(self._feature_names):
                if i < len(features):
                    deviation = abs(features[i])
                    feature_contribution[name] = float(deviation)

        return is_anomaly, confidence, feature_contribution

    def decision_function(self, data: List[Dict[str, float]]) -> np.ndarray:
        """
        对批量数据进行决策函数计算

        Args:
            data: 数据列表

        Returns:
            异常分数数组（分数越低越异常）
        """
        if not self._is_trained or self._model is None:
            raise RuntimeError("模型尚未训练")

        features = []
        for item in data:
            feature_vector = [item.get(f, 0.0) for f in self._feature_names]
            features.append(feature_vector)

        X = np.array(features)
        return self._model.score_samples(X)

    def predict(self, data: List[Dict[str, float]]) -> List[int]:
        """
        批量预测

        Args:
            data: 数据列表

        Returns:
            预测结果列表（1=正常，-1=异常）
        """
        if not self._is_trained or self._model is None:
            raise RuntimeError("模型尚未训练")

        features = []
        for item in data:
            feature_vector = [item.get(f, 0.0) for f in self._feature_names]
            features.append(feature_vector)

        X = np.array(features)
        return self._model.predict(X).tolist()
