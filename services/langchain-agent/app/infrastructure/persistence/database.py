"""
Database connection.

This module provides database connection functionality for the LangChain Agent Service.
"""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.persistence.models import Base

# Configure logging
logger = logging.getLogger(__name__)

# Global engine instance
engine: Optional[AsyncEngine] = None


async def init_db() -> None:
    """
    Initialize database connection.
    
    This function creates the database engine and initializes tables if they don't exist.
    """
    global engine
    try:
        # Create engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO_LOG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE
        )
        
        # Create tables if they don't exist
        async with engine.begin() as conn:
            if settings.DB_CREATE_TABLES:
                logger.info("Creating database tables")
                await conn.run_sync(Base.metadata.create_all)
        
        logger.info(f"Database initialized: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


async def close_db() -> None:
    """
    Shutdown database connection.
    
    This function disposes the database engine.
    """
    global engine
    if engine:
        await engine.dispose()
        engine = None
        logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session.
    
    This function creates a new session for each request and closes it when the request is finished.
    
    Yields:
        Database session
    """
    global engine
    if not engine:
        await init_db()
    
    # Create session factory
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    # Create and yield session
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error in database session: {str(e)}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()
