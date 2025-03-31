"""
Custom agent implementation.

This module provides the custom agent implementation for executing custom Python code.
"""

import logging
import sys
from io import StringIO
from typing import Optional
from contextlib import redirect_stdout, redirect_stderr

from app.core.agents.base_agent import BaseAgent
from app.core.entities.agent import Agent
from app.core.entities.execution import ExecutionResult


# Configure logging
logger = logging.getLogger(__name__)


class CustomAgent(BaseAgent):
    """
    Custom agent implementation for executing custom Python code.
    """
    
    def __init__(self, agent: Agent):
        """
        Initialize the custom agent.
        
        Args:
            agent: Agent entity
        """
        super().__init__(agent)
        self.globals = {
            'print': print,
            'logger': logger,
            'sys': sys,
        }
        self.locals = {}
    
    async def run(self, input_text: str, execution_id: Optional[str] = None) -> ExecutionResult:
        """
        Run the custom agent.
        
        Args:
            input_text: Python code to execute
            execution_id: Optional execution ID for tracking
            
        Returns:
            Execution result
        """
        # Capture stdout and stderr
        stdout = StringIO()
        stderr = StringIO()
        
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                # Execute the code
                exec(input_text, self.globals, self.locals)
            
            # Get output
            output = stdout.getvalue()
            error = stderr.getvalue()
            
            return ExecutionResult(
                output=output if output else None,
                error=error if error else None,
                metadata={
                    "locals": list(self.locals.keys()),
                    "globals": list(self.globals.keys())
                }
            )
        except Exception as e:
            return ExecutionResult(
                output=stdout.getvalue() if stdout.getvalue() else None,
                error=f"{str(e)}\n{stderr.getvalue()}" if stderr.getvalue() else str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "locals": list(self.locals.keys()),
                    "globals": list(self.globals.keys())
                }
            )
    
    @classmethod
    async def create(cls, agent: Agent) -> "CustomAgent":
        """
        Create a new custom agent instance.
        
        Args:
            agent: Agent entity
            
        Returns:
            Custom agent instance
        """
        return cls(agent=agent) 