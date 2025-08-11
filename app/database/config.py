# app/database/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Database
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None

    # App
    APP_NAME: str = "ML_API"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # Security
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def validate(self) -> None:
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASS, self.DB_NAME]):
            raise ValueError("Missing required database configuration")

@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    s.validate()
    return s
