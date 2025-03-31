"""
Agent result.

This module provides the agent result class for handling agent execution results.
"""

from typing import Dict, Optional, Any


class AgentResult:
    """
    Agent execution result.
    
    This class represents the result of an agent execution.
    """
    
    def __init__(
        self,
        output: str,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an agent result.
        
        Args:
            output: Output of the agent execution
            error: Optional error message if the execution failed
            metadata: Optional metadata about the execution
        """
        self.output = output
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent result to a dictionary.
        
        Returns:
            Dictionary representation of the agent result
        """
        return {
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """
        Create an agent result from a dictionary.
        
        Args:
            data: Dictionary representation of an agent result
            
        Returns:
            Agent result instance
        """
        return cls(
            output=data.get("output", ""),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        ) 