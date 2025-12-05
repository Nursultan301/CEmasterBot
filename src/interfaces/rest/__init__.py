from fastapi import APIRouter

from core.config import settings
from interfaces.rest.v1 import router as router_v1

router = APIRouter(prefix=settings.api.prefix)

router.include_router(router_v1)
