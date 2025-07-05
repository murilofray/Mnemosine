"""
JWT authentication utilities for token creation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.config.settings import settings
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class TokenData(BaseModel):
    """Token data model."""

    username: Optional[str] = None


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None or not isinstance(username, str):
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials (single user system)."""
    if username != settings.ADMIN_USERNAME:
        return False

    # Direct password comparison - the hashed password should be stored in settings
    # For security, the admin password should be hashed once and stored
    return verify_password(password, settings.ADMIN_PASSWORD_HASH)
