"""
Data Windowing for Time Series
时序数据窗口化处理
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class WindowConfig:
    """窗口配置"""
    sequence_length: int = 30
    step_size: int = 1
    normalize: bool = True
    min_window_size: int = 10


class DataWindow:
    """数据窗口化处理器"""

    FEATURE_NAMES = [
        "temperature",
        "conductivity",
        "flow_rate",
        "pressure",
        "vibration",
        "runtime_hours"
    ]

    def __init__(
        self,
        config: Optional[WindowConfig] = None
    ):
        """
        初始化窗口处理器

        Args:
            config: 窗口配置
        """
        self.config = config or WindowConfig()
        self.scaler_params: Dict[str, Dict[str, float]] = {}

    def create_windows(
        self,
        data: List[Dict[str, float]],
        target_column: str = "health_score"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建滑动窗口数据

        Args:
            data: 时序数据列表
            target_column: 目标列名

        Returns:
            (特征数据, 标签数据)
        """
        if len(data) < self.config.sequence_length:
            raise ValueError(
                f"数据长度 {len(data)} 小于序列长度 {self.config.sequence_length}"
            )

        df = self._list_to_array(data)
        labels = self._extract_labels(df, target_column)

        windows = []
        window_labels = []

        for i in range(0, len(df) - self.config.sequence_length, self.config.step_size):
            window = df[i:i + self.config.sequence_length]
            label = labels[i + self.config.sequence_length - 1]

            windows.append(window)
            window_labels.append(label)

        X = np.array(windows)
        y = np.array(window_labels)

        if self.config.normalize:
            X, y = self._normalize(X, y)

        logger.info(f"创建窗口: X.shape={X.shape}, y.shape={y.shape}")

        return X, y

    def create_prediction_window(
        self,
        data: List[Dict[str, float]]
    ) -> np.ndarray:
        """
        创建预测窗口（使用最新的sequence_length条数据）

        Args:
            data: 时序数据列表

        Returns:
            特征数据 (1, sequence_length, n_features)
        """
        if len(data) < self.config.sequence_length:
            raise ValueError(
                f"数据长度 {len(data)} 小于序列长度 {self.config.sequence_length}"
            )

        df = self._list_to_array(data)

        window = df[-self.config.sequence_length:]

        if self.config.normalize:
            window = self._normalize_single_window(window)

        return window.unsqueeze(0)

    def _list_to_array(self, data: List[Dict[str, float]]) -> np.ndarray:
        """将数据列表转换为numpy数组"""
        features = []

        for item in data:
            feature_vector = []
            for name in self.FEATURE_NAMES:
                value = item.get(name, 0.0)
                feature_vector.append(value)
            features.append(feature_vector)

        return np.array(features)

    def _extract_labels(
        self,
        df: np.ndarray,
        target_column: str
    ) -> np.ndarray:
        """提取标签"""
        target_idx = self.FEATURE_NAMES.index(target_column)
        return df[:, target_idx]

    def _normalize(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """标准化数据"""
        n_samples, seq_len, n_features = X.shape

        X_flat = X.reshape(-1, n_features)

        if not self.scaler_params:
            for i in range(n_features):
                col = X_flat[:, i]
                self.scaler_params[self.FEATURE_NAMES[i]] = {
                    'mean': float(np.mean(col)),
                    'std': float(np.std(col) + 1e-8)
                }

        X_normalized = np.zeros_like(X)
        for i in range(n_features):
            feature_name = self.FEATURE_NAMES[i]
            mean = self.scaler_params[feature_name]['mean']
            std = self.scaler_params[feature_name]['std']
            X_normalized[:, :, i] = (X[:, :, i] - mean) / std

        y_mean = np.mean(y)
        y_std = np.std(y) + 1e-8
        y_normalized = (y - y_mean) / y_std

        self.scaler_params['target'] = {
            'mean': float(y_mean),
            'std': float(y_std)
        }

        return X_normalized, y_normalized

    def _normalize_single_window(self, window: np.ndarray) -> np.ndarray:
        """标准化单个窗口"""
        if not self.scaler_params:
            return window

        normalized = np.zeros_like(window)
        for i in range(window.shape[1]):
            feature_name = self.FEATURE_NAMES[i]
            if feature_name in self.scaler_params:
                mean = self.scaler_params[feature_name]['mean']
                std = self.scaler_params[feature_name]['std']
                normalized[:, i] = (window[:, i] - mean) / std
            else:
                normalized[:, i] = window[:, i]

        return normalized

    def inverse_transform(self, y_normalized: np.ndarray) -> np.ndarray:
        """反标准化"""
        if 'target' not in self.scaler_params:
            return y_normalized

        mean = self.scaler_params['target']['mean']
        std = self.scaler_params['target']['std']

        return y_normalized * std + mean

    def add_features(
        self,
        data: List[Dict[str, float]]
    ) -> List[Dict[str, float]]:
        """
        添加派生特征

        Args:
            data: 原始数据

        Returns:
            添加特征后的数据
        """
        enriched = []

        for i, item in enumerate(data):
            new_item = item.copy()

            if i > 0:
                prev = data[i - 1]

                for feature in ["temperature", "conductivity", "flow_rate", "pressure"]:
                    if feature in item and feature in prev:
                        rate_key = f"{feature}_rate"
                        new_item[rate_key] = item[feature] - prev[feature]

                if "runtime_hours" in item and "runtime_hours" in prev:
                    new_item["runtime_increment"] = item["runtime_hours"] - prev["runtime_hours"]

            if i >= 2:
                prev_prev = data[i - 2]
                for feature in ["temperature", "conductivity", "flow_rate", "pressure"]:
                    if feature in item and feature in prev_prev:
                        accel_key = f"{feature}_acceleration"
                        rate1 = item[feature] - prev[feature]
                        rate2 = prev[feature] - prev_prev[feature]
                        new_item[accel_key] = rate1 - rate2

            rolling_window = 5
            if i >= rolling_window:
                window_data = data[i - rolling_window:i + 1]
                for feature in ["temperature", "conductivity", "flow_rate", "pressure"]:
                    if feature in item:
                        values = [d.get(feature, 0.0) for d in window_data]
                        new_item[f"{feature}_ma5"] = np.mean(values)
                        new_item[f"{feature}_std5"] = np.std(values)

            enriched.append(new_item)

        return enriched

    def validate_sequence(
        self,
        sequence: List[Dict[str, float]]
    ) -> Tuple[bool, List[str]]:
        """
        验证序列数据

        Args:
            sequence: 输入序列

        Returns:
            (是否有效, 警告信息)
        """
        warnings = []

        if len(sequence) < self.config.min_window_size:
            warnings.append(
                f"序列长度 {len(sequence)} 小于最小窗口大小 {self.config.min_window_size}"
            )

        missing_features = set()
        for item in sequence:
            for feature in self.FEATURE_NAMES:
                if feature not in item:
                    missing_features.add(feature)

        if missing_features:
            warnings.append(f"缺少特征: {missing_features}")

        null_count = sum(
            1 for item in sequence
            for feature in self.FEATURE_NAMES
            if item.get(feature) is None
        )
        if null_count > 0:
            warnings.append(f"发现 {null_count} 个空值")

        return len(warnings) == 0, warnings

    def get_feature_importance(
        self,
        importance_scores: np.ndarray
    ) -> List[Tuple[str, float]]:
        """
        获取特征重要性排序

        Args:
            importance_scores: 重要性分数

        Returns:
            [(特征名, 分数)] 列表
        """
        importance_list = []
        for i, score in enumerate(importance_scores):
            if i < len(self.FEATURE_NAMES):
                importance_list.append((self.FEATURE_NAMES[i], float(score)))

        return sorted(importance_list, key=lambda x: x[1], reverse=True)
