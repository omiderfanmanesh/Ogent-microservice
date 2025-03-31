"""
API schemas for agent-related endpoints.

This module defines the request and response schemas for agent operations.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from app.domain.entities.agent import AgentConfiguration, AgentPermissions


class AgentTypeEnum(str, Enum):
    """Agent type enumeration."""
    CONVERSATIONAL = "conversational"
    COMMAND = "command"


class AgentPermissionsSchema(BaseModel):
    """Agent permissions schema."""
    execute_commands: bool = Field(False, description="Whether the agent can execute commands")
    allowed_commands: List[str] = Field(default_factory=list, description="List of allowed commands")
    allowed_paths: List[str] = Field(default_factory=list, description="List of allowed file paths")
    network_access: bool = Field(False, description="Whether the agent has network access")
    memory_limit: Optional[int] = Field(None, description="Memory limit in MB")


class AgentConfigSchema(BaseModel):
    """Agent configuration schema."""
    model_name: str = Field("gpt-4o", description="Model name")
    temperature: float = Field(0.7, description="Temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens")
    system_message: Optional[str] = Field(None, description="System message")
    streaming: bool = Field(False, description="Whether to stream the response")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="List of tools")
    max_iterations: int = Field(10, description="Maximum iterations")


class AgentSchema(BaseModel):
    """Agent schema."""
    id: Optional[str] = Field(None, description="Agent ID")
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    agent_type: AgentTypeEnum = Field(..., description="Agent type")
    user_id: Optional[str] = Field(None, description="User ID")
    configuration: AgentConfigSchema = Field(..., description="Agent configuration")
    permissions: AgentPermissionsSchema = Field(..., description="Agent permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    class Config:
        """Pydantic config."""
        from_attributes = True


class AgentCreateSchema(BaseModel):
    """Agent creation schema."""
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    agent_type: AgentTypeEnum = Field(..., description="Agent type")
    configuration: AgentConfigSchema = Field(..., description="Agent configuration")
    permissions: Optional[AgentPermissionsSchema] = Field(None, description="Agent permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentUpdateSchema(BaseModel):
    """Agent update schema."""
    name: Optional[str] = Field(None, description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    configuration: Optional[AgentConfigSchema] = Field(None, description="Agent configuration")
    permissions: Optional[AgentPermissionsSchema] = Field(None, description="Agent permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentExecuteSchema(BaseModel):
    """Agent execution schema."""
    input: str = Field(..., description="Input text")
    stream: bool = Field(False, description="Whether to stream the execution")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Execution metadata")


class AgentConfigurationResponse(BaseModel):
    """
    Response schema for agent configuration.
    """
    model_name: str = Field(..., description="LLM model name to use")
    temperature: float = Field(..., description="Temperature for LLM generation")
    max_tokens: int = Field(..., description="Maximum tokens for LLM responses")
    system_message: Optional[str] = Field(None, description="Custom system message")
    streaming: bool = Field(..., description="Whether to stream responses")
    tools: List[str] = Field(..., description="Tools available to the agent")
    max_iterations: int = Field(..., description="Maximum iterations for execution")
    
    class Config:
        from_attributes = True


class AgentPermissionsResponse(BaseModel):
    """
    Response schema for agent permissions.
    """
    execute_commands: bool = Field(..., description="Whether the agent can execute commands")
    allowed_commands: List[str] = Field(..., description="List of allowed command patterns")
    allowed_paths: List[str] = Field(..., description="List of allowed filesystem paths")
    network_access: bool = Field(..., description="Whether network access is allowed")
    memory_limit: Optional[int] = Field(None, description="Memory limit in MB")
    
    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """
    Response schema for agent details.
    """
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    type: str = Field(..., description="Type of agent")
    configuration: AgentConfigurationResponse
    permissions: AgentPermissionsResponse
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User ID of creator")
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """
    Response schema for listing agents.
    """
    items: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total count of agents matching filters")
    skip: int = Field(..., description="Number of agents skipped (offset)")
    limit: int = Field(..., description="Maximum number of agents returned")


class ExecuteAgentRequest(BaseModel):
    """
    Request schema for executing an agent.
    """
    input: str = Field(..., description="Input text/query for the agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional execution metadata") 