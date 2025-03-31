"""
Agent repository implementation.

This module provides the SQLAlchemy implementation of the agent repository.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, cast

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.agent import Agent, AgentType, AgentConfiguration, AgentPermissions
from app.domain.repositories.agent_repository import AgentRepository
from app.infrastructure.persistence.models import AgentModel


class SQLAgentRepository(AgentRepository):
    """
    SQLAlchemy implementation of the agent repository.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: The agent to create
            
        Returns:
            The created agent with ID and timestamps
        """
        agent_model = AgentModel(
            id=uuid.UUID(agent.id) if isinstance(agent.id, str) else agent.id,
            name=agent.name,
            user_id=agent.user_id,
            agent_type=agent.agent_type.value,
            description=agent.description,
            config=agent.configuration.dict() if agent.configuration else {},
            permissions=agent.permissions.dict() if agent.permissions else {},
            agent_metadata=agent.metadata
        )
        
        self.session.add(agent_model)
        await self.session.commit()
        await self.session.refresh(agent_model)
        
        return self._model_to_entity(agent_model)
    
    async def get_by_id(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The agent if found, None otherwise
        """
        query = select(AgentModel).where(AgentModel.id == uuid.UUID(agent_id))
        
        if user_id:
            query = query.where(AgentModel.user_id == user_id)
        
        result = await self.session.execute(query)
        agent_model = result.scalars().first()
        
        if not agent_model:
            return None
        
        return self._model_to_entity(agent_model)
    
    async def update(
        self, 
        agent_id: str, 
        user_id: Optional[str] = None, 
        **kwargs
    ) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: The ID of the agent to update
            user_id: Optional user ID for access control
            **kwargs: Fields to update
            
        Returns:
            The updated agent if found, None otherwise
        """
        query = select(AgentModel).where(AgentModel.id == uuid.UUID(agent_id))
        
        if user_id:
            query = query.where(AgentModel.user_id == user_id)
        
        result = await self.session.execute(query)
        agent_model = result.scalars().first()
        
        if not agent_model:
            return None
        
        # Process configuration if provided
        if 'configuration' in kwargs:
            kwargs['config'] = kwargs.pop('configuration').dict() if kwargs['configuration'] else {}
        
        # Process permissions if provided
        if 'permissions' in kwargs:
            kwargs['permissions'] = kwargs.pop('permissions').dict() if kwargs['permissions'] else {}
        
        # Process metadata if provided
        if 'metadata' in kwargs:
            kwargs['agent_metadata'] = kwargs.pop('metadata')
        
        # Update the model
        for key, value in kwargs.items():
            if hasattr(agent_model, key):
                setattr(agent_model, key, value)
        
        # Update timestamp
        agent_model.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(agent_model)
        
        return self._model_to_entity(agent_model)
    
    async def delete(self, agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: The ID of the agent to delete
            user_id: Optional user ID for access control
            
        Returns:
            True if deleted, False otherwise
        """
        stmt = delete(AgentModel).where(AgentModel.id == uuid.UUID(agent_id))
        
        if user_id:
            stmt = stmt.where(AgentModel.user_id == user_id)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def list(
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
        query = select(AgentModel).order_by(AgentModel.created_at.desc())
        
        if user_id:
            query = query.where(AgentModel.user_id == user_id)
        
        if agent_type:
            query = query.where(AgentModel.agent_type == agent_type.value)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        agent_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in agent_models]
    
    async def count(
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
        query = select(func.count()).select_from(AgentModel)
        
        if user_id:
            query = query.where(AgentModel.user_id == user_id)
        
        if agent_type:
            query = query.where(AgentModel.agent_type == agent_type.value)
        
        result = await self.session.execute(query)
        count = result.scalar_one()
        
        return cast(int, count)
    
    def _model_to_entity(self, model: AgentModel) -> Agent:
        """
        Convert a database model to a domain entity.
        
        Args:
            model: Database model
            
        Returns:
            Domain entity
        """
        return Agent(
            id=str(model.id),
            name=model.name,
            user_id=model.user_id,
            agent_type=AgentType(model.agent_type),
            description=model.description,
            configuration=AgentConfiguration(**model.config) if model.config else None,
            permissions=AgentPermissions(**model.permissions) if model.permissions else None,
            metadata=model.agent_metadata or {},
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 