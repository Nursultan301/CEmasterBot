from fastapi import APIRouter

from .api import router as router_api
from .webhooks import router as router_webhooks

router = APIRouter()

router.include_router(router=router_api)

router.include_router(router=router_webhooks)
