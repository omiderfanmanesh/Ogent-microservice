"""
Execution entities module.

This module defines the execution domain entities.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """
    Status of an execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class CommandStatus(str, Enum):
    """
    Status of a command execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"


class StepType(str, Enum):
    """
    Type of execution step.
    """
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    ERROR = "error"


@dataclass
class Command:
    """
    Command executed during an agent execution.
    """
    id: Optional[str] = None
    execution_id: Optional[str] = None
    command: str = ""
    status: CommandStatus = CommandStatus.PENDING
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStep:
    """
    Step in an agent execution.
    """
    id: Optional[str] = None
    execution_id: Optional[str] = None
    type: StepType = StepType.THOUGHT
    content: str = ""
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Execution:
    """
    Execution entity representing a run of an agent.
    """
    id: Optional[str] = None
    agent_id: str = ""
    user_id: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    input: str = ""
    output: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionStep(BaseModel):
    """
    Represents a single step in an execution.
    """
    step_id: str
    execution_id: str
    step_number: int
    description: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CommandExecution(BaseModel):
    """
    Represents a command execution within a step.
    """
    command_id: str
    step_id: str
    command: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionResult(BaseModel):
    """
    Represents the result of an agent execution.
    """
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    steps: List[ExecutionStep] = Field(default_factory=list)
    commands: List[CommandExecution] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 