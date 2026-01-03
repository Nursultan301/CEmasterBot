from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
import structlog

from core.i18n import DEFAULT_LANG, get_translator, normalize_lang

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject

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

        client: ClientInfoSchema | None = data.get("client")

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
