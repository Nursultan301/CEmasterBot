import uuid

from pydantic import BaseModel


class TelegramSchema(BaseModel):
    uuid: uuid.UUID
    name: str
    token: str
    is_active: bool
