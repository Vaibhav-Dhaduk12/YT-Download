import json
from typing import Any, Optional

import structlog

from app.infrastructure.cache.base import BaseCache

logger = structlog.get_logger()


class RedisCache(BaseCache):
    """Redis-backed cache for production."""

    def __init__(self, redis_url: str) -> None:
        self._url = redis_url
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(self._url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            value = await client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            client = await self._get_client()
            serialized = json.dumps(value)
            if ttl:
                await client.setex(key, ttl, serialized)
            else:
                await client.set(key, serialized)
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))

    async def exists(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.exists(key))
        except Exception as e:
            logger.warning("Redis exists failed", key=key, error=str(e))
            return False
