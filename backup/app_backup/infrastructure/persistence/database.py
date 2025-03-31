"""
Database configuration.

This module provides database connection management and session utilities.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine - convert PostgresDsn to string
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Import models at the end to avoid circular imports
from app.infrastructure.persistence.models import Base
# Import additional models needed by other modules
from app.infrastructure.persistence.models import AgentModel, ExecutionModel, ExecutionStepModel, CommandModel, UserModel

__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_session",
    "Base",
    "AgentModel", 
    "ExecutionModel", 
    "ExecutionStepModel", 
    "CommandModel", 
    "UserModel"
] 