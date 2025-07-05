"""
User service for authentication and user management.
"""

from datetime import timedelta
from typing import Optional

from app.config.settings import settings
from app.core.security.auth import (TokenData, authenticate_user,
                                    create_access_token, verify_token)
from app.models.user import User, get_user_by_username
from app.schemas.auth import LoginRequest, LoginResponse
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def login_user(login_data: LoginRequest) -> LoginResponse:
    """Authenticate user and return access token."""
    if not authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials,
) -> User:
    """Get current user from JWT token."""
    token_data = verify_token(credentials.credentials)

    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_username(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def validate_user_permissions(user: User) -> bool:
    """Validate user has necessary permissions."""
    return user.is_active and user.is_admin
