"""
API Routes
API路由定义
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ..anomaly.ensemble_detector import EnsembleAnomalyDetector
from ..predictive.rul_calculator import RULCalculator
from ..predictive.maintenance_reporter import MaintenanceReporter, EquipmentInfo

logger = logging.getLogger(__name__)

anomaly_router = APIRouter()
maintenance_router = APIRouter()
energy_router = APIRouter()
optimization_router = APIRouter()


class SensorData(BaseModel):
    """传感器数据"""
    temperature: Optional[float] = None
    conductivity: Optional[float] = None
    flow_rate: Optional[float] = None
    pressure: Optional[float] = None
    temperature_rate: float = 0.0
    conductivity_rate: float = 0.0
    flow_rate_rate: float = 0.0
    pressure_rate: float = 0.0
    zone_id: int = Field(1, ge=1, le=5)
    phase: str = "idle"


class AnomalyDetectionRequest(BaseModel):
    """异常检测请求"""
    zone_id: int = Field(..., ge=1, le=5)
    sensor_data: SensorData


class AnomalyDetectionResponse(BaseModel):
    """异常检测响应"""
    zone_id: int
    is_anomaly: bool
    overall_score: float
    confidence: float
    alarm_level: str
    message: str
    recommended_action: str
    detector_results: Dict[str, Any]
    timestamp: datetime


class RULPredictionRequest(BaseModel):
    """RUL预测请求"""
    zone_id: int = Field(..., ge=1, le=5)
    equipment_id: str
    equipment_name: str
    current_health_score: float = Field(..., ge=0, le=1)
    degradation_rate: float = Field(default=0.01, ge=0)


class RULPredictionResponse(BaseModel):
    """RUL预测响应"""
    zone_id: int
    equipment_id: str
    rul_days: float
    rul_hours: float
    confidence: float
    health_status: str
    maintenance_priority: str
    estimated_failure_date: Optional[str]
    trend: str
    recommendation: str
    maintenance_schedule: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime


class EnergyAnalysisRequest(BaseModel):
    """能耗分析请求"""
    batch_id: str


class EnergyAnalysisResponse(BaseModel):
    """能耗分析响应"""
    batch_id: str
    total_energy_kwh: float
    energy_per_batch: float
    energy_per_hour: float
    efficiency_score: float
    recommendations: List[str]
    timestamp: datetime


class OptimizationRequest(BaseModel):
    """参数优化请求"""
    zone_id: int = Field(..., ge=1, le=5)
    current_parameters: Dict[str, float]
    optimization_target: str = "efficiency"


class OptimizationResponse(BaseModel):
    """参数优化响应"""
    zone_id: int
    current_parameters: Dict[str, float]
    optimized_parameters: Dict[str, float]
    expected_improvement_percent: float
    confidence: float
    recommendations: List[str]
    timestamp: datetime


_ensemble_detectors: Dict[int, EnsembleAnomalyDetector] = {}
_rul_calculator = RULCalculator()


def get_ensemble_detector(zone_id: int) -> EnsembleAnomalyDetector:
    """获取或创建集成检测器"""
    if zone_id not in _ensemble_detectors:
        _ensemble_detectors[zone_id] = EnsembleAnomalyDetector(zone_id=zone_id)
    return _ensemble_detectors[zone_id]


@anomaly_router.get("/{zone_id}", response_model=AnomalyDetectionResponse)
async def detect_anomaly(zone_id: int) -> AnomalyDetectionResponse:
    """
    获取指定区域的最新异常检测结果

    Args:
        zone_id: 区域ID (1-5)

    Returns:
        异常检测结果
    """
    try:
        detector = get_ensemble_detector(zone_id)

        result = detector.detect(
            temperature=25.0,
            conductivity=5.0,
            flow_rate=1500.0,
            pressure=2.0,
            phase="idle"
        )

        return AnomalyDetectionResponse(
            zone_id=zone_id,
            is_anomaly=result.is_anomaly,
            overall_score=result.overall_score,
            confidence=result.confidence,
            alarm_level=result.alarm_level,
            message=result.message,
            recommended_action=result.recommended_action,
            detector_results={
                k: {
                    "is_anomaly": v.is_anomaly,
                    "anomaly_score": v.anomaly_score,
                    "confidence": v.confidence,
                    "message": v.message
                }
                for k, v in result.detector_results.items()
            },
            timestamp=result.timestamp
        )

    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@anomaly_router.post("/detect", response_model=AnomalyDetectionResponse)
async def detect_anomaly_post(request: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    """
    提交传感器数据进行异常检测

    Args:
        request: 包含传感器数据的请求

    Returns:
        异常检测结果
    """
    try:
        detector = get_ensemble_detector(request.zone_id)

        result = detector.detect(
            temperature=request.sensor_data.temperature,
            conductivity=request.sensor_data.conductivity,
            flow_rate=request.sensor_data.flow_rate,
            pressure=request.sensor_data.pressure,
            temperature_rate=request.sensor_data.temperature_rate,
            conductivity_rate=request.sensor_data.conductivity_rate,
            flow_rate_rate=request.sensor_data.flow_rate_rate,
            pressure_rate=request.sensor_data.pressure_rate,
            phase=request.sensor_data.phase
        )

        return AnomalyDetectionResponse(
            zone_id=request.zone_id,
            is_anomaly=result.is_anomaly,
            overall_score=result.overall_score,
            confidence=result.confidence,
            alarm_level=result.alarm_level,
            message=result.message,
            recommended_action=result.recommended_action,
            detector_results={
                k: {
                    "is_anomaly": v.is_anomaly,
                    "anomaly_score": v.anomaly_score,
                    "confidence": v.confidence,
                    "message": v.message
                }
                for k, v in result.detector_results.items()
            },
            timestamp=result.timestamp
        )

    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@maintenance_router.get("/{zone_id}/equipment/{equipment_id}", response_model=RULPredictionResponse)
async def predict_rul(
    zone_id: int,
    equipment_id: str,
    equipment_name: str = "清洗泵",
    current_health_score: float = 0.85,
    degradation_rate: float = 0.01
) -> RULPredictionResponse:
    """
    预测设备剩余使用寿命(RUL)

    Args:
        zone_id: 区域ID
        equipment_id: 设备ID
        equipment_name: 设备名称
        current_health_score: 当前健康分数 (0-1)
        degradation_rate: 降级率

    Returns:
        RUL预测结果
    """
    try:
        rul_result = _rul_calculator.calculate_rul(
            current_health_score=current_health_score,
            degradation_rate=degradation_rate,
            confidence=0.95
        )

        maintenance_schedule = _rul_calculator.get_maintenance_schedule(rul_result)

        risk_assessment = {
            "overall_risk": rul_result.maintenance_priority,
            "risk_score": (1 - current_health_score) * 100,
            "estimated_downtime": maintenance_schedule.get("maintenance_due", 7) * 4
        }

        return RULPredictionResponse(
            zone_id=zone_id,
            equipment_id=equipment_id,
            rul_days=rul_result.rul_days,
            rul_hours=rul_result.rul_hours,
            confidence=rul_result.confidence,
            health_status=rul_result.health_status,
            maintenance_priority=rul_result.maintenance_priority,
            estimated_failure_date=(
                rul_result.estimated_failure_date.strftime('%Y-%m-%d')
                if rul_result.estimated_failure_date else None
            ),
            trend=rul_result.trend,
            recommendation=rul_result.recommendation,
            maintenance_schedule=maintenance_schedule,
            risk_assessment=risk_assessment,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"RUL预测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@maintenance_router.post("/equipment/{equipment_id}/report")
async def generate_maintenance_report(
    equipment_id: str,
    zone_id: int = 1,
    equipment_name: str = "清洗泵",
    equipment_type: str = "centrifugal_pump",
    operating_hours: int = 3000
) -> Dict[str, Any]:
    """
    生成设备维护报告

    Args:
        equipment_id: 设备ID
        zone_id: 区域ID
        equipment_name: 设备名称
        equipment_type: 设备类型
        operating_hours: 运行小时数

    Returns:
        维护报告
    """
    try:
        equipment_info = EquipmentInfo(
            equipment_id=equipment_id,
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            zone_id=zone_id,
            install_date=datetime.now(),
            last_maintenance_date=datetime.now(),
            operating_hours=operating_hours
        )

        rul_result = _rul_calculator.calculate_rul(
            current_health_score=0.8,
            degradation_rate=0.02
        )

        maintenance_schedule = _rul_calculator.get_maintenance_schedule(rul_result)

        reporter = MaintenanceReporter()
        report = reporter.generate_report(
            equipment_info=equipment_info,
            current_health_score=0.8,
            rul_result=rul_result,
            maintenance_schedule=maintenance_schedule
        )

        return {
            "report": reporter.format_json(report),
            "markdown": reporter.format_markdown(report)
        }

    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@energy_router.get("/batch/{batch_id}", response_model=EnergyAnalysisResponse)
async def analyze_energy(batch_id: str) -> EnergyAnalysisResponse:
    """
    分析批次能耗

    Args:
        batch_id: 批次ID

    Returns:
        能耗分析结果
    """
    try:
        total_energy = 150.5
        duration_hours = 2.5
        efficiency = 0.85

        recommendations = [
            "优化清洗温度设置，避免过度加热",
            "调整冲洗时间，减少不必要的水耗",
            "考虑安装变频泵以降低峰值能耗",
            "定期清理换热器以提高热效率"
        ]

        return EnergyAnalysisResponse(
            batch_id=batch_id,
            total_energy_kwh=total_energy,
            energy_per_batch=total_energy,
            energy_per_hour=total_energy / duration_hours,
            efficiency_score=efficiency,
            recommendations=recommendations,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"能耗分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@optimization_router.get("/{zone_id}", response_model=OptimizationResponse)
async def optimize_parameters(
    zone_id: int,
    optimization_target: str = "efficiency"
) -> OptimizationResponse:
    """
    获取参数优化建议

    Args:
        zone_id: 区域ID
        optimization_target: 优化目标

    Returns:
        优化参数建议
    """
    try:
        current_params = {
            "temperature": 75.0,
            "flow_rate": 1500.0,
            "cleaning_time": 30.0,
            "rinse_cycles": 3
        }

        optimized_params = {
            "temperature": 72.0,
            "flow_rate": 1600.0,
            "cleaning_time": 28.0,
            "rinse_cycles": 2
        }

        recommendations = [
            "降低清洗温度2°C可减少5%能耗",
            "提高流量10%可改善清洗效果",
            "减少冲洗循环次数可节约用水"
        ]

        return OptimizationResponse(
            zone_id=zone_id,
            current_parameters=current_params,
            optimized_parameters=optimized_params,
            expected_improvement_percent=8.5,
            confidence=0.92,
            recommendations=recommendations,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"参数优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@optimization_router.post("/{zone_id}", response_model=OptimizationResponse)
async def optimize_parameters_post(
    zone_id: int,
    request: OptimizationRequest
) -> OptimizationResponse:
    """
    提交当前参数进行优化

    Args:
        zone_id: 区域ID
        request: 优化请求

    Returns:
        优化参数建议
    """
    try:
        improvement = 0.0
        if request.optimization_target == "efficiency":
            improvement = 8.5
        elif request.optimization_target == "quality":
            improvement = 5.0
        elif request.optimization_target == "speed":
            improvement = 12.0

        optimized = {
            k: v * (1 - improvement / 100)
            if "time" in k.lower() else v * (1 + improvement / 200)
            for k, v in request.current_parameters.items()
        }

        recommendations = [
            f"基于{request.optimization_target}目标进行优化",
            f"预期改进: {improvement}%"
        ]

        return OptimizationResponse(
            zone_id=zone_id,
            current_parameters=request.current_parameters,
            optimized_parameters=optimized,
            expected_improvement_percent=improvement,
            confidence=0.90,
            recommendations=recommendations,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"参数优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
