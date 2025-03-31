"""
Main application module.

This module provides the main FastAPI application.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router
from app.infrastructure.persistence.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for FastAPI application.
    
    This function is called when the application starts and stops.
    It's used for initialization and cleanup.
    """
    # Startup: initialize database
    logger.info("Initializing application...")
    await init_db()
    
    yield
    
    # Shutdown: close database connection
    logger.info("Shutting down application...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LangChain Agent Service API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add exception handler for 500 errors
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """
    Handle internal server errors.
    
    Args:
        request: Request that caused the error
        exc: Exception that was raised
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Internal server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Include API router
app.include_router(api_router)


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok", "version": settings.app_version}


@app.get("/api/info")
async def get_info():
    """
    API information endpoint.
    
    Returns:
        API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "agent_types": [
            "conversational",
            "command",
            "sql",
            "custom"
        ]
    }
