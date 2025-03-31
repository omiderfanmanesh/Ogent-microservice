"""
API dependencies.

This module provides dependencies for FastAPI endpoints.
"""

import logging
from typing import Annotated
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.persistence.database import get_session
from app.infrastructure.adapters.command_client import CommandClient
from app.core.services.agent_service import AgentService
from app.infrastructure.persistence.repositories import SQLAgentRepository, SQLExecutionRepository
from app.core.agents.factory import AgentFactory

# Configure logging
logger = logging.getLogger(__name__)


# Type alias for current user
CurrentUser = str


async def verify_api_key(api_key: str) -> str:
    """
    Verify API key and return user ID.
    
    Args:
        api_key: API key to verify
        
    Returns:
        User ID associated with the API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    # For now, we'll use a simple API key verification
    # In production, this should validate against a database or auth service
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return "default_user"  # For now, return a default user ID


async def get_current_user(x_user_id: str = Header(...)) -> str:
    """
    Get current user from request header.
    
    Args:
        x_user_id: User ID from header
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If user ID is not provided
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not provided"
        )
    return x_user_id


def get_command_client() -> CommandClient:
    """
    Get command client dependency.
    
    Returns:
        CommandClient instance
    """
    return CommandClient(base_url=settings.COMMAND_SERVICE_URL)


async def get_agent_service(
    db: AsyncSession = Depends(get_session),
    command_client: CommandClient = Depends(get_command_client),
) -> AgentService:
    """
    Get agent service dependency.
    
    Args:
        db: Database session
        command_client: Command client
        
    Returns:
        AgentService instance
    """
    agent_repository = SQLAgentRepository(db)
    execution_repository = SQLExecutionRepository(db)
    agent_factory = AgentFactory(command_client=command_client)
    
    return AgentService(
        agent_repository=agent_repository,
        execution_repository=execution_repository,
        agent_factory=agent_factory
    ) 