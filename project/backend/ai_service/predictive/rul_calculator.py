"""
RUL Calculator
剩余使用寿命(RUL)计算器
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RULResult:
    """RUL计算结果"""
    rul_days: float
    rul_hours: float
    confidence: float
    health_status: str
    maintenance_priority: str
    estimated_failure_date: Optional[datetime]
    trend: str
    recommendation: str


@dataclass
class HealthThreshold:
    """健康阈值配置"""
    excellent_max: float = 0.9
    good_max: float = 0.75
    fair_max: float = 0.6
    poor_max: float = 0.4


class RULCalculator:
    """RUL计算器"""

    def __init__(
        self,
        thresholds: Optional[HealthThreshold] = None,
        degradation_rate_warning: float = 0.05,
        degradation_rate_critical: float = 0.1
    ):
        """
        初始化RUL计算器

        Args:
            thresholds: 健康阈值配置
            degradation_rate_warning: 警告级降级率
            degradation_rate_critical: 临界级降级率
        """
        self.thresholds = thresholds or HealthThreshold()
        self.degradation_rate_warning = degradation_rate_warning
        self.degradation_rate_critical = degradation_rate_critical

    def calculate_rul(
        self,
        current_health_score: float,
        degradation_rate: float,
        confidence: float = 0.95,
        prediction_horizon_days: int = 30
    ) -> RULResult:
        """
        计算剩余使用寿命

        Args:
            current_health_score: 当前健康分数 (0-1)
            degradation_rate: 降级率 (每天下降的比例)
            confidence: 预测置信度
            prediction_horizon_days: 预测时间范围

        Returns:
            RUL计算结果
        """
        rul_days = self._calculate_rul_days(current_health_score, degradation_rate)
        rul_hours = rul_days * 24

        health_status = self._get_health_status(current_health_score)
        maintenance_priority = self._get_maintenance_priority(
            rul_days, current_health_score, degradation_rate
        )

        estimated_failure = None
        if rul_days < prediction_horizon_days:
            estimated_failure = datetime.now() + timedelta(days=rul_days)

        trend = self._get_trend(current_health_score, degradation_rate)
        recommendation = self._generate_recommendation(
            rul_days, health_status, maintenance_priority, trend
        )

        return RULResult(
            rul_days=round(rul_days, 1),
            rul_hours=round(rul_hours, 1),
            confidence=confidence,
            health_status=health_status,
            maintenance_priority=maintenance_priority,
            estimated_failure_date=estimated_failure,
            trend=trend,
            recommendation=recommendation
        )

    def _calculate_rul_days(
        self,
        health_score: float,
        degradation_rate: float
    ) -> float:
        """计算RUL（天）"""
        failure_threshold = 0.3

        if degradation_rate <= 0:
            return 365.0

        health_distance = health_score - failure_threshold

        if health_distance <= 0:
            return 0.0

        rul = health_distance / degradation_rate

        return min(rul, 365.0)

    def _get_health_status(self, health_score: float) -> str:
        """获取健康状态"""
        if health_score >= self.thresholds.excellent_max:
            return "excellent"
        elif health_score >= self.thresholds.good_max:
            return "good"
        elif health_score >= self.thresholds.fair_max:
            return "fair"
        elif health_score >= self.thresholds.poor_max:
            return "poor"
        else:
            return "critical"

    def _get_maintenance_priority(
        self,
        rul_days: float,
        health_score: float,
        degradation_rate: float
    ) -> str:
        """获取维护优先级"""
        if rul_days <= 7 or health_score < self.thresholds.poor_max:
            return "critical"
        elif rul_days <= 14 or degradation_rate > self.degradation_rate_critical:
            return "high"
        elif rul_days <= 30 or degradation_rate > self.degradation_rate_warning:
            return "medium"
        else:
            return "low"

    def _get_trend(
        self,
        health_score: float,
        degradation_rate: float
    ) -> str:
        """获取趋势"""
        if degradation_rate > self.degradation_rate_critical:
            return "rapid_degradation"
        elif degradation_rate > self.degradation_rate_warning:
            return "moderate_degradation"
        elif degradation_rate > 0:
            return "slow_degradation"
        elif degradation_rate == 0:
            return "stable"
        else:
            return "improving"

    def _generate_recommendation(
        self,
        rul_days: float,
        health_status: str,
        maintenance_priority: str,
        trend: str
    ) -> str:
        """生成维护建议"""
        recommendations = {
            ("critical", "critical", "rapid_degradation"):
                "紧急维护！设备可能在7天内故障，立即安排停机检修",
            ("critical", "critical", _):
                "紧急维护！设备健康状态临界，优先安排检修",
            ("poor", "high", _):
                "高优先级维护。建议在未来1-2周内安排维护计划",
            ("fair", "medium", "moderate_degradation"):
                "中等优先级。建议进行预防性维护检查",
            ("fair", "medium", _):
                "监控状态。可考虑安排例行维护",
            ("good", "low", _):
                "设备状态良好。继续常规监控",
            ("excellent", "low", "stable"):
                "设备状态优秀。继续保持当前维护计划",
        }

        for (status, priority, trend_pattern), recommendation in recommendations.items():
            if status == health_status and priority == maintenance_priority:
                if callable(trend_pattern):
                    if trend_pattern(trend):
                        return recommendation
                elif trend == trend_pattern:
                    return recommendation

        return f"建议: {health_status}状态，{maintenance_priority}优先级"

    def calculate_degradation_rate(
        self,
        health_scores: List[float],
        time_intervals: List[float]
    ) -> float:
        """
        计算降级率

        Args:
            health_scores: 健康分数历史
            time_intervals: 时间间隔（天）

        Returns:
            日均降级率
        """
        if len(health_scores) < 2:
            return 0.0

        health_change = health_scores[0] - health_scores[-1]
        total_days = sum(time_intervals)

        if total_days <= 0:
            return 0.0

        degradation_rate = health_change / total_days

        return max(0.0, degradation_rate)

    def predict_health_score(
        self,
        current_health_score: float,
        degradation_rate: float,
        future_days: int
    ) -> float:
        """
        预测未来健康分数

        Args:
            current_health_score: 当前健康分数
            degradation_rate: 降级率
            future_days: 未来天数

        Returns:
            预测的健康分数
        """
        predicted = current_health_score - (degradation_rate * future_days)
        return max(0.0, min(1.0, predicted))

    def analyze_trend(
        self,
        recent_scores: List[float],
        window_size: int = 5
    ) -> Dict[str, Any]:
        """
        分析健康趋势

        Args:
            recent_scores: 最近健康分数
            window_size: 分析窗口大小

        Returns:
            趋势分析结果
        """
        if len(recent_scores) < 2:
            return {
                "trend": "insufficient_data",
                "avg_change": 0.0,
                "volatility": 0.0,
                "prediction_stable": True
            }

        changes = np.diff(recent_scores)

        avg_change = float(np.mean(changes))
        volatility = float(np.std(changes))

        if avg_change > 0.01:
            trend = "improving"
        elif avg_change < -0.01:
            trend = "degrading"
        else:
            trend = "stable"

        is_stable = volatility < 0.05

        return {
            "trend": trend,
            "avg_change": round(avg_change, 4),
            "volatility": round(volatility, 4),
            "prediction_stable": is_stable,
            "data_points": len(recent_scores)
        }

    def calculate_confidence_interval(
        self,
        rul: float,
        data_points: int,
        volatility: float
    ) -> Tuple[float, float]:
        """
        计算RUL置信区间

        Args:
            rul: RUL估算值
            data_points: 数据点数量
            volatility: 波动性

        Returns:
            (下限, 上限)
        """
        base_confidence = min(data_points / 100, 1.0)
        volatility_factor = 1 + volatility

        uncertainty = (1 - base_confidence) * volatility_factor * rul

        lower = max(0, rul - uncertainty)
        upper = rul + uncertainty

        return (round(lower, 1), round(upper, 1))

    def get_maintenance_schedule(
        self,
        rul_result: RULResult
    ) -> Dict[str, Any]:
        """
        生成维护计划

        Args:
            rul_result: RUL计算结果

        Returns:
            维护计划
        """
        schedule = {
            "next_inspection": None,
            "maintenance_due": None,
            "spare_parts_order": None,
            "maintenance_team_alert": False
        }

        if rul_result.maintenance_priority in ["critical", "high"]:
            schedule["next_inspection"] = max(1, int(rul_result.rul_days / 3))
            schedule["maintenance_due"] = max(3, int(rul_result.rul_days * 0.8))
            schedule["spare_parts_order"] = max(1, int(rul_result.rul_days / 5))
            schedule["maintenance_team_alert"] = True

        elif rul_result.maintenance_priority == "medium":
            schedule["next_inspection"] = 14
            schedule["maintenance_due"] = int(rul_result.rul_days * 0.7)
            schedule["spare_parts_order"] = 30
            schedule["maintenance_team_alert"] = False

        else:
            schedule["next_inspection"] = 30
            schedule["maintenance_due"] = int(rul_result.rul_days * 0.5)
            schedule["spare_parts_order"] = 60
            schedule["maintenance_team_alert"] = False

        return schedule
