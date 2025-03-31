"""
Create admin user command.

This script creates an admin user in the database.
"""

import asyncio
import logging
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.infrastructure.persistence.repositories.user_repository import SQLUserRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """
    Create admin user if it doesn't exist.
    """
    # Create engine and session
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
    )
    
    async with async_session() as session:
        # Create user repository
        user_repo = SQLUserRepository(session)
        
        # Check if admin user exists
        admin = await user_repo.get_by_username(settings.admin_username)
        
        if admin:
            logger.info(f"Admin user '{settings.admin_username}' already exists")
            return
        
        # Create admin user
        user_id = str(uuid.uuid4())
        admin = await user_repo.create(
            id=user_id,
            username=settings.admin_username,
            email=settings.admin_email,
            password=settings.admin_password,
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        
        logger.info(f"Created admin user '{settings.admin_username}' with ID: {user_id}")


if __name__ == "__main__":
    """
    Run the command.
    
    Usage:
        python -m app.commands.create_admin
    """
    asyncio.run(create_admin_user()) 