from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional, TypeVar

from redis.asyncio import Redis
from redis.asyncio.client import Redis as RedisClient

from core.config import settings, RedisConfig

T = TypeVar("T")


class RedisError(Exception):
    """Базовая ошибка Redis-клиента."""


@dataclass(frozen=True, slots=True, kw_only=True)
class RedisStorage:
    config: RedisConfig
    _client: Optional[RedisClient] = None

    def _mk_key(self, key: str) -> str:
        return f"{self.config.prefix}:{key}"

    async def connect(self) -> None:
        if self._client is not None:
            return
        client = Redis.from_url(
            self.config.url,
            decode_responses=self.config.decode_responses,
        )
        # Проверка соединения
        await client.ping()
        object.__setattr__(self, "_client", client)

    async def close(self) -> None:
        if self._client is None:
            return
        await self._client.close()
        object.__setattr__(self, "_client", None)

    @property
    def client(self) -> RedisClient:
        if self._client is None:
            raise RedisError("Redis client is not connected. Call connect() first.")
        return self._client

    # --------- базовые операции ---------
    async def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        ttl = self.config.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        return bool(await self.client.set(self._mk_key(key), payload, ex=ttl))

    async def get(self, key: str) -> Optional[Any]:
        raw = await self.client.get(self._mk_key(key))
        if raw is None:
            return None
        # raw может быть bytes или str — зависит от decode_responses
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    async def delete(self, key: str) -> int:
        return int(await self.client.delete(self._mk_key(key)))

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(self._mk_key(key)))

    async def expire(self, key: str, ttl_seconds: int) -> bool:
        return bool(await self.client.expire(self._mk_key(key), ttl_seconds))

    # --------- удобные хелперы ---------
    async def set_str(
        self, key: str, value: str, *, ttl_seconds: Optional[int] = None
    ) -> bool:
        ttl = self.config.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        return bool(await self.client.set(self._mk_key(key), value, ex=ttl))

    async def get_str(self, key: str) -> Optional[str]:
        raw = await self.client.get(self._mk_key(key))
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            return raw.decode("utf-8")
        return str(raw)

    # --------- контекст-менеджер ---------
    async def __aenter__(self) -> "RedisStorage":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


redis_storage = RedisStorage(config=settings.redis)
