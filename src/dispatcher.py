from aiogram import Dispatcher
from routers import router as main_router


dp = Dispatcher()

dp.include_routers(main_router)
