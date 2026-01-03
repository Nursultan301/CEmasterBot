from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
import structlog

from infrastructures.cache.client_cache import get_client_cached

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject

    from core.structlog import Logger
    from schemas.client import ClientInfoSchema

logger: Logger = structlog.get_logger(__name__)


def _extract_chat_id(
    event: TelegramObject,
    data: dict[str, Any],
) -> int | None:
    event_chat = data.get("event_chat")
    if event_chat:
        return event_chat.id

    message = getattr(event, "message", None)
    if message and getattr(message, "chat", None):
        return message.chat.id

    chat = getattr(event, "chat", None)
    if chat:
        return chat.id

    return None


class ClientInfoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, dict[str, Any]],
            Awaitable[Any],
        ],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        server_api = data.get("server_api")
        organization_id = data.get("organization_id")
        chat_id = _extract_chat_id(event, data)

        client: ClientInfoSchema | None = None

        if server_api and organization_id and chat_id:
            try:
                client = await get_client_cached(
                    server_api=server_api,
                    org_id=organization_id,
                    chat_id=chat_id,
                )
            except Exception:
                client = None

        data["client"] = client
        return await handler(event, data)
