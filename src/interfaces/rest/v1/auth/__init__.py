from collections.abc import Sequence

from fastapi import APIRouter

from core.config import settings

from .base import router as base_router
from .oauth2 import router as oauth2_router

router = APIRouter()

router.include_router(
    router=base_router,
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

router.include_router(
    router=oauth2_router,
    prefix=settings.api.v1.oauth2,
    tags=["OAuth2"],
)

__all__: Sequence[str] = ["router"]
