import uuid

from pydantic import BaseModel


class TelegramSchema(BaseModel):
    uuid: uuid.UUID
    token: str
