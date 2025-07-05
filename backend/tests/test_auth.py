"""
Tests for authentication functionality.
"""

from unittest.mock import patch

import pytest
from app.config.settings import settings
from app.core.security.auth import create_access_token, verify_token
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints and functionality."""

    def test_login_success(self):
        """Test successful login."""
        with patch("app.config.settings.settings.ADMIN_USERNAME", "testuser"), patch(
            "app.config.settings.settings.ADMIN_PASSWORD", "testpass"
        ):

            response = client.post(
                f"{settings.API_V1_PREFIX}/auth/login",
                json={"username": "testuser", "password": "testpass"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            json={"username": "wrong", "password": "wrong"},
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login", json={"username": "test"}
        )

        assert response.status_code == 422

    def test_get_current_user_success(self):
        """Test getting current user with valid token."""
        # Create a valid token
        token = create_access_token(data={"sub": settings.ADMIN_USERNAME})

        response = client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == settings.ADMIN_USERNAME
        assert data["is_active"] == True
        assert data["is_admin"] == True

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        response = client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_get_current_user_no_token(self):
        """Test getting current user without token."""
        response = client.get(f"{settings.API_V1_PREFIX}/auth/me")

        assert response.status_code == 403


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_and_verify_token(self):
        """Test token creation and verification."""
        test_data = {"sub": "testuser"}
        token = create_access_token(test_data)

        assert token is not None
        assert isinstance(token, str)

        # Verify token
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.username == "testuser"

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        token_data = verify_token(invalid_token)

        assert token_data is None

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        from datetime import timedelta

        # Create token that expires immediately
        token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(seconds=-1)
        )

        token_data = verify_token(token)
        assert token_data is None
