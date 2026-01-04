from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
import structlog

from services.client_service import ClientService

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
            client_service = ClientService(
                chat_id=chat_id,
                organization_id=organization_id,
                server_api=server_api,
            )
            try:
                client = await client_service.get_me()
            except Exception:
                client = None
        else:
            client_service = None

        data["client"] = client
        data["client_service"] = client_service
        return await handler(event, data)
