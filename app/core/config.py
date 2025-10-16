from __future__ import annotations

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses pydantic-settings to read a local .env file in development.
    """

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    APP_NAME: str = "Moverly Backend"
    ENV: str = Field(default="dev")

    # Security
    SECRET_KEY: str = Field(default="change-me-in-prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"

    # Database (async URL, e.g., postgresql+asyncpg://user:pass@localhost:5432/moverly)
    DATABASE_URL: AnyUrl | str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/moverly")


settings = Settings()



