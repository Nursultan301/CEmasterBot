from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR / '.env'}",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="BOT__",
    )

    bot_token: str
    admin_ids: frozenset[int] = frozenset({42, 3595399})


# noinspection PyArgumentList
settings = Settings()
