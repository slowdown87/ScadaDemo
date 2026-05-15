from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal


class DataService:
    async def save_batch_record(self, record_data: dict) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                from app.models.batch import BatchRecordModel
                record = BatchRecordModel(**record_data)
                session.add(record)
                await session.commit()
                return True
            except Exception as e:
                print(f"Save batch record error: {e}")
                await session.rollback()
                return False

    async def get_batch_records(
        self,
        zone_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        limit = min(limit, 1000)
        async with AsyncSessionLocal() as session:
            try:
                from app.models.batch import BatchRecordModel
                query = select(BatchRecordModel)
                if zone_id:
                    query = query.where(BatchRecordModel.zone_id == zone_id)
                if start_time:
                    query = query.where(BatchRecordModel.start_time >= start_time)
                if end_time:
                    query = query.where(BatchRecordModel.end_time <= end_time)
                query = query.order_by(desc(BatchRecordModel.start_time)).limit(limit)
                result = await session.execute(query)
                records = result.scalars().all()
                return [
                    {
                        "id": record.id,
                        "record_id": record.record_id,
                        "zone_id": record.zone_id,
                        "zone_name": record.zone_name,
                        "recipe_id": record.recipe_id,
                        "recipe_name": record.recipe_name,
                        "start_time": record.start_time,
                        "end_time": record.end_time,
                        "total_time": record.total_time,
                        "result": record.result,
                        "final_conductivity": record.final_conductivity,
                        "fail_reason": record.fail_reason,
                        "steps_data": record.steps_data,
                        "created_at": record.created_at,
                    }
                    for record in records
                ]
            except Exception as e:
                print(f"Get batch records error: {e}")
                return []

    async def get_alarm_history(
        self,
        zone_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[dict]:
        async with AsyncSessionLocal() as session:
            try:
                from app.models.alarm import AlarmRecordModel
                query = select(AlarmRecordModel)
                if zone_id:
                    query = query.where(AlarmRecordModel.zone_id == zone_id)
                if start_time:
                    query = query.where(AlarmRecordModel.trigger_time >= start_time)
                if end_time:
                    query = query.where(AlarmRecordModel.trigger_time <= end_time)
                query = query.order_by(desc(AlarmRecordModel.trigger_time)).limit(limit)
                result = await session.execute(query)
                records = result.scalars().all()
                return [
                    {
                        "id": record.id,
                        "alarm_id": record.alarm_id,
                        "alarm_code": record.alarm_code,
                        "alarm_text": record.alarm_text,
                        "level": record.level,
                        "zone_id": record.zone_id,
                        "trigger_time": record.trigger_time,
                        "ack_time": record.ack_time,
                        "ack_user": record.ack_user,
                        "status": record.status,
                        "created_at": record.created_at,
                    }
                    for record in records
                ]
            except Exception as e:
                print(f"Get alarm history error: {e}")
                return []
