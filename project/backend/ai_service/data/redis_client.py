"""
Redis Client
Redis数据读取客户端
支持连接管理、自动重连、数据读取
"""

import redis.asyncio as redis
from typing import Optional, Dict, List, Any
import json
import logging
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端封装类"""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connected: bool = False
        self._reconnect_attempts: int = 0
        self._max_reconnect_attempts: int = 5

    async def connect(self) -> bool:
        """建立Redis连接"""
        try:
            if self._client:
                await self.close()

            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 测试连接
            await self._client.ping()

            self._connected = True
            self._reconnect_attempts = 0
            logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return True

        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self._connected = False
            return False

    async def close(self):
        """关闭Redis连接"""
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None
                self._connected = False

    async def reconnect(self) -> bool:
        """尝试重新连接"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return False

        self._reconnect_attempts += 1
        logger.info(f"Attempting Redis reconnection ({self._reconnect_attempts}/{self._max_reconnect_attempts})")

        for attempt in range(self._max_reconnect_attempts):
            try:
                if await self.connect():
                    return True
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")

        return False

    async def ensure_connection(self) -> bool:
        """确保连接可用，必要时重连"""
        if not self._connected or not self._client:
            return await self.reconnect()

        try:
            await self._client.ping()
            return True
        except Exception:
            logger.warning("Redis connection lost, attempting reconnect")
            return await self.reconnect()

    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected

    async def get(self, key: str) -> Optional[str]:
        """获取单个值"""
        try:
            if not await self.ensure_connection():
                return None

            value = await self._client.get(key)
            return value

        except Exception as e:
            logger.error(f"Redis GET error ({key}): {e}")
            return None

    async def get_json(self, key: str) -> Optional[Dict]:
        """获取JSON格式的数据"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for {key}: {e}")
                return None
        return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """设置单个值"""
        try:
            if not await self.ensure_connection():
                return False

            if expire:
                await self._client.setex(key, expire, value)
            else:
                await self._client.set(key, value)

            return True

        except Exception as e:
            logger.error(f"Redis SET error ({key}): {e}")
            return False

    async def set_json(
        self,
        key: str,
        value: Dict,
        expire: Optional[int] = None
    ) -> bool:
        """设置JSON格式的数据"""
        try:
            json_str = json.dumps(value, default=str)
            return await self.set(key, json_str, expire)

        except Exception as e:
            logger.error(f"JSON SET error ({key}): {e}")
            return False

    async def get_zone_latest(self, zone_id: int) -> Optional[Dict]:
        """
        获取指定区域的最新传感器数据

        Redis Key Pattern: cip:zone:{zone_id}:latest

        Args:
            zone_id: 区域ID (1-5)

        Returns:
            传感器数据字典
        """
        key = f"cip:zone:{zone_id}:latest"
        return await self.get_json(key)

    async def get_all_zones_latest(self) -> Dict[int, Optional[Dict]]:
        """
        获取所有区域的最新传感器数据

        Returns:
            {zone_id: sensor_data}
        """
        results = {}
        for zone_id in range(1, 6):
            results[zone_id] = await self.get_zone_latest(zone_id)
        return results

    async def get_zone_history(
        self,
        zone_id: int,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取指定区域的历史传感器数据

        Redis Key Pattern: cip:zone:{zone_id}:history

        Args:
            zone_id: 区域ID (1-5)
            limit: 返回记录数量

        Returns:
            历史数据列表
        """
        key = f"cip:zone:{zone_id}:history"

        try:
            if not await self.ensure_connection():
                return []

            # 使用LPUSH + LRANGE获取历史数据
            data = await self._client.lrange(key, 0, limit - 1)

            results = []
            for item in data:
                try:
                    results.append(json.loads(item))
                except json.JSONDecodeError:
                    continue

            return results

        except Exception as e:
            logger.error(f"Redis GET history error (Zone {zone_id}): {e}")
            return []

    async def get_batch_data(self, batch_id: str) -> Optional[Dict]:
        """
        获取批次数据

        Redis Key Pattern: cip:batch:{batch_id}

        Args:
            batch_id: 批次ID

        Returns:
            批次数据字典
        """
        key = f"cip:batch:{batch_id}"
        return await self.get_json(key)

    async def get_anomaly_results(self, zone_id: int) -> List[Dict]:
        """
        获取区域异常检测历史结果

        Redis Key Pattern: cip:zone:{zone_id}:anomalies

        Args:
            zone_id: 区域ID (1-5)

        Returns:
            异常记录列表
        """
        key = f"cip:zone:{zone_id}:anomalies"

        try:
            if not await self.ensure_connection():
                return []

            data = await self._client.lrange(key, 0, 99)

            results = []
            for item in data:
                try:
                    results.append(json.loads(item))
                except json.JSONDecodeError:
                    continue

            return results

        except Exception as e:
            logger.error(f"Redis GET anomalies error (Zone {zone_id}): {e}")
            return []

    async def save_anomaly_result(self, zone_id: int, result: Dict) -> bool:
        """
        保存异常检测结果

        Args:
            zone_id: 区域ID (1-5)
            result: 异常检测结果

        Returns:
            是否保存成功
        """
        key = f"cip:zone:{zone_id}:anomalies"

        try:
            if not await self.ensure_connection():
                return False

            # 添加时间戳
            result['timestamp'] = datetime.now().isoformat()
            json_str = json.dumps(result)

            # 存入列表，最多保留100条
            await self._client.lpush(key, json_str)
            await self._client.ltrim(key, 0, 99)

            return True

        except Exception as e:
            logger.error(f"Redis save anomaly error (Zone {zone_id}): {e}")
            return False

    async def get_model_cache(self, model_name: str) -> Optional[Dict]:
        """
        获取模型缓存数据

        Redis Key Pattern: cip:ai:model:{model_name}

        Args:
            model_name: 模型名称

        Returns:
            缓存数据
        """
        key = f"cip:ai:model:{model_name}"
        return await self.get_json(key)

    async def set_model_cache(
        self,
        model_name: str,
        data: Dict,
        expire: int = 3600
    ) -> bool:
        """
        设置模型缓存数据

        Args:
            model_name: 模型名称
            data: 缓存数据
            expire: 过期时间(秒)，默认1小时

        Returns:
            是否保存成功
        """
        key = f"cip:ai:model:{model_name}"
        return await self.set_json(key, data, expire)

    async def publish(self, channel: str, message: Dict) -> bool:
        """
        发布消息到指定频道

        Args:
            channel: 频道名称
            message: 消息内容

        Returns:
            是否发布成功
        """
        try:
            if not await self.ensure_connection():
                return False

            json_str = json.dumps(message, default=str)
            await self._client.publish(channel, json_str)
            return True

        except Exception as e:
            logger.error(f"Redis PUBLISH error ({channel}): {e}")
            return False


# 全局Redis客户端实例
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """获取Redis客户端实例"""
    if not redis_client.is_connected:
        await redis_client.connect()
    return redis_client
