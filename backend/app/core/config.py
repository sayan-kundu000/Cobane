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
    FRONTEND_PORT: int = 3000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def parse_database_url(cls, v) -> str:
        if not v or (isinstance(v, str) and not v.strip()):
            return "sqlite+aiosqlite:///test.db"
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("sqlite://"):
                v = v.replace("sqlite://", "sqlite+aiosqlite://", 1)
            if "sslmode=" in v:
                v = v.replace("sslmode=", "ssl=")

            # Check reachability of the database, fallback to SQLite if unreachable
            if not v.startswith("sqlite"):
                import os

                if os.getenv("SKIP_DB_REACHABILITY_CHECK") == "1":
                    return v
                from app.core.logging import app_logger

                url_parts = v.split("@")
                host_info = url_parts[-1] if len(url_parts) > 1 else v
                app_logger.info(f"Verifying reachability for configured database at {host_info}...")

                if not cls._is_db_reachable(v):
                    app_logger.warning(
                        f"Database at {host_info} is unreachable or non-operational. Falling back to local SQLite database (test.db)."
                    )
                    return "sqlite+aiosqlite:///test.db"

                app_logger.info(f"Database at {host_info} is reachable and operational.")
        return v

    @staticmethod
    def _is_db_reachable(url: str) -> bool:
        """Performs a fast TCP socket check followed by an isolated connection test."""
        if not url or "sqlite" in url:
            return True

        # 1. Quick TCP socket check to prevent blocking long timeouts
        try:
            temp_url = url
            for scheme in ["postgresql+asyncpg://", "postgres://", "postgresql://"]:
                if temp_url.startswith(scheme):
                    temp_url = temp_url.replace(scheme, "http://", 1)
                    break
            from urllib.parse import urlparse

            parsed = urlparse(temp_url)
            host = parsed.hostname
            port = parsed.port or 5432
            if not host:
                return False
            import socket

            with socket.create_connection((host, port), timeout=2.0):
                pass
        except Exception:
            return False

        # 2. Detailed connection test in an isolated thread to support all event loops
        async def _check_conn():
            try:
                from sqlalchemy.ext.asyncio import create_async_engine
                from sqlalchemy import text

                engine = create_async_engine(url)
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                await engine.dispose()
                return True
            except Exception:
                return False

        import asyncio
        import threading

        result = [False]

        def target():
            try:
                result[0] = asyncio.run(_check_conn())
            except Exception:
                pass

        t = threading.Thread(target=target)
        t.start()
        t.join(timeout=5.0)
        return result[0]

    @field_validator("ALLOWED_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


settings = Settings()
