"""
Agent service implementation.

This module provides the agent service implementation for executing agents.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, cast
import asyncio
import time

from app.domain.repositories.agent_repository import AgentRepository
from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.entities.agent import Agent, AgentConfiguration, AgentPermissions, AgentType
from app.core.entities.execution import (
    Execution, ExecutionStep, Command, 
    ExecutionStatus, CommandStatus, StepType
)
from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.agents.factory import AgentFactory
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionCallback(AgentCallback):
    def __init__(self, execution_id: str, execution_repository):
        """
        Initialize the execution callback.
        
        Args:
            execution_id: ID of the execution
            execution_repository: Repository for execution operations
        """
        super().__init__(execution_id, execution_repository)
        self.agent_service = None
        
    async def on_step(self, step_type: str, content: str) -> None:
        """
        Handle execution step.
        
        Args:
            step_type: Type of the step
            content: Content of the step
        """
        try:
            # Create step entity
            step = ExecutionStep(
                execution_id=self.execution_id,
                step_type=step_type,
                content=content
            )
            
            # Save step to database
            added_step = await self.execution_repository.add_step(step)
            
            # Send streaming update if available
            if hasattr(self, 'agent_service') and self.agent_service:
                await self.agent_service.send_execution_event(
                    self.execution_id,
                    {
                        "type": "step",
                        "step_type": step_type,
                        "content": content,
                        "created_at": added_step.created_at.isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error saving execution step: {str(e)}", exc_info=True)
    
    async def on_command(
        self,
        command: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Handle command execution.
        
        Args:
            command: Command string
            status: Status of the command
            exit_code: Exit code of the command
            stdout: Standard output from the command
            stderr: Standard error from the command
            duration_ms: Duration of the command execution in milliseconds
        """
        try:
            # Create command entity
            cmd = Command(
                execution_id=self.execution_id,
                command=command,
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms
            )
            
            # Save command to database
            added_command = await self.execution_repository.add_command(cmd)
            
            # Send streaming update if available
            if hasattr(self, 'agent_service') and self.agent_service:
                await self.agent_service.send_execution_event(
                    self.execution_id,
                    {
                        "type": "command",
                        "command": command,
                        "status": status,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "duration_ms": duration_ms,
                        "created_at": added_command.created_at.isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}", exc_info=True)


class AgentService:
    """
    Concrete implementation of the agent service.
    """
    
    def __init__(
        self,
        agent_repo: AgentRepository,
        execution_repo: ExecutionRepository,
        command_client: CommandClient
    ):
        """
        Initialize the agent service with repositories and dependencies.
        
        Args:
            agent_repo: Repository for agent operations
            execution_repo: Repository for execution operations
            command_client: Client for command execution
        """
        self.agent_repo = agent_repo
        self.execution_repo = execution_repo
        self.command_client = command_client
        self.agent_factory = AgentFactory(execution_repo, command_client)
        
        # Track streaming connections - maps connection ID to asyncio Queue
        self.streaming_connections: Dict[str, asyncio.Queue] = {}
    
    async def create_agent(
        self,
        name: str,
        agent_type: str,
        description: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
        permissions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Name of the agent
            agent_type: Type of the agent
            description: Optional description of the agent
            configuration: Optional configuration parameters
            permissions: Optional permission settings
            metadata: Optional additional metadata
            user_id: Optional user ID of the creator
            
        Returns:
            The created agent
            
        Raises:
            ValueError: If the agent data is invalid
        """
        # Validate agent type
        try:
            agent_type_enum = AgentType(agent_type)
        except ValueError:
            valid_types = ", ".join([t.value for t in AgentType])
            raise ValueError(f"Invalid agent type: {agent_type}. Valid types are: {valid_types}")
        
        # Create default configuration if none provided
        if not configuration:
            configuration = {
                "model_name": settings.DEFAULT_MODEL,
                "temperature": settings.DEFAULT_TEMPERATURE,
                "max_tokens": settings.DEFAULT_MAX_TOKENS,
                "streaming": False,
                "tools": [],
                "max_iterations": 10
            }
            
        # Create default permissions if none provided
        if not permissions:
            permissions = {
                "execute_commands": False,
                "allowed_commands": [],
                "allowed_paths": settings.ALLOWED_PATHS,
                "network_access": False,
                "memory_limit": settings.MAX_MEMORY_MB
            }
            
        # Create the agent entity
        agent = Agent(
            id=str(uuid.uuid4()),
            name=name,
            user_id=user_id or "system",
            agent_type=agent_type_enum,
            description=description,
            configuration=AgentConfiguration(**configuration),
            permissions=AgentPermissions(**permissions),
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to repository
        return await self.agent_repo.create(agent)
    
    async def get_agent(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The agent if found, None otherwise
        """
        return await self.agent_repo.get_by_id(agent_id, user_id)
    
    async def update_agent(
        self, 
        agent_id: str,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None,
        permissions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: The ID of the agent to update
            user_id: Optional user ID for access control
            name: Optional new name for the agent
            description: Optional new description
            configuration: Optional new configuration
            permissions: Optional new permissions
            metadata: Optional new metadata
            
        Returns:
            The updated agent if found, None otherwise
        
        Raises:
            ValueError: If the update data is invalid
        """
        # Get the agent first to validate
        agent = await self.agent_repo.get_by_id(agent_id, user_id)
        if not agent:
            return None
            
        # Update the agent
        return await self.agent_repo.update(
            agent_id=agent_id,
            user_id=user_id,
            name=name,
            description=description,
            configuration=configuration,
            permissions=permissions,
            metadata=metadata,
        )
    
    async def delete_agent(self, agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: The ID of the agent to delete
            user_id: Optional user ID for access control
            
        Returns:
            True if deleted, False otherwise
        """
        return await self.agent_repo.delete(agent_id, user_id)
    
    async def list_agents(
        self, 
        user_id: Optional[str] = None, 
        agent_type: Optional[AgentType] = None, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Agent]:
        """
        List agents with filtering and pagination.
        
        Args:
            user_id: Optional user ID for filtering
            agent_type: Optional agent type for filtering
            skip: Number of agents to skip
            limit: Maximum number of agents to return
            
        Returns:
            List of agents
        """
        return await self.agent_repo.list(
            user_id=user_id,
            agent_type=agent_type,
            skip=skip,
            limit=limit
        )
    
    async def count_agents(
        self, 
        user_id: Optional[str] = None, 
        agent_type: Optional[AgentType] = None
    ) -> int:
        """
        Count agents with filtering.
        
        Args:
            user_id: Optional user ID for filtering
            agent_type: Optional agent type for filtering
            
        Returns:
            Number of agents matching the filters
        """
        return await self.agent_repo.count(
            user_id=user_id,
            agent_type=agent_type
        )
    
    async def execute_agent(
        self,
        agent_id: str,
        input: str,
        user_id: Optional[str] = None,
        stream: bool = False
    ) -> Execution:
        """
        Execute an agent.
        
        Args:
            agent_id: Agent ID
            input: Input for the agent
            user_id: ID of the user who started the execution
            stream: Whether to stream execution results
            
        Returns:
            Execution
            
        Raises:
            ValueError: If the agent is not found
        """
        # Get agent
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Create execution entity
        execution = Execution(
            agent_id=agent_id,
            input=input,
            status="running",
            user_id=user_id
        )
        
        # Save execution to database
        execution = await self.execution_repo.create(execution)
        
        # Create callback
        callback = ExecutionCallback(execution.id, self.execution_repo)
        
        # Add agent_service reference for streaming if needed
        if stream:
            callback.agent_service = self
        
        try:
            # Create agent instance
            agent_instance = self.agent_factory.create_agent(agent)
            
            # Execute agent
            start_time = time.time()
            
            # Update execution status
            await self.execution_repo.update_status(execution.id, "running")
            
            # Send status event if streaming
            if stream:
                await self.send_execution_event(
                    execution.id,
                    {
                        "type": "status",
                        "execution_id": execution.id,
                        "status": "running"
                    }
                )
            
            # Run agent
            result = await agent_instance.run(input_text=input, execution_id=execution.id)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Determine status
            status = "failed" if result.error else "completed"
            
            # Update execution
            execution = await self.execution_repo.update_status(
                execution_id=execution.id,
                status=status,
                output=result.output,
                error=result.error,
                metadata={
                    **(result.metadata or {}),
                    "duration_ms": duration_ms
                }
            )
            
            # Send completion event if streaming
            if stream:
                await self.send_execution_event(
                    execution.id,
                    {
                        "type": "completion",
                        "execution_id": execution.id,
                        "status": status,
                        "output": result.output,
                        "error": result.error,
                        "metadata": {
                            **(result.metadata or {}),
                            "duration_ms": duration_ms
                        }
                    }
                )
                
                # Signal end of stream
                await self.send_execution_event(execution.id, None)
            
            logger.info(f"Executed agent with ID {agent_id}, execution ID {execution.id}")
            
            return execution
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}", exc_info=True)
            
            # Update execution status
            await self.execution_repo.update_status(
                execution_id=execution.id,
                status="failed",
                error=str(e)
            )
            
            # Send error event if streaming
            if stream:
                await self.send_execution_event(
                    execution.id,
                    {
                        "type": "error",
                        "execution_id": execution.id,
                        "status": "failed",
                        "error": str(e)
                    }
                )
                
                # Signal end of stream
                await self.send_execution_event(execution.id, None)
            
            # Get updated execution
            execution = await self.execution_repo.get_by_id(execution.id)
            
            return execution
    
    async def send_execution_event(self, execution_id: str, event: Optional[Dict[str, Any]]) -> None:
        """
        Send an event to all WebSocket connections listening to an execution.
        
        Args:
            execution_id: ID of the execution
            event: Event to send, or None to signal end of stream
        """
        # Find all connections for this execution
        connection_ids = [
            conn_id for conn_id in self.streaming_connections.keys()
            if conn_id.endswith(f"_{execution_id}")
        ]
        
        # Send event to all connections
        for conn_id in connection_ids:
            queue = self.streaming_connections.get(conn_id)
            if queue:
                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Error sending event to connection {conn_id}: {str(e)}")
    
    async def get_execution(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: The ID of the execution to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The execution if found, None otherwise
        """
        return await self.execution_repo.get_by_id(execution_id, user_id)
    
    async def list_executions(
        self, 
        user_id: Optional[str] = None, 
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 10
    ) -> List[Execution]:
        """
        List executions with filtering and pagination.
        
        Args:
            user_id: Optional user ID for filtering
            agent_id: Optional agent ID for filtering
            status: Optional status for filtering
            skip: Number of executions to skip
            limit: Maximum number of executions to return
            
        Returns:
            List of executions
        """
        return await self.execution_repo.list(
            user_id=user_id,
            agent_id=agent_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def count_executions(
        self, 
        user_id: Optional[str] = None, 
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count executions with filtering.
        
        Args:
            user_id: Optional user ID for filtering
            agent_id: Optional agent ID for filtering
            status: Optional status for filtering
            
        Returns:
            Number of executions matching the filters
        """
        return await self.execution_repo.count(
            user_id=user_id,
            agent_id=agent_id,
            status=status
        )
    
    async def cancel_execution(self, execution_id: str) -> Optional[Execution]:
        """
        Cancel an execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Updated execution or None if not found
        """
        # Get execution
        execution = await self.execution_repo.get_by_id(execution_id)
        if not execution:
            return None
            
        # Only cancel if not already completed or failed
        if execution.status in ["completed", "failed", "canceled"]:
            return execution
            
        # Update execution status
        execution = await self.execution_repo.update_status(
            execution_id=execution_id,
            status="canceled",
            error="Execution canceled by user"
        )
        
        # Send cancel event
        await self.send_execution_event(
            execution_id,
            {
                "type": "completion",
                "execution_id": execution_id,
                "status": "canceled",
                "error": "Execution canceled by user"
            }
        )
        
        # Signal end of stream
        await self.send_execution_event(execution_id, None)
        
        logger.info(f"Canceled execution with ID {execution_id}")
        
        return execution 