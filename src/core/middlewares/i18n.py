from __future__ import annotations

from typing import Any, Awaitable, Callable

import structlog
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.i18n import get_translator, normalize_lang, DEFAULT_LANG
from core.structlog import Logger
from schemas.client import ClientInfoSchema

logger: Logger = structlog.get_logger(__name__)


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Пытаемся достать пользователя/чат
        tg_user = data.get("event_from_user")
        lang_from_tg = getattr(tg_user, "language_code", None)

        # Ожидаем: Client от Диспедчера
        client: ClientInfoSchema = data.get("client", None)

        lang: str = DEFAULT_LANG
        if client and tg_user:
            try:
                lang = normalize_lang(getattr(client, "language_code", None))
            except Exception:
                # если пользователь ещё не зарегистрирован или API недоступен
                lang = normalize_lang(lang_from_tg)

        else:
            lang = normalize_lang(lang_from_tg)

        data["lang"] = lang
        data["_"] = get_translator(lang)

        return await handler(event, data)
