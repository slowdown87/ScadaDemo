"""
Cache Manager
多级缓存管理
支持内存缓存 + Redis缓存 + 预热机制
"""

import asyncio
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime, timedelta
from functools import wraps
import logging
import hashlib
import json

from data.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class CacheManager:
    """多级缓存管理器"""

    def __init__(self):
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl: Dict[str, datetime] = {}
        self._default_ttl: int = 300  # 5 minutes
        self._max_memory_size: int = 1000  # Maximum entries in memory
        self._redis_enabled: bool = True
        self._hit_count: int = 0
        self._miss_count: int = 0

    async def initialize(self):
        """初始化缓存管理器"""
        try:
            redis_client = await get_redis_client()
            self._redis_enabled = await redis_client.ensure_connection()
            logger.info(f"Cache manager initialized (Redis: {'enabled' if self._redis_enabled else 'disabled'})")
        except Exception as e:
            logger.warning(f"Cache manager initialization failed: {e}, running without Redis")
            self._redis_enabled = False

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

        key_string = ":".join(key_parts)

        if len(key_string) > 200:
            hash_key = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{hash_key}"

        return key_string

    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key not in self._cache_ttl:
            return True

        return datetime.now() > self._cache_ttl[key]

    def _cleanup_expired(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self._cache_ttl.items()
            if now > expiry
        ]

        for key in expired_keys:
            self._memory_cache.pop(key, None)
            self._cache_ttl.pop(key, None)

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _evict_lru(self):
        """LRU驱逐：当内存缓存满时，移除最老的条目"""
        if len(self._memory_cache) >= self._max_memory_size:
            oldest_key = min(
                self._cache_ttl.keys(),
                key=lambda k: self._cache_ttl[k]
            )
            self._memory_cache.pop(oldest_key, None)
            self._cache_ttl.pop(oldest_key, None)
            logger.debug(f"Evicted LRU cache entry: {oldest_key}")

    async def get(
        self,
        prefix: str,
        *args,
        fetch_func: Optional[Callable] = None,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        获取缓存值，支持回退到fetch_func

        Args:
            prefix: 缓存键前缀
            *args: 缓存键参数
            fetch_func: 数据获取函数（缓存未命中时调用）
            ttl: 缓存过期时间（秒）
            **kwargs: 缓存键关键字参数

        Returns:
            缓存值或fetch_func的返回值
        """
        cache_key = self._generate_key(prefix, *args, **kwargs)

        # 1. 尝试从内存缓存获取
        if cache_key in self._memory_cache and not self._is_expired(cache_key):
            self._hit_count += 1
            logger.debug(f"Memory cache hit: {cache_key}")
            return self._memory_cache[cache_key]

        # 2. 尝试从Redis缓存获取
        if self._redis_enabled:
            try:
                redis_client = await get_redis_client()
                redis_data = await redis_client.get_json(cache_key)

                if redis_data:
                    self._hit_count += 1
                    logger.debug(f"Redis cache hit: {cache_key}")

                    # 回填内存缓存
                    self._evict_lru()
                    self._memory_cache[cache_key] = redis_data
                    self._cache_ttl[cache_key] = datetime.now() + timedelta(
                        seconds=ttl or self._default_ttl
                    )

                    return redis_data
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # 3. 调用fetch_func获取新数据
        if fetch_func:
            try:
                self._miss_count += 1
                logger.debug(f"Cache miss, fetching: {cache_key}")

                data = await fetch_func(*args, **kwargs)

                if data is not None:
                    await self.set(cache_key, data, ttl)
                    return data

            except Exception as e:
                logger.error(f"Fetch function failed: {e}")

        self._miss_count += 1
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        ttl = ttl or self._default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)

        # 1. 设置内存缓存
        self._evict_lru()
        self._memory_cache[key] = value
        self._cache_ttl[key] = expiry

        # 2. 设置Redis缓存
        if self._redis_enabled:
            try:
                redis_client = await get_redis_client()
                await redis_client.set_json(key, value, ttl)
                logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        return True

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        # 1. 删除内存缓存
        self._memory_cache.pop(key, None)
        self._cache_ttl.pop(key, None)

        # 2. 删除Redis缓存
        if self._redis_enabled:
            try:
                redis_client = await get_redis_client()
                await redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

        logger.debug(f"Cache deleted: {key}")
        return True

    async def clear(self, pattern: str = "*"):
        """清空缓存"""
        # 清空内存缓存
        if pattern == "*":
            self._memory_cache.clear()
            self._cache_ttl.clear()
        else:
            keys_to_delete = [
                k for k in self._memory_cache.keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                self._memory_cache.pop(key, None)
                self._cache_ttl.pop(key, None)

        # 清空Redis缓存
        if self._redis_enabled:
            try:
                redis_client = await get_redis_client()
                # Note: Redis KEYS command should be avoided in production
                # This is simplified for demonstration
                logger.info(f"Cache cleared: {pattern}")
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (
            self._hit_count / total_requests * 100
            if total_requests > 0 else 0
        )

        return {
            "memory_cache_size": len(self._memory_cache),
            "max_memory_size": self._max_memory_size,
            "redis_enabled": self._redis_enabled,
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2)
        }

    async def warm_up(self, warm_up_funcs: Dict[str, Callable]):
        """
        缓存预热

        Args:
            warm_up_funcs: 预热函数字典 {cache_prefix: fetch_function}
        """
        logger.info(f"Starting cache warm-up ({len(warm_up_funcs)} entries)")

        for prefix, func in warm_up_funcs.items():
            try:
                data = await func()
                if data:
                    cache_key = self._generate_key(prefix)
                    await self.set(cache_key, data, ttl=3600)  # 1 hour TTL for warm-up data
                    logger.info(f"Warmed cache: {prefix}")
            except Exception as e:
                logger.error(f"Cache warm-up failed for {prefix}: {e}")

        logger.info("Cache warm-up completed")


def cached(
    prefix: str,
    ttl: int = 300,
    ttl_name: str = None
):
    """
    缓存装饰器

    Usage:
        @cached("user_data", ttl=600)
        async def get_user(user_id: int):
            return await db.get_user(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_mgr = cache_manager
            
            cache_key = cache_mgr._generate_key(
                prefix,
                *args,
                **{k: v for k, v in kwargs.items() if k != ttl_name}
            )

            cached_value = await cache_mgr.get(cache_key)

            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)

            if result is not None:
                effective_ttl = kwargs.get(ttl_name, ttl) if ttl_name else ttl
                await cache_mgr.set(cache_key, result, effective_ttl)

            return result

        return wrapper
    return decorator


_cache_manager_instance: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
        await _cache_manager_instance.initialize()
    return _cache_manager_instance


class CacheWarmUpManager:
    """缓存预热管理器"""

    def __init__(self):
        self._warm_up_history: List[Dict[str, Any]] = []
        self._warm_up_tasks: Dict[str, Dict[str, Any]] = {}
        self._last_warm_up: Optional[datetime] = None
        self._warm_up_interval: int = 3600

    async def register_warm_up_task(
        self,
        name: str,
        fetch_func: Callable,
        ttl: int = 3600
    ):
        """注册预热任务"""
        self._warm_up_tasks[name] = {
            "fetch_func": fetch_func,
            "ttl": ttl
        }

    async def warm_up_all(self, cache_manager: CacheManager):
        """执行所有预热任务"""
        logger.info(f"Starting warm-up for {len(self._warm_up_tasks)} tasks")
        start_time = datetime.now()

        for name, task in self._warm_up_tasks.items():
            try:
                data = await task["fetch_func"]()
                if data is not None:
                    cache_key = cache_manager._generate_key(f"warmup:{name}")
                    await cache_manager.set(cache_key, data, task["ttl"])
                    logger.info(f"Warmed up: {name}")
            except Exception as e:
                logger.error(f"Warm-up failed for {name}: {e}")

        elapsed = (datetime.now() - start_time).total_seconds()
        self._last_warm_up = datetime.now()
        self._warm_up_history.append({
            "timestamp": self._last_warm_up,
            "duration": elapsed,
            "task_count": len(self._warm_up_tasks)
        })
        logger.info(f"Warm-up completed in {elapsed:.2f}s")

    async def should_warm_up(self) -> bool:
        """检查是否需要预热"""
        if self._last_warm_up is None:
            return True
        elapsed = (datetime.now() - self._last_warm_up).total_seconds()
        return elapsed > self._warm_up_interval

    def get_warm_up_history(self) -> List[Dict[str, Any]]:
        """获取预热历史"""
        return self._warm_up_history


class CacheEvictionPolicy:
    """缓存驱逐策略"""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"


class CacheEvictionManager:
    """缓存驱逐管理器"""

    def __init__(self, policy: str = CacheEvictionPolicy.LRU):
        self._policy = policy
        self._access_count: Dict[str, int] = {}
        self._access_times: Dict[str, datetime] = {}

    async def evict(
        self,
        cache_manager: CacheManager,
        count: int = 1
    ) -> List[str]:
        """根据策略驱逐缓存"""
        evicted_keys = []

        if self._policy == CacheEvictionPolicy.LRU:
            evicted_keys = self._evict_lru(cache_manager, count)
        elif self._policy == CacheEvictionPolicy.LFU:
            evicted_keys = self._evict_lfu(cache_manager, count)
        elif self._policy == CacheEvictionPolicy.FIFO:
            evicted_keys = self._evict_fifo(cache_manager, count)
        elif self._policy == CacheEvictionPolicy.TTL:
            evicted_keys = self._evict_by_ttl(cache_manager, count)

        return evicted_keys

    def _evict_lru(
        self,
        cache_manager: CacheManager,
        count: int
    ) -> List[str]:
        """LRU驱逐"""
        keys = list(cache_manager._cache_ttl.keys())
        keys.sort(key=lambda k: self._access_times.get(k, datetime.min))
        
        evicted = []
        for key in keys[:count]:
            cache_manager._memory_cache.pop(key, None)
            cache_manager._cache_ttl.pop(key, None)
            self._access_count.pop(key, None)
            self._access_times.pop(key, None)
            evicted.append(key)
        
        return evicted

    def _evict_lfu(
        self,
        cache_manager: CacheManager,
        count: int
    ) -> List[str]:
        """LFU驱逐"""
        keys = list(self._access_count.keys())
        keys.sort(key=lambda k: self._access_count.get(k, 0))
        
        evicted = []
        for key in keys[:count]:
            cache_manager._memory_cache.pop(key, None)
            cache_manager._cache_ttl.pop(key, None)
            self._access_count.pop(key, None)
            self._access_times.pop(key, None)
            evicted.append(key)
        
        return evicted

    def _evict_fifo(
        self,
        cache_manager: CacheManager,
        count: int
    ) -> List[str]:
        """FIFO驱逐"""
        keys = list(cache_manager._cache_ttl.keys())
        keys.sort(key=lambda k: cache_manager._cache_ttl[k])
        
        evicted = []
        for key in keys[:count]:
            cache_manager._memory_cache.pop(key, None)
            cache_manager._cache_ttl.pop(key, None)
            self._access_count.pop(key, None)
            self._access_times.pop(key, None)
            evicted.append(key)
        
        return evicted

    def _evict_by_ttl(
        self,
        cache_manager: CacheManager,
        count: int
    ) -> List[str]:
        """按TTL驱逐（即将过期的优先）"""
        now = datetime.now()
        keys = list(cache_manager._cache_ttl.keys())
        keys.sort(key=lambda k: (cache_manager._cache_ttl[k] - now).total_seconds())
        
        evicted = []
        for key in keys[:count]:
            cache_manager._memory_cache.pop(key, None)
            cache_manager._cache_ttl.pop(key, None)
            self._access_count.pop(key, None)
            self._access_times.pop(key, None)
            evicted.append(key)
        
        return evicted

    def record_access(self, key: str):
        """记录缓存访问"""
        self._access_count[key] = self._access_count.get(key, 0) + 1
        self._access_times[key] = datetime.now()


class CacheMetrics:
    """缓存性能指标"""

    def __init__(self):
        self._metrics: Dict[str, Any] = {
            "total_hits": 0,
            "total_misses": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "evictions": 0,
            "errors": 0,
            "total_latency_ms": 0,
            "operations": []
        }
        self._operation_limit = 1000

    def record_hit(self, source: str = "memory"):
        """记录缓存命中"""
        self._metrics["total_hits"] += 1
        if source == "memory":
            self._metrics["memory_hits"] += 1
        elif source == "redis":
            self._metrics["redis_hits"] += 1

    def record_miss(self):
        """记录缓存未命中"""
        self._metrics["total_misses"] += 1

    def record_eviction(self):
        """记录缓存驱逐"""
        self._metrics["evictions"] += 1

    def record_error(self):
        """记录错误"""
        self._metrics["errors"] += 1

    def record_latency(self, latency_ms: float):
        """记录延迟"""
        self._metrics["total_latency_ms"] += latency_ms
        self._metrics["operations"].append({
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency_ms
        })
        if len(self._metrics["operations"]) > self._operation_limit:
            self._metrics["operations"] = self._metrics["operations"][-self._operation_limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        total = self._metrics["total_hits"] + self._metrics["total_misses"]
        hit_rate = (
            self._metrics["total_hits"] / total * 100
            if total > 0 else 0
        )
        avg_latency = (
            self._metrics["total_latency_ms"] / total
            if total > 0 else 0
        )

        return {
            "hit_rate_percent": round(hit_rate, 2),
            "memory_hit_rate_percent": round(
                self._metrics["memory_hits"] / total * 100
                if total > 0 else 0,
                2
            ),
            "redis_hit_rate_percent": round(
                self._metrics["redis_hits"] / total * 100
                if total > 0 else 0,
                2
            ),
            "eviction_count": self._metrics["evictions"],
            "error_count": self._metrics["errors"],
            "average_latency_ms": round(avg_latency, 2),
            "total_requests": total
        }

    def reset(self):
        """重置指标"""
        self._metrics = {
            "total_hits": 0,
            "total_misses": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "evictions": 0,
            "errors": 0,
            "total_latency_ms": 0,
            "operations": []
        }


cache_metrics = CacheMetrics()
warm_up_manager = CacheWarmUpManager()


# 全局缓存管理器实例
cache_manager = CacheManager()
