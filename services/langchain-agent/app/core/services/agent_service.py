"""
Agent service.

This module provides the agent service implementation for managing agents and executions.
"""

import logging
import uuid
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator, Union, Tuple
import json

from app.domain.repositories.agent_repository import AgentRepository
from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.entities.agent import Agent, AgentType, AgentConfiguration, AgentPermissions
from app.core.entities.execution import (
    Execution, ExecutionStep, Command, 
    ExecutionStatus, CommandStatus, StepType
)
from app.core.agents.factory import AgentFactory
from app.core.agents import (
    AgentResult,
    AgentCallback
)

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionCallback(AgentCallback):
    """Callback for tracking execution steps and commands."""
    
    def __init__(self, execution_id: str, execution_repository: ExecutionRepository):
        """
        Initialize execution callback.
        
        Args:
            execution_id: ID of the execution
            execution_repository: Execution repository for persisting steps and commands
        """
        self.execution_id = execution_id
        self.execution_repository = execution_repository
    
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
            await self.execution_repository.add_step(step)
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
            status: Command status
            exit_code: Command exit code
            stdout: Command standard output
            stderr: Command standard error
            duration_ms: Command duration in milliseconds
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
            await self.execution_repository.add_command(cmd)
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}", exc_info=True)


class AgentService:
    """
    Agent service.
    
    This service is responsible for managing agents and their executions.
    """
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        execution_repository: ExecutionRepository,
        agent_factory: AgentFactory
    ):
        """
        Initialize agent service.
        
        Args:
            agent_repository: Repository for agent persistence
            execution_repository: Repository for execution persistence
            agent_factory: Factory for creating agent instances
        """
        self.agent_repository = agent_repository
        self.execution_repository = execution_repository
        self.agent_factory = agent_factory
        
        # Track streaming executions
        self._streaming_executions: Dict[str, asyncio.Queue] = {}
    
    async def create_agent(
        self,
        name: str,
        description: str,
        agent_type: str,
        config: Dict[str, Any],
        permissions: Optional[AgentPermissions] = None,
        user_id: Optional[str] = None
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            description: Agent description
            agent_type: Type of agent
            config: Agent configuration
            permissions: Agent permissions
            user_id: ID of the user who owns the agent
            
        Returns:
            Created agent
            
        Raises:
            ValueError: If the agent type is not supported or the configuration is invalid
        """
        # Validate agent type
        available_types = self.agent_factory.get_available_agent_types()
        if agent_type not in available_types:
            raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {', '.join(available_types)}")
        
        # Create default permissions if none provided
        if not permissions:
            permissions = AgentPermissions()
        
        # Create agent entity
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            config=config,
            permissions=permissions,
            user_id=user_id
        )
        
        # Validate configuration by creating an agent instance
        try:
            self.agent_factory.create_agent(
                agent_type=agent_type,
                config=config,
                permissions=permissions
            )
        except Exception as e:
            raise ValueError(f"Invalid agent configuration: {str(e)}")
        
        # Save agent to database
        created_agent = await self.agent_repository.create(agent)
        
        logger.info(f"Created agent '{name}' with ID {created_agent.id}")
        return created_agent
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None if not found
        """
        return await self.agent_repository.get_by_id(agent_id)
    
    async def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        permissions: Optional[AgentPermissions] = None
    ) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            name: New agent name
            description: New agent description
            config: New agent configuration
            permissions: New agent permissions
            
        Returns:
            Updated agent or None if not found
            
        Raises:
            ValueError: If the configuration is invalid
        """
        # Get agent
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            return None
        
        # Update agent fields
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if config is not None:
            data["config"] = config
        if permissions is not None:
            data["permissions"] = permissions
        
        # Validate configuration if provided
        if config is not None:
            try:
                self.agent_factory.create_agent(
                    agent_type=agent.agent_type,
                    config=config,
                    permissions=permissions or agent.permissions
                )
            except Exception as e:
                raise ValueError(f"Invalid agent configuration: {str(e)}")
        
        # Update agent in database
        updated_agent = await self.agent_repository.update(agent_id, data)
        
        logger.info(f"Updated agent with ID {agent_id}")
        return updated_agent
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if the agent was deleted, False otherwise
        """
        # Delete agent from database
        result = await self.agent_repository.delete(agent_id)
        
        if result:
            logger.info(f"Deleted agent with ID {agent_id}")
            
        return result
    
    async def list_agents(
        self,
        user_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """
        List agents with optional filtering.
        
        Args:
            user_id: Optional user ID to filter by creator.
            agent_type: Optional agent type to filter by.
            offset: Number of records to skip (pagination).
            limit: Maximum number of records to return (pagination).
            
        Returns:
            List of agents matching the criteria.
        """
        try:
            # Define filter conditions
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            if agent_type:
                filters["agent_type"] = agent_type
            
            # Query the database
            agents, _ = await self.agent_repository.list(
                user_id=user_id,
                agent_type=agent_type,
                offset=offset,
                limit=limit
            )
            
            return agents
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            raise
    
    async def execute_agent(
        self,
        agent_id: str,
        input: str,
        user_id: Optional[str] = None
    ) -> Execution:
        """
        Execute an agent.
        
        Args:
            agent_id: Agent ID
            input: Input for the agent
            user_id: ID of the user who started the execution
            
        Returns:
            Execution
            
        Raises:
            ValueError: If the agent is not found
        """
        # Get agent
        agent = await self.agent_repository.get_by_id(agent_id)
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
        execution = await self.execution_repository.create(execution)
        
        # Create callback
        callback = ExecutionCallback(execution.id, self.execution_repository)
        
        try:
            # Create agent instance
            agent_instance = self.agent_factory.create_agent(
                agent_type=agent.agent_type,
                config=agent.config,
                permissions=agent.permissions
            )
            
            # Execute agent
            start_time = time.time()
            
            # Update execution status
            await self.execution_repository.update_status(execution.id, "running")
            
            # Run agent
            result = await agent_instance.run(input=input, callback=callback)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Determine status
            status = "failed" if result.error else "completed"
            
            # Update execution
            await self.execution_repository.update_status(
                execution_id=execution.id,
                status=status,
                output=result.output,
                error=result.error,
                metadata={
                    **(result.metadata or {}),
                    "duration_ms": duration_ms
                }
            )
            
            # Get updated execution
            execution = await self.execution_repository.get_by_id(execution.id)
            
            logger.info(f"Executed agent with ID {agent_id}, execution ID {execution.id}")
            
            return execution
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}", exc_info=True)
            
            # Update execution status
            await self.execution_repository.update_status(
                execution_id=execution.id,
                status="failed",
                error=str(e)
            )
            
            # Get updated execution
            execution = await self.execution_repository.get_by_id(execution.id)
            
            return execution
    
    async def get_execution(self, execution_id: str) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution or None if not found
        """
        return await self.execution_repository.get_by_id(execution_id)
    
    async def list_executions(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[Execution], int]:
        """
        List executions.
        
        Args:
            agent_id: Filter by agent ID
            user_id: Filter by user ID
            status: Filter by status
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Tuple of (list of executions, total count)
        """
        # Get executions from database
        return await self.execution_repository.list(
            agent_id=agent_id,
            user_id=user_id,
            status=status,
            offset=offset,
            limit=limit
        )
    
    async def start_execution(
        self,
        agent_id: str,
        input: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        streaming: bool = False,
    ) -> Execution:
        """
        Start an agent execution.
        
        This method starts the execution and returns the initial execution object.
        The actual execution happens asynchronously.
        
        Args:
            agent_id: Agent ID
            input: User input
            user_id: User ID
            metadata: Optional metadata
            streaming: Whether to enable streaming
            
        Returns:
            Execution object
            
        Raises:
            ValueError: If the agent is not found
        """
        # Get agent
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found")
        
        # Create execution
        execution_id = str(uuid.uuid4())
        execution = Execution(
            id=execution_id,
            agent_id=agent_id,
            user_id=user_id,
            input=input,
            status=ExecutionStatus.PENDING,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        
        # Save execution
        execution = await self.execution_repository.create(execution)
        
        # If streaming, create a queue for this execution
        if streaming:
            self._streaming_executions[execution_id] = asyncio.Queue()
        
        # Start execution in background task
        asyncio.create_task(self._execute_agent(execution_id, user_id, streaming))
        
        logger.info(f"Started execution: {execution_id} for agent: {agent_id}")
        return execution
    
    async def execute_agent(
        self,
        agent_id: str,
        input: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Execution:
        """
        Execute an agent and wait for completion.
        
        Args:
            agent_id: Agent ID
            input: User input
            user_id: User ID
            metadata: Optional metadata
            
        Returns:
            Completed execution
            
        Raises:
            ValueError: If the agent is not found or execution fails
        """
        # Start execution
        execution = await self.start_execution(agent_id, input, user_id, metadata)
        
        # Poll for completion
        max_wait_time = 300  # 5 minutes
        poll_interval = 1  # 1 second
        waited = 0
        
        while waited < max_wait_time:
            # Get updated execution
            updated_execution = await self.execution_repository.get_by_id(execution.id)
            if not updated_execution:
                raise ValueError(f"Execution with ID {execution.id} not found")
            
            # Check if completed or failed
            if updated_execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                return updated_execution
            
            # Wait before polling again
            await asyncio.sleep(poll_interval)
            waited += poll_interval
        
        # Timeout
        await self.cancel_execution(execution.id)
        raise ValueError(f"Execution timed out after {max_wait_time} seconds")
    
    async def _execute_agent(
        self,
        execution_id: str,
        user_id: str,
        streaming: bool = False
    ) -> None:
        """
        Execute an agent.
        
        This method is called as a background task and updates the execution status.
        
        Args:
            execution_id: Execution ID
            user_id: User ID
            streaming: Whether to enable streaming
        """
        try:
            # Get execution
            execution = await self.execution_repository.get_by_id(execution_id)
            if not execution:
                logger.error(f"Execution not found: {execution_id}")
                return
            
            # Get agent
            agent = await self.agent_repository.get_by_id(execution.agent_id)
            if not agent:
                logger.error(f"Agent not found: {execution.agent_id}")
                await self.execution_repository.update_status(
                    execution_id=execution_id, 
                    status=ExecutionStatus.FAILED, 
                    error="Agent not found"
                )
                return
            
            # Update status to running
            started_at = datetime.utcnow()
            execution = await self.execution_repository.update_status(
                execution_id=execution_id, 
                status=ExecutionStatus.RUNNING,
                started_at=started_at
            )
            
            # Send execution start event if streaming
            if streaming:
                await self._send_stream_event(execution_id, {
                    "type": "status",
                    "status": ExecutionStatus.RUNNING.value,
                    "execution_id": execution_id,
                    "started_at": started_at.isoformat(),
                })
            
            # Create agent instance
            agent_instance = self.agent_factory.create_agent(
                agent_type=agent.agent_type,
                config=agent.config,
                permissions=agent.permissions
            )
            
            # Create callback to track steps and commands
            callback = ExecutionCallback(execution_id, self.execution_repository)
            
            # Run agent
            result = await agent_instance.run(
                input=execution.input,
                callback=callback
            )
            
            # Update execution with result
            execution = await self.execution_repository.update_status(
                execution_id=execution_id, 
                status=ExecutionStatus.COMPLETED,
                output=result.output,
                error=result.error,
                metadata={
                    **(result.metadata or {}),
                    "duration_ms": int((datetime.utcnow() - started_at).total_seconds() * 1000)
                }
            )
            
            # Send execution complete event if streaming
            if streaming:
                await self._send_stream_event(execution_id, {
                    "type": "status",
                    "status": ExecutionStatus.COMPLETED.value,
                    "execution_id": execution_id,
                    "output": result.output,
                    "error": result.error,
                    "duration_ms": execution.metadata.get("duration_ms"),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                })
        
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}", exc_info=True)
            
            # Update execution with error
            await self.execution_repository.update_status(
                execution_id=execution_id, 
                status=ExecutionStatus.FAILED,
                error=str(e),
                completed_at=datetime.utcnow()
            )
            
            # Send execution error event if streaming
            if streaming:
                await self._send_stream_event(execution_id, {
                    "type": "error",
                    "error": str(e),
                    "execution_id": execution_id,
                })
        
        finally:
            # Close streaming queue if streaming
            if streaming and execution_id in self._streaming_executions:
                queue = self._streaming_executions.pop(execution_id)
                await queue.put(None)  # Signal end of stream
    
    async def _update_execution_status(
        self,
        execution_id: str,
        status: ExecutionStatus,
        output: Optional[str] = None,
        error: Optional[str] = None,
        tokens_used: Optional[int] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> Execution:
        """
        Update the status of an execution.
        
        Args:
            execution_id: Execution ID
            status: New status
            output: Optional output text
            error: Optional error message
            tokens_used: Optional tokens used
            started_at: Optional start timestamp
            completed_at: Optional completion timestamp
            
        Returns:
            Updated execution
        """
        # Update execution
        execution = await self.execution_repository.update_status(
            execution_id=execution_id,
            status=status.value,
            output=output,
            error=error,
            tokens_used=tokens_used
        )
        
        # If execution not found, create a dummy one to return
        if not execution:
            logger.warning(f"Execution not found when updating status: {execution_id}")
            execution = Execution(
                id=execution_id,
                agent_id="unknown",
                user_id="unknown",
                input="",
                status=status,
                output=output,
                error=error,
                tokens_used=tokens_used,
                started_at=started_at,
                completed_at=completed_at,
                created_at=datetime.utcnow()
            )
        
        return execution
    
    async def _send_stream_event(
        self,
        execution_id: str,
        event: Dict[str, Any]
    ) -> None:
        """
        Send an event to the stream.
        
        Args:
            execution_id: Execution ID
            event: Event data
        """
        queue = self._streaming_executions.get(execution_id)
        if queue:
            await queue.put(event)
    
    async def cancel_execution(self, execution_id: str) -> Optional[Execution]:
        """
        Cancel an execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Updated execution if found, None otherwise
        """
        # Get execution first to validate it exists
        execution = await self.execution_repository.get_by_id(execution_id)
        if not execution:
            return None
        
        # Only pending or running executions can be canceled
        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            raise ValueError(f"Cannot cancel execution with status: {execution.status}")
        
        # Update execution status
        updated_execution = await self.execution_repository.update_status(
            execution_id=execution_id,
            status=ExecutionStatus.CANCELED.value,
            completed_at=datetime.utcnow()
        )
        
        # Send execution canceled event if streaming
        if execution_id in self._streaming_executions:
            await self._send_stream_event(execution_id, {
                "type": "status",
                "status": ExecutionStatus.CANCELED.value,
                "execution_id": execution_id,
            })
        
        if updated_execution:
            logger.info(f"Canceled execution: {execution_id}")
        
        return updated_execution 