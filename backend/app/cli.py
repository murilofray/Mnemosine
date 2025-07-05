"""
CLI tools for administrative tasks using Typer.
"""

import hashlib
import secrets
from typing import Optional

import typer
from app.config.settings import settings

app = typer.Typer(help="Mnemosine Backend CLI Tools")


@app.command()
def generate_secret_key(length: int = 32) -> None:
    """
    Generate a secure secret key for JWT authentication.

    Args:
        length: Length of the secret key (default: 32)
    """
    secret_key = secrets.token_urlsafe(length)
    typer.echo(f"Generated secret key: {secret_key}")
    typer.echo(f'Add this to your .env file: SECRET_KEY="{secret_key}"')


@app.command()
def hash_password(password: str) -> None:
    """
    Generate a hash for a password (for development/testing).

    Args:
        password: The password to hash
    """
    from app.core.security.auth import get_password_hash

    hashed = get_password_hash(password)
    typer.echo(f"Password hash: {hashed}")


@app.command()
def validate_config() -> None:
    """
    Validate the current configuration settings.
    """
    typer.echo("Validating configuration...")

    try:
        # Test settings loading
        typer.echo(f"✓ App Name: {settings.APP_NAME}")
        typer.echo(f"✓ Version: {settings.APP_VERSION}")
        typer.echo(f"✓ Debug Mode: {settings.DEBUG}")
        typer.echo(f"✓ API Prefix: {settings.API_V1_PREFIX}")

        # Check required settings
        if len(settings.SECRET_KEY) < 32:
            typer.echo("⚠️  SECRET_KEY should be at least 32 characters long", err=True)
        else:
            typer.echo("✓ Secret Key: Valid length")

        if settings.ADMIN_PASSWORD and len(settings.ADMIN_PASSWORD) < 8:
            typer.echo(
                "⚠️  ADMIN_PASSWORD should be at least 8 characters long", err=True
            )
        else:
            typer.echo("✓ Admin Password: Valid length")

        # Check API keys
        if settings.OPENAI_API_KEY:
            typer.echo("✓ OpenAI API Key: Configured")
        else:
            typer.echo("⚠️  OpenAI API Key: Not configured")

        if settings.ANTHROPIC_API_KEY:
            typer.echo("✓ Anthropic API Key: Configured")
        else:
            typer.echo("⚠️  Anthropic API Key: Not configured")

        if settings.GEMINI_API_KEY:
            typer.echo("✓ Gemini API Key: Configured")
        else:
            typer.echo("⚠️  Gemini API Key: Not configured")

        typer.echo(f"✓ Default Provider: {settings.DEFAULT_PROVIDER}")
        typer.echo(f"✓ Default Model: {settings.DEFAULT_MODEL}")

        typer.echo("Configuration validation complete!")

    except Exception as e:
        typer.echo(f"❌ Configuration error: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info",
) -> None:
    """
    Run the FastAPI server with custom settings.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        log_level: Log level (debug, info, warning, error)
    """
    import uvicorn

    typer.echo(f"Starting server on {host}:{port}")

    uvicorn.run(
        "app.main:app", host=host, port=port, reload=reload, log_level=log_level
    )


@app.command()
def test_auth(username: str, password: str) -> None:
    """
    Test authentication with given credentials.

    Args:
        username: Username to test
        password: Password to test
    """
    from app.core.security.auth import authenticate_user

    typer.echo(f"Testing authentication for user: {username}")

    if authenticate_user(username, password):
        typer.echo("✓ Authentication successful!")
    else:
        typer.echo("❌ Authentication failed!")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
