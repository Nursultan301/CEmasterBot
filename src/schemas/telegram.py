import uuid

from pydantic import BaseModel


class TelegramSchema(BaseModel):
    organization_id: uuid.UUID
    token: str
