from aiogram import Dispatcher

from core.middlewares import I18nMiddleware
from core.middlewares.client import ClientInfoMiddleware
from infrastructures.aiogram.routers import router as main_router

dispatcher = Dispatcher()

dispatcher.update.middleware(ClientInfoMiddleware())
dispatcher.update.middleware(I18nMiddleware())

dispatcher.include_routers(main_router)
