"""
Main application module.

This module defines the FastAPI application and includes all routes.
"""

import logging
import uuid
from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from app.api.routes import agent, execution, websocket, auth
from app.api.dependencies import get_session
from app.config import settings
from app.infrastructure.persistence.database import engine, Base, AsyncSessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter(prefix=settings.api_prefix)

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(agent.router)
api_router.include_router(execution.router)
api_router.include_router(websocket.router)

# Create application
app = FastAPI(
    title=settings.app_name,
    description="API for creating and executing LangChain agents",
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to index.html."""
    return RedirectResponse(url="/static/index.html")


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    """Run startup tasks."""
    logger.info("Starting up application...")
    # Perform startup tasks here
    
    # Create database tables (in dev/test only)
    if settings.debug:
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        
        # Initialize admin user if not exists
        try:
            from app.infrastructure.persistence.repositories.user_repository import SQLUserRepository
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.core.entities.user import User
            from app.api.auth import get_password_hash
            
            async with AsyncSessionLocal() as session:
                # Check if admin user exists
                user_repo = SQLUserRepository(session)
                admin = await user_repo.get_by_username(settings.admin_username)
                
                if not admin:
                    # Create admin user
                    logger.info(f"Creating admin user: {settings.admin_username}")
                    admin_user = User(
                        id=str(uuid.uuid4()),
                        username=settings.admin_username,
                        email=settings.admin_email,
                        hashed_password=get_password_hash(settings.admin_password),
                        is_active=True,
                        is_superuser=True,
                    )
                    await user_repo.create(admin_user)
                    logger.info(f"Admin user created successfully")
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}", exc_info=True)


@app.on_event("shutdown")
async def on_shutdown():
    """Run shutdown tasks."""
    logger.info("Shutting down application...")
    # Perform shutdown tasks here


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 