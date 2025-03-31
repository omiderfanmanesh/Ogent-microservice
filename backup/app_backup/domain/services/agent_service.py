"""
Agent service interface.

This module defines the interface for agent services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.entities.agent import Agent, AgentType
from app.core.entities.execution import Execution


class AgentService(ABC):
    """
    Interface for agent services.
    """

    @abstractmethod
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
            name: Name of the agent.
            agent_type: Type of the agent.
            description: Optional description of the agent.
            configuration: Optional configuration parameters.
            permissions: Optional permission settings.
            metadata: Optional additional metadata.
            user_id: Optional user ID of the creator.

        Returns:
            The created agent.

        Raises:
            ValueError: If the agent data is invalid.
        """
        pass

    @abstractmethod
    async def get_agent(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Get an agent by ID.

        Args:
            agent_id: The ID of the agent to retrieve.
            user_id: Optional user ID for access control.

        Returns:
            The agent if found, None otherwise.
        """
        pass

    @abstractmethod
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
            agent_id: The ID of the agent to update.
            user_id: Optional user ID for access control.
            name: Optional new name for the agent.
            description: Optional new description.
            configuration: Optional new configuration.
            permissions: Optional new permissions.
            metadata: Optional new metadata.

        Returns:
            The updated agent if found, None otherwise.
        
        Raises:
            ValueError: If the update data is invalid.
        """
        pass

    @abstractmethod
    async def delete_agent(self, agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: The ID of the agent to delete.
            user_id: Optional user ID for access control.

        Returns:
            True if deleted, False otherwise.
        """
        pass

    @abstractmethod
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
            user_id: Optional user ID for filtering.
            agent_type: Optional agent type for filtering.
            skip: Number of agents to skip.
            limit: Maximum number of agents to return.

        Returns:
            List of agents.
        """
        pass

    @abstractmethod
    async def count_agents(
        self, 
        user_id: Optional[str] = None, 
        agent_type: Optional[AgentType] = None
    ) -> int:
        """
        Count agents with filtering.

        Args:
            user_id: Optional user ID for filtering.
            agent_type: Optional agent type for filtering.

        Returns:
            Number of agents matching the filters.
        """
        pass

    @abstractmethod
    async def execute_agent(
        self,
        agent_id: str,
        input: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Execution:
        """
        Execute an agent with the given input.

        Args:
            agent_id: The ID of the agent to execute.
            input: The input text/query for the agent.
            user_id: Optional user ID for access control and tracking.
            metadata: Optional additional metadata for the execution.

        Returns:
            The execution result.
        
        Raises:
            ValueError: If the agent is not found or the input is invalid.
        """
        pass

    @abstractmethod
    async def get_execution(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """
        Get an execution by ID.

        Args:
            execution_id: The ID of the execution to retrieve.
            user_id: Optional user ID for access control.

        Returns:
            The execution if found, None otherwise.
        """
        pass

    @abstractmethod
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
            user_id: Optional user ID for filtering.
            agent_id: Optional agent ID for filtering.
            status: Optional status for filtering.
            skip: Number of executions to skip.
            limit: Maximum number of executions to return.

        Returns:
            List of executions.
        """
        pass

    @abstractmethod
    async def count_executions(
        self, 
        user_id: Optional[str] = None, 
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count executions with filtering.

        Args:
            user_id: Optional user ID for filtering.
            agent_id: Optional agent ID for filtering.
            status: Optional status for filtering.

        Returns:
            Number of executions matching the filters.
        """
        pass

    @abstractmethod
    async def cancel_execution(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """
        Cancel an execution.

        Args:
            execution_id: The ID of the execution to cancel.
            user_id: Optional user ID for access control.

        Returns:
            The updated execution if found, None otherwise.
        
        Raises:
            ValueError: If the execution cannot be canceled.
        """
        pass 