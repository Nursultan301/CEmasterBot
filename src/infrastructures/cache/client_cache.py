import uuid

import structlog

from core.structlog import Logger
from infrastructures.http.exceptions import ClientNotFoundException
from infrastructures.http.server_api import ServerAPI
from infrastructures.redis.base import redis_storage
from schemas.client import ClientInfoSchema


logger: Logger = structlog.get_logger(__name__)

TOKEN_TTL_SECONDS = 10 * 60


async def get_client_cached(
    server_api: ServerAPI,
    org_id: uuid.UUID,
    chat_id: int,
) -> ClientInfoSchema | None:
    key = f"{org_id}:clients:{chat_id}"

    cached = await redis_storage.get(key)
    if cached:
        cached_client = ClientInfoSchema.model_validate_json(cached)
        return cached_client

    try:
        client = await server_api.client.get_me(chat_id=chat_id)
        logger.info("Client in cache not found", client=client)
    except ClientNotFoundException:
        return None

    await redis_storage.set(
        key=key,
        value=client.model_dump_json(),
        ttl_seconds=TOKEN_TTL_SECONDS,
    )
    return client
