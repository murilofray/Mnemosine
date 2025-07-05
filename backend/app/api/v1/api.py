"""
Main API router for version 1 endpoints.
"""
from typing import Any, Dict

from app.api.v1 import agent, auth
from fastapi import APIRouter

# Create the main v1 router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(agent.router)


@api_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    API health check endpoint.

    Returns basic health information about the API.
    """
    return {
        "status": "healthy",
        "version": "v1",
        "message": "Mnemosine Backend API is running",
    }
