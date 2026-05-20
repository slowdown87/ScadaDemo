"""
FastAPI Application Entry
FastAPI应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

from .routes import anomaly_router, maintenance_router, energy_router, optimization_router
from .websocket import router as websocket_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CIP AI Service",
    description="茶饮料CIP清洗系统AI推理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(anomaly_router, prefix="/api/v1/ai/anomaly", tags=["异常检测"])
app.include_router(maintenance_router, prefix="/api/v1/ai/maintenance", tags=["预测维护"])
app.include_router(energy_router, prefix="/api/v1/ai/energy", tags=["能耗分析"])
app.include_router(optimization_router, prefix="/api/v1/ai/optimization", tags=["参数优化"])
app.include_router(websocket_router, prefix="/api/v1/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "CIP AI Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "anomaly": "/api/v1/ai/anomaly",
            "maintenance": "/api/v1/ai/maintenance",
            "energy": "/api/v1/ai/energy",
            "optimization": "/api/v1/ai/optimization",
            "websocket": "/api/v1/ws"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "timestamp": "2026-05-19T00:00:00Z"
    }


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("AI Service starting...")
    logger.info(f"CORS enabled for all origins")
    logger.info("AI Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("AI Service shutting down...")
    logger.info("AI Service stopped")
