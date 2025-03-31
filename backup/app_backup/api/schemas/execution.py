"""
API schemas for execution-related endpoints.

This module defines the request and response schemas for execution operations.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class ExecutionStepResponse(BaseModel):
    """
    Response schema for execution step details.
    """
    id: str = Field(..., description="Step ID")
    type: str = Field(..., description="Type of step (thought, action, observation)")
    content: str = Field(..., description="Content of the step")
    timestamp: datetime = Field(..., description="Step timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional step metadata")
    
    class Config:
        from_attributes = True


class CommandResponse(BaseModel):
    """
    Response schema for command details.
    """
    id: str = Field(..., description="Command ID")
    command: str = Field(..., description="The command that was executed")
    status: str = Field(..., description="Status of command execution")
    exit_code: Optional[int] = Field(None, description="Exit code of the command")
    stdout: Optional[str] = Field(None, description="Standard output of the command")
    stderr: Optional[str] = Field(None, description="Standard error of the command")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")
    timestamp: datetime = Field(..., description="Command timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional command metadata")
    
    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """
    Response schema for execution details.
    """
    id: str = Field(..., description="Execution ID")
    agent_id: str = Field(..., description="ID of the agent that was executed")
    user_id: str = Field(..., description="ID of the user who initiated the execution")
    status: str = Field(..., description="Status of the execution")
    input: str = Field(..., description="The input provided to the agent")
    output: Optional[str] = Field(None, description="The final output of the agent")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    steps: List[ExecutionStepResponse] = Field(default_factory=list, description="Steps taken during execution")
    commands: List[CommandResponse] = Field(default_factory=list, description="Commands executed")
    started_at: Optional[datetime] = Field(None, description="When execution started")
    completed_at: Optional[datetime] = Field(None, description="When execution completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional execution metadata")
    
    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """
    Response schema for listing executions.
    """
    items: List[ExecutionResponse] = Field(..., description="List of executions")
    total: int = Field(..., description="Total count of executions matching filters")
    skip: int = Field(..., description="Number of executions skipped (offset)")
    limit: int = Field(..., description="Maximum number of executions returned")


class BasicExecutionResponse(BaseModel):
    """
    Simplified response schema for execution details without steps and commands.
    """
    id: str = Field(..., description="Execution ID")
    agent_id: str = Field(..., description="ID of the agent that was executed")
    user_id: str = Field(..., description="ID of the user who initiated the execution")
    status: str = Field(..., description="Status of the execution")
    input: str = Field(..., description="The input provided to the agent")
    output: Optional[str] = Field(None, description="The final output of the agent")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    started_at: Optional[datetime] = Field(None, description="When execution started")
    completed_at: Optional[datetime] = Field(None, description="When execution completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ExecutionStatusResponse(BaseModel):
    """
    Response schema for execution status.
    """
    id: str = Field(..., description="Execution ID")
    status: str = Field(..., description="Status of the execution")
    started_at: Optional[datetime] = Field(None, description="When execution started")
    completed_at: Optional[datetime] = Field(None, description="When execution completed")
    error: Optional[str] = Field(None, description="Error message if execution failed")


class StreamEventType(str, Enum):
    """Stream event type."""
    STATUS = "status"
    STEP = "step"
    COMMAND = "command"
    COMPLETION = "completion"
    ERROR = "error"
    PING = "ping"


class BaseStreamEvent(BaseModel):
    """Base schema for stream events."""
    type: StreamEventType = Field(..., description="Event type")


class StatusStreamEvent(BaseStreamEvent):
    """Schema for status events."""
    type: StreamEventType = StreamEventType.STATUS
    execution_id: str = Field(..., description="Execution ID")
    status: str = Field(..., description="Execution status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")


class StepStreamEvent(BaseStreamEvent):
    """Schema for step events."""
    type: StreamEventType = StreamEventType.STEP
    step_type: str = Field(..., description="Step type")
    content: str = Field(..., description="Step content")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class CommandStreamEvent(BaseStreamEvent):
    """Schema for command events."""
    type: StreamEventType = StreamEventType.COMMAND
    command: str = Field(..., description="Command string")
    status: str = Field(..., description="Command status")
    exit_code: Optional[int] = Field(None, description="Command exit code")
    stdout: Optional[str] = Field(None, description="Command standard output")
    stderr: Optional[str] = Field(None, description="Command standard error")
    duration_ms: Optional[int] = Field(None, description="Command duration in milliseconds")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class CompletionStreamEvent(BaseStreamEvent):
    """Schema for completion events."""
    type: StreamEventType = StreamEventType.COMPLETION
    execution_id: str = Field(..., description="Execution ID")
    status: str = Field(..., description="Execution status")
    output: Optional[str] = Field(None, description="Execution output")
    error: Optional[str] = Field(None, description="Execution error")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class ErrorStreamEvent(BaseStreamEvent):
    """Schema for error events."""
    type: StreamEventType = StreamEventType.ERROR
    message: str = Field(..., description="Error message")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    status: Optional[str] = Field(None, description="Execution status")
    error: Optional[str] = Field(None, description="Execution error")


class PingStreamEvent(BaseStreamEvent):
    """Schema for ping events."""
    type: StreamEventType = StreamEventType.PING


StreamEvent = Union[
    StatusStreamEvent,
    StepStreamEvent,
    CommandStreamEvent,
    CompletionStreamEvent,
    ErrorStreamEvent,
    PingStreamEvent,
]


class StepTypeEnum(str, Enum):
    """Step type enumeration."""
    THINKING = "thinking"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL_ANSWER = "final_answer"
    ERROR = "error"


class CommandStatusEnum(str, Enum):
    """Command status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ExecutionStatusEnum(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ExecutionStepSchema(BaseModel):
    """Execution step schema."""
    id: Optional[str] = Field(None, description="Step ID")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    type: StepTypeEnum = Field(..., description="Step type")
    content: str = Field(..., description="Step content")
    timestamp: Optional[datetime] = Field(None, description="Step timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional step metadata")


class CommandSchema(BaseModel):
    """Command schema."""
    id: Optional[str] = Field(None, description="Command ID")
    execution_id: Optional[str] = Field(None, description="Execution ID")
    command: str = Field(..., description="Command string")
    status: CommandStatusEnum = Field(..., description="Command status")
    exit_code: Optional[int] = Field(None, description="Exit code")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    timestamp: Optional[datetime] = Field(None, description="Command timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional command metadata")


class ExecutionSchema(BaseModel):
    """Execution schema."""
    id: Optional[str] = Field(None, description="Execution ID")
    agent_id: str = Field(..., description="Agent ID")
    user_id: Optional[str] = Field(None, description="User ID")
    status: ExecutionStatusEnum = Field(..., description="Execution status")
    input: str = Field(..., description="Input text")
    output: Optional[str] = Field(None, description="Output text")
    error: Optional[str] = Field(None, description="Error message")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    steps: List[ExecutionStepSchema] = Field(default_factory=list, description="Execution steps")
    commands: List[CommandSchema] = Field(default_factory=list, description="Commands executed")
    metadata: Dict[str, Any] = Field(..., description="Additional execution metadata")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    created_at: Optional[datetime] = Field(None, description="Creation time")

    class Config:
        """Pydantic config."""
        from_attributes = True


class ExecutionCreateSchema(BaseModel):
    """Execution creation schema."""
    agent_id: str = Field(..., description="Agent ID")
    input: str = Field(..., description="Input text")
    stream: bool = Field(False, description="Whether to stream the execution")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class ExecutionUpdateSchema(BaseModel):
    """Execution update schema."""
    status: Optional[ExecutionStatusEnum] = Field(None, description="New status")
    output: Optional[str] = Field(None, description="Output text")
    error: Optional[str] = Field(None, description="Error message")
    tokens_used: Optional[int] = Field(None, description="Tokens used")


class StreamEvent(BaseModel):
    """WebSocket stream event base schema."""
    type: str = Field(..., description="Event type")


class StatusEvent(StreamEvent):
    """Status update event."""
    type: str = "status"
    status: ExecutionStatusEnum = Field(..., description="Execution status")
    execution_id: str = Field(..., description="Execution ID")


class StepEvent(StreamEvent):
    """Step event."""
    type: str = "step"
    step_type: StepTypeEnum = Field(..., description="Step type")
    content: str = Field(..., description="Step content")
    execution_id: str = Field(..., description="Execution ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Step metadata")


class CommandEvent(StreamEvent):
    """Command event."""
    type: str = "command"
    command: str = Field(..., description="Command string")
    status: CommandStatusEnum = Field(..., description="Command status")
    execution_id: str = Field(..., description="Execution ID")
    exit_code: Optional[int] = Field(None, description="Exit code")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Command metadata")


class CompletionEvent(StreamEvent):
    """Completion event."""
    type: str = "completion"
    execution_id: str = Field(..., description="Execution ID")
    status: ExecutionStatusEnum = Field(..., description="Execution status")
    output: Optional[str] = Field(None, description="Output text")
    error: Optional[str] = Field(None, description="Error message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class ErrorEvent(StreamEvent):
    """Error event."""
    type: str = "error"
    message: str = Field(..., description="Error message")
    execution_id: Optional[str] = Field(None, description="Execution ID") 