import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions.handlers import register_exception_handlers
from core.middlewares import LogCorrelationIdMiddleware
from core.structlog import configure as logging_configure
from create_app import FastAPIApp
from interfaces import router

logging_configure()

fastapi_app = FastAPIApp()

main_app = fastapi_app.create(
    title="CEmasterBot API",
    description="CEmasterBot",
)


main_app.add_middleware(LogCorrelationIdMiddleware)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(main_app)

main_app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
