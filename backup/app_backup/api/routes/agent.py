"""
Agent routes.

This module provides API routes for agent operations.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_agent_service, get_current_user
from app.api.schemas.agent import (
    AgentSchema, 
    AgentCreateSchema, 
    AgentUpdateSchema,
    AgentExecuteSchema
)
from app.api.schemas.execution import ExecutionSchema
from app.core.entities.user import User
from app.core.services.agent_service import AgentService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentSchema, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreateSchema,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new agent.
    
    Args:
        agent_data: Agent creation data
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Created agent
    """
    try:
        # Create configuration dictionary from the fields
        config = {
            "model_name": agent_data.configuration.model_name,
            "temperature": agent_data.configuration.temperature,
            "max_tokens": agent_data.configuration.max_tokens,
            "system_message": agent_data.configuration.system_message,
            "streaming": agent_data.configuration.streaming,
            "tools": agent_data.configuration.tools,
            "max_iterations": agent_data.configuration.max_iterations
        }
        
        # Create permissions dictionary if provided
        permissions = None
        if agent_data.permissions:
            permissions = {
                "execute_commands": agent_data.permissions.execute_commands,
                "allowed_commands": agent_data.permissions.allowed_commands,
                "allowed_paths": agent_data.permissions.allowed_paths,
                "network_access": agent_data.permissions.network_access,
                "memory_limit": agent_data.permissions.memory_limit
            }
            
        agent = await agent_service.create_agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            configuration=config,
            permissions=permissions,
            metadata=agent_data.metadata,
            user_id=current_user.id,
        )
        return agent
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}",
        )


@router.get("", response_model=List[AgentSchema])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    agent_type: Optional[str] = Query(None),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    List agents.
    
    Args:
        skip: Number of agents to skip
        limit: Maximum number of agents to return
        agent_type: Filter by agent type
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        List of agents
    """
    try:
        agents = await agent_service.list_agents(
            user_id=current_user.id,
            agent_type=agent_type,
            skip=skip,
            limit=limit,
        )
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
        )


@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(
    agent_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get an agent by ID.
    
    Args:
        agent_id: Agent ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Agent details
    """
    try:
        agent = await agent_service.get_agent(
            agent_id=str(agent_id),
            user_id=current_user.id,
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found",
            )
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}",
        )


@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(
    agent_data: AgentUpdateSchema,
    agent_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Update an agent.
    
    Args:
        agent_data: Agent update data
        agent_id: Agent ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Updated agent
    """
    try:
        # Check if agent exists
        agent = await agent_service.get_agent(
            agent_id=str(agent_id),
            user_id=current_user.id,
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found",
            )
        
        # Prepare configuration dictionary if provided
        config = None
        if agent_data.configuration:
            config = {
                "model_name": agent_data.configuration.model_name,
                "temperature": agent_data.configuration.temperature,
                "max_tokens": agent_data.configuration.max_tokens,
                "system_message": agent_data.configuration.system_message,
                "streaming": agent_data.configuration.streaming,
                "tools": agent_data.configuration.tools,
                "max_iterations": agent_data.configuration.max_iterations
            }
            
        # Prepare permissions dictionary if provided
        permissions = None
        if agent_data.permissions:
            permissions = {
                "execute_commands": agent_data.permissions.execute_commands,
                "allowed_commands": agent_data.permissions.allowed_commands,
                "allowed_paths": agent_data.permissions.allowed_paths,
                "network_access": agent_data.permissions.network_access,
                "memory_limit": agent_data.permissions.memory_limit
            }
        
        # Update agent
        updated_agent = await agent_service.update_agent(
            agent_id=str(agent_id),
            name=agent_data.name,
            description=agent_data.description,
            configuration=config,
            permissions=permissions,
            metadata=agent_data.metadata,
            user_id=current_user.id,
        )
        return updated_agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}",
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an agent.
    
    Args:
        agent_id: Agent ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
    """
    try:
        # Check if agent exists
        agent = await agent_service.get_agent(
            agent_id=str(agent_id),
            user_id=current_user.id,
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found",
            )
        
        # Delete agent
        await agent_service.delete_agent(
            agent_id=str(agent_id),
            user_id=current_user.id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}",
        )


@router.post("/{agent_id}/execute", response_model=ExecutionSchema)
async def execute_agent(
    execution_data: AgentExecuteSchema,
    agent_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Execute an agent.
    
    Args:
        execution_data: Execution data
        agent_id: Agent ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Execution details
    """
    try:
        # Check if agent exists
        agent = await agent_service.get_agent(
            agent_id=str(agent_id),
            user_id=current_user.id,
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found",
            )
        
        # Execute agent
        execution = await agent_service.execute_agent(
            agent_id=str(agent_id),
            input=execution_data.input,
            user_id=current_user.id,
            stream=execution_data.stream,
            metadata=execution_data.metadata,
        )
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}",
        ) 