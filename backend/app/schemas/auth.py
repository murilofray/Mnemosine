"""
Authentication schemas for request and response models.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""

    username: str
    is_active: bool
    is_admin: bool


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str  # subject (username)
    exp: int  # expiration time
