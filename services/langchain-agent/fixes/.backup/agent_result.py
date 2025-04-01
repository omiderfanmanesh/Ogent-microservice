"""
Simple implementation of agent result classes.
"""
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentStatus(str, Enum):
    """Agent execution status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentResult:
    """Agent execution result."""
    
    def __init__(
        self,
        output: Optional[str] = None,
        error: Optional[str] = None,
        status: AgentStatus = AgentStatus.COMPLETED,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize the result.
        
        Args:
            output: Execution output
            error: Execution error
            status: Execution status
            metadata: Execution metadata
        """
        self.output = output
        self.error = error
        self.status = status
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "output": self.output,
            "error": self.error,
            "status": self.status.value if isinstance(self.status, AgentStatus) else self.status,
            "metadata": self.metadata
        }
