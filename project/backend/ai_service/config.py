"""
Configuration Management
统一配置管理，支持环境变量和环境配置
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # Application
    APP_NAME: str = "CIP AI Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_KEY_PREFIX: str = "cip:ai:"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cip_scada"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # AI Models
    MODEL_CACHE_DIR: str = "./models"
    ANOMALY_MODEL_PATH: str = "./models/anomaly_detector.joblib"
    MAINTENANCE_MODEL_PATH: str = "./models/maintenance_lstm.pt"

    # Anomaly Detection
    ANOMALY_THRESHOLD: float = -0.5
    ANOMALY_CONTAMINATION: float = 0.01
    ANOMALY_N_ESTIMATORS: int = 100
    ANOMALY_DETECTION_INTERVAL: int = 10  # seconds

    # Predictive Maintenance
    LSTM_HIDDEN_SIZE: int = 64
    LSTM_NUM_LAYERS: int = 2
    LSTM_DROPOUT: float = 0.2
    HEALTH_THRESHOLD: float = 0.7
    MAINTENANCE_WINDOW_DAYS: int = 7
    MAX_RUL_DAYS: int = 90

    # Parameter Optimization
    BAYESIAN_ITERATIONS: int = 30
    BAYESIAN_INIT_POINTS: int = 10

    # Energy Management
    STEAM_PRICE: float = 0.15  # yuan/kg
    WATER_PRICE: float = 0.005  # yuan/L
    ELECTRICITY_PRICE: float = 0.8  # yuan/kWh

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_CONNECTIONS: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    return Settings()


# 全局配置实例
settings = get_settings()
