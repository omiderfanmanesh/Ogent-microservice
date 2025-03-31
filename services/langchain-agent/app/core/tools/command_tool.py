"""
Command tool.

This module provides a command tool for executing system commands.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Type, Callable, Awaitable
import shlex

from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field

from app.infrastructure.adapters.command_client import CommandClient

# Configure logging
logger = logging.getLogger(__name__)


class CommandInput(BaseModel):
    """Command input schema."""
    command: str = Field(..., description="The command to execute")


class CommandTool(BaseTool):
    """Tool for executing system commands."""
    
    name = "execute_command"
    description = "Execute a system command and return the result."
    args_schema: Type[BaseModel] = CommandInput
    
    command_client: CommandClient
    allowed_commands: List[str]
    allowed_paths: Optional[List[str]] = None
    memory_limit: Optional[int] = None
    network_access: bool = False
    handle_command_callback: Optional[Callable[..., Awaitable[None]]] = None
    
    def _run(self, command: str) -> str:
        """Execute synchronous command (not supported)."""
        raise NotImplementedError("CommandTool only supports async execution")
    
    async def _arun(self, command: str) -> str:
        """
        Execute a command asynchronously.
        
        Args:
            command: Command to execute
            
        Returns:
            Command output as a string
        """
        try:
            # Check if command is allowed
            command_parts = shlex.split(command)
            base_command = command_parts[0]
            
            if self.allowed_commands and base_command not in self.allowed_commands:
                return f"Error: Command '{base_command}' is not allowed. Allowed commands: {', '.join(self.allowed_commands)}"
            
            # Validate with command service
            try:
                validation = await self.command_client.validate_command(
                    command=command,
                    allowed_paths=self.allowed_paths,
                    memory_limit=self.memory_limit,
                    network_access=self.network_access
                )
                
                if not validation.get("valid", False):
                    return f"Error: Command validation failed: {validation.get('message', 'Unknown error')}"
            except Exception as e:
                logger.error(f"Error validating command: {str(e)}", exc_info=True)
                return f"Error: Failed to validate command: {str(e)}"
            
            # Notify about command execution if callback exists
            if self.handle_command_callback:
                await self.handle_command_callback(command=command, status="running")
            
            # Execute command
            result = await self.command_client.execute_command(
                command=command,
                timeout=30,  # Default timeout
                allowed_paths=self.allowed_paths,
                memory_limit=self.memory_limit,
                network_access=self.network_access
            )
            
            # Get command data
            exit_code = result.get("exit_code")
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            duration_ms = result.get("duration_ms", 0)
            
            # Determine status
            status = "completed" if exit_code == 0 else "failed"
            
            # Send command result if callback exists
            if self.handle_command_callback:
                await self.handle_command_callback(
                    command=command,
                    status=status,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=duration_ms
                )
            
            # Format the output
            output = f"Exit Code: {exit_code}\n"
            
            if stdout:
                output += f"Output:\n{stdout}\n"
                
            if stderr:
                output += f"Error:\n{stderr}\n"
                
            return output
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}", exc_info=True)
            
            # Notify about command failure if callback exists
            if self.handle_command_callback:
                await self.handle_command_callback(
                    command=command,
                    status="failed",
                    stderr=str(e)
                )
                
            return f"Error executing command: {str(e)}" 