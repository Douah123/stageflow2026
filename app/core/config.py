from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    APP_NAME: str = "Mon API FastAPI"
    API_V1_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Durée de vie du token d'accès
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Durée de vie du token de rafraîchissement
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8000").split(",")  # Pour CORS, à restreindre en production

@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
