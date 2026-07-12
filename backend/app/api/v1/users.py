from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, get_db
from app.core.responses import StandardJSONResponse
from app.schemas.user import UserResponse, UserProfileUpdate, UserProfileResponse, PasswordChangeRequest
from app.models.user import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users-management"])


@router.get("/me", response_class=StandardJSONResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile metadata and settings of the active user."""
    return UserResponse.model_validate(current_user)


@router.put("/me/profile", response_class=StandardJSONResponse)
async def update_profile(
    profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Updates user biographical profile attributes."""
    updated_profile = await AuthService.update_profile(db, current_user.id, profile_data)
    return UserProfileResponse.model_validate(updated_profile)


@router.put("/me/password", response_class=StandardJSONResponse)
async def change_password(
    pwd_data: PasswordChangeRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Changes password credentials after verifying old credentials."""
    await AuthService.change_password(db, current_user.id, pwd_data)
    return {"message": "Password successfully updated."}
