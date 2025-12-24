from pydantic import BaseModel


class OrganizationTelegramTokenSchema(BaseModel):
    telegram_token: str
