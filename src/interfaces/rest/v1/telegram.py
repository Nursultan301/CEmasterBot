from fastapi import APIRouter, status

from schemas.base import SuccessResponse

router = APIRouter()


@router.post(
    "/set_webhook/{token}/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_telegram_service(token: str) -> SuccessResponse:
    ...
    return SuccessResponse(
        detail="Telegram service has been successfully set up!",
    )
