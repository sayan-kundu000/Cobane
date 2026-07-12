from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.core.responses import StandardJSONResponse
from app.schemas.auth import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_class=StandardJSONResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registers new user profiles, generating default preferences and details."""
    user = await AuthService.register(db, register_data)
    # Output matches UserResponse standard serialization
    return UserResponse.model_validate(user)


@router.post("/login", response_class=StandardJSONResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Validates user account email and password, returning Access/Refresh tokens."""
    token_response = await AuthService.authenticate(db, credentials)
    return token_response


@router.post("/logout", response_class=StandardJSONResponse)
async def logout():
    """Sign-out endpoint stub."""
    return {"message": "Successfully logged out from session."}


@router.post("/refresh", response_class=StandardJSONResponse)
async def refresh_token(refresh_token_val: str, db: AsyncSession = Depends(get_db)):
    """Rotates expired Access tokens using a active Refresh token."""
    new_tokens = await AuthService.refresh_session(db, refresh_token_val)
    return new_tokens


@router.post("/forgot-password", response_class=StandardJSONResponse)
async def forgot_password(_data: ForgotPasswordRequest):
    """Forgot password handler placeholder. Emails aren't dispatched."""
    return {"message": "If the account exists, a reset code was generated."}


@router.post("/reset-password", response_class=StandardJSONResponse)
async def reset_password(_data: ResetPasswordRequest):
    """Password reset modifier placeholder. Stub outputs success."""
    return {"message": "Password successfully updated."}
