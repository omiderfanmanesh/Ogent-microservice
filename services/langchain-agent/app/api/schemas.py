"""
API schema models.

This module provides Pydantic models for API request and response validation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, validator


# Agent schemas
class AgentConfigurationSchema(BaseModel):
    """Agent configuration schema."""
    model_name: str = Field("gpt-3.5-turbo", description="Model name to use")
    temperature: float = Field(0.7, description="Temperature for model")
    max_tokens: Optional[int] = Field(None, description="Max tokens for model")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    streaming: bool = Field(False, description="Enable streaming responses")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Custom tools for the agent")
    max_iterations: int = Field(10, description="Maximum iterations for agent")


class AgentPermissionsSchema(BaseModel):
    """Agent permissions schema."""
    execute_commands: bool = Field(False, description="Allow command execution")
    allowed_commands: List[str] = Field(default_factory=list, description="List of allowed commands")
    allowed_paths: List[str] = Field(default_factory=list, description="List of allowed file system paths")
    network_access: bool = Field(False, description="Allow network access")
    memory_limit: Optional[int] = Field(None, description="Memory limit in MB")


class AgentCreate(BaseModel):
    """Create agent request schema."""
    name: str = Field(..., description="Name of the agent")
    agent_type: str = Field(..., description="Type of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    configuration: Optional[AgentConfigurationSchema] = Field(None, description="Agent configuration")
    permissions: Optional[AgentPermissionsSchema] = Field(None, description="Agent permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentUpdate(BaseModel):
    """Update agent request schema."""
    name: Optional[str] = Field(None, description="Name of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    configuration: Optional[AgentConfigurationSchema] = Field(None, description="Agent configuration")
    permissions: Optional[AgentPermissionsSchema] = Field(None, description="Agent permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentResponse(BaseModel):
    """Agent response schema."""
    id: UUID4 = Field(..., description="Agent ID")
    name: str = Field(..., description="Name of the agent")
    user_id: str = Field(..., description="User ID")
    agent_type: str = Field(..., description="Type of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    configuration: AgentConfigurationSchema = Field(..., description="Agent configuration")
    permissions: AgentPermissionsSchema = Field(..., description="Agent permissions")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class AgentList(BaseModel):
    """Agent list response schema."""
    items: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")
    skip: int = Field(..., description="Number of agents skipped")
    limit: int = Field(..., description="Maximum number of agents returned")


# Execution schemas
class ExecutionCreate(BaseModel):
    """Create execution request schema."""
    input: str = Field(..., description="Input text for the agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CommandResponse(BaseModel):
    """Command response schema."""
    id: UUID4 = Field(..., description="Command ID")
    execution_id: UUID4 = Field(..., description="Execution ID")
    command: str = Field(..., description="Command executed")
    status: str = Field(..., description="Command status")
    exit_code: Optional[int] = Field(None, description="Command exit code")
    stdout: Optional[str] = Field(None, description="Command stdout")
    stderr: Optional[str] = Field(None, description="Command stderr")
    duration_ms: Optional[int] = Field(None, description="Command duration in milliseconds")
    timestamp: datetime = Field(..., description="Timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

    class Config:
        from_attributes = True


class ExecutionStepResponse(BaseModel):
    """Execution step response schema."""
    id: UUID4 = Field(..., description="Step ID")
    execution_id: UUID4 = Field(..., description="Execution ID")
    type: str = Field(..., description="Step type")
    content: str = Field(..., description="Step content")
    timestamp: datetime = Field(..., description="Timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """Execution response schema."""
    id: UUID4 = Field(..., description="Execution ID")
    agent_id: UUID4 = Field(..., description="Agent ID")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Execution status")
    input: str = Field(..., description="Input text")
    output: Optional[str] = Field(None, description="Output text")
    error: Optional[str] = Field(None, description="Error message")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    steps: List[ExecutionStepResponse] = Field(default_factory=list, description="Execution steps")
    commands: List[CommandResponse] = Field(default_factory=list, description="Commands executed")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

    class Config:
        from_attributes = True


class ExecutionList(BaseModel):
    """Execution list response schema."""
    items: List[ExecutionResponse] = Field(..., description="List of executions")
    total: int = Field(..., description="Total number of executions")
    skip: int = Field(..., description="Number of executions skipped")
    limit: int = Field(..., description="Maximum number of executions returned")


class ExecutionStatusResponse(BaseModel):
    """Execution status response schema."""
    id: UUID4 = Field(..., description="Execution ID")
    status: str = Field(..., description="Execution status")
    output: Optional[str] = Field(None, description="Output text")
    error: Optional[str] = Field(None, description="Error message")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        from_attributes = True


# API key schema
class ApiKeyHeader(BaseModel):
    """API key header schema."""
    x_api_key: str = Field(..., alias="X-API-Key") 