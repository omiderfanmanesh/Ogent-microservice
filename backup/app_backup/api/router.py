"""
Main API router.

This module includes all route modules and provides the main FastAPI router.
"""

from fastapi import APIRouter
from app.api.routes import agent, execution

# Create the main API router
router = APIRouter(prefix="/api/v1")

# Include all route modules
router.include_router(agent.router)
router.include_router(execution.router) 