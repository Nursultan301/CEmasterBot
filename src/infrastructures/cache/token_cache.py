import uuid

from infrastructures.http.server_api import ServerAPI
from infrastructures.redis.base import redis_storage

TOKEN_TTL_SECONDS = 30 * 60  # 30 минут


async def get_token_cached(
    server_api: ServerAPI,
    org_id: uuid.UUID,
) -> str:
    key = f"{org_id}:token"

    cached = await redis_storage.get(key)
    if cached:
        return str(cached)

    token = await server_api.organization.get_token(org_id)

    await redis_storage.set(
        key=key,
        value=token,
        ttl_seconds=TOKEN_TTL_SECONDS,
    )
    return token
