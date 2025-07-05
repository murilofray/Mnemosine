"""
Rate limiting using SlowAPI for API protection.
"""

from app.config.settings import settings
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def get_client_ip(request: Request) -> str:
    """Get client IP address for rate limiting."""
    return get_remote_address(request)


# Initialize rate limiter
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=(
        [f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
        if settings.RATE_LIMIT_ENABLED
        else []
    ),
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom rate limit exceeded handler."""
    # Safely get retry_after from the exception with proper validation
    retry_after = 60  # Default value
    
    if hasattr(exc, 'retry_after') and exc.retry_after is not None:
        try:
            retry_after = int(exc.retry_after)
            # Ensure retry_after is reasonable (between 1 and 3600 seconds)
            retry_after = max(1, min(retry_after, 3600))
        except (ValueError, TypeError):
            retry_after = 60  # Fall back to default if conversion fails
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Limit: {exc.detail}",
            "retry_after": retry_after,
        },
        headers={"Retry-After": str(retry_after)},
    )
