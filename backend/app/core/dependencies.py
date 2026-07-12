from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from app.core.database import get_db as db_provider
from app.core.config import settings, Settings
from app.core.security import decode_token
from app.core.exceptions import AuthException, ForbiddenException
from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.logging import app_logger
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncSession:
    """Dependency session provider yielding asynchronous database sessions."""
    async for session in db_provider():
        yield session


def get_settings() -> Settings:
    """Dependency provider yielding global system settings configurations."""
    return settings


def get_app_logger() -> logging.Logger:
    """Dependency provider yielding base application logs handler."""
    return app_logger


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Dependency extraction helper retrieving active user profile models from decoded bearer tokens."""
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise AuthException("Token claims missing identifier.")
    except Exception as e:
        raise AuthException("Could not validate credentials.") from e

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if user is None:
        raise AuthException("User associated with token does not exist.")
    if not user.is_active:
        raise AuthException("User account is inactive.")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency restriction layer blocking non-administrative account access."""
    if not current_user.is_superuser:
        raise ForbiddenException("Administrative access required.")
    return current_user
