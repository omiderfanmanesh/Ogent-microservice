"""
Execution repository interface.

This module defines the interface for execution repositories.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.core.entities.execution import Execution, ExecutionStep, Command


class ExecutionRepository(ABC):
    """
    Execution repository interface.
    
    This interface defines the contract for repositories that manage executions.
    """
    
    @abstractmethod
    async def create(self, execution: Execution) -> Execution:
        """
        Create a new execution.
        
        Args:
            execution: The execution to create
            
        Returns:
            The created execution with ID and timestamps
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, execution_id: str, user_id: Optional[str] = None) -> Optional[Execution]:
        """
        Get an execution by ID.
        
        Args:
            execution_id: The ID of the execution to retrieve
            user_id: Optional user ID for access control
            
        Returns:
            The execution if found, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def add_step(self, step: ExecutionStep) -> ExecutionStep:
        """
        Add a step to an execution.
        
        Args:
            step: The step to add
            
        Returns:
            The created step with ID and timestamp
        """
        pass
    
    @abstractmethod
    async def add_command(self, command: Command) -> Command:
        """
        Add a command to an execution.
        
        Args:
            command: The command to add
            
        Returns:
            The created command with ID and timestamp
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
