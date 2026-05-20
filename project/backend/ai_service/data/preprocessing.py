"""
Data Preprocessing
数据预处理模块
特征工程、数据标准化、异常值处理
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """数据预处理器"""

    def __init__(self):
        # 传感器正常范围定义
        self.sensor_ranges = {
            'temp_outlet': (60, 95),      # 清洗温度范围
            'temp_return': (40, 90),     # 回流温度范围
            'conductivity': (0, 500),    # 电导率 (μS/cm)
            'pressure': (0.1, 0.8),      # 压力 (MPa)
            'flow': (0, 10)               # 流量 (m³/h)
        }

        # 标准化参数（从历史数据计算）
        self.normalization_params: Dict[str, Dict[str, float]] = {}

    def validate_sensor_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        验证传感器数据的合法性

        Args:
            data: 传感器数据字典

        Returns:
            (is_valid, warning_messages)
        """
        warnings = []
        is_valid = True

        for sensor, (min_val, max_val) in self.sensor_ranges.items():
            if sensor in data and data[sensor] is not None:
                value = data[sensor]

                if value < min_val:
                    warnings.append(f"{sensor}低于正常范围: {value} < {min_val}")
                    is_valid = False
                elif value > max_val:
                    warnings.append(f"{sensor}高于正常范围: {value} > {max_val}")
                    is_valid = False

        return is_valid, warnings

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失值

        Args:
            df: 包含传感器数据的DataFrame

        Returns:
            处理后的DataFrame
        """
        df = df.copy()

        # 使用前向填充处理缺失值
        df = df.fillna(method='ffill')

        # 如果前面没有值，使用后向填充
        df = df.fillna(method='bfill')

        # 如果仍有缺失，使用中位数填充
        for col in df.columns:
            if df[col].isna().any():
                median_value = df[col].median()
                df[col] = df[col].fillna(median_value)

        return df

    def remove_outliers(self, df: pd.DataFrame, n_std: float = 3.0) -> pd.DataFrame:
        """
        使用Z-score方法移除异常值

        Args:
            df: 包含传感器数据的DataFrame
            n_std: 标准差倍数

        Returns:
            移除异常值后的DataFrame
        """
        df = df.copy()

        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.sensor_ranges:
                mean = df[col].mean()
                std = df[col].std()

                if std > 0:
                    z_scores = np.abs((df[col] - mean) / std)
                    df = df[z_scores < n_std]

        return df

    def normalize_features(
        self,
        features: np.ndarray,
        fit: bool = False
    ) -> np.ndarray:
        """
        标准化特征向量（Z-score标准化）

        Args:
            features: 特征数组
            fit: 是否拟合标准化参数（True=训练模式，False=推理模式）

        Returns:
            标准化后的特征
        """
        if len(features.shape) == 1:
            features = features.reshape(1, -1)

        normalized = np.zeros_like(features)

        for i in range(features.shape[1]):
            col_data = features[:, i]
            col_mean = np.mean(col_data)
            col_std = np.std(col_data)

            if col_std > 0:
                normalized[:, i] = (col_data - col_mean) / col_std
            else:
                normalized[:, i] = 0

        return normalized

    def extract_features_from_timeseries(
        self,
        data: List[Dict],
        window_size: int = 30
    ) -> np.ndarray:
        """
        从时序数据中提取特征

        Args:
            data: 时序数据列表
            window_size: 窗口大小

        Returns:
            特征矩阵
        """
        if not data:
            return np.array([])

        df = pd.DataFrame(data)

        # 定义要提取的统计特征
        feature_columns = ['temp_outlet', 'temp_return', 'conductivity', 'pressure', 'flow']
        available_columns = [col for col in feature_columns if col in df.columns]

        if not available_columns:
            logger.warning("No valid feature columns found")
            return np.array([])

        # 使用滑动窗口提取特征
        features_list = []

        for i in range(len(df) - window_size + 1):
            window = df[available_columns].iloc[i:i + window_size]

            # 计算统计特征
            window_features = []
            for col in available_columns:
                window_features.extend([
                    window[col].mean(),    # 均值
                    window[col].std(),     # 标准差
                    window[col].min(),     # 最小值
                    window[col].max(),     # 最大值
                    window[col].median()   # 中位数
                ])

            features_list.append(window_features)

        if features_list:
            return np.array(features_list)

        return np.array([])

    def calculate_rolling_statistics(
        self,
        data: pd.Series,
        window: int = 5
    ) -> Dict[str, float]:
        """
        计算滚动统计特征

        Args:
            data: 时间序列数据
            window: 窗口大小

        Returns:
            统计特征字典
        """
        return {
            'mean': float(data.rolling(window).mean().iloc[-1]),
            'std': float(data.rolling(window).std().iloc[-1]),
            'min': float(data.rolling(window).min().iloc[-1]),
            'max': float(data.rolling(window).max().iloc[-1]),
            'trend': float(data.diff().rolling(window).mean().iloc[-1])
        }

    def calculate_anomaly_score(
        self,
        data: Dict[str, float],
        model_scores: Optional[np.ndarray] = None
    ) -> float:
        """
        计算综合异常分数

        Args:
            data: 传感器数据
            model_scores: 模型预测的异常分数

        Returns:
            综合异常分数 (0-1)
        """
        if model_scores is not None:
            # 如果有模型分数，取平均
            return float(np.mean(np.abs(model_scores)))

        # 基于规则的异常分数
        anomaly_score = 0.0
        total_checks = 0

        # 检查每个传感器
        for sensor, (min_val, max_val) in self.sensor_ranges.items():
            if sensor in data and data[sensor] is not None:
                value = data[sensor]
                total_checks += 1

                if value < min_val:
                    deviation = (min_val - value) / min_val
                    anomaly_score += deviation
                elif value > max_val:
                    deviation = (value - max_val) / max_val
                    anomaly_score += deviation

        # 归一化
        if total_checks > 0:
            anomaly_score = anomaly_score / total_checks

        # 将分数映射到0-1范围
        return min(1.0, anomaly_score)

    def prepare_training_data(
        self,
        historical_data: List[Dict],
        labels: Optional[List[int]] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        准备训练数据

        Args:
            historical_data: 历史传感器数据
            labels: 标签（0=正常，1=异常）

        Returns:
            (features, labels)
        """
        if not historical_data:
            return np.array([]), None

        # 转换为DataFrame
        df = pd.DataFrame(historical_data)

        # 处理缺失值
        df = self.handle_missing_values(df)

        # 移除异常值
        df = self.remove_outliers(df)

        # 选择特征列
        feature_columns = ['temp_outlet', 'temp_return', 'conductivity', 'pressure', 'flow']
        available_columns = [col for col in feature_columns if col in df.columns]

        if not available_columns:
            return np.array([]), None

        # 提取特征
        features = df[available_columns].values

        # 标准化
        features = self.normalize_features(features, fit=True)

        # 标签处理
        if labels:
            labels = np.array(labels)
        else:
            labels = None

        return features, labels

    def get_feature_importance(
        self,
        feature_names: List[str],
        model
    ) -> Dict[str, float]:
        """
        获取特征重要性

        Args:
            feature_names: 特征名称列表
            model: 训练好的模型

        Returns:
            特征重要性字典
        """
        importance = {}

        try:
            if hasattr(model, 'feature_importances_'):
                # Random Forest / Isolation Forest
                scores = model.feature_importances_
            elif hasattr(model, 'coef_'):
                # Linear models
                scores = np.abs(model.coef_)
            else:
                return {}

            for name, score in zip(feature_names, scores):
                importance[name] = float(score)

        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")

        return importance


# 全局预处理器实例
preprocessor = DataPreprocessor()
