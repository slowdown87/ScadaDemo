from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON
from datetime import datetime
from app.core.database import Base


class BatchRecordModel(Base):
    __tablename__ = "batch_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(String(50), unique=True, index=True, nullable=False)
    zone_id = Column(Integer, nullable=False, index=True)
    zone_name = Column(String(50), nullable=False)
    recipe_id = Column(Integer, nullable=False)
    recipe_name = Column(String(50), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_time = Column(Integer, nullable=False)

    result = Column(Boolean, nullable=False)
    final_conductivity = Column(Float, nullable=True)
    fail_reason = Column(String(200), nullable=True)

    steps_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
