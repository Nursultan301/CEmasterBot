from fastapi import APIRouter

from interfaces.api_prefix import api_prefix
from interfaces.rest.v1 import router as router_v1

router = APIRouter(prefix=api_prefix.prefix)

router.include_router(router_v1)
