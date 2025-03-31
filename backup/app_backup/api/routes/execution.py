"""
API routes for execution endpoints.

This module defines the routes for execution operations.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, WebSocket, WebSocketDisconnect
from uuid import UUID
import json
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_agent_service, get_current_user, validate_token_ws
from app.api.schemas.execution import (
    ExecutionResponse,
    ExecutionListResponse,
    BasicExecutionResponse,
    ExecutionStatusResponse,
    ExecutionSchema,
    ExecutionCreateSchema,
    ExecutionUpdateSchema,
)
from app.core.services.agent_service import AgentService
from app.core.entities.execution import Execution
from app.core.entities.user import User


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
)


@router.post("", response_model=ExecutionSchema, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_data: ExecutionCreateSchema,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new execution.
    
    Args:
        execution_data: Execution creation data
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Created execution
    """
    try:
        # Check if agent exists
        agent = await agent_service.get_agent(
            agent_id=execution_data.agent_id,
            user_id=current_user.id,
        )
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {execution_data.agent_id} not found",
            )
        
        # Execute agent
        execution = await agent_service.execute_agent(
            agent_id=execution_data.agent_id,
            input=execution_data.input,
            user_id=current_user.id,
            stream=execution_data.stream,
        )
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating execution: {str(e)}", exc_info=True)
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Stack trace: {tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create execution: {str(e)}",
        )


@router.get("", response_model=List[ExecutionSchema])
async def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    agent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    List executions.
    
    Args:
        skip: Number of executions to skip
        limit: Maximum number of executions to return
        agent_id: Filter by agent ID
        status: Filter by status
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        List of executions
    """
    try:
        executions = await agent_service.list_executions(
            user_id=current_user.id,
            agent_id=agent_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        return executions
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}",
        )


@router.get("/{execution_id}", response_model=ExecutionSchema)
async def get_execution(
    execution_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get an execution by ID.
    
    Args:
        execution_id: Execution ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Execution details
    """
    try:
        execution = await agent_service.get_execution(
            execution_id=str(execution_id),
            user_id=current_user.id,
        )
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found",
            )
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}",
        )


@router.get("/agent/{agent_id}", response_model=List[ExecutionSchema])
async def list_agent_executions(
    agent_id: UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    List executions for an agent.
    
    Args:
        agent_id: Agent ID
        skip: Number of executions to skip
        limit: Maximum number of executions to return
        status: Filter by status
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        List of executions
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
        
        # List executions
        executions = await agent_service.list_executions(
            user_id=current_user.id,
            agent_id=str(agent_id),
            status=status,
            skip=skip,
            limit=limit,
        )
        return executions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing agent executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agent executions: {str(e)}",
        )


@router.put("/{execution_id}", response_model=ExecutionSchema)
async def update_execution(
    execution_data: ExecutionUpdateSchema,
    execution_id: UUID = Path(...),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Update an execution.
    
    Args:
        execution_data: Execution update data
        execution_id: Execution ID
        agent_service: Agent service dependency
        current_user: Current authenticated user
        
    Returns:
        Updated execution
    """
    try:
        # Check if execution exists
        execution = await agent_service.get_execution(
            execution_id=str(execution_id),
            user_id=current_user.id,
        )
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found",
            )
        
        # Update execution
        updated_execution = await agent_service.update_execution_status(
            execution_id=str(execution_id),
            status=execution_data.status.value if execution_data.status else None,
            output=execution_data.output,
            error=execution_data.error,
            tokens_used=execution_data.tokens_used,
            user_id=current_user.id,
        )
        return updated_execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update execution: {str(e)}",
        )


@router.get("/{execution_id}/status", response_model=ExecutionStatusResponse)
async def get_execution_status(
    execution_id: UUID = Path(..., description="The execution ID"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Get the status of an execution.

    Args:
        execution_id: The execution ID.
        agent_service: The agent service dependency.
        current_user: The current authenticated user.

    Returns:
        The execution status.

    Raises:
        HTTPException: If the execution is not found or the user doesn't have access.
    """
    execution = await agent_service.get_execution(str(execution_id), current_user.id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID {execution_id} not found",
        )
    return ExecutionStatusResponse(
        id=execution.id,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        error=execution.error,
    )


@router.post("/{execution_id}/cancel", response_model=BasicExecutionResponse)
async def cancel_execution(
    execution_id: UUID = Path(..., description="The execution ID"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel an execution.

    Args:
        execution_id: The execution ID.
        agent_service: The agent service dependency.
        current_user: The current authenticated user.

    Returns:
        The updated execution.

    Raises:
        HTTPException: If the execution is not found, the user doesn't have access,
        or the execution cannot be canceled.
    """
    try:
        execution = await agent_service.cancel_execution(str(execution_id), current_user.id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found",
            )
        return BasicExecutionResponse(
            id=execution.id,
            agent_id=execution.agent_id,
            user_id=execution.user_id,
            status=execution.status,
            input=execution.input,
            output=execution.output,
            error=execution.error,
            tokens_used=execution.tokens_used,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            created_at=execution.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.websocket("/{execution_id}/stream")
async def stream_execution(
    websocket: WebSocket,
    execution_id: UUID,
    token: str = Query(...),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Stream execution updates via WebSocket.
    
    This endpoint streams real-time updates for an execution, including
    steps, commands, and status changes.
    
    Args:
        websocket: The WebSocket connection
        execution_id: The execution ID to stream
        token: Authentication token
        agent_service: The agent service
    """
    # Validate token and get user
    try:
        user = await validate_token_ws(token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect to WebSocket
    await websocket.accept()
    
    try:
        # Get execution to verify existence and permissions
        execution = await agent_service.get_execution(str(execution_id))
        if not execution:
            await websocket.send_json({
                "type": "error",
                "message": f"Execution {execution_id} not found"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify user has access to this execution
        if execution.user_id and execution.user_id != str(user.id):
            await websocket.send_json({
                "type": "error",
                "message": "You don't have permission to access this execution"
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Send initial execution state
        await websocket.send_json({
            "type": "status",
            "execution_id": str(execution_id),
            "status": execution.status,
            "created_at": execution.created_at.isoformat(),
            "updated_at": execution.updated_at.isoformat()
        })
        
        # Send existing steps
        for step in execution.steps:
            await websocket.send_json({
                "type": "step",
                "step_type": step.step_type,
                "content": step.content,
                "created_at": step.created_at.isoformat()
            })
        
        # Send existing commands
        for command in execution.commands:
            await websocket.send_json({
                "type": "command",
                "command": command.command,
                "status": command.status,
                "exit_code": command.exit_code,
                "stdout": command.stdout,
                "stderr": command.stderr,
                "duration_ms": command.duration_ms,
                "created_at": command.created_at.isoformat()
            })
        
        # If execution is completed, send completion message and close
        if execution.status in ["completed", "failed", "canceled"]:
            await websocket.send_json({
                "type": "completion",
                "execution_id": str(execution_id),
                "status": execution.status,
                "output": execution.output,
                "error": execution.error,
                "metadata": execution.metadata
            })
            await websocket.close()
            return
        
        # Set up execution streaming
        # Create streaming queue for this connection
        queue = asyncio.Queue()
        
        # Register for streaming updates
        connection_id = f"ws_{str(user.id)}_{str(execution_id)}"
        agent_service.streaming_connections[connection_id] = queue
        
        # Listen for updates from the queue
        try:
            while True:
                # Wait for events from the queue with a timeout
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    
                    # None signals end of stream
                    if event is None:
                        break
                    
                    # Send event to client
                    await websocket.send_json(event)
                    
                    # If this is a completion event, exit after sending
                    if event.get("type") == "completion":
                        break
                        
                except asyncio.TimeoutError:
                    # Send a ping to keep the connection alive
                    await websocket.send_json({"type": "ping"})
                    
                    # Check if execution is still in progress by fetching latest status
                    execution = await agent_service.get_execution(str(execution_id))
                    if execution and execution.status in ["completed", "failed", "canceled"]:
                        # Execution finished while we were waiting
                        await websocket.send_json({
                            "type": "completion",
                            "execution_id": str(execution_id),
                            "status": execution.status,
                            "output": execution.output,
                            "error": execution.error,
                            "metadata": execution.metadata
                        })
                        break
        
        finally:
            # Clean up streaming connection
            agent_service.streaming_connections.pop(connection_id, None)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for execution {execution_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Internal server error: {str(e)}"
            })
        except:
            pass
    finally:
        # Ensure WebSocket is closed
        try:
            await websocket.close()
        except:
            pass 