from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties

from aiogram.enums import ParseMode

from config import settings
from routers import router as main_router


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(main_router)
    return dp


def create_bot() -> Bot:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )
    return bot
