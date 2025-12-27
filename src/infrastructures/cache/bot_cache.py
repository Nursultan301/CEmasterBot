import uuid

from aiogram import Bot
from fastapi import Request


def get_bot_cached(request: Request, org_id: uuid.UUID, token: str) -> Bot:
    bot_cache: dict[uuid.UUID, Bot] = request.app.state.bot_cache

    bot = bot_cache.get(org_id)
    if bot and bot.token == token:
        return bot

    # если бот был, но токен поменялся — закрываем старую сессию и заменяем
    if bot:
        bot_cache.pop(org_id, None)

    new_bot = Bot(token=token)
    bot_cache[org_id] = new_bot
    return new_bot
