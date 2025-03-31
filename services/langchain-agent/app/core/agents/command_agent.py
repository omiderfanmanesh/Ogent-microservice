"""
Command agent.

This module provides a command agent specialized in executing system commands.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
import json

from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.agents.agent_result import AgentResult

# Configure logging
logger = logging.getLogger(__name__)


class CommandAgent(BaseAgent):
    """
    Command agent.
    
    This agent executes system commands directly with minimal LLM interaction.
    """
    
    async def run(
        self,
        input: str,
        callback: Optional[AgentCallback] = None,
    ) -> AgentResult:
        """
        Run the agent.
        
        Args:
            input: Command to execute
            callback: Optional callback for execution events
            
        Returns:
            Agent result
        """
        # Record start time
        start_time = time.time()
        
        try:
            # Check permissions
            if not self.permissions.execute_commands:
                error_msg = "Command execution is not allowed for this agent"
                if callback:
                    await self._handle_step(
                        callback, 
                        "thought", 
                        error_msg
                    )
                return AgentResult(
                    output=error_msg,
                    error=error_msg,
                    metadata={"duration_ms": int((time.time() - start_time) * 1000)}
                )
            
            # Validate command
            valid = await self._validate_command(input)
            if not valid:
                error_msg = f"Command not allowed: {input}"
                if callback:
                    await self._handle_step(
                        callback, 
                        "thought", 
                        error_msg
                    )
                return AgentResult(
                    output=error_msg,
                    error=error_msg,
                    metadata={"duration_ms": int((time.time() - start_time) * 1000)}
                )
            
            # Send thinking step
            if callback:
                await self._handle_step(
                    callback, 
                    "thought", 
                    f"Executing command: {input}"
                )
                await self._handle_command(
                    callback,
                    command=input,
                    status="running"
                )
            
            # Execute command
            result = await self._execute_command(input)
            
            # Get output and status
            status = "completed" if result.get("exit_code", 1) == 0 else "failed"
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            
            # Create output
            output = f"Command: {input}\n"
            output += f"Exit Code: {result.get('exit_code', 'Unknown')}\n"
            if stdout:
                output += f"Output:\n{stdout}\n"
            if stderr:
                output += f"Error:\n{stderr}\n"
            
            # Send command result
            if callback:
                await self._handle_command(
                    callback,
                    command=input,
                    status=status,
                    exit_code=result.get("exit_code"),
                    stdout=stdout,
                    stderr=stderr,
                    duration_ms=result.get("duration_ms")
                )
                await self._handle_step(
                    callback, 
                    "final_answer", 
                    output
                )
            
            # Create result
            error = stderr if status == "failed" else None
            return AgentResult(
                output=output,
                error=error,
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "command": input,
                    "exit_code": result.get("exit_code"),
                }
            )
        
        except Exception as e:
            logger.error(f"Error running command agent: {str(e)}", exc_info=True)
            
            # Create error result
            error_msg = f"Error executing command: {str(e)}"
            return AgentResult(
                output=error_msg,
                error=str(e),
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "command": input,
                }
            )
    
    async def _validate_command(self, command: str) -> bool:
        """
        Validate a command against permissions.
        
        Args:
            command: Command to validate
            
        Returns:
            True if the command is allowed, False otherwise
        """
        # Check if command execution is allowed
        if not self.permissions.execute_commands:
            return False
        
        # Check allowed commands
        if not self._can_execute_command(command):
            return False
        
        # Validate with command service if needed
        try:
            result = await self.command_client.validate_command(
                command=command,
                allowed_paths=self.permissions.allowed_paths,
                memory_limit=self.permissions.memory_limit,
                network_access=self.permissions.network_access
            )
            return result.get("valid", False)
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}", exc_info=True)
            return False
    
    async def _execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute
            
        Returns:
            Command execution result
        """
        try:
            # Execute via command service
            result = await self.command_client.execute_command(
                command=command,
                timeout=30,  # Default timeout
                allowed_paths=self.permissions.allowed_paths,
                memory_limit=self.permissions.memory_limit,
                network_access=self.permissions.network_access
            )
            
            return {
                "exit_code": result.get("exit_code"),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "duration_ms": result.get("duration_ms")
            }
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}", exc_info=True)
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": 0
            } 