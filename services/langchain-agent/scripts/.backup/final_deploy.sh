#!/bin/bash
# Final deployment script for langchain-agent service fixes

set -e
echo "Deploying fixes for the langchain-agent service..."

# Copy fixed files to Docker container
echo "Copying fix for agent_result.py..."
docker cp fixes/agent_result.py ogent-agent-service-test:/app/app/core/agents/agent_result.py

echo "Copying fix for factory.py..."
docker cp fixes/factory.py ogent-agent-service-test:/app/app/core/agents/factory.py

# Create temporary file with complete Agent entity
echo "Creating fixed agent entity..."
cat > agent_entity.py << 'EOF'
"""
Agent entity.

This module provides the agent entity model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union


class AgentType(Enum):
    """
    Agent type enum.
    
    Defines the available agent types.
    """
    CONVERSATIONAL = "conversational"
    COMMAND = "command"
    SQL = "sql"
    CUSTOM = "custom"


@dataclass
class AgentConfiguration:
    """
    Agent configuration.
    
    Contains configurable settings for an agent.
    """
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    streaming: bool = False
    tools: List[Dict[str, Any]] = field(default_factory=list)
    max_iterations: int = 10
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfiguration':
        """
        Create an AgentConfiguration from a dictionary.
        
        Args:
            data: Dictionary with configuration values
            
        Returns:
            AgentConfiguration instance
        """
        # Filter out None values and unknown fields
        filtered_data = {}
        for key, value in data.items():
            if key in cls.__annotations__ and value is not None:
                filtered_data[key] = value
        
        return cls(**filtered_data)


@dataclass
class AgentPermissions:
    """
    Agent permissions.
    
    Defines what actions an agent is allowed to perform.
    """
    execute_commands: bool = False
    allowed_commands: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)
    network_access: bool = False
    memory_limit: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentPermissions':
        """
        Create an AgentPermissions from a dictionary.
        
        Args:
            data: Dictionary with permissions values
            
        Returns:
            AgentPermissions instance
        """
        # Filter out None values and unknown fields
        filtered_data = {}
        for key, value in data.items():
            if key in cls.__annotations__ and value is not None:
                filtered_data[key] = value
        
        return cls(**filtered_data)


@dataclass
class Agent:
    """
    Agent entity.
    
    Represents an agent in the system.
    """
    name: str
    user_id: str
    agent_type: Union[AgentType, str]
    id: Optional[str] = None
    description: Optional[str] = None
    configuration: Union[AgentConfiguration, Dict[str, Any]] = field(default_factory=AgentConfiguration)
    permissions: Union[AgentPermissions, Dict[str, Any]] = field(default_factory=AgentPermissions)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Post-initialization processing.
        
        Converts string agent_type to enum and dictionary configurations to proper objects.
        """
        # Convert agent_type string to enum if needed
        if isinstance(self.agent_type, str):
            try:
                self.agent_type = AgentType(self.agent_type)
            except ValueError:
                # Keep as string if not a valid enum value
                pass
        
        # Convert configuration dictionary to AgentConfiguration if needed
        if isinstance(self.configuration, dict):
            self.configuration = AgentConfiguration.from_dict(self.configuration)
        
        # Convert permissions dictionary to AgentPermissions if needed
        if isinstance(self.permissions, dict):
            self.permissions = AgentPermissions.from_dict(self.permissions)
EOF

# Create temporary file with complete content for agent_service.py
echo "Creating fixed agent_service.py..."
cat > agent_service.py << 'EOF'
"""
Agent service.

This module provides the agent service implementation for managing agents and executions.
"""

import logging
import uuid
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator, Union, Tuple
import json

from app.domain.repositories.agent_repository import AgentRepository
from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.entities.agent import Agent, AgentType, AgentConfiguration, AgentPermissions
from app.core.entities.execution import (
    Execution, ExecutionStep, Command, 
    ExecutionStatus, CommandStatus, StepType
)
from app.core.agents.factory import AgentFactory
from app.core.agents import (
    AgentResult,
    AgentCallback
)

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionCallback(AgentCallback):
    """Callback for tracking execution steps and commands."""
    
    def __init__(self, execution_id: str, execution_repository: ExecutionRepository):
        """
        Initialize execution callback.
        
        Args:
            execution_id: ID of the execution
            execution_repository: Execution repository for persisting steps and commands
        """
        self.execution_id = execution_id
        self.execution_repository = execution_repository
    
    async def on_step(self, step_type: str, content: str) -> None:
        """
        Handle execution step.
        
        Args:
            step_type: Type of the step
            content: Content of the step
        """
        try:
            # Create step entity
            step = ExecutionStep(
                execution_id=self.execution_id,
                step_type=step_type,
                content=content
            )
            
            # Save step to database
            await self.execution_repository.add_step(step)
        except Exception as e:
            logger.error(f"Error saving execution step: {str(e)}", exc_info=True)
    
    async def on_command(
        self,
        command: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Handle command execution.
        
        Args:
            command: Command string
            status: Command status
            exit_code: Command exit code
            stdout: Command standard output
            stderr: Command standard error
            duration_ms: Command duration in milliseconds
        """
        try:
            # Create command entity
            cmd = Command(
                execution_id=self.execution_id,
                command=command,
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration_ms
            )
            
            # Save command to database
            await self.execution_repository.add_command(cmd)
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}", exc_info=True)


class AgentService:
    """
    Agent service.
    
    This service is responsible for managing agents and their executions.
    """
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        execution_repository: ExecutionRepository,
        agent_factory: AgentFactory
    ):
        """
        Initialize agent service.
        
        Args:
            agent_repository: Repository for agent persistence
            execution_repository: Repository for execution persistence
            agent_factory: Factory for creating agent instances
        """
        self.agent_repository = agent_repository
        self.execution_repository = execution_repository
        self.agent_factory = agent_factory
        
        # Track streaming executions
        self._streaming_executions: Dict[str, asyncio.Queue] = {}
    
    async def create_agent(
        self,
        name: str,
        description: str,
        agent_type: str,
        configuration: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        permissions: Optional[AgentPermissions] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            description: Agent description
            agent_type: Type of agent
            configuration: Agent configuration (primary parameter)
            config: Agent configuration (legacy parameter)
            permissions: Agent permissions
            metadata: Additional metadata
            user_id: ID of the user who owns the agent
            
        Returns:
            Created agent
            
        Raises:
            ValueError: If the agent type is not supported or the configuration is invalid
        """
        # Use proper configuration (prioritize configuration over config)
        final_config = configuration if configuration is not None else config or {}
        
        # Validate agent type
        available_types = self.agent_factory.get_available_agent_types()
        if agent_type not in available_types:
            raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {', '.join(available_types)}")
        
        # Create default permissions if none provided
        if not permissions:
            permissions = AgentPermissions()
        
        # Create agent entity
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            configuration=final_config,
            permissions=permissions,
            metadata=metadata or {},
            user_id=user_id
        )
        
        # Validate configuration by creating an agent instance
        try:
            self.agent_factory.create_agent(
                agent_type=agent_type,
                configuration=final_config,
                permissions=permissions
            )
        except Exception as e:
            raise ValueError(f"Invalid agent configuration: {str(e)}")
        
        # Save agent to database
        created_agent = await self.agent_repository.create(agent)
        
        logger.info(f"Created agent '{name}' with ID {created_agent.id}")
        return created_agent

    async def get_agent(self, agent_id: str, user_id: Optional[str] = None) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            user_id: Optional user ID for permission check
            
        Returns:
            Agent if found, None otherwise
        """
        return await self.agent_repository.get(agent_id, user_id)
    
    async def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        permissions: Optional[AgentPermissions] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            name: New name
            description: New description
            config: New configuration
            permissions: New permissions
            metadata: New metadata
            user_id: User ID for permission check
            
        Returns:
            Updated agent if found, None otherwise
        """
        # Get existing agent
        agent = await self.agent_repository.get(agent_id, user_id)
        if not agent:
            return None
        
        # Update fields if provided
        if name is not None:
            agent.name = name
        
        if description is not None:
            agent.description = description
        
        if config is not None:
            # Validate configuration
            try:
                self.agent_factory.create_agent(
                    agent_type=agent.agent_type,
                    config=config,
                    permissions=agent.permissions
                )
                agent.configuration = config
            except Exception as e:
                raise ValueError(f"Invalid agent configuration: {str(e)}")
        
        if permissions is not None:
            agent.permissions = permissions
        
        if metadata is not None:
            # Merge metadata instead of replacing
            agent.metadata = {**agent.metadata, **metadata}
        
        # Save updated agent
        updated_agent = await self.agent_repository.update(agent)
        
        logger.info(f"Updated agent with ID {agent_id}")
        return updated_agent
    
    async def delete_agent(self, agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            user_id: User ID for permission check
            
        Returns:
            True if agent was deleted, False otherwise
        """
        # Check if agent exists
        agent = await self.agent_repository.get(agent_id, user_id)
        if not agent:
            return False
        
        # Delete agent
        result = await self.agent_repository.delete(agent_id, user_id)
        
        if result:
            logger.info(f"Deleted agent with ID {agent_id}")
        
        return result
    
    async def execute_agent(
        self,
        agent_id: str,
        input: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Execution:
        """
        Execute an agent.
        
        Args:
            agent_id: Agent ID
            input: Input text
            metadata: Optional execution metadata
            user_id: User ID for permission check
            
        Returns:
            Execution details
            
        Raises:
            ValueError: If the agent is not found
        """
        # Get agent
        agent = await self.agent_repository.get(agent_id, user_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found")
        
        # Create execution
        execution = Execution(
            agent_id=agent_id,
            user_id=user_id or agent.user_id,
            status=ExecutionStatus.RUNNING,
            input=input,
            metadata=metadata or {}
        )
        
        # Save execution to database
        created_execution = await self.execution_repository.create(execution)
        
        # Start execution in background
        asyncio.create_task(self._execute_agent(agent, created_execution))
        
        logger.info(f"Started execution {created_execution.id} for agent {agent_id}")
        return created_execution
    
    async def _execute_agent(self, agent: Agent, execution: Execution) -> None:
        """
        Execute agent in background.
        
        Args:
            agent: Agent to execute
            execution: Execution details
        """
        # Update execution status
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()
        await self.execution_repository.update(execution)
        
        try:
            # Create agent instance
            agent_instance = self.agent_factory.create_agent(
                agent_type=agent.agent_type,
                configuration=agent.configuration,
                permissions=agent.permissions
            )
            
            # Create callback
            callback = ExecutionCallback(
                execution_id=execution.id,
                execution_repository=self.execution_repository
            )
            
            # Run agent
            result = await agent_instance.run(execution.input, callback)
            
            # Update execution with result
            execution.status = ExecutionStatus.COMPLETED
            execution.output = result.output
            execution.error = result.error
            execution.tokens_used = getattr(result, 'tokens_used', None)
            execution.completed_at = datetime.now()
            
            await self.execution_repository.update(execution)
            
            # If we're streaming this execution, send completion and close queue
            if execution.id in self._streaming_executions:
                queue = self._streaming_executions[execution.id]
                await queue.put({"event": "complete", "data": result.to_dict()})
                await queue.put(None)  # Signal end of stream
            
            logger.info(f"Completed execution {execution.id} for agent {agent.id}")
            
        except Exception as e:
            logger.error(f"Error executing agent: {str(e)}", exc_info=True)
            
            # Update execution with error
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            
            await self.execution_repository.update(execution)
            
            # If we're streaming this execution, send error and close queue
            if execution.id in self._streaming_executions:
                queue = self._streaming_executions[execution.id]
                await queue.put({"event": "error", "data": {"error": str(e)}})
                await queue.put(None)  # Signal end of stream
            
            logger.info(f"Failed execution {execution.id} for agent {agent.id}")
EOF

# Create temporary file with complete content for conversational_agent.py
echo "Creating fixed conversational_agent.py..."
cat > conversational_agent.py << 'EOF'
"""
Conversational agent.

This module provides a conversational agent implementation using LangChain.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AgentAction, AgentFinish, AIMessage, HumanMessage
from langchain.schema.runnable import RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools.base import BaseTool

from app.core.agents.base_agent import BaseAgent, AgentCallback
from app.core.agents.agent_result import AgentResult
from app.core.tools.command_tool import CommandTool

# Configure logging
logger = logging.getLogger(__name__)


class AgentCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler.
    
    This handler captures events from LangChain and forwards them to our callback.
    """
    
    def __init__(self, callback: Optional[AgentCallback] = None):
        """
        Initialize the handler.
        
        Args:
            callback: Agent callback
        """
        self.callback = callback
    
    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """
        Handle agent action.
        
        Args:
            action: LangChain agent action
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="action",
                content=f"{action.tool}: {action.tool_input}",
                metadata={"tool": action.tool, "input": action.tool_input}
            )
    
    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """
        Handle agent finish.
        
        Args:
            finish: LangChain agent finish
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="final_answer",
                content=finish.return_values.get("output", ""),
                metadata=finish.return_values
            )
    
    async def on_tool_start(
        self, 
        serialized: Dict[str, Any], 
        input_str: str, 
        **kwargs: Any
    ) -> None:
        """
        Handle tool start.
        
        Args:
            serialized: Serialized tool
            input_str: Tool input
            **kwargs: Additional arguments
        """
        tool_name = serialized.get("name", "unknown_tool")
        if tool_name == "execute_command" and self.callback:
            await self.callback.on_command(
                command=input_str,
                status="running",
                metadata={"tool": tool_name}
            )
    
    async def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Handle tool end.
        
        Args:
            output: Tool output
            observation_prefix: Observation prefix
            llm_prefix: LLM prefix
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="observation",
                content=output
            )
    
    async def on_tool_error(
        self, 
        error: Exception, 
        **kwargs: Any
    ) -> None:
        """
        Handle tool error.
        
        Args:
            error: Exception
            **kwargs: Additional arguments
        """
        if self.callback:
            await self.callback.on_step(
                step_type="observation",
                content=f"Error: {str(error)}"
            )
    
    async def on_chat_model_start(
        self, 
        serialized: Dict[str, Any], 
        messages: List[List[Dict[str, Any]]], 
        **kwargs: Any
    ) -> None:
        """
        Handle chat model start.
        
        Args:
            serialized: Serialized model
            messages: Messages
            **kwargs: Additional arguments
        """
        pass
    
    async def on_text(self, text: str, **kwargs: Any) -> None:
        """
        Handle text.
        
        Args:
            text: Text
            **kwargs: Additional arguments
        """
        if self.callback and text.strip():
            await self.callback.on_step(
                step_type="thought",
                content=text
            )


class ConversationalAgent(BaseAgent):
    """
    Conversational agent.
    
    This agent uses LangChain and LLMs to have conversations and perform actions.
    """
    
    async def run(
        self,
        input: str,
        callback: Optional[AgentCallback] = None,
    ) -> AgentResult:
        """
        Run the agent.
        
        Args:
            input: User input
            callback: Optional callback for execution events
            
        Returns:
            Agent result
        """
        # Record start time
        start_time = time.time()
        
        try:
            # Set up tools
            tools = self._create_tools()
            
            # Create LLM
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming
            )
            
            # Create agent callback handler
            handler = AgentCallbackHandler(callback)
            
            # Set up the prompt with system message
            system_message = self.system_message or "You are a helpful AI assistant that follows instructions precisely."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Set up agent with tools
            agent = create_openai_tools_agent(llm, tools, prompt)
            
            # Create executor
            executor = AgentExecutor(
                agent=agent,
                tools=tools,
                max_iterations=self.max_iterations,
                handle_parsing_errors=True,
                verbose=True,
            )
            
            # Set up the execution config
            config = RunnableConfig(
                callbacks=[handler],
            )
            
            # Execute the agent
            result = await executor.ainvoke(
                {"input": input, "chat_history": []},
                config=config
            )
            
            # Calculate tokens used (if available in metadata)
            tokens_used = 0
            usage = getattr(llm, 'last_token_usage', None)
            if usage:
                tokens_used = usage.get('total_tokens', 0)
            
            # Return agent result
            return AgentResult(
                output=result["output"],
                tokens_used=tokens_used,
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "iterations": result.get("intermediate_steps", [])
                }
            )
        
        except Exception as e:
            logger.error(f"Error running conversational agent: {str(e)}", exc_info=True)
            
            # Return error result
            return AgentResult(
                output="I encountered an error while processing your request.",
                error=str(e),
                tokens_used=0,
                metadata={
                    "duration_ms": int((time.time() - start_time) * 1000),
                }
            )
    
    def _create_tools(self) -> List[BaseTool]:
        """
        Create tools for the agent.
        
        Returns:
            List of tools
        """
        tools = []
        
        # Add command execution tool if allowed
        if self.permissions.execute_commands:
            tools.append(
                CommandTool(
                    command_client=self.command_client,
                    allowed_commands=self.permissions.allowed_commands,
                    allowed_paths=self.permissions.allowed_paths
                )
            )
        
        return tools
EOF

# Deploy the files
echo "Copying fixed files..."
docker cp fixes/agent_result.py ogent-agent-service-test:/app/app/core/agents/agent_result.py
docker cp fixes/factory.py ogent-agent-service-test:/app/app/core/agents/factory.py
docker cp agent_entity.py ogent-agent-service-test:/app/app/core/entities/agent.py
docker cp agent_service.py ogent-agent-service-test:/app/app/core/services/agent_service.py
docker cp conversational_agent.py ogent-agent-service-test:/app/app/core/agents/conversational_agent.py

# Clean up temporary files
rm -f agent_entity.py
rm -f agent_service.py
rm -f conversational_agent.py

# Restart the service to apply changes
echo "Restarting the agent service..."
docker restart ogent-agent-service-test

echo "Fixes deployed successfully! Waiting for service to start..."
sleep 5
echo "Done. The service should now be functioning correctly." 