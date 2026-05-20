"""
Maintenance Reporter
维护报告生成器
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json

from .rul_calculator import RULResult

logger = logging.getLogger(__name__)


@dataclass
class EquipmentInfo:
    """设备信息"""
    equipment_id: str
    equipment_name: str
    equipment_type: str
    zone_id: int
    install_date: datetime
    last_maintenance_date: Optional[datetime]
    operating_hours: int


@dataclass
class MaintenanceReport:
    """维护报告"""
    report_id: str
    generated_at: datetime
    equipment_info: EquipmentInfo
    current_health_score: float
    rul_result: RULResult
    maintenance_schedule: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    historical_trend: List[Dict[str, Any]]
    executive_summary: str


class MaintenanceReporter:
    """维护报告生成器"""

    def __init__(self):
        self.report_counter = 0

    def generate_report(
        self,
        equipment_info: EquipmentInfo,
        current_health_score: float,
        rul_result: RULResult,
        maintenance_schedule: Dict[str, Any],
        historical_trend: Optional[List[Dict[str, Any]]] = None
    ) -> MaintenanceReport:
        """
        生成维护报告

        Args:
            equipment_info: 设备信息
            current_health_score: 当前健康分数
            rul_result: RUL计算结果
            maintenance_schedule: 维护计划
            historical_trend: 历史趋势数据

        Returns:
            维护报告
        """
        self.report_counter += 1
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{self.report_counter:04d}"

        risk_assessment = self._assess_risk(
            current_health_score, rul_result, equipment_info
        )

        recommendations = self._generate_recommendations(
            equipment_info, rul_result, maintenance_schedule
        )

        executive_summary = self._generate_executive_summary(
            equipment_info, current_health_score, rul_result, recommendations
        )

        return MaintenanceReport(
            report_id=report_id,
            generated_at=datetime.now(),
            equipment_info=equipment_info,
            current_health_score=current_health_score,
            rul_result=rul_result,
            maintenance_schedule=maintenance_schedule,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            historical_trend=historical_trend or [],
            executive_summary=executive_summary
        )

    def _assess_risk(
        self,
        health_score: float,
        rul_result: RULResult,
        equipment_info: EquipmentInfo
    ) -> Dict[str, Any]:
        """评估风险"""
        risk_factors = []

        if health_score < 0.4:
            risk_factors.append({
                "factor": "low_health_score",
                "severity": "high",
                "description": f"健康分数 {health_score:.1%} 低于临界值"
            })

        if rul_result.rul_days < 14:
            risk_factors.append({
                "factor": "short_rul",
                "severity": "critical",
                "description": f"剩余寿命 {rul_result.rul_days:.0f} 天不足14天"
            })

        if rul_result.trend == "rapid_degradation":
            risk_factors.append({
                "factor": "rapid_degradation",
                "severity": "high",
                "description": "设备处于快速降级状态"
            })

        days_since_maintenance = None
        if equipment_info.last_maintenance_date:
            days_since_maintenance = (
                datetime.now() - equipment_info.last_maintenance_date
            ).days

        if days_since_maintenance and days_since_maintenance > 90:
            risk_factors.append({
                "factor": "overdue_maintenance",
                "severity": "medium",
                "description": f"距上次维护已 {days_since_maintenance} 天"
            })

        overall_risk = "low"
        if any(f["severity"] == "critical" for f in risk_factors):
            overall_risk = "critical"
        elif any(f["severity"] == "high" for f in risk_factors):
            overall_risk = "high"
        elif any(f["severity"] == "medium" for f in risk_factors):
            overall_risk = "medium"

        return {
            "overall_risk": overall_risk,
            "risk_score": max(0, min(100, (1 - health_score) * 100 + (1 - rul_result.confidence) * 50)),
            "risk_factors": risk_factors,
            "production_impact": self._estimate_production_impact(overall_risk)
        }

    def _estimate_production_impact(self, risk_level: str) -> Dict[str, Any]:
        """估算生产影响"""
        impacts = {
            "critical": {
                "downtime_probability": 0.8,
                "estimated_downtime_hours": 48,
                "cost_estimate": 50000,
                "quality_impact": "high"
            },
            "high": {
                "downtime_probability": 0.5,
                "estimated_downtime_hours": 24,
                "cost_estimate": 25000,
                "quality_impact": "medium"
            },
            "medium": {
                "downtime_probability": 0.2,
                "estimated_downtime_hours": 8,
                "cost_estimate": 10000,
                "quality_impact": "low"
            },
            "low": {
                "downtime_probability": 0.05,
                "estimated_downtime_hours": 2,
                "cost_estimate": 2000,
                "quality_impact": "minimal"
            }
        }

        return impacts.get(risk_level, impacts["low"])

    def _generate_recommendations(
        self,
        equipment_info: EquipmentInfo,
        rul_result: RULResult,
        maintenance_schedule: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """生成建议"""
        recommendations = []

        if rul_result.maintenance_priority in ["critical", "high"]:
            recommendations.append({
                "priority": "immediate",
                "action": "安排紧急维护",
                "reason": f"剩余寿命 {rul_result.rul_days:.0f} 天，{rul_result.maintenance_priority} 优先级",
                "deadline": "3天内"
            })

        if rul_result.trend in ["rapid_degradation", "moderate_degradation"]:
            recommendations.append({
                "priority": "high",
                "action": "增加监控频率",
                "reason": "设备处于降级状态",
                "deadline": "立即"
            })

        if maintenance_schedule.get("spare_parts_order"):
            recommendations.append({
                "priority": "medium",
                "action": "订购备件",
                "reason": "建议在维护前准备好备件",
                "deadline": f"{maintenance_schedule['spare_parts_order']}天内"
            })

        recommendations.append({
            "priority": "routine",
            "action": "进行预防性维护检查",
            "reason": "确保设备运行参数正常",
            "deadline": f"{maintenance_schedule.get('next_inspection', 14)}天内"
        })

        if equipment_info.operating_hours > 5000:
            recommendations.append({
                "priority": "advisory",
                "action": "考虑设备更新评估",
                "reason": f"运行时间已达 {equipment_info.operating_hours} 小时",
                "deadline": "下次大修时"
            })

        return recommendations

    def _generate_executive_summary(
        self,
        equipment_info: EquipmentInfo,
        health_score: float,
        rul_result: RULResult,
        recommendations: List[Dict[str, str]]
    ) -> str:
        """生成执行摘要"""
        status_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }

        emoji = status_emoji.get(rul_result.maintenance_priority, "⚪")

        summary_parts = [
            f"{emoji} 设备 {equipment_info.equipment_name} ({equipment_info.equipment_id})",
            f"当前健康状态: {health_score:.1%}",
            f"剩余使用寿命: {rul_result.rul_days:.0f} 天 ({rul_result.maintenance_priority.upper()} 优先级)",
        ]

        if rul_result.estimated_failure_date:
            summary_parts.append(
                f"预计故障日期: {rul_result.estimated_failure_date.strftime('%Y-%m-%d')}"
            )

        critical_actions = [r for r in recommendations if r["priority"] == "immediate"]
        if critical_actions:
            summary_parts.append(f"\n⚠️ 紧急行动: {critical_actions[0]['action']}")

        return "\n".join(summary_parts)

    def format_markdown(self, report: MaintenanceReport) -> str:
        """
        格式化为Markdown

        Args:
            report: 维护报告

        Returns:
            Markdown格式报告
        """
        lines = [
            f"# 设备维护报告",
            f"",
            f"**报告ID**: {report.report_id}",
            f"**生成时间**: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 执行摘要",
            f"",
            f"{report.executive_summary}",
            f"",
            f"## 设备信息",
            f"",
            f"| 项目 | 内容 |",
            f"|------|------|",
            f"| 设备ID | {report.equipment_info.equipment_id} |",
            f"| 设备名称 | {report.equipment_info.equipment_name} |",
            f"| 设备类型 | {report.equipment_info.equipment_type} |",
            f"| 区域 | Zone {report.equipment_info.zone_id} |",
            f"| 安装日期 | {report.equipment_info.install_date.strftime('%Y-%m-%d')} |",
            f"| 运行小时 | {report.equipment_info.operating_hours:,} h |",
            f"| 上次维护 | {report.equipment_info.last_maintenance_date.strftime('%Y-%m-%d') if report.equipment_info.last_maintenance_date else 'N/A'} |",
            f"",
            f"## 健康评估",
            f"",
            f"- **当前健康分数**: {report.current_health_score:.1%}",
            f"- **健康状态**: {report.rul_result.health_status.upper()}",
            f"- **趋势**: {report.rul_result.trend}",
            f"- **置信度**: {report.rul_result.confidence:.1%}",
            f"",
            f"## RUL预测",
            f"",
            f"- **剩余使用寿命**: {report.rul_result.rul_days:.0f} 天 ({report.rul_result.rul_hours:.0f} 小时)",
            f"- **维护优先级**: {report.rul_result.maintenance_priority.upper()}",
            f"- **预计故障日期**: {report.rul_result.estimated_failure_date.strftime('%Y-%m-%d') if report.rul_result.estimated_failure_date else 'N/A'}",
            f"- **建议**: {report.rul_result.recommendation}",
            f"",
            f"## 风险评估",
            f"",
            f"- **整体风险等级**: {report.risk_assessment['overall_risk'].upper()}",
            f"- **风险分数**: {report.risk_assessment['risk_score']:.1f}/100",
            f"- **生产影响**: {report.risk_assessment['production_impact']['quality_impact']}",
            f"",
            f"## 维护计划",
            f"",
            f"| 项目 | 时间 |",
            f"|------|------|",
        ]

        for key, value in report.maintenance_schedule.items():
            if value:
                lines.append(f"| {key.replace('_', ' ').title()} | {value}天 |")

        lines.extend([
            f"",
            f"## 建议行动",
            f"",
        ])

        for rec in report.recommendations:
            lines.append(f"- **[{rec['priority'].upper()}]** {rec['action']}")
            lines.append(f"  - 原因: {rec['reason']}")
            lines.append(f"  - 期限: {rec['deadline']}")

        return "\n".join(lines)

    def format_json(self, report: MaintenanceReport) -> str:
        """
        格式化为JSON

        Args:
            report: 维护报告

        Returns:
            JSON格式报告
        """
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, '__dataclass_fields__'):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, list):
                return [serialize(i) for i in obj]
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj

        return json.dumps(serialize(report), indent=2, ensure_ascii=False)
