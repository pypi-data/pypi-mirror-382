# src/wopr/sessions/sql_storage.py
import datetime
import json
from typing import Any, Dict, Optional

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None

from .storage import SESSION_EXPIRATION_TIME, AsyncBaseSessionStorage


class PostgresSessionStorage(AsyncBaseSessionStorage):
    def __init__(
        self,
        pool: asyncpg.Pool,
        ttl_seconds: int = SESSION_EXPIRATION_TIME,
        table: str = "sessions",
    ):
        self.pool = pool
        self.ttl = ttl_seconds
        self.table = table

    async def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT data, expires_at FROM {self.table} WHERE session_id=$1",
                session_id,
            )
            if not row:
                return None
            now = datetime.datetime.now(datetime.timezone.utc)
            if row["expires_at"] < now:
                await conn.execute(
                    f"DELETE FROM {self.table} WHERE session_id=$1", session_id
                )
                return None
            data = row["data"]
            if isinstance(data, dict):
                return data
            return json.loads(data)

    async def save(self, session_id: str, data: Dict[str, Any]) -> None:
        expires = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(seconds=self.ttl)
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self.table} (session_id, data, expires_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (session_id) DO UPDATE
                  SET data = EXCLUDED.data, expires_at = EXCLUDED.expires_at
            """,
                session_id,
                json.dumps(data),
                expires,
            )

    async def delete(self, session_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {self.table} WHERE session_id=$1", session_id
            )

    async def cleanup(self) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(f"DELETE FROM {self.table} WHERE expires_at < NOW()")
