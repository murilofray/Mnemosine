"""
Error handling middleware for unified exception management.
"""

import logging
import traceback
from typing import Any, Callable, Union

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle all exceptions uniformly."""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        """Process request and handle any exceptions."""
        try:
            response = await call_next(request)
            return response
        except RateLimitExceeded as e:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": str(e.detail),
                    "type": "rate_limit_error",
                },
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "type": "http_error"},
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid input",
                    "detail": str(e),
                    "type": "validation_error",
                },
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred",
                    "type": "internal_error",
                },
            )


def create_http_exception_handler() -> Callable[..., Any]:
    """Create custom HTTP exception handler."""

    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "type": "http_error",
                "path": request.url.path,
            },
        )

    return http_exception_handler


def create_validation_exception_handler() -> Callable[..., Any]:
    """Create custom validation exception handler."""

    async def validation_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": str(exc),
                "type": "validation_error",
                "path": request.url.path,
            },
        )

    return validation_exception_handler
