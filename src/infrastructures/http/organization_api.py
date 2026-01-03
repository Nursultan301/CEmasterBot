import uuid

import httpx
import structlog

from core.structlog import Logger
from schemas.base import ResponsePayload
from schemas.organization import OrganizationTelegramTokenSchema

logger: Logger = structlog.get_logger(__name__)


class OrganizationAPI:

    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http

    async def get_token(self, organization_id: uuid.UUID) -> str:
        try:
            response = await self.http.get(
                f"/organizations/telegram/{organization_id}/"
            )
            response.raise_for_status()

            payload = ResponsePayload[OrganizationTelegramTokenSchema](
                **response.json()
            )
            return payload.result.telegram_token

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Organization API request failed",
                status_code=exc.response.status_code,
                response_text=exc.response.text[:500],
            )
            raise RuntimeError(
                f"Organization API error: HTTP {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            logger.warning("Organization API is unavailable", error=str(exc))
            raise RuntimeError("Organization API is unavailable") from exc
