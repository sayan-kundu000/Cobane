from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator

class UserBase(BaseModel):
    """Base schema holding general user identifiers."""
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """Schema for account registration creation properties."""
    password: str

class UserProfileResponse(BaseModel):
    """Schema mapping profile metadata."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class UserPreferenceResponse(BaseModel):
    """Schema mapping customization preference details."""
    theme: str
    receiving_notifications: bool

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """Schema representing complete user model outputs."""
    id: int
    is_active: bool
    is_superuser: bool
    profile: Optional[UserProfileResponse] = None
    preference: Optional[UserPreferenceResponse] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Schema for changing profile properties."""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)

class PasswordChangeRequest(BaseModel):
    """Schema mapping secure password overrides verifying old password constraints."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def passwords_match(self) -> 'PasswordChangeRequest':
        if self.new_password != self.new_password_confirm:
            raise ValueError("new passwords do not match")
        return self
