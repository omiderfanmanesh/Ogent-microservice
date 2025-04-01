"""
Fixed repository implementation for the SQLAgentRepository.

This module fixes the repository to use 'configuration' instead of 'config'.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import AgentRepository
from app.domain.entities import Agent, AgentPermissions
from app.infrastructure.persistence.models import AgentModel

# Configure logging
logger = logging.getLogger(__name__)


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
            # Extract configuration from agent - supporting both attribute names
            config_data = {}
            if hasattr(agent, 'configuration'):
                if hasattr(agent.configuration, 'to_dict'):
                    config_data = agent.configuration.to_dict()
                elif hasattr(agent.configuration, 'dict'):
                    config_data = agent.configuration.dict()
                else:
                    config_data = agent.configuration
            elif hasattr(agent, 'config'):
                if hasattr(agent.config, 'to_dict'):
                    config_data = agent.config.to_dict()
                elif hasattr(agent.config, 'dict'):
                    config_data = agent.config.dict()
                else:
                    config_data = agent.config
            
            # Extract permissions
            permissions_data = {}
            if hasattr(agent.permissions, 'to_dict'):
                permissions_data = agent.permissions.to_dict()
            elif hasattr(agent.permissions, 'dict'):
                permissions_data = agent.permissions.dict()
            else:
                permissions_data = agent.permissions
            
            # Convert entity to model
            agent_model = AgentModel(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                agent_type=agent.agent_type,
                config=config_data,  # Using config as that's what the model expects
                permissions=permissions_data,
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
            
            # Handle both config and configuration fields
            config_data = None
            if "configuration" in data:
                config_data = data["configuration"]
                if hasattr(config_data, 'to_dict'):
                    config_data = config_data.to_dict()
                elif hasattr(config_data, 'dict'):
                    config_data = config_data.dict()
            elif "config" in data:
                config_data = data["config"]
                if hasattr(config_data, 'to_dict'):
                    config_data = config_data.to_dict()
                elif hasattr(config_data, 'dict'):
                    config_data = config_data.dict()
            
            # Update fields
            if "name" in data:
                agent_model.name = data["name"]
            if "description" in data:
                agent_model.description = data["description"]
            if config_data is not None:
                agent_model.config = config_data
            if "permissions" in data:
                if hasattr(data["permissions"], 'to_dict'):
                    agent_model.permissions = data["permissions"].to_dict()
                elif hasattr(data["permissions"], 'dict'):
                    agent_model.permissions = data["permissions"].dict()
                else:
                    agent_model.permissions = data["permissions"]
            
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
        # Create permissions from dict
        permissions = None
        if hasattr(AgentPermissions, 'from_dict'):
            permissions = AgentPermissions.from_dict(model.permissions)
        else:
            permissions = AgentPermissions(**model.permissions)
        
        # Create agent with configuration instead of config
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            agent_type=model.agent_type,
            configuration=model.config,  # Using configuration instead of config
            permissions=permissions,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 