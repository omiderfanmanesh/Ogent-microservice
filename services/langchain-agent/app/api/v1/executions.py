"""
Executions API endpoints.

This module provides REST API endpoints for execution management.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.api.schemas import (
    ExecutionResponse,
    ExecutionList,
    ExecutionStatusResponse
)
from app.api.dependencies import CurrentUser, get_agent_service
from app.core.services.agent_service import AgentService
from app.core.entities.execution import ExecutionStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/executions", 
    tags=["executions"]
)


@router.get("", response_model=ExecutionList)
async def list_executions(
    user_id: CurrentUser,
    agent_service: AgentService = Depends(get_agent_service),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    agent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """
    List executions with filtering and pagination.
    
    Args:
        user_id: Current user ID
        agent_service: Agent service
        skip: Number of executions to skip
        limit: Maximum number of executions to return
        agent_id: Optional filter by agent ID
        status: Optional filter by execution status
        
    Returns:
        List of executions
    """
    try:
        # Validate status if provided
        if status:
            try:
                ExecutionStatus(status)
            except ValueError:
                # Invalid status, return empty list
                return ExecutionList(items=[], total=0, skip=skip, limit=limit)
        
        # Get executions
        executions = await agent_service.list_executions(
            user_id=user_id,
            agent_id=agent_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        # Get total count
        total = await agent_service.count_executions(
            user_id=user_id,
            agent_id=agent_id,
            status=status
        )
        
        return ExecutionList(
            items=executions,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing executions"
        )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    user_id: CurrentUser,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Get an execution by ID.
    
    Args:
        execution_id: Execution ID
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Execution details
        
    Raises:
        HTTPException: If the execution is not found
    """
    try:
        execution = await agent_service.get_execution(execution_id, user_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found"
            )
        
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting the execution"
        )


@router.get("/{execution_id}/status", response_model=ExecutionStatusResponse)
async def get_execution_status(
    execution_id: str,
    user_id: CurrentUser,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Get the status of an execution.
    
    Args:
        execution_id: Execution ID
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Execution status
        
    Raises:
        HTTPException: If the execution is not found
    """
    try:
        execution = await agent_service.get_execution(execution_id, user_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found"
            )
        
        # Return a subset of the execution data for status
        return ExecutionStatusResponse(
            id=execution.id,
            status=execution.status.value if hasattr(execution.status, "value") else execution.status,
            output=execution.output,
            error=execution.error,
            tokens_used=execution.tokens_used,
            started_at=execution.started_at,
            completed_at=execution.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting the execution status"
        )


@router.post("/{execution_id}/cancel", response_model=ExecutionStatusResponse)
async def cancel_execution(
    execution_id: str,
    user_id: CurrentUser,
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Cancel an execution.
    
    Args:
        execution_id: Execution ID
        user_id: Current user ID
        agent_service: Agent service
        
    Returns:
        Updated execution status
        
    Raises:
        HTTPException: If the execution is not found or cannot be canceled
    """
    try:
        execution = await agent_service.cancel_execution(execution_id, user_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found"
            )
        
        # Return a subset of the execution data for status
        return ExecutionStatusResponse(
            id=execution.id,
            status=execution.status.value if hasattr(execution.status, "value") else execution.status,
            output=execution.output,
            error=execution.error,
            tokens_used=execution.tokens_used,
            started_at=execution.started_at,
            completed_at=execution.completed_at
        )
    except ValueError as e:
        logger.error(f"Error canceling execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while canceling the execution"
        ) 