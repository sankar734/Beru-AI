import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("nova.redis")

class InMemoryRedis:
    def __init__(self):
        self._store: Dict[str, str] = {}
        self._ttls: Dict[str, float] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = str(value)
        return True

    async def delete(self, key: str) -> int:
        if key in self._store:
            del self._store[key]
            return 1
        return 0

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = str(val)
        return val

    async def ping(self) -> bool:
        return True

class RedisManager:
    def __init__(self):
        self._client = None
        self._is_in_memory = True

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            from apps.api.config import settings
            client = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            await client.ping()
            self._client = client
            self._is_in_memory = False
            logger.info("Connected to Redis at %s", settings.REDIS_URL)
        except Exception as e:
            logger.info("Redis not available (%s), using In-Memory Cache fallback", e)
            self._client = InMemoryRedis()
            self._is_in_memory = True

    def get_client(self):
        if self._client is None:
            self._client = InMemoryRedis()
        return self._client

    @property
    def is_in_memory(self) -> bool:
        return self._is_in_memory

redis_manager = RedisManager()
