"""
WebSocket endpoints.

This module provides WebSocket endpoints for real-time agent interaction.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from uuid import UUID

from app.api.dependencies import verify_api_key, get_agent_service
from app.core.services.agent_service import AgentService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/ws",
    tags=["websockets"]
)


class ConnectionManager:
    """
    WebSocket connection manager.
    
    This class manages active WebSocket connections.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.execution_connections: Dict[str, str] = {}  # execution_id -> connection_id
    
    async def connect(self, connection_id: str, websocket: WebSocket) -> None:
        """
        Connect a new WebSocket.
        
        Args:
            connection_id: Connection ID
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str) -> None:
        """
        Disconnect a WebSocket.
        
        Args:
            connection_id: Connection ID
        """
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
            
            # Clean up execution connections
            to_remove = []
            for execution_id, conn_id in self.execution_connections.items():
                if conn_id == connection_id:
                    to_remove.append(execution_id)
            
            for execution_id in to_remove:
                self.execution_connections.pop(execution_id)
            
            logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a specific connection.
        
        Args:
            connection_id: Connection ID
            message: Message to send
            
        Returns:
            True if message was sent, False otherwise
        """
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message))
            return True
        return False
    
    def register_execution(self, execution_id: str, connection_id: str) -> None:
        """
        Register an execution with a connection.
        
        Args:
            execution_id: Execution ID
            connection_id: Connection ID
        """
        self.execution_connections[execution_id] = connection_id
        logger.info(f"Registered execution {execution_id} with connection {connection_id}")
    
    def get_connection_for_execution(self, execution_id: str) -> Optional[str]:
        """
        Get the connection ID for an execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Connection ID if found, None otherwise
        """
        return self.execution_connections.get(execution_id)


# Create connection manager
manager = ConnectionManager()


@router.websocket("/agent/{agent_id}")
async def agent_websocket(
    websocket: WebSocket, 
    agent_id: str,
    api_key: str = Query(...),
    agent_service: AgentService = Depends(get_agent_service),
):
    """
    WebSocket endpoint for agent interaction.
    
    This endpoint allows real-time interaction with an agent.
    
    Args:
        websocket: WebSocket connection
        agent_id: Agent ID
        api_key: API key for authentication
        agent_service: Agent service
    """
    connection_id = f"{agent_id}_{websocket.client.host}_{websocket.client.port}"
    
    try:
        # Verify API key
        user_id = await verify_api_key(api_key)
        
        # Verify agent exists
        agent = await agent_service.get_agent(agent_id, user_id)
        if not agent:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Agent not found")
            return
        
        # Accept connection
        await manager.connect(connection_id, websocket)
        
        # Handle messages
        while True:
            # Receive message
            message_text = await websocket.receive_text()
            try:
                # Parse message
                message = json.loads(message_text)
                
                # Handle message based on type
                if message.get("type") == "execute":
                    await handle_execute_message(
                        connection_id=connection_id,
                        agent_id=agent_id,
                        user_id=user_id,
                        message=message,
                        agent_service=agent_service
                    )
                elif message.get("type") == "cancel":
                    await handle_cancel_message(
                        connection_id=connection_id,
                        message=message,
                        agent_service=agent_service
                    )
                else:
                    await manager.send_message(
                        connection_id=connection_id,
                        message={"type": "error", "error": f"Unknown message type: {message.get('type')}"}
                    )
            except json.JSONDecodeError:
                await manager.send_message(
                    connection_id=connection_id,
                    message={"type": "error", "error": "Invalid JSON message"}
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}", exc_info=True)
                await manager.send_message(
                    connection_id=connection_id,
                    message={"type": "error", "error": str(e)}
                )
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        if connection_id in manager.active_connections:
            manager.disconnect(connection_id)


async def handle_execute_message(
    connection_id: str,
    agent_id: str,
    user_id: str,
    message: Dict[str, Any],
    agent_service: AgentService
) -> None:
    """
    Handle an execute message.
    
    Args:
        connection_id: Connection ID
        agent_id: Agent ID
        user_id: User ID
        message: Message data
        agent_service: Agent service
    """
    # Get input from message
    input_text = message.get("input")
    if not input_text:
        await manager.send_message(
            connection_id=connection_id,
            message={"type": "error", "error": "Missing input field"}
        )
        return
    
    # Get metadata from message
    metadata = message.get("metadata", {})
    
    try:
        # Start execution with streaming
        execution = await agent_service.start_execution(
            agent_id=agent_id,
            input=input_text,
            user_id=user_id,
            metadata=metadata,
            streaming=True,
        )
        
        # Register execution with this connection
        manager.register_execution(str(execution.id), connection_id)
        
        # Send initial response
        await manager.send_message(
            connection_id=connection_id,
            message={
                "type": "execution_started",
                "execution_id": str(execution.id),
                "agent_id": agent_id,
                "status": execution.status.value if hasattr(execution.status, "value") else execution.status,
            }
        )
        
        # Start background task to stream updates
        asyncio.create_task(
            stream_execution_updates(
                execution_id=str(execution.id),
                connection_id=connection_id,
                agent_service=agent_service,
                user_id=user_id
            )
        )
    
    except Exception as e:
        logger.error(f"Error starting execution: {str(e)}", exc_info=True)
        await manager.send_message(
            connection_id=connection_id,
            message={"type": "error", "error": str(e)}
        )


async def handle_cancel_message(
    connection_id: str,
    message: Dict[str, Any],
    agent_service: AgentService
) -> None:
    """
    Handle a cancel message.
    
    Args:
        connection_id: Connection ID
        message: Message data
        agent_service: Agent service
    """
    # Get execution ID from message
    execution_id = message.get("execution_id")
    if not execution_id:
        await manager.send_message(
            connection_id=connection_id,
            message={"type": "error", "error": "Missing execution_id field"}
        )
        return
    
    # Get connection ID for this execution
    registered_connection = manager.get_connection_for_execution(execution_id)
    if not registered_connection or registered_connection != connection_id:
        await manager.send_message(
            connection_id=connection_id,
            message={"type": "error", "error": "Not authorized to cancel this execution"}
        )
        return
    
    try:
        # Cancel execution
        await agent_service.cancel_execution(execution_id)
        
        # Send confirmation
        await manager.send_message(
            connection_id=connection_id,
            message={
                "type": "execution_canceled",
                "execution_id": execution_id
            }
        )
    
    except Exception as e:
        logger.error(f"Error canceling execution: {str(e)}", exc_info=True)
        await manager.send_message(
            connection_id=connection_id,
            message={"type": "error", "error": str(e)}
        )


async def stream_execution_updates(
    execution_id: str,
    connection_id: str,
    agent_service: AgentService,
    user_id: str
) -> None:
    """
    Stream execution updates to the WebSocket.
    
    Args:
        execution_id: Execution ID
        connection_id: Connection ID
        agent_service: Agent service
        user_id: User ID
    """
    try:
        async for update in agent_service.stream_execution(execution_id, user_id):
            # Check if connection is still active
            if connection_id not in manager.active_connections:
                logger.info(f"Connection {connection_id} no longer active, stopping stream")
                break
            
            # Send update
            await manager.send_message(connection_id, update)
    
    except Exception as e:
        logger.error(f"Error streaming execution updates: {str(e)}", exc_info=True)
        # Try to send error if connection is still active
        if connection_id in manager.active_connections:
            await manager.send_message(
                connection_id=connection_id,
                message={"type": "error", "error": str(e)}
            )
    
    finally:
        # Clean up execution connection
        if execution_id in manager.execution_connections:
            manager.execution_connections.pop(execution_id) 