"""
API v1 router.

This module provides the main router for API v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.executions import router as executions_router
from app.api.v1.websockets import router as websockets_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include individual routers
api_router.include_router(agents_router)
api_router.include_router(executions_router)
api_router.include_router(websockets_router) 