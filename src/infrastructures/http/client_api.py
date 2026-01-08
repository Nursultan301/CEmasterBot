from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import httpx
import structlog

from schemas.base import ErrorResponse, ResponseListPayload, ResponsePayload
from schemas.client import ClientCreateSchema, ClientInfoSchema, ClientUpdateSchema
from schemas.shipment import ShipmentListRead

if TYPE_CHECKING:
    import uuid

    from core.structlog import Logger
    from enums.commons import ClientCodeTypeEnum

logger: Logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ClientAPI:
    http: httpx.AsyncClient

    def __init__(self, http: httpx.AsyncClient) -> None:
        self.http = http

    async def get_me(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
    ) -> ClientInfoSchema | None:
        try:
            response = await self.http.get(
                "/clients/me/",
                headers={
                    "x-data-chat-id": str(chat_id),
                    "x-data-organization-id": str(organization_id),
                },
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            errors = ErrorResponse(**exc.response.json())
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                exception_type=errors.exception_type,
                errors=errors.errors,
            )

        except httpx.RequestError as exc:
            logger.warning("Client API is unavailable", error=str(exc))

        return None

    async def create(
        self,
        client_data: ClientCreateSchema,
    ) -> ClientInfoSchema | None:
        try:
            response = await self.http.post(
                "/clients/registration/",
                content=client_data.model_dump_json(),
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result

        except httpx.HTTPStatusError as exc:
            errors = ErrorResponse(**exc.response.json())
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                exception_type=errors.exception_type,
                errors=errors.errors,
            )

        except httpx.RequestError:
            logger.exception("Client API is unavailable")

        return None

    async def generate_code(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
        type_client_code: ClientCodeTypeEnum,
    ) -> ClientInfoSchema | None:
        try:
            response = await self.http.post(
                "/clients/generate/client-code/",
                headers={
                    "x-data-chat-id": str(chat_id),
                    "x-data-organization-id": str(organization_id),
                },
                json={
                    "type_client_code": type_client_code,
                },
            )
            response.raise_for_status()
            payload = ResponsePayload[ClientInfoSchema](**response.json())
            return payload.result
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Client API request failed",
                status_code=exc.response.status_code,
                errors=exc.response.json(),
            )
        except httpx.RequestError:
            logger.exception("Client API is unavailable")

        return None

    async def get_me_shipments(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
    ) -> list[ShipmentListRead] | None:
        try:
            response = await self.http.get(
                "/clients/me/shipments/",
                headers={
                    "x-data-chat-id": str(chat_id),
                    "x-data-organization-id": str(organization_id),
                },
            )
            response.raise_for_status()
            payload = ResponseListPayload[ShipmentListRead](**response.json())
            return payload.results
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Client Shipments API request failed",
                status_code=exc.response.status_code,
                errors=exc.response.json(),
            )
        except httpx.RequestError:
            logger.exception("Client Shipments API is unavailable")
        return None

    async def update_client(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
        update_data: ClientUpdateSchema,
    ) -> ClientInfoSchema | None:
        response = await self.http.patch(
            "/clients/me/",
            headers={
                "x-data-chat-id": str(chat_id),
                "x-data-organization-id": str(organization_id),
            },
            json=update_data.model_dump(exclude_unset=True),
        )
        response.raise_for_status()
        payload = ResponsePayload[ClientInfoSchema](**response.json())
        return payload.result

    async def set_lang(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
        lang_code: str,
    ) -> ClientInfoSchema | None:
        return await self.update_client(
            chat_id=chat_id,
            organization_id=organization_id,
            update_data=ClientUpdateSchema(language_code=lang_code),
        )
