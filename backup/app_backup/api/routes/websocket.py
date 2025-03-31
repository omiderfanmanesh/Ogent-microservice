"""
WebSocket routes for real-time communication.

This module defines WebSocket endpoints for streaming agent execution.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends, Query
from fastapi.responses import JSONResponse

from app.api.dependencies import get_agent_service, validate_token_ws
from app.core.services.agent_service import AgentService
from app.core.entities.user import User
from app.api.schemas.execution import StreamEvent

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


@router.websocket("/agents/{agent_id}/execute")
async def execute_agent_ws(
    websocket: WebSocket,
    agent_id: UUID,
    token: str = Query(..., description="Authentication token"),
    input: str = Query(..., description="Input for the agent"),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    Execute an agent and stream the results via WebSocket.
    
    Args:
        websocket: The WebSocket connection
        agent_id: The agent ID to execute
        token: Authentication token
        input: The input for the agent
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
    
    # Accept the WebSocket connection
    await websocket.accept()
    
    try:
        # Check if agent exists
        agent = await agent_service.get_agent(str(agent_id), str(user.id))
        if not agent:
            await websocket.send_json({
                "type": "error",
                "message": f"Agent {agent_id} not found or you don't have access"
            })
            await websocket.close()
            return
        
        # Execute agent with streaming enabled
        execution = await agent_service.execute_agent(
            agent_id=str(agent_id),
            input=input,
            user_id=str(user.id),
            stream=True
        )
        
        # Create streaming connection
        connection_id = f"ws_{str(user.id)}_{str(execution.id)}"
        queue = asyncio.Queue()
        agent_service.streaming_connections[connection_id] = queue
        
        # Listen for streaming events
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
                    
                    # Check if execution is still in progress
                    execution = await agent_service.get_execution(execution.id, str(user.id))
                    if execution and execution.status in ["completed", "failed", "canceled"]:
                        # Execution finished while we were waiting
                        await websocket.send_json({
                            "type": "completion",
                            "execution_id": execution.id,
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
        logger.info(f"WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error executing agent: {str(e)}"
            })
        except:
            pass
    finally:
        # Ensure WebSocket is closed
        try:
            await websocket.close()
        except:
            pass 