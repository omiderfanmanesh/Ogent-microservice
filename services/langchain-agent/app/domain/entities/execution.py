"""
Execution entity module.

Defines the Execution entity which tracks the execution of agents.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class ExecutionStatus(str, Enum):
    """
    Status of an agent execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionStep(BaseModel):
    """
    Represents a single step in an agent execution.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(..., description="Type of step (thought, action, observation)")
    content: str = Field(..., description="Content of the step")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this step"
    )


class Command(BaseModel):
    """
    Represents a command executed by an agent.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    command: str = Field(..., description="The command that was executed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", description="Status of command execution")
    exit_code: Optional[int] = Field(default=None, description="Exit code of the command")
    stdout: Optional[str] = Field(default=None, description="Standard output of the command")
    stderr: Optional[str] = Field(default=None, description="Standard error of the command")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in milliseconds")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this command"
    )


class Execution(BaseModel):
    """
    Represents an execution of an agent.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = Field(..., description="ID of the agent that was executed")
    user_id: str = Field(..., description="ID of the user who initiated the execution")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    input: str = Field(..., description="The input provided to the agent")
    output: Optional[str] = Field(default=None, description="The final output of the agent")
    steps: List[ExecutionStep] = Field(
        default_factory=list,
        description="Steps taken during agent execution"
    )
    commands: List[Command] = Field(
        default_factory=list,
        description="Commands executed during this execution"
    )
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    tokens_used: Optional[int] = Field(default=None, description="Number of tokens used in this execution")
    started_at: Optional[datetime] = Field(default=None, description="When execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When execution completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this execution"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "exec-123456",
                "agent_id": "agent-789012",
                "user_id": "user-345678",
                "status": "completed",
                "input": "Show me the largest files in the /data directory",
                "output": "The largest files in the /data directory are:\n1. database.db (1.2GB)\n2. archive.zip (800MB)\n3. logs.txt (250MB)",
                "steps": [
                    {
                        "id": "step-1",
                        "timestamp": "2023-06-15T14:31:00Z",
                        "type": "thought",
                        "content": "I need to find the largest files in the /data directory. I can use the 'du' command with sorting."
                    },
                    {
                        "id": "step-2",
                        "timestamp": "2023-06-15T14:31:05Z",
                        "type": "action",
                        "content": "Execute command: du -h /data | sort -rh | head -n 3"
                    }
                ],
                "commands": [
                    {
                        "id": "cmd-1",
                        "command": "du -h /data | sort -rh | head -n 3",
                        "timestamp": "2023-06-15T14:31:05Z",
                        "status": "completed",
                        "exit_code": 0,
                        "stdout": "1.2G    /data/database.db\n800M    /data/archive.zip\n250M    /data/logs.txt",
                        "stderr": "",
                        "duration_ms": 1200
                    }
                ],
                "tokens_used": 320,
                "started_at": "2023-06-15T14:30:55Z",
                "completed_at": "2023-06-15T14:31:10Z",
                "created_at": "2023-06-15T14:30:50Z",
                "metadata": {
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0..."
                }
            }
        }
    )
