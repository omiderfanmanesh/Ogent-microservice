"""
LangChain tool for executing commands via the Command Service.
"""

from typing import Dict, List, Optional, Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.infrastructure.adapters.command_client import CommandClient


class CommandInput(BaseModel):
    """Input schema for the Command Tool."""
    command: str = Field(..., description="The command to execute")
    timeout: Optional[int] = Field(30, description="Maximum execution time in seconds")
    allowed_paths: Optional[List[str]] = Field(
        None, 
        description="List of paths the command is allowed to access"
    )
    memory_limit: Optional[int] = Field(
        None, 
        description="Memory limit in MB for the command process"
    )
    network_access: Optional[bool] = Field(
        False, 
        description="Whether the command is allowed network access"
    )
    description: Optional[str] = Field(
        None,
        description="A description of what this command does"
    )


class CommandTool(BaseTool):
    """
    A LangChain tool for executing commands via the Command Service.
    
    This tool allows agents to execute shell commands in a controlled 
    environment with configurable restrictions.
    """
    name = "execute_command"
    description = """
    Execute a shell command in a secure, isolated environment.
    Use this when you need to run a command on the system.
    """
    args_schema: Type[BaseModel] = CommandInput
    command_client: CommandClient

    def __init__(self, command_client: CommandClient) -> None:
        """
        Initialize the CommandTool with a CommandClient.
        
        Args:
            command_client: Client for communicating with the Command Service
        """
        super().__init__()
        self.command_client = command_client

    def _run(self, command: str, timeout: int = 30, 
             allowed_paths: Optional[List[str]] = None,
             memory_limit: Optional[int] = None, 
             network_access: bool = False,
             description: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a command via the Command Service.
        
        Args:
            command: The command to execute
            timeout: Maximum execution time in seconds
            allowed_paths: List of paths the command is allowed to access
            memory_limit: Memory limit in MB for the command process
            network_access: Whether the command is allowed network access
            description: A description of what this command does
            
        Returns:
            Dict containing execution results with stdout, stderr, exit_code, etc.
        """
        try:
            result = self.command_client.execute_command(
                command=command,
                timeout=timeout,
                allowed_paths=allowed_paths,
                memory_limit=memory_limit,
                network_access=network_access
            )
            
            return {
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "exit_code": result.get("exit_code"),
                "duration_ms": result.get("duration_ms"),
                "execution_id": result.get("execution_id"),
                "status": result.get("status"),
                "command": command,
                "description": description,
            }
        except Exception as e:
            return {
                "error": str(e),
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "exit_code": 1,
                "status": "failed",
                "command": command,
                "description": description,
            }

    async def _arun(self, command: str, timeout: int = 30, 
                   allowed_paths: Optional[List[str]] = None,
                   memory_limit: Optional[int] = None, 
                   network_access: bool = False,
                   description: Optional[str] = None) -> Dict[str, Any]:
        """
        Asynchronously execute a command via the Command Service.
        
        This implementation is the same as _run but kept for compatibility with async LangChain.
        """
        return self._run(
            command=command,
            timeout=timeout,
            allowed_paths=allowed_paths,
            memory_limit=memory_limit,
            network_access=network_access,
            description=description
        ) 