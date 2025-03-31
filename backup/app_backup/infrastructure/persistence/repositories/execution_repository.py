"""
Execution repository implementation.

This module provides the SQLAlchemy implementation of the execution repository.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, cast

from sqlalchemy import select, delete, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories.execution_repository import ExecutionRepository
from app.core.entities.execution import Execution, ExecutionStep, Command, ExecutionStatus, CommandStatus, StepType
from app.infrastructure.persistence.models import ExecutionModel, ExecutionStepModel, CommandModel


class SQLExecutionRepository(ExecutionRepository):
    """
    SQLAlchemy implementation of the execution repository.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, execution: Execution) -> Execution:
        """
        Create a new execution.
        
        Args:
            execution: The execution to create
            
        Returns:
            The created execution with ID and timestamps
        """
        # Convert entity to model
        execution_model = ExecutionModel(
            id=uuid.UUID(execution.id) if isinstance(execution.id, str) else execution.id,
            agent_id=uuid.UUID(execution.agent_id) if isinstance(execution.agent_id, str) else execution.agent_id,
            input=execution.input,
            status=execution.status.value if isinstance(execution.status, ExecutionStatus) else execution.status,
            output=execution.output,
            error=execution.error,
            tokens_used=execution.tokens_used,
            execution_metadata=execution.metadata or {},
            user_id=execution.user_id,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            created_at=execution.created_at or datetime.utcnow()
        )
        
        # Add to session and flush to get ID
        self.session.add(execution_model)
        await self.session.commit()
        await self.session.refresh(execution_model)
        
        # Convert back to entity
        result = self._model_to_entity(execution_model)
        
        # Add steps and commands if any
        if execution.steps:
            for step in execution.steps:
                step.execution_id = str(execution_model.id)
                await self.add_step(step)
                
        if execution.commands:
            for command in execution.commands:
                command.execution_id = str(execution_model.id)
                await self.add_command(command)
        
        return result
    
    async def get_by_id(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: The ID of the execution to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The execution if found, None otherwise
        """
        try:
            # Create query with eager loading of steps and commands
            query = (
                select(ExecutionModel)
                .options(
                    selectinload(ExecutionModel.steps),
                    selectinload(ExecutionModel.commands)
                )
                .where(ExecutionModel.id == uuid.UUID(execution_id))
            )
            
            # Add user filter if provided
            if user_id:
                query = query.where(ExecutionModel.user_id == user_id)
            
            # Execute query
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            
            # Convert to entity if found
            if model:
                return self._model_to_entity(model)
            
            return None
        except Exception as e:
            return None
    
    async def update_status(
        self, 
        execution_id: str, 
        status: str, 
        output: Optional[str] = None,
        error: Optional[str] = None,
        tokens_used: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Execution]:
        """
        Update the status of an execution.
        
        Args:
            execution_id: The ID of the execution to update
            status: The new status
            output: Optional output to set
            error: Optional error message to set
            tokens_used: Optional number of tokens used
            user_id: Optional user ID for access control
            
        Returns:
            The updated execution if found, None otherwise
        """
        try:
            # Start building update values
            update_values = {"status": status}
            
            # Add completed_at if status is terminal
            if status in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value, ExecutionStatus.CANCELED.value]:
                update_values["completed_at"] = datetime.utcnow()
                
            # Add started_at if status is running and not already set
            if status == ExecutionStatus.RUNNING.value:
                # Check if started_at is already set
                check_query = select(ExecutionModel.started_at).where(ExecutionModel.id == uuid.UUID(execution_id))
                check_result = await self.session.execute(check_query)
                started_at = check_result.scalar_one_or_none()
                
                if not started_at:
                    update_values["started_at"] = datetime.utcnow()
            
            # Add optional values if provided
            if output is not None:
                update_values["output"] = output
                
            if error is not None:
                update_values["error"] = error
                
            if tokens_used is not None:
                update_values["tokens_used"] = tokens_used
            
            # Create query conditions
            conditions = [ExecutionModel.id == uuid.UUID(execution_id)]
            if user_id:
                conditions.append(ExecutionModel.user_id == user_id)
                
            # Execute update
            query = (
                update(ExecutionModel)
                .where(and_(*conditions))
                .values(**update_values)
                .returning(ExecutionModel)
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            
            # If model is None, the execution wasn't found or user doesn't have access
            if not model:
                return None
                
            # Commit changes
            await self.session.commit()
                
            # Get the updated execution
            return await self.get_by_id(execution_id, user_id)
        except Exception as e:
            return None
    
    async def add_step(self, step: ExecutionStep) -> ExecutionStep:
        """
        Add a step to an execution.
        
        Args:
            step: The step to add
            
        Returns:
            The created step with ID and timestamp
        """
        try:
            # Convert entity to model
            model = ExecutionStepModel(
                id=uuid.uuid4() if not step.id else uuid.UUID(step.id),
                execution_id=uuid.UUID(step.execution_id),
                type=step.type.value if isinstance(step.type, StepType) else step.type,
                content=step.content,
                timestamp=step.timestamp or datetime.utcnow(),
                step_metadata=step.metadata or {},
            )
            
            # Add to session and commit
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            
            # Convert back to entity
            return ExecutionStep(
                id=str(model.id),
                execution_id=str(model.execution_id),
                type=StepType(model.type) if model.type in [e.value for e in StepType] else model.type,
                content=model.content,
                timestamp=model.timestamp,
                metadata=model.step_metadata or {},
            )
        except Exception as e:
            raise
    
    async def add_command(self, command: Command) -> Command:
        """
        Add a command to an execution.
        
        Args:
            command: The command to add
            
        Returns:
            The created command with ID and timestamp
        """
        try:
            # Convert entity to model
            model = CommandModel(
                id=uuid.uuid4() if not command.id else uuid.UUID(command.id),
                execution_id=uuid.UUID(command.execution_id),
                command=command.command,
                status=command.status.value if isinstance(command.status, CommandStatus) else command.status,
                exit_code=command.exit_code,
                stdout=command.stdout,
                stderr=command.stderr,
                duration_ms=command.duration_ms,
                timestamp=command.timestamp or datetime.utcnow(),
                command_metadata=command.metadata or {},
            )
            
            # Add to session and commit
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            
            # Convert back to entity
            return Command(
                id=str(model.id),
                execution_id=str(model.execution_id),
                command=model.command,
                status=CommandStatus(model.status) if model.status in [e.value for e in CommandStatus] else model.status,
                exit_code=model.exit_code,
                stdout=model.stdout,
                stderr=model.stderr,
                duration_ms=model.duration_ms,
                timestamp=model.timestamp,
                metadata=model.command_metadata or {},
            )
        except Exception as e:
            raise
    
    async def list(
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
        try:
            # Create query with eager loading
            query = (
                select(ExecutionModel)
                .options(
                    selectinload(ExecutionModel.steps),
                    selectinload(ExecutionModel.commands)
                )
            )
            
            # Add filters if provided
            if user_id:
                query = query.where(ExecutionModel.user_id == user_id)
                
            if agent_id:
                query = query.where(ExecutionModel.agent_id == uuid.UUID(agent_id))
                
            if status:
                query = query.where(ExecutionModel.status == status)
                
            # Add pagination
            query = query.offset(skip).limit(limit)
            
            # Add ordering
            query = query.order_by(ExecutionModel.created_at.desc())
            
            # Execute query
            result = await self.session.execute(query)
            models = result.scalars().all()
            
            # Convert to entities
            return [self._model_to_entity(model) for model in models]
        except Exception as e:
            return []
    
    async def count(
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
        try:
            # Create query
            query = select(func.count()).select_from(ExecutionModel)
            
            # Add filters if provided
            if user_id:
                query = query.where(ExecutionModel.user_id == user_id)
                
            if agent_id:
                query = query.where(ExecutionModel.agent_id == uuid.UUID(agent_id))
                
            if status:
                query = query.where(ExecutionModel.status == status)
                
            # Execute query
            result = await self.session.execute(query)
            count = result.scalar_one()
            
            return cast(int, count)
        except Exception as e:
            return 0
    
    def _model_to_entity(self, model: ExecutionModel) -> Execution:
        """
        Convert a database model to an entity.
        
        Args:
            model: The database model
            
        Returns:
            The corresponding entity
        """
        # Convert steps
        steps = []
        if hasattr(model, "steps") and model.steps:
            for step_model in model.steps:
                steps.append(ExecutionStep(
                    id=str(step_model.id),
                    execution_id=str(step_model.execution_id),
                    type=StepType(step_model.type) if step_model.type in [e.value for e in StepType] else step_model.type,
                    content=step_model.content,
                    timestamp=step_model.timestamp,
                    metadata=step_model.step_metadata or {},
                ))
        
        # Convert commands
        commands = []
        if hasattr(model, "commands") and model.commands:
            for cmd_model in model.commands:
                commands.append(Command(
                    id=str(cmd_model.id),
                    execution_id=str(cmd_model.execution_id),
                    command=cmd_model.command,
                    status=CommandStatus(cmd_model.status) if cmd_model.status in [e.value for e in CommandStatus] else cmd_model.status,
                    exit_code=cmd_model.exit_code,
                    stdout=cmd_model.stdout,
                    stderr=cmd_model.stderr,
                    duration_ms=cmd_model.duration_ms,
                    timestamp=cmd_model.timestamp,
                    metadata=cmd_model.command_metadata or {},
                ))
        
        # Create entity
        return Execution(
            id=str(model.id),
            agent_id=str(model.agent_id),
            input=model.input,
            status=ExecutionStatus(model.status) if model.status in [e.value for e in ExecutionStatus] else model.status,
            output=model.output,
            error=model.error,
            tokens_used=model.tokens_used,
            metadata=model.execution_metadata or {},
            steps=steps,
            commands=commands,
            user_id=model.user_id,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at
        ) 