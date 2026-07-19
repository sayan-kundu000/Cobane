from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.base_repository import BaseRepository
from app.models.user import User, UserProfile, UserPreference
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserProfileUpdate, PasswordChangeRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthException, ValidationException, NotFoundException
from app.core.logging import security_logger


class AuthService:
    """Service orchestrating business operations for user registrations, authentication, and token cycles."""

    @staticmethod
    async def register(db: AsyncSession, register_data: RegisterRequest) -> User:
        user_repo = UserRepository(db)

        # Check duplicate email
        existing_email = await user_repo.get_by_email(register_data.email)
        if existing_email:
            security_logger.warning("Registration blocked: email %s already registered.", register_data.email)
            raise ValidationException("Email address already registered.")

        # Check duplicate username
        existing_username = await user_repo.get_by_username(register_data.username)
        if existing_username:
            security_logger.warning("Registration blocked: username %s already taken.", register_data.username)
            raise ValidationException("Username already in use.")

        # Hash credentials before storage
        hashed = hash_password(register_data.password)

        # Save User object with profile and preference
        user = User(
            email=register_data.email,
            username=register_data.username,
            hashed_password=hashed,
            is_superuser=False,
            profile=UserProfile(full_name=None, avatar_url=None, bio=None),
            preference=UserPreference(theme="light", receiving_notifications=True),
        )
        db.add(user)
        await db.commit()
        
        # Load user eagerly with relationships to prevent validation errors in schemas
        registered_user = await user_repo.get(user.id)

        security_logger.info("Successfully registered user account: %s", user.username)
        return registered_user

    @staticmethod
    async def authenticate(db: AsyncSession, credentials: LoginRequest) -> Dict[str, str]:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.hashed_password):
            security_logger.warning("Failed login attempt for email: %s", credentials.email)
            raise AuthException("Incorrect email or password.")

        if not user.is_active:
            security_logger.warning("Blocked login attempt for inactive account: %s", user.username)
            raise AuthException("User account is disabled.")

        security_logger.info("Successful login for user: %s", user.username)

        # Generate Access and Refresh Tokens
        token_data = {"sub": user.username, "role": "admin" if user.is_superuser else "user"}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh_session(db: AsyncSession, refresh_token: str) -> Dict[str, str]:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthException("Invalid token type.")
            username = payload.get("sub")
            if not username:
                raise AuthException("Token claims missing subject.")
        except Exception as e:
            raise AuthException("Invalid or expired refresh token.") from e

        user_repo = UserRepository(db)
        user = await user_repo.get_by_username(username)
        if not user or not user.is_active:
            raise AuthException("User associated with token is inactive.")

        # Re-issue Access Token, keep same Refresh Token
        token_data = {"sub": user.username, "role": "admin" if user.is_superuser else "user"}
        return {"access_token": create_access_token(token_data), "refresh_token": refresh_token, "token_type": "bearer"}

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, profile_data: UserProfileUpdate) -> UserProfile:
        profile_repo = BaseRepository(UserProfile, db)
        # Fetch profile
        profiles = await profile_repo.list(filters={"user_id": user_id})
        if not profiles:
            raise NotFoundException("User profile not found.")
        profile = profiles[0]

        update_dict = {k: v for k, v in profile_data.model_dump().items() if v is not None}
        updated = await profile_repo.update(profile, update_dict)
        await db.commit()
        await db.refresh(updated)
        return updated

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, pwd_data: PasswordChangeRequest) -> bool:
        user_repo = UserRepository(db)
        user = await user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found.")

        # Verify old password
        if not verify_password(pwd_data.old_password, user.hashed_password):
            raise AuthException("Incorrect old password.")

        # Hash and update
        hashed = hash_password(pwd_data.new_password)
        await user_repo.update(user, {"hashed_password": hashed})
        await db.commit()
        security_logger.info("Password successfully changed for user: %s", user.username)
        return True
