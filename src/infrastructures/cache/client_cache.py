from dataclasses import dataclass
from typing import final
import uuid

import structlog

from core.structlog import Logger
from infrastructures.redis.base import redis_storage
from schemas.client import ClientInfoSchema

logger: Logger = structlog.get_logger(__name__)

TOKEN_TTL_SECONDS = 10 * 60


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ClientCache:
    chat_id: int
    organization_id: uuid.UUID
    ttl_seconds: int = 10 * 60

    async def _get_key(self) -> str:
        return f"{self.organization_id}:clients:{self.chat_id}"

    async def get(self) -> ClientInfoSchema | None:
        cached = await redis_storage.get(await self._get_key())
        if cached:
            return ClientInfoSchema.model_validate_json(cached)
        return None

    async def set(self, client: ClientInfoSchema) -> None:
        await redis_storage.set(
            key=await self._get_key(),
            value=client.model_dump_json(),
            ttl_seconds=TOKEN_TTL_SECONDS,
        )

    async def delete(self) -> None:
        await redis_storage.delete(await self._get_key())
