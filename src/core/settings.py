from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    ADMINISTRATOR_IDS: list
    PROJECT_FLAG: str

    MJ_BOT_KEY: str
    MJ_BOT_ID: int

    DISCORD_GUILD_ID: int
    DISCORD_CHANNEL_ID: int
    DISCORD_USER_ID: int
    DISCORD_USER_EMAIL: str
    DISCORD_USER_PASSWORD: str
    DISCORD_SECRET_CODES: List[str]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")