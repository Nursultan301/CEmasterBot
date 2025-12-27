import uuid
from datetime import datetime

from pydantic import BaseModel

from enums.commons import ClientCodeTypeEnum


class ClientInfoSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str
    chat_id: str
    code: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ClientCreateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str
    chat_id: str
    organization_id: uuid.UUID


class ClientCodeGenerateSchema(BaseModel):
    type_client_code: ClientCodeTypeEnum
