from __future__ import annotations

from dataclasses import dataclass, replace
import json
from typing import TYPE_CHECKING, Any, TypeVar

from redis.asyncio import Redis

from core.config import RedisConfig, settings

if TYPE_CHECKING:
    from types import TracebackType

    from redis.asyncio.client import Redis as RedisClient

T = TypeVar("T")


class RedisError(Exception):
    """Базовая ошибка Redis-клиента."""


@dataclass(frozen=True, slots=True, kw_only=True)
class RedisStorage:
    config: RedisConfig
    _client: RedisClient | None = None

    def _mk_key(self, key: str) -> str:
        return f"{self.config.prefix}:{key}"

    async def connect(self) -> RedisStorage:
        if self._client is not None:
            return self
        if self.config.url is None:
            raise RedisError("Redis URL is not configured.")
        client = Redis.from_url(
            url=self.config.url,
            decode_responses=self.config.decode_responses,
        )
        await client.ping()
        return replace(self, _client=client)

    async def close(self) -> RedisStorage:
        if self._client is None:
            return self

        await self._client.close()
        return replace(self, _client=None)

    @property
    def client(self) -> RedisClient:
        if self._client is None:
            raise RedisError("Redis client is not connected. Call connect() first.")
        return self._client

    # --------- контекст-менеджер ---------
    async def __aenter__(self) -> RedisStorage:
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.close()

    # --------- базовые операции ---------
    async def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        ttl = self.config.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        return bool(await self.client.set(self._mk_key(key), payload, ex=ttl))

    async def get(self, key: str) -> Any | None:
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
        self,
        key: str,
        value: str,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        ttl = self.config.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        return bool(await self.client.set(self._mk_key(key), value, ex=ttl))

    async def get_str(self, key: str) -> str | None:
        raw = await self.client.get(self._mk_key(key))
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            return raw.decode("utf-8")
        return str(raw)


redis_storage = RedisStorage(config=settings.redis)
