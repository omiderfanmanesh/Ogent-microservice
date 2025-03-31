"""
Create tables command.

This script creates all database tables directly without using Alembic.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.infrastructure.persistence.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """
    Create all database tables.
    """
    # Create engine
    database_url = str(settings.database_url)
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    
    # Close engine
    await engine.dispose()


if __name__ == "__main__":
    """
    Run the command.
    
    Usage:
        python -m app.commands.create_tables
    """
    asyncio.run(create_tables()) 