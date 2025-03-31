"""
Domain interfaces.

This module provides interface definitions for the LangChain Agent Service.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple

from app.core.domain.entities import Agent, Execution, ExecutionStep, Command


class AgentRepository(ABC):
    """
    Interface for agent repository.
    
    This interface defines the contract for agent repositories.
    """
    
    @abstractmethod
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: Agent to create
            
        Returns:
            Created agent
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None if not found
        """
        pass
    
    @abstractmethod
    async def update(self, agent_id: str, data: Dict[str, Any]) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            data: Data to update
            
        Returns:
            Updated agent or None if not found
        """
        pass
    
    @abstractmethod
    async def delete(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if deleted, False otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass


class ExecutionRepository(ABC):
    """
    Interface for execution repository.
    
    This interface defines the contract for execution repositories.
    """
    
    @abstractmethod
    async def create(self, execution: Execution) -> Execution:
        """
        Create a new execution.
        
        Args:
            execution: Execution to create
            
        Returns:
            Created execution
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, execution_id: str) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution or None if not found
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def add_step(self, step: ExecutionStep) -> ExecutionStep:
        """
        Add a step to an execution.
        
        Args:
            step: Step to add
            
        Returns:
            Added step
        """
        pass
    
    @abstractmethod
    async def add_command(self, command: Command) -> Command:
        """
        Add a command to an execution.
        
        Args:
            command: Command to add
            
        Returns:
            Added command
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass 