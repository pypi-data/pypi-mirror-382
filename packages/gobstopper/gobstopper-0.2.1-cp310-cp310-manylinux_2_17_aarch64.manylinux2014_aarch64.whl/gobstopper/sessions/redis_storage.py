# src/wopr/sessions/redis_storage.py
import json
from typing import Optional, Dict, Any

try:
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from .storage import AsyncBaseSessionStorage, SESSION_EXPIRATION_TIME

class AsyncRedisSessionStorage(AsyncBaseSessionStorage):
    """
    An asynchronous session storage backend using Redis.
    This backend is recommended for production deployments.
    """

    def __init__(self, client: Redis, key_prefix: str = "session:", ttl: int = SESSION_EXPIRATION_TIME):
        self.client = client
        self.key_prefix = key_prefix
        self.ttl = ttl

    def _key(self, session_id: str) -> str:
        return f"{self.key_prefix}{session_id}"

    async def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        raw = await self.client.get(self._key(session_id))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            # Handle cases where data in Redis is corrupted or not valid JSON
            return None

    async def save(self, session_id: str, data: Dict[str, Any]) -> None:
        await self.client.set(self._key(session_id), json.dumps(data), ex=self.ttl)

    async def delete(self, session_id: str) -> None:
        await self.client.delete(self._key(session_id))

    async def cleanup(self) -> None:
        # Redis handles TTL automatically, so no explicit cleanup is needed.
        pass
