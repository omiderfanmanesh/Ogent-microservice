"""
Command tool for executing system commands.

This module provides a tool for executing system commands securely.
"""

import logging
from typing import List, Dict, Any, Optional
import re

from langchain.tools import BaseTool, tool
from langchain.pydantic_v1 import BaseModel, Field

from app.infrastructure.adapters.command_client import CommandClient
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


def create_command_tool(
    command_client: CommandClient,
    allowed_commands: Optional[List[str]] = None,
    allowed_paths: Optional[List[str]] = None,
    memory_limit: Optional[int] = None,
    network_access: bool = False,
) -> BaseTool:
    """
    Create a command execution tool.
    
    Args:
        command_client: Client for executing commands
        allowed_commands: List of allowed command patterns
        allowed_paths: List of allowed file system paths
        memory_limit: Memory limit in MB
        network_access: Whether to allow network access
        
    Returns:
        Command execution tool
    """
    # Set defaults
    allowed_commands = allowed_commands or []
    allowed_paths = allowed_paths or settings.ALLOWED_PATHS
    memory_limit = memory_limit or settings.MAX_MEMORY_MB
    
    # Define the arguments class
    class CommandSchema(BaseModel):
        command: str = Field(
            ..., 
            description="The command to execute with its arguments"
        )
    
    # Create the tool
    @tool("command", args_schema=CommandSchema, return_direct=False)
    def command_tool(command: str) -> Dict[str, Any]:
        """
        Execute a system command securely.
        
        Use this tool to run shell commands. The command will be executed in a secure 
        environment with limited permissions. Commands that are not allowed or that 
        access restricted paths will be rejected.
        
        Args:
            command: The command to execute with its arguments
            
        Returns:
            Result of command execution with stdout, stderr, and exit code
        """
        logger.info(f"Executing command: {command}")
        
        try:
            # Check if the command is allowed
            if not _is_command_allowed(command, allowed_commands):
                return {
                    "status": "denied",
                    "error": f"Command not allowed: {command}",
                    "stdout": "",
                    "stderr": "Permission denied: This command is not on the allowed list.",
                    "exit_code": 1
                }
            
            # Execute the command
            result = command_client.execute_command(
                command=command,
                timeout=settings.DEFAULT_TIMEOUT_SECONDS,
                allowed_paths=allowed_paths,
                memory_limit=memory_limit,
                network_access=network_access
            )
            
            # Format the result
            return {
                "status": "success" if result["exit_code"] == 0 else "failed",
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "duration_ms": result["duration_ms"]
            }
        except Exception as e:
            logger.error(f"Error executing command {command}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "stdout": "",
                "stderr": f"Error: {str(e)}",
                "exit_code": 1
            }
    
    return command_tool


def _is_command_allowed(command: str, allowed_patterns: List[str]) -> bool:
    """
    Check if a command is allowed based on patterns.
    
    Args:
        command: The command to check
        allowed_patterns: List of allowed command patterns (using regex)
        
    Returns:
        True if the command is allowed, False otherwise
    """
    # If no patterns are specified, deny all
    if not allowed_patterns:
        return False
    
    # If "*" is in the patterns, allow all
    if "*" in allowed_patterns:
        return True
    
    # Extract the base command (before any arguments)
    base_command = command.split(" ")[0]
    
    # Check if the command matches any allowed pattern
    for pattern in allowed_patterns:
        try:
            if re.match(f"^{pattern}$", base_command) or re.match(f"^{pattern}", command):
                return True
        except re.error:
            # If the pattern is not a valid regex, check for exact match
            if base_command == pattern or command.startswith(pattern):
                return True
    
    return False 