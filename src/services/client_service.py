import uuid

import structlog

from core.structlog import Logger
from infrastructures.cache.client_cache import ClientCache
from infrastructures.http.exceptions import ClientNotFoundException
from infrastructures.http.server_api import ServerAPI
from schemas.client import ClientInfoSchema

logger: Logger = structlog.get_logger(__name__)


class ClientService:
    def __init__(
        self,
        chat_id: int,
        organization_id: uuid.UUID,
        server_api: ServerAPI,
        is_cached: bool = True,
    ):
        self.chat_id = chat_id
        self.organization_id = organization_id
        self.server_api = server_api
        self.is_cached = is_cached
        self.cache = ClientCache(
            chat_id=chat_id,
            organization_id=organization_id,
        )

    async def get_me(self) -> ClientInfoSchema | None:
        cached = await self.cache.get()
        if cached:
            return cached

        try:
            client = await self.server_api.client.get_me(
                chat_id=self.chat_id,
                organization_id=self.organization_id,
            )
            logger.info("Client in cache not found", client=client)
        except ClientNotFoundException:
            return None

        await self.cache.set(client)
        return client

    async def set_language(self, lang_code: str) -> ClientInfoSchema | None:
        try:
            client = await self.server_api.client.set_lang(
                chat_id=self.chat_id,
                organization_id=self.organization_id,
                lang_code=lang_code,
            )
            await self.cache.delete()
            await self.cache.set(client)
            return client

        except Exception:
            return None
