from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class AlarmRecordModel(Base):
    __tablename__ = "alarm_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alarm_id = Column(Integer, nullable=False, index=True)
    alarm_code = Column(Integer, nullable=False, index=True)
    alarm_text = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)
    zone_id = Column(Integer, nullable=False, index=True)

    trigger_time = Column(DateTime, nullable=False, index=True)
    ack_time = Column(DateTime, nullable=True)
    ack_user = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
