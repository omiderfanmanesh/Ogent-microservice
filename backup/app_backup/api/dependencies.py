"""
Dependencies module for FastAPI.

This module provides dependencies that can be injected into API routes.
"""

import logging
from typing import AsyncGenerator, Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.database import get_session
from app.infrastructure.persistence.repositories import SQLAgentRepository, SQLExecutionRepository, SQLUserRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.domain.repositories.agent_repository import AgentRepository
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.user_repository import UserRepository
from app.core.services.agent_service import AgentService
from app.config import settings
from app.api.auth import get_current_user, validate_token_ws
from app.core.entities.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Export common dependencies
__all__ = [
    "get_session",
    "get_agent_repository",
    "get_execution_repository",
    "get_user_repository",
    "get_command_client",
    "get_agent_service",
    "get_current_user",
    "validate_token_ws",
]


async def get_agent_repository(
    session: AsyncSession = Depends(get_session)
) -> AgentRepository:
    """
    Get the agent repository implementation.
    
    Args:
        session: Database session from dependency
        
    Returns:
        Agent repository implementation
    """
    return SQLAgentRepository(session=session)


async def get_execution_repository(
    session: AsyncSession = Depends(get_session)
) -> ExecutionRepository:
    """
    Get the execution repository implementation.
    
    Args:
        session: Database session from dependency
        
    Returns:
        Execution repository implementation
    """
    return SQLExecutionRepository(session=session)


async def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> UserRepository:
    """
    Get the user repository implementation.
    
    Args:
        session: Database session from dependency
        
    Returns:
        User repository implementation
    """
    return SQLUserRepository(session=session)


async def get_command_client() -> AsyncGenerator[CommandClient, None]:
    """
    Get the command client implementation.
    
    Yields:
        Command client implementation
    """
    command_client = CommandClient(base_url=settings.command_service_url)
    try:
        yield command_client
    finally:
        await command_client.close()


async def get_agent_service(
    agent_repo: AgentRepository = Depends(get_agent_repository),
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
    command_client: CommandClient = Depends(get_command_client),
    current_user: User = Depends(get_current_user),
) -> AgentService:
    """
    Get the agent service.
    
    Args:
        agent_repo: Agent repository
        execution_repo: Execution repository
        command_client: Command client
        current_user: Current user
    
    Returns:
        The agent service
    """
    # Create service
    return AgentService(
        agent_repo=agent_repo,
        execution_repo=execution_repo,
        command_client=command_client
    ) 