from fastapi import APIRouter, Depends

from core.config import settings
from interfaces.rest.dependencies.base import http_bearer
from interfaces.rest.v1.agent import router as agent_router

from .auth import router as auth_router
from .chats import router as chat_router
from .users import router as user_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[
        Depends(http_bearer),
    ],
)

router.include_router(router=auth_router)

router.include_router(
    router=user_router,
    prefix=settings.api.v1.users,
    tags=["Users"],
)

router.include_router(
    router=agent_router,
    prefix=settings.api.v1.agents,
    tags=["Agents"],
)

router.include_router(
    router=chat_router,
    prefix=settings.api.v1.chats,
    tags=["Chats"],
)


__all__ = ["router"]
