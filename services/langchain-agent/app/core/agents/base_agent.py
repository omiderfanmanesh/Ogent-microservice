"""
Base agent.

This module provides the base agent class that all agent implementations will extend.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from app.core.entities.agent import AgentConfiguration, AgentPermissions
from app.core.agents.agent_result import AgentResult
from app.infrastructure.adapters.command_client import CommandClient

# Configure logging
logger = logging.getLogger(__name__)


class AgentCallback:
    """
    Agent callback.
    
    This class provides callback methods for agent execution events.
    """
    
    async def on_step(
        self,
        step_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle an execution step.
        
        Args:
            step_type: Step type
            content: Step content
            metadata: Optional metadata
        """
        pass
    
    async def on_command(
        self,
        command: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle a command execution.
        
        Args:
            command: Command text
            status: Command status
            exit_code: Optional exit code
            stdout: Optional standard output
            stderr: Optional standard error
            duration_ms: Optional duration in milliseconds
            metadata: Optional metadata
        """
        pass


class BaseAgent(ABC):
    """
    Base agent.
    
    This is the base class for all agent implementations.
    """
    
    def __init__(
        self,
        configuration: AgentConfiguration,
        permissions: AgentPermissions,
        command_client: CommandClient
    ):
        """
        Initialize the agent.
        
        Args:
            configuration: Agent configuration
            permissions: Agent permissions
            command_client: Command client
        """
        self.configuration = configuration
        self.permissions = permissions
        self.command_client = command_client
        
        # Set up any common configuration
        self.model_name = configuration.model_name
        self.temperature = configuration.temperature
        self.max_tokens = configuration.max_tokens
        self.system_message = configuration.system_message
        self.streaming = configuration.streaming
        self.max_iterations = configuration.max_iterations
    
    @abstractmethod
    async def run(
        self,
        input: str,
        callback: Optional[AgentCallback] = None,
    ) -> AgentResult:
        """
        Run the agent.
        
        Args:
            input: User input
            callback: Optional callback for execution events
            
        Returns:
            Agent result
        """
        pass
    
    async def _handle_step(
        self,
        callback: Optional[AgentCallback],
        step_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle a step and send it to the callback if provided.
        
        Args:
            callback: Optional callback
            step_type: Step type
            content: Step content
            metadata: Optional metadata
        """
        if callback:
            await callback.on_step(step_type, content, metadata)
        logger.debug(f"Agent step: {step_type} - {content}")
    
    async def _handle_command(
        self,
        callback: Optional[AgentCallback],
        command: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle a command and send it to the callback if provided.
        
        Args:
            callback: Optional callback
            command: Command text
            status: Command status
            exit_code: Optional exit code
            stdout: Optional standard output
            stderr: Optional standard error
            duration_ms: Optional duration in milliseconds
            metadata: Optional metadata
        """
        if callback:
            await callback.on_command(
                command=command,
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms,
                metadata=metadata
            )
        logger.debug(f"Agent command: {command} - Status: {status}")
    
    def _can_execute_command(self, command: str) -> bool:
        """
        Check if a command can be executed.
        
        Args:
            command: Command to check
            
        Returns:
            True if the command can be executed, False otherwise
        """
        if not self.permissions.execute_commands:
            return False
        
        # If allowed_commands is empty, all commands are allowed
        if not self.permissions.allowed_commands:
            return True
        
        # Check if the command is in the list of allowed commands
        # This is a simple check, a more robust implementation would parse
        # the command and check if it matches allowed patterns
        for allowed_command in self.permissions.allowed_commands:
            if command.startswith(allowed_command):
                return True
        
        return False 