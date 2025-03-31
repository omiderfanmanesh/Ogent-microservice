"""
Agents API endpoints.

This module provides REST API endpoints for agent management.
"""

import logging
from typing import Optional, AsyncIterator
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
import json

from app.api.schemas import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentList,
    ExecutionCreate,
    ExecutionResponse
)
from app.api.dependencies import CurrentUser, get_agent_service, get_current_user
from app.core.services.agent_service import AgentService
from app.core.entities.agent import AgentType

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/agents", 
    tags=["agents"]
)


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Create a new agent.
    
    Args:
        agent_data: Agent data
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Created agent
        
    Raises:
        HTTPException: If the agent data is invalid
    """
    try:
        # Convert Pydantic models to dicts
        configuration = agent_data.configuration.dict() if agent_data.configuration else None
        permissions = agent_data.permissions.dict() if agent_data.permissions else None
        
        # Create agent
        agent = await agent_service.create_agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            configuration=configuration,
            permissions=permissions,
            metadata=agent_data.metadata,
            user_id=user_id,
        )
        
        return agent
    except ValueError as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the agent"
        )


@router.get("", response_model=AgentList)
async def list_agents(
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    agent_type: Optional[str] = Query(None),
):
    """
    List agents with filtering and pagination.
    
    Args:
        user_id: Current user ID
        agent_service: Agent service
        offset: Number of agents to skip
        limit: Maximum number of agents to return
        agent_type: Optional filter by agent type
        
    Returns:
        List of agents
    """
    try:
        # Convert agent_type to enum if provided
        agent_type_enum = None
        if agent_type:
            try:
                agent_type_enum = AgentType(agent_type)
            except ValueError:
                # Invalid agent type, return empty list
                return AgentList(items=[], total=0, skip=offset, limit=limit)
        
        # Get agents
        agents, total = await agent_service.agent_repository.list(
            user_id=user_id,
            agent_type=agent_type_enum,
            offset=offset,
            limit=limit
        )
        
        # Get total count
        if total is None:
            total = await agent_service.agent_repository.count(
                user_id=user_id,
                agent_type=agent_type_enum
            )
        
        return AgentList(
            items=agents,
            total=total,
            skip=offset,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing agents"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Get an agent by ID.
    
    Args:
        agent_id: Agent ID
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Agent details
        
    Raises:
        HTTPException: If the agent is not found
    """
    try:
        agent = await agent_service.get_agent(agent_id, user_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting the agent"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Update an agent.
    
    Args:
        agent_id: Agent ID
        agent_data: Agent data to update
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If the agent is not found or the data is invalid
    """
    try:
        # Convert Pydantic models to dicts
        configuration = agent_data.configuration.dict() if agent_data.configuration else None
        permissions = agent_data.permissions.dict() if agent_data.permissions else None
        
        # Update agent
        agent = await agent_service.update_agent(
            agent_id=agent_id,
            user_id=user_id,
            name=agent_data.name,
            description=agent_data.description,
            configuration=configuration,
            permissions=permissions,
            metadata=agent_data.metadata,
        )
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        return agent
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the agent"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Delete an agent.
    
    Args:
        agent_id: Agent ID
        user_id: Current user ID
        agent_service: Agent service
        
    Raises:
        HTTPException: If the agent is not found
    """
    try:
        deleted = await agent_service.delete_agent(agent_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the agent"
        )


@router.post("/{agent_id}/execute", response_model=ExecutionResponse)
async def execute_agent(
    agent_id: str,
    execution_data: ExecutionCreate,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Execute an agent with input.
    
    Args:
        agent_id: Agent ID
        execution_data: Execution data
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Execution details
        
    Raises:
        HTTPException: If the agent is not found or the input is invalid
    """
    try:
        execution = await agent_service.execute_agent(
            agent_id=agent_id,
            input=execution_data.input,
            user_id=user_id,
            metadata=execution_data.metadata,
        )
        
        return execution
    except ValueError as e:
        logger.error(f"Error executing agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error executing agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while executing the agent"
        )


@router.post("/{agent_id}/execute/stream")
async def stream_execute_agent(
    agent_id: str,
    execution_data: ExecutionCreate,
    user_id: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Execute an agent with streaming results.
    
    Args:
        agent_id: Agent ID
        execution_data: Execution data
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Streaming response with execution updates
        
    Raises:
        HTTPException: If the agent is not found or the input is invalid
    """
    try:
        # Start the execution
        execution = await agent_service.start_execution(
            agent_id=agent_id,
            input=execution_data.input,
            user_id=user_id,
            metadata=execution_data.metadata,
            streaming=True,
        )
        
        # Return a streaming response
        return StreamingResponse(
            _stream_execution(agent_service, execution.id, user_id),
            media_type="text/event-stream",
        )
    except ValueError as e:
        logger.error(f"Error executing agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error executing agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while executing the agent"
        )


async def _stream_execution(
    agent_service: AgentService, 
    execution_id: str, 
    user_id: str
) -> AsyncIterator[str]:
    """
    Stream execution updates.
    
    Args:
        agent_service: Agent service
        execution_id: Execution ID
        user_id: User ID
        
    Yields:
        Execution updates as server-sent events
    """
    try:
        async for update in agent_service.stream_execution(execution_id, user_id):
            # Prepare the SSE data
            if isinstance(update, dict):
                data = json.dumps(update)
            else:
                data = json.dumps({"type": "content", "content": str(update)})
            
            # Yield as server-sent event
            yield f"data: {data}\n\n"
    except Exception as e:
        logger.error(f"Error streaming execution: {str(e)}")
        # Send error event
        error_data = json.dumps({"type": "error", "content": str(e)})
        yield f"data: {error_data}\n\n"
    finally:
        # Send end event
        yield f"data: {json.dumps({'type': 'end'})}\n\n" 