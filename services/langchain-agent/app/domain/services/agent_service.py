"""
Agent service for managing LangChain agents.

This service contains the core business logic for agent management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities import Agent
from app.domain.repositories import AgentRepository


class AgentService:
    """
    Service for managing LangChain agents.
    """
    
    def __init__(self, agent_repository: AgentRepository):
        """
        Initialize the agent service.
        
        Args:
            agent_repository: Repository for agent persistence.
        """
        self.agent_repository = agent_repository
    
    async def create_agent(self, agent_data: Dict[str, Any], user_id: str) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent_data: The data for the new agent.
            user_id: ID of the user creating the agent.
            
        Returns:
            The created agent.
        """
        # Create agent object from data
        agent = Agent(
            **agent_data,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Persist agent
        return await self.agent_repository.create(agent)
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve.
            
        Returns:
            The agent if found, None otherwise.
        """
        return await self.agent_repository.get_by_id(agent_id)
    
    async def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Optional[Agent]:
        """
        Update an existing agent.
        
        Args:
            agent_id: ID of the agent to update.
            agent_data: New data for the agent.
            
        Returns:
            The updated agent if found, None otherwise.
        """
        # Add updated timestamp
        agent_data["updated_at"] = datetime.utcnow()
        
        # Update agent
        return await self.agent_repository.update(agent_id, agent_data)
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of the agent to delete.
            
        Returns:
            True if the agent was deleted, False otherwise.
        """
        return await self.agent_repository.delete(agent_id)
    
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
        return await self.agent_repository.list(
            user_id=user_id,
            agent_type=agent_type,
            offset=offset,
            limit=limit
        )
    
    async def count_agents(
        self, 
        user_id: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> int:
        """
        Count agents with optional filtering.
        
        Args:
            user_id: Optional user ID to filter by creator.
            agent_type: Optional agent type to filter by.
            
        Returns:
            Count of agents matching the criteria.
        """
        return await self.agent_repository.count(
            user_id=user_id,
            agent_type=agent_type
        )
