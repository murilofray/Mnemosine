"""
Authentication API endpoints.
"""

from app.core.security.limiter import limiter
from app.dependencies import CurrentUserDep
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.services.user import login_user
from fastapi import APIRouter, Request

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return access token.

    - **username**: User's username
    - **password**: User's password

    Returns access token for authenticated requests.
    """
    return await login_user(login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: CurrentUserDep) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        username=current_user.username, 
        is_active=current_user.is_active, 
        is_admin=current_user.is_admin
    )


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(
    request: Request, current_user: CurrentUserDep
) -> LoginResponse:
    """
    Refresh access token.

    Requires valid JWT token and returns new token.
    """
    # Create new token for the user
    from datetime import timedelta

    from app.config.settings import settings
    from app.core.security.auth import create_access_token

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
