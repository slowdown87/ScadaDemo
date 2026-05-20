"""
SQL Client
PostgreSQL历史数据查询客户端
支持连接管理、数据查询、连接池
"""

import asyncpg
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging
from config import settings

logger = logging.getLogger(__name__)


class SQLClient:
    """PostgreSQL客户端封装类"""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._connected: bool = False

    async def connect(self) -> bool:
        """建立数据库连接池"""
        try:
            if self._pool:
                await self.close()

            self._pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=2,
                max_size=10,
                command_timeout=60
            )

            self._connected = True
            logger.info(
                f"PostgreSQL connected: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
            return True

        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            self._connected = False
            return False

    async def close(self):
        """关闭数据库连接池"""
        if self._pool:
            try:
                await self._pool.close()
                logger.info("PostgreSQL connection pool closed")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL pool: {e}")
            finally:
                self._pool = None
                self._connected = False

    async def ensure_connection(self) -> bool:
        """确保连接池可用"""
        if not self._connected or not self._pool:
            return await self.connect()
        return True

    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """执行查询并返回结果"""
        try:
            if not await self.ensure_connection():
                return []

            async with self._pool.acquire() as connection:
                results = await connection.fetch(query, *args)
                return results

        except Exception as e:
            logger.error(f"SQL FETCH error: {e}")
            return []

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """执行查询并返回单条结果"""
        try:
            if not await self.ensure_connection():
                return None

            async with self._pool.acquire() as connection:
                result = await connection.fetchrow(query, *args)
                return result

        except Exception as e:
            logger.error(f"SQL FETCHROW error: {e}")
            return None

    async def execute(self, query: str, *args) -> str:
        """执行SQL语句"""
        try:
            if not await self.ensure_connection():
                return ""

            async with self._pool.acquire() as connection:
                result = await connection.execute(query, *args)
                return result

        except Exception as e:
            logger.error(f"SQL EXECUTE error: {e}")
            return ""

    # ============ CIP批次数据查询 ============

    async def get_batch_by_id(self, batch_id: str) -> Optional[Dict]:
        """
        根据批次ID获取批次信息

        Args:
            batch_id: 批次ID

        Returns:
            批次信息字典
        """
        query = """
            SELECT
                batch_id,
                zone_id,
                recipe_name,
                status,
                start_time,
                end_time,
                duration,
                final_conductivity,
                pass_fail,
                operator
            FROM cip_batches
            WHERE batch_id = $1
        """

        result = await self.fetchrow(query, batch_id)

        if result:
            return dict(result)
        return None

    async def get_batch_list(
        self,
        zone_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取批次列表

        Args:
            zone_id: 区域ID (可选)
            start_date: 开始日期 (可选)
            end_date: 结束日期 (可选)
            limit: 返回数量限制

        Returns:
            批次列表
        """
        conditions = []
        params = []
        param_idx = 1

        if zone_id is not None:
            conditions.append(f"zone_id = ${param_idx}")
            params.append(zone_id)
            param_idx += 1

        if start_date:
            conditions.append(f"start_time >= ${param_idx}")
            params.append(start_date)
            param_idx += 1

        if end_date:
            conditions.append(f"start_time <= ${param_idx}")
            params.append(end_date)
            param_idx += 1

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT
                batch_id,
                zone_id,
                recipe_name,
                status,
                start_time,
                end_time,
                duration,
                final_conductivity,
                pass_fail,
                operator
            FROM cip_batches
            {where_clause}
            ORDER BY start_time DESC
            LIMIT ${param_idx}
        """
        params.append(limit)

        results = await self.fetch(query, *params)
        return [dict(row) for row in results]

    async def get_batch_steps(self, batch_id: str) -> List[Dict]:
        """
        获取批次的步骤数据

        Args:
            batch_id: 批次ID

        Returns:
            步骤列表
        """
        query = """
            SELECT
                step_id,
                batch_id,
                step_number,
                media_name,
                target_temp,
                actual_temp,
                target_time,
                actual_duration,
                flow_rate,
                conductivity,
                status
            FROM cip_batch_steps
            WHERE batch_id = $1
            ORDER BY step_number
        """

        results = await self.fetch(query, batch_id)
        return [dict(row) for row in results]

    async def get_batch_datapoints(
        self,
        batch_id: str,
        limit: int = 1000
    ) -> List[Dict]:
        """
        获取批次的数据点

        Args:
            batch_id: 批次ID
            limit: 返回数量限制

        Returns:
            数据点列表
        """
        query = """
            SELECT
                timestamp,
                zone_id,
                temp_outlet,
                temp_return,
                conductivity,
                pressure,
                flow,
                pump_frequency,
                valve_status
            FROM cip_batch_datapoints
            WHERE batch_id = $1
            ORDER BY timestamp
            LIMIT $2
        """

        results = await self.fetch(query, batch_id, limit)
        return [dict(row) for row in results]

    async def get_zone_sensor_features(
        self,
        zone_id: int,
        days: int = 30
    ) -> List[Dict]:
        """
        获取区域传感器特征数据（用于模型训练）

        聚合最近N天的数据，计算统计特征

        Args:
            zone_id: 区域ID (1-5)
            days: 历史天数

        Returns:
            特征数据列表
        """
        query = """
            WITH aggregated AS (
                SELECT
                    date_trunc('hour', timestamp) as time_bucket,
                    AVG(temp_outlet) as avg_temp_outlet,
                    AVG(temp_return) as avg_temp_return,
                    AVG(conductivity) as avg_conductivity,
                    AVG(pressure) as avg_pressure,
                    AVG(flow) as avg_flow,
                    MIN(temp_outlet) as min_temp_outlet,
                    MAX(temp_outlet) as max_temp_outlet,
                    STDDEV(flow) as std_flow
                FROM cip_batch_datapoints
                WHERE zone_id = $1
                    AND timestamp > NOW() - INTERVAL '1 day' * $2
                GROUP BY time_bucket
                ORDER BY time_bucket
            )
            SELECT
                time_bucket,
                avg_temp_outlet,
                avg_temp_return,
                avg_conductivity,
                avg_pressure,
                avg_flow,
                min_temp_outlet,
                max_temp_outlet,
                std_flow
            FROM aggregated
        """

        results = await self.fetch(query, zone_id, days)
        return [dict(row) for row in results]

    async def get_equipment_maintenance_records(
        self,
        zone_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        获取设备维护记录

        Args:
            zone_id: 区域ID (1-5)
            limit: 返回数量限制

        Returns:
            维护记录列表
        """
        query = """
            SELECT
                record_id,
                zone_id,
                equipment_type,
                equipment_id,
                maintenance_type,
                maintenance_date,
                description,
                duration_minutes,
                technician,
                result
            FROM equipment_maintenance
            WHERE zone_id = $1
            ORDER BY maintenance_date DESC
            LIMIT $2
        """

        results = await self.fetch(query, zone_id, limit)
        return [dict(row) for row in results]

    async def get_equipment_failures(
        self,
        zone_id: int,
        days: int = 90
    ) -> List[Dict]:
        """
        获取设备故障记录

        Args:
            zone_id: 区域ID (1-5)
            days: 历史天数

        Returns:
            故障记录列表
        """
        query = """
            SELECT
                failure_id,
                zone_id,
                equipment_id,
                failure_type,
                failure_time,
                recovery_time,
                root_cause,
                solution,
                duration_minutes
            FROM equipment_failures
            WHERE zone_id = $1
                AND failure_time > NOW() - INTERVAL '1 day' * $2
            ORDER BY failure_time DESC
        """

        results = await self.fetch(query, zone_id, days)
        return [dict(row) for row in results]

    async def get_energy_consumption(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'
    ) -> List[Dict]:
        """
        获取能源消耗数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            group_by: 分组方式 ('day', 'week', 'month')

        Returns:
            能源消耗数据
        """
        date_format = {
            'day': 'YYYY-MM-DD',
            'week': 'IYYY-IW',
            'month': 'YYYY-MM'
        }.get(group_by, 'YYYY-MM-DD')

        conditions = []
        params = []
        param_idx = 1

        if start_date:
            conditions.append(f"start_time >= ${param_idx}")
            params.append(start_date)
            param_idx += 1

        if end_date:
            conditions.append(f"start_time <= ${param_idx}")
            params.append(end_date)
            param_idx += 1

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        query = f"""
            SELECT
                TO_CHAR(start_time, '{date_format}') as period,
                COUNT(*) as batch_count,
                SUM(duration) as total_duration,
                -- 这里应该关联能耗表，简化版本使用估算
                SUM(duration * 0.5) as estimated_steam_kg,
                SUM(duration * 0.1) as estimated_water_l,
                SUM(duration * 0.05) as estimated_electricity_kwh
            FROM cip_batches
            {where_clause}
            GROUP BY period
            ORDER BY period DESC
        """

        results = await self.fetch(query, *params)
        return [dict(row) for row in results]

    async def save_anomaly_detection(
        self,
        zone_id: int,
        anomaly_type: str,
        anomaly_score: float,
        confidence: float,
        recommendation: str
    ) -> bool:
        """
        保存异常检测记录到数据库

        Args:
            zone_id: 区域ID
            anomaly_type: 异常类型
            anomaly_score: 异常分数
            confidence: 置信度
            recommendation: 建议

        Returns:
            是否保存成功
        """
        query = """
            INSERT INTO anomaly_detections (
                zone_id,
                detection_time,
                anomaly_type,
                anomaly_score,
                confidence,
                recommendation
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """

        try:
            await self.execute(
                query,
                zone_id,
                datetime.now(),
                anomaly_type,
                anomaly_score,
                confidence,
                recommendation
            )
            return True

        except Exception as e:
            logger.error(f"Save anomaly detection failed: {e}")
            return False


# 全局SQL客户端实例
sql_client = SQLClient()


async def get_sql_client() -> SQLClient:
    """获取SQL客户端实例"""
    if not sql_client.is_connected:
        await sql_client.connect()
    return sql_client
