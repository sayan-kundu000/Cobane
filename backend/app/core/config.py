from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List

class Settings(BaseSettings):
    """Cobane System Configuration.

    Environment variables are automatically mapped and typed with Pydantic settings parsing.
    """
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/cobane")
    JWT_SECRET_KEY: str = Field(default="devsecretkeychangeinproductionatleast32chars")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS origins config, comma-separated string converted to list
    ALLOWED_CORS_ORIGINS: List[str] = Field(default=["*"])

    # AI Service Settings
    AI_PROVIDER: str = "openai"
    AI_API_KEY: str = "mock-key"
    AI_BASE_URL: str = "https://api.openai.com/v1"

    # Environment
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("ALLOWED_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

settings = Settings()
