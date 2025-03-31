"""
Agent repository interface.

This module defines the interface for agent repositories.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.core.entities.agent import Agent, AgentType


class AgentRepository(ABC):
    """
    Agent repository interface.
    
    This interface defines the contract for repositories that manage agents.
    """
    
    @abstractmethod
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: The agent to create
            
        Returns:
            The created agent with ID and timestamps
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The agent if found, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def delete(self, agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: The ID of the agent to delete
            user_id: Optional user ID for access control
            
        Returns:
            True if deleted, False otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
