"""
Execution entity.

This module provides the execution entity models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional


class ExecutionStatus(Enum):
    """
    Execution status enum.
    
    Defines the possible states of an execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class CommandStatus(Enum):
    """
    Command status enum.
    
    Defines the possible states of a command.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class StepType(Enum):
    """
    Step type enum.
    
    Defines the possible types of execution steps.
    """
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL_ANSWER = "final_answer"


@dataclass
class ExecutionStep:
    """
    Execution step entity.
    
    Represents a step in an agent execution.
    """
    execution_id: str
    type: StepType
    content: str
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Command:
    """
    Command entity.
    
    Represents a command executed during an agent execution.
    """
    execution_id: str
    command: str
    status: CommandStatus = CommandStatus.PENDING
    id: Optional[str] = None
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Execution:
    """
    Execution entity.
    
    Represents an agent execution.
    """
    agent_id: str
    user_id: str
    input: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    id: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict) 