from aiogram import Dispatcher
from src.routers import router as main_router


dispatcher = Dispatcher()

dispatcher.include_routers(main_router)
