"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

import logfire
from app.api.v1.api import api_router
from app.config.settings import settings
from app.core.security.limiter import limiter, rate_limit_exceeded_handler
from app.middleware.errors import (ErrorHandlingMiddleware,
                                   create_http_exception_handler,
                                   create_validation_exception_handler)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

# Initialize Logfire if enabled
if settings.LOGFIRE_ENABLED and settings.LOGFIRE_TOKEN:
    logfire.configure(token=settings.LOGFIRE_TOKEN)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager."""
    # Startup
    if settings.LOGFIRE_ENABLED:
        logfire.info("Application starting up", app_name=settings.APP_NAME)

    yield

    # Shutdown
    if settings.LOGFIRE_ENABLED:
        logfire.info("Application shutting down", app_name=settings.APP_NAME)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered backend with LangGraph agents and comprehensive security",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add rate limiting to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Add exception handlers
app.add_exception_handler(HTTPException, create_http_exception_handler())
app.add_exception_handler(ValueError, create_validation_exception_handler())

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with basic API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "api": {"v1": settings.API_V1_PREFIX},
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Application health check endpoint.
    """
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
    }


# For development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
