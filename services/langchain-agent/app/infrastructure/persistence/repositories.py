"""
Repository implementations using SQLAlchemy for database operations.

These classes implement the domain repository interfaces using SQLAlchemy.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json
import logging

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.repositories import AgentRepository, ExecutionRepository
from app.domain.entities import (
    Agent, AgentConfiguration, AgentPermissions,
    Execution, ExecutionStatus, ExecutionStep, Command
)
from app.infrastructure.persistence.models import (
    AgentModel, ExecutionModel, ExecutionStepModel, CommandModel
)

# Configure logging
logger = logging.getLogger(__name__)


def agent_model_to_entity(model: AgentModel) -> Agent:
    """Convert an AgentModel to an Agent entity."""
    return Agent(
        id=model.id,
        name=model.name,
        description=model.description,
        type=model.type,
        configuration=AgentConfiguration(**model.configuration),
        permissions=AgentPermissions(**model.permissions),
        metadata=model.metadata,
        created_at=model.created_at,
        updated_at=model.updated_at,
        created_by=model.created_by
    )


def execution_model_to_entity(model: ExecutionModel) -> Execution:
    """Convert an ExecutionModel to an Execution entity."""
    # Convert steps
    steps = [
        ExecutionStep(
            id=step.id,
            timestamp=step.timestamp,
            type=step.type,
            content=step.content,
            metadata=step.metadata
        )
        for step in model.steps
    ]
    
    # Convert commands
    commands = [
        Command(
            id=command.id,
            command=command.command,
            timestamp=command.timestamp,
            status=command.status,
            exit_code=command.exit_code,
            stdout=command.stdout,
            stderr=command.stderr,
            duration_ms=command.duration_ms,
            metadata=command.metadata
        )
        for command in model.commands
    ]
    
    return Execution(
        id=model.id,
        agent_id=model.agent_id,
        user_id=model.user_id,
        status=ExecutionStatus(model.status),
        input=model.input,
        output=model.output,
        error=model.error,
        steps=steps,
        commands=commands,
        tokens_used=model.tokens_used,
        started_at=model.started_at,
        completed_at=model.completed_at,
        created_at=model.created_at,
        metadata=model.metadata
    )


class SQLAgentRepository(AgentRepository):
    """
    SQL implementation of agent repository.
    
    This repository uses SQLAlchemy to persist agents to a database.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize SQL agent repository.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: Agent to create
            
        Returns:
            Created agent
        """
        try:
            # Convert entity to model
            agent_model = AgentModel(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                agent_type=agent.agent_type,
                config=agent.config,
                permissions=agent.permissions.to_dict(),
                user_id=agent.user_id,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
            
            # Add to session and commit
            self.session.add(agent_model)
            await self.session.commit()
            await self.session.refresh(agent_model)
            
            # Convert back to entity
            return self._model_to_entity(agent_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            raise
    
    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None if not found
        """
        try:
            # Query the database
            query = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(query)
            agent_model = result.scalar_one_or_none()
            
            # Convert to entity if found
            if agent_model:
                return self._model_to_entity(agent_model)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting agent by ID: {str(e)}", exc_info=True)
            raise
    
    async def update(self, agent_id: str, data: Dict[str, Any]) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            data: Data to update
            
        Returns:
            Updated agent or None if not found
        """
        try:
            # Query the database
            query = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(query)
            agent_model = result.scalar_one_or_none()
            
            # Return None if not found
            if not agent_model:
                return None
            
            # Update fields
            if "name" in data:
                agent_model.name = data["name"]
            if "description" in data:
                agent_model.description = data["description"]
            if "config" in data:
                agent_model.config = data["config"]
            if "permissions" in data:
                agent_model.permissions = data["permissions"].to_dict() if isinstance(data["permissions"], AgentPermissions) else data["permissions"]
            
            # Update timestamp
            agent_model.updated_at = datetime.utcnow()
            
            # Commit changes
            await self.session.commit()
            await self.session.refresh(agent_model)
            
            # Convert back to entity
            return self._model_to_entity(agent_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating agent: {str(e)}", exc_info=True)
            raise
    
    async def delete(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            # Query the database
            query = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(query)
            agent_model = result.scalar_one_or_none()
            
            # Return False if not found
            if not agent_model:
                return False
            
            # Delete the agent
            await self.session.delete(agent_model)
            await self.session.commit()
            
            return True
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting agent: {str(e)}", exc_info=True)
            raise
    
    async def list(
        self,
        user_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[Agent], int]:
        """
        List agents.
        
        Args:
            user_id: Filter by user ID
            agent_type: Filter by agent type
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Tuple of (list of agents, total count)
        """
        try:
            # Build query
            filters = []
            if user_id:
                filters.append(AgentModel.user_id == user_id)
            if agent_type:
                filters.append(AgentModel.agent_type == agent_type)
            
            # Create query for data
            query = select(AgentModel)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(AgentModel.created_at.desc()).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            agent_models = result.scalars().all()
            
            # Convert to entities
            agents = [self._model_to_entity(model) for model in agent_models]
            
            # Get total count
            count = await self.count(user_id, agent_type)
            
            return agents, count
        
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}", exc_info=True)
            raise
    
    async def count(
        self,
        user_id: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> int:
        """
        Count agents.
        
        Args:
            user_id: Filter by user ID
            agent_type: Filter by agent type
            
        Returns:
            Number of agents
        """
        try:
            # Build query
            filters = []
            if user_id:
                filters.append(AgentModel.user_id == user_id)
            if agent_type:
                filters.append(AgentModel.agent_type == agent_type)
            
            # Create count query
            query = select(func.count()).select_from(AgentModel)
            if filters:
                query = query.where(and_(*filters))
            
            # Execute query
            result = await self.session.execute(query)
            count = result.scalar_one()
            
            return count
        
        except Exception as e:
            logger.error(f"Error counting agents: {str(e)}", exc_info=True)
            raise
    
    def _model_to_entity(self, model: AgentModel) -> Agent:
        """
        Convert agent model to entity.
        
        Args:
            model: Agent model
            
        Returns:
            Agent entity
        """
        permissions = AgentPermissions.from_dict(model.permissions)
        
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            agent_type=model.agent_type,
            config=model.config,
            permissions=permissions,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class SQLExecutionRepository(ExecutionRepository):
    """
    SQL implementation of execution repository.
    
    This repository uses SQLAlchemy to persist executions to a database.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize SQL execution repository.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    async def create(self, execution: Execution) -> Execution:
        """
        Create a new execution.
        
        Args:
            execution: Execution to create
            
        Returns:
            Created execution
        """
        try:
            # Convert entity to model
            execution_model = ExecutionModel(
                id=execution.id,
                agent_id=execution.agent_id,
                input=execution.input,
                status=execution.status,
                output=execution.output,
                error=execution.error,
                metadata=execution.metadata,
                user_id=execution.user_id,
                created_at=execution.created_at,
                updated_at=execution.updated_at
            )
            
            # Add to session and commit
            self.session.add(execution_model)
            await self.session.commit()
            await self.session.refresh(execution_model)
            
            # Convert back to entity
            return self._model_to_entity(execution_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating execution: {str(e)}", exc_info=True)
            raise
    
    async def get_by_id(self, execution_id: str) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution or None if not found
        """
        try:
            # Query the database
            query = (
                select(ExecutionModel)
                .where(ExecutionModel.id == execution_id)
                .options(
                    selectinload(ExecutionModel.steps),
                    selectinload(ExecutionModel.commands)
                )
            )
            result = await self.session.execute(query)
            execution_model = result.scalar_one_or_none()
            
            # Convert to entity if found
            if execution_model:
                return self._model_to_entity(execution_model)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting execution by ID: {str(e)}", exc_info=True)
            raise
    
    async def update_status(
        self,
        execution_id: str,
        status: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Execution]:
        """
        Update execution status.
        
        Args:
            execution_id: Execution ID
            status: New status
            output: Optional output
            error: Optional error
            metadata: Optional metadata
            
        Returns:
            Updated execution or None if not found
        """
        try:
            # Query the database
            query = (
                select(ExecutionModel)
                .where(ExecutionModel.id == execution_id)
                .options(
                    selectinload(ExecutionModel.steps),
                    selectinload(ExecutionModel.commands)
                )
            )
            result = await self.session.execute(query)
            execution_model = result.scalar_one_or_none()
            
            # Return None if not found
            if not execution_model:
                return None
            
            # Update fields
            execution_model.status = status
            if output is not None:
                execution_model.output = output
            if error is not None:
                execution_model.error = error
            if metadata is not None:
                # Merge metadata
                if execution_model.metadata:
                    execution_model.metadata.update(metadata)
                else:
                    execution_model.metadata = metadata
            
            # Update timestamp
            execution_model.updated_at = datetime.utcnow()
            
            # Commit changes
            await self.session.commit()
            await self.session.refresh(execution_model)
            
            # Convert back to entity
            return self._model_to_entity(execution_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating execution status: {str(e)}", exc_info=True)
            raise
    
    async def add_step(self, step: ExecutionStep) -> ExecutionStep:
        """
        Add a step to an execution.
        
        Args:
            step: Step to add
            
        Returns:
            Added step
        """
        try:
            # Convert entity to model
            step_model = ExecutionStepModel(
                id=step.id,
                execution_id=step.execution_id,
                step_type=step.step_type,
                content=step.content,
                created_at=step.created_at
            )
            
            # Add to session and commit
            self.session.add(step_model)
            await self.session.commit()
            await self.session.refresh(step_model)
            
            # Convert back to entity
            return self._step_model_to_entity(step_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding execution step: {str(e)}", exc_info=True)
            raise
    
    async def add_command(self, command: Command) -> Command:
        """
        Add a command to an execution.
        
        Args:
            command: Command to add
            
        Returns:
            Added command
        """
        try:
            # Convert entity to model
            command_model = CommandModel(
                id=command.id,
                execution_id=command.execution_id,
                command=command.command,
                status=command.status,
                exit_code=command.exit_code,
                stdout=command.stdout,
                stderr=command.stderr,
                duration_ms=command.duration_ms,
                created_at=command.created_at,
                updated_at=command.updated_at
            )
            
            # Add to session and commit
            self.session.add(command_model)
            await self.session.commit()
            await self.session.refresh(command_model)
            
            # Convert back to entity
            return self._command_model_to_entity(command_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding command: {str(e)}", exc_info=True)
            raise
    
    async def list(
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
        try:
            # Build query
            filters = []
            if agent_id:
                filters.append(ExecutionModel.agent_id == agent_id)
            if user_id:
                filters.append(ExecutionModel.user_id == user_id)
            if status:
                filters.append(ExecutionModel.status == status)
            
            # Create query for data
            query = (
                select(ExecutionModel)
                .options(
                    selectinload(ExecutionModel.steps),
                    selectinload(ExecutionModel.commands)
                )
            )
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(ExecutionModel.created_at.desc()).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            execution_models = result.scalars().all()
            
            # Convert to entities
            executions = [self._model_to_entity(model) for model in execution_models]
            
            # Get total count
            count = await self.count(agent_id, user_id, status)
            
            return executions, count
        
        except Exception as e:
            logger.error(f"Error listing executions: {str(e)}", exc_info=True)
            raise
    
    async def count(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Count executions.
        
        Args:
            agent_id: Filter by agent ID
            user_id: Filter by user ID
            status: Filter by status
            
        Returns:
            Number of executions
        """
        try:
            # Build query
            filters = []
            if agent_id:
                filters.append(ExecutionModel.agent_id == agent_id)
            if user_id:
                filters.append(ExecutionModel.user_id == user_id)
            if status:
                filters.append(ExecutionModel.status == status)
            
            # Create count query
            query = select(func.count()).select_from(ExecutionModel)
            if filters:
                query = query.where(and_(*filters))
            
            # Execute query
            result = await self.session.execute(query)
            count = result.scalar_one()
            
            return count
        
        except Exception as e:
            logger.error(f"Error counting executions: {str(e)}", exc_info=True)
            raise
    
    def _model_to_entity(self, model: ExecutionModel) -> Execution:
        """
        Convert execution model to entity.
        
        Args:
            model: Execution model
            
        Returns:
            Execution entity
        """
        steps = [self._step_model_to_entity(step) for step in model.steps]
        commands = [self._command_model_to_entity(command) for command in model.commands]
        
        return Execution(
            id=model.id,
            agent_id=model.agent_id,
            input=model.input,
            status=model.status,
            output=model.output,
            error=model.error,
            metadata=model.metadata,
            steps=steps,
            commands=commands,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _step_model_to_entity(self, model: ExecutionStepModel) -> ExecutionStep:
        """
        Convert execution step model to entity.
        
        Args:
            model: Execution step model
            
        Returns:
            Execution step entity
        """
        return ExecutionStep(
            id=model.id,
            execution_id=model.execution_id,
            step_type=model.step_type,
            content=model.content,
            created_at=model.created_at
        )
    
    def _command_model_to_entity(self, model: CommandModel) -> Command:
        """
        Convert command model to entity.
        
        Args:
            model: Command model
            
        Returns:
            Command entity
        """
        return Command(
            id=model.id,
            execution_id=model.execution_id,
            command=model.command,
            status=model.status,
            exit_code=model.exit_code,
            stdout=model.stdout,
            stderr=model.stderr,
            duration_ms=model.duration_ms,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
