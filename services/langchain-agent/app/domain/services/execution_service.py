"""
Execution service for running and managing LangChain agent executions.

This service contains the core business logic for agent execution.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import asyncio
import time
import json

from app.domain.entities import (
    Agent, 
    Execution, 
    ExecutionStatus, 
    ExecutionStep,
    Command
)
from app.domain.repositories import ExecutionRepository, AgentRepository


class ExecutionService:
    """
    Service for managing LangChain agent executions.
    """
    
    def __init__(
        self, 
        execution_repository: ExecutionRepository,
        agent_repository: AgentRepository,
        command_client: Any,  # Will be defined in infrastructure layer
        redis_client: Any,    # Will be defined in infrastructure layer
    ):
        """
        Initialize the execution service.
        
        Args:
            execution_repository: Repository for execution persistence.
            agent_repository: Repository for agent retrieval.
            command_client: Client for executing commands.
            redis_client: Client for real-time updates.
        """
        self.execution_repository = execution_repository
        self.agent_repository = agent_repository
        self.command_client = command_client
        self.redis_client = redis_client
    
    async def start_execution(
        self, 
        agent_id: str, 
        user_id: str, 
        input_text: str,
        metadata: Dict[str, Any] = None
    ) -> Execution:
        """
        Start a new agent execution.
        
        Args:
            agent_id: ID of the agent to execute.
            user_id: ID of the user starting the execution.
            input_text: Input text for the agent.
            metadata: Additional metadata for the execution.
            
        Returns:
            The created execution record.
            
        Raises:
            ValueError: If the agent doesn't exist.
        """
        # Get the agent
        agent = await self.agent_repository.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found")
        
        # Create initial execution record
        execution = Execution(
            agent_id=agent_id,
            user_id=user_id,
            status=ExecutionStatus.PENDING,
            input=input_text,
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Persist execution
        execution = await self.execution_repository.create(execution)
        
        # Start execution in background
        asyncio.create_task(self._execute_agent(execution, agent))
        
        return execution
    
    async def _execute_agent(self, execution: Execution, agent: Agent) -> None:
        """
        Execute an agent in the background.
        
        Args:
            execution: The execution record.
            agent: The agent to execute.
        """
        try:
            # Update status to running
            start_time = time.time()
            execution = await self.execution_repository.update_status(
                execution_id=execution.id,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow()
            )
            
            # Publish status update
            await self._publish_execution_update(execution)
            
            # Initialize LangChain agent (implementation will be added later)
            # This is a placeholder for the actual agent execution logic
            
            # Add thinking step
            thinking_step = ExecutionStep(
                type="thought",
                content=f"I need to process the request: '{execution.input}'"
            )
            await self.execution_repository.add_step(execution.id, thinking_step)
            await self._publish_step_update(execution.id, thinking_step)
            
            # Execute a test command (for placeholder purposes)
            command = Command(
                command="echo 'Hello, this is a test command'",
            )
            await self.execution_repository.add_command(execution.id, command)
            await self._publish_command_update(execution.id, command)
            
            # Call command execution service
            command_result = await self.command_client.execute_command(
                command=command.command,
                timeout=agent.permissions.max_execution_time,
                allowed_paths=agent.permissions.allowed_paths,
                memory_limit=agent.permissions.memory_quota,
                network_access=agent.permissions.network_access
            )
            
            # Update command with results
            await self.execution_repository.update_command(
                execution_id=execution.id,
                command_id=command.id,
                status="completed",
                exit_code=command_result.get("exit_code"),
                stdout=command_result.get("stdout"),
                stderr=command_result.get("stderr"),
                duration_ms=command_result.get("duration_ms")
            )
            
            # Add observation step
            observation_step = ExecutionStep(
                type="observation",
                content=command_result.get("stdout", "")
            )
            await self.execution_repository.add_step(execution.id, observation_step)
            await self._publish_step_update(execution.id, observation_step)
            
            # Add final output step
            output = f"Task completed. The command returned: {command_result.get('stdout', '')}"
            
            # Update status to completed
            execution_time = time.time() - start_time
            tokens_used = len(execution.input) // 4  # Simplified token counting
            
            await self.execution_repository.update_status(
                execution_id=execution.id,
                status=ExecutionStatus.COMPLETED,
                output=output,
                tokens_used=tokens_used,
                completed_at=datetime.utcnow()
            )
            
            # Get the updated execution
            execution = await self.execution_repository.get_by_id(execution.id)
            
            # Publish final update
            await self._publish_execution_update(execution)
            
        except Exception as e:
            # Handle any exceptions during execution
            error_message = f"Execution failed: {str(e)}"
            
            # Update status to failed
            await self.execution_repository.update_status(
                execution_id=execution.id,
                status=ExecutionStatus.FAILED,
                error=error_message,
                completed_at=datetime.utcnow()
            )
            
            # Get the updated execution
            execution = await self.execution_repository.get_by_id(execution.id)
            
            # Publish error update
            await self._publish_execution_update(execution)
    
    async def _publish_execution_update(self, execution: Execution) -> None:
        """
        Publish execution update to Redis.
        
        Args:
            execution: The execution to publish.
        """
        channel = f"execution:{execution.id}:status"
        message = {
            "type": "status_update",
            "execution_id": execution.id,
            "status": execution.status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add additional fields based on status
        if execution.status == ExecutionStatus.COMPLETED:
            message["output"] = execution.output
            message["tokens_used"] = execution.tokens_used
        elif execution.status == ExecutionStatus.FAILED:
            message["error"] = execution.error
        
        await self.redis_client.publish(channel, json.dumps(message))
    
    async def _publish_step_update(self, execution_id: str, step: ExecutionStep) -> None:
        """
        Publish step update to Redis.
        
        Args:
            execution_id: ID of the execution.
            step: The step to publish.
        """
        channel = f"execution:{execution_id}:steps"
        message = {
            "type": "step_update",
            "execution_id": execution_id,
            "step_id": step.id,
            "step_type": step.type,
            "content": step.content,
            "timestamp": step.timestamp.isoformat()
        }
        
        await self.redis_client.publish(channel, json.dumps(message))
    
    async def _publish_command_update(self, execution_id: str, command: Command) -> None:
        """
        Publish command update to Redis.
        
        Args:
            execution_id: ID of the execution.
            command: The command to publish.
        """
        channel = f"execution:{execution_id}:commands"
        message = {
            "type": "command_update",
            "execution_id": execution_id,
            "command_id": command.id,
            "command": command.command,
            "status": command.status,
            "timestamp": command.timestamp.isoformat()
        }
        
        # Add result fields if available
        if command.exit_code is not None:
            message["exit_code"] = command.exit_code
            message["stdout"] = command.stdout
            message["stderr"] = command.stderr
            message["duration_ms"] = command.duration_ms
        
        await self.redis_client.publish(channel, json.dumps(message))
    
    async def get_execution(self, execution_id: str) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: ID of the execution to retrieve.
            
        Returns:
            The execution if found, None otherwise.
        """
        return await self.execution_repository.get_by_id(execution_id)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an ongoing execution.
        
        Args:
            execution_id: ID of the execution to cancel.
            
        Returns:
            True if cancellation was successful, False otherwise.
        """
        # Get the execution
        execution = await self.execution_repository.get_by_id(execution_id)
        if not execution:
            return False
            
        # Can only cancel pending or running executions
        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            return False
            
        # Update status to cancelled
        await self.execution_repository.update_status(
            execution_id=execution_id,
            status=ExecutionStatus.CANCELLED,
            completed_at=datetime.utcnow()
        )
        
        # Get the updated execution
        execution = await self.execution_repository.get_by_id(execution_id)
        
        # Publish cancellation update
        await self._publish_execution_update(execution)
        
        return True
    
    async def list_executions(
        self, 
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Execution]:
        """
        List executions with optional filtering.
        
        Args:
            user_id: Optional user ID to filter by.
            agent_id: Optional agent ID to filter by.
            status: Optional status to filter by.
            from_date: Optional start date for filtering.
            to_date: Optional end date for filtering.
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return (pagination).
            
        Returns:
            List of executions matching the criteria.
        """
        return await self.execution_repository.list(
            user_id=user_id,
            agent_id=agent_id,
            status=status,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit
        )
    
    async def count_executions(
        self, 
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> int:
        """
        Count executions with optional filtering.
        
        Args:
            user_id: Optional user ID to filter by.
            agent_id: Optional agent ID to filter by.
            status: Optional status to filter by.
            from_date: Optional start date for filtering.
            to_date: Optional end date for filtering.
            
        Returns:
            Count of executions matching the criteria.
        """
        return await self.execution_repository.count(
            user_id=user_id,
            agent_id=agent_id,
            status=status,
            from_date=from_date,
            to_date=to_date
        )
