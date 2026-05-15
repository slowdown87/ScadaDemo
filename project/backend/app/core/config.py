from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "CIP SCADA Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://scada:scada123@localhost:5432/cip_scada"
    redis_url: str = "redis://localhost:6379/0"

    mqtt_broker_url: str = "mqtt://localhost:1883"
    mqtt_username: str = "scada"
    mqtt_password: str = "scada123"

    plc_ip: str = "192.168.2.100"
    plc_rack: int = 0
    plc_slot: int = 1
    plc_tcp_port: int = 102

    scada_zone_count: int = 5
    scada_refresh_interval_ms: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
