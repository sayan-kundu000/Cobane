from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator

class LoginRequest(BaseModel):
    """Schema representing user login credentials."""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Schema representing user registration details with verification constraints."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def passwords_match(self) -> 'RegisterRequest':
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self

class Token(BaseModel):
    """Schema representing JWT credentials payloads returned after login sessions."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema mapping user references extracted from decoded tokens."""
    username: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    """Schema mapping credentials requests for password resets."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Schema tracking new passwords assignments verifying reset tokens validity."""
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)

    @model_validator(mode="after")
    def passwords_match(self) -> 'ResetPasswordRequest':
        if self.new_password != self.new_password_confirm:
            raise ValueError("passwords do not match")
        return self
