from aiogram import Dispatcher

from core.middlewares import I18nMiddleware
from routers import router as main_router


dp = Dispatcher()

dp.update.middleware(I18nMiddleware())

dp.include_routers(main_router)
