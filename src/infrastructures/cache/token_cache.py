import uuid

from fastapi import Request

TOKEN_TTL_SECONDS = 30 * 60  # 30 минут


def token_key(org_id: uuid.UUID) -> str:
    return f"tg:token:{org_id}"


async def get_token_cached(request: Request, org_id: uuid.UUID) -> str:
    redis = request.app.state.redis
    key = token_key(org_id)

    cached = await redis.get(key)
    if cached:
        return cached

    server = request.app.state.server
    token = await server.organization.get_token(org_id)

    # кладём в redis с TTL
    await redis.set(key, token, ex=TOKEN_TTL_SECONDS)
    return token


async def invalidate_token_cache(request: Request, org_id: uuid.UUID) -> None:
    redis = request.app.state.redis
    await redis.delete(token_key(org_id))
