import uuid
from dataclasses import dataclass
from typing import final

import httpx
import structlog

from core.config import settings
from core.structlog import Logger
from schemas.base import ResponsePayload
from schemas.organization import OrganizationTelegramTokenSchema


logger: Logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class OrganizationAPIClient:
    base_url: str = f"{settings.server_site_url}/api/v1/organizations"

    async def get_token(self, organization_id: uuid.UUID) -> str:
        url = f"{self.base_url}/telegram/{organization_id}/"

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(url)
                response.raise_for_status()

                payload = ResponsePayload[OrganizationTelegramTokenSchema](
                    **response.json()
                )

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Organization API returned", status_code=exc.response.status_code
            )
            raise RuntimeError(
                f"Organization API returned {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            logger.warning("Organization API is unavailable")
            raise RuntimeError("Organization API is unavailable") from exc

        return payload.result.telegram_token
