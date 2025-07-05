"""
User model for single user authentication system.
"""

from typing import Optional

from app.config.settings import settings
from pydantic import BaseModel


class User(BaseModel):
    """Simple user model for single user system."""

    username: str
    is_active: bool = True
    is_admin: bool = True


def get_current_user() -> User:
    """Get the current (only) user in the system."""
    return User(username=settings.ADMIN_USERNAME, is_active=True, is_admin=True)


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username (single user system)."""
    if username == settings.ADMIN_USERNAME:
        return get_current_user()
    return None
