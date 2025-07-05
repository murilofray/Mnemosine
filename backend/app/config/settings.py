"""
Application configuration using Pydantic BaseSettings.
Handles environment variables and application settings.
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_NAME: str = "Mnemosine Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # Security settings
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True

    DATABASE_URL: str

    DATABASE_ECHO: bool = False

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE"]
    ALLOWED_HEADERS: List[str] = ["*"]

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    DEFAULT_PROVIDER: str = "gemini"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    # Logfire settings (Pydantic observability)
    LOGFIRE_TOKEN: Optional[str] = None
    LOGFIRE_ENABLED: bool = False

    # Single user authentication (no database required)
    ADMIN_USERNAME: str = Field(..., description="Admin username - must be set via environment variable")
    ADMIN_PASSWORD_HASH: str = Field(..., description="Admin password hash - must be set via environment variable")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        elif isinstance(v, str):
            return [v]
        raise ValueError(v)

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is properly formatted."""
        if not v:
            raise ValueError("SECRET_KEY must not be empty")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("postgresql://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")
        return v

    @field_validator("ADMIN_PASSWORD_HASH")
    @classmethod
    def validate_admin_password_hash(cls, v: str) -> str:
        """Validate admin password hash format."""
        if not v or not v.startswith("$2b$"):
            raise ValueError("ADMIN_PASSWORD_HASH must be a valid bcrypt hash")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()


# Global settings instance
settings = get_settings()
