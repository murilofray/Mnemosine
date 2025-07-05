"""
FastAPI dependencies for dependency injection.
Contains reusable dependencies for authentication, database access, etc.
"""

from typing import Annotated

from app.db.session import get_db as _get_db
from app.models.user import User
from app.services.user import get_current_user_from_token, security
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Database dependency
DatabaseDep = Annotated[Session, Depends(_get_db)]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    Validates JWT token and returns the User model.
    Raises HTTPException if token is invalid or user not found.
    
    Usage:
        @app.get("/protected-route")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    return await get_current_user_from_token(credentials)


# Type annotation for current user dependency
CurrentUserDep = Annotated[User, Depends(get_current_user)]


# For backward compatibility, you can also use get_db directly
# But prefer using DatabaseDep type annotation for new code
get_db = _get_db 