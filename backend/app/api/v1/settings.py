from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from pydantic import BaseModel, Field
from app.core.dependencies import get_db, get_current_user
from app.core.responses import StandardJSONResponse
from app.models.user import User, UserPreference
from app.schemas.user import UserPreferenceResponse

router = APIRouter(prefix="/settings", tags=["settings"])


class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = Field(
        default=None, pattern="^(light|dark)$", description="User preference theme selection (light or dark)"
    )
    receiving_notifications: Optional[bool] = Field(
        default=None, description="Whether the user wants to receive system notifications"
    )


@router.get("/user", response_class=StandardJSONResponse)
async def get_user_settings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Retrieves active preference settings (theme, notifications) for the logged-in user."""
    result = await db.execute(select(UserPreference).filter(UserPreference.user_id == current_user.id))
    prefs = result.scalars().first()

    if not prefs:
        # Fallback default values
        return {"theme": "light", "receiving_notifications": True}

    return UserPreferenceResponse.model_validate(prefs)


@router.put("/user", response_class=StandardJSONResponse)
async def update_user_settings(
    pref_in: UserPreferenceUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Updates theme styling parameters and notifications settings for the logged-in user."""
    result = await db.execute(select(UserPreference).filter(UserPreference.user_id == current_user.id))
    prefs = result.scalars().first()

    if not prefs:
        prefs = UserPreference(user_id=current_user.id, theme="light", receiving_notifications=True)
        db.add(prefs)

    if pref_in.theme is not None:
        prefs.theme = pref_in.theme
    if pref_in.receiving_notifications is not None:
        prefs.receiving_notifications = pref_in.receiving_notifications

    await db.commit()
    await db.refresh(prefs)

    return UserPreferenceResponse.model_validate(prefs)


@router.get("/system", response_class=StandardJSONResponse)
async def get_system_settings():
    """Retrieves general system config settings (version, features configurations). Public access."""
    return {
        "app_name": "Cobane Code Review Assistant",
        "system_version": "1.0.0",
        "features": {"pylint": True, "bandit": True, "radon": True, "ai_review": True},
    }
