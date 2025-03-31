"""
Base agent implementation.

This module provides the base agent class for all agent types.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass

from langchain.schema import ChatResult
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models.base import BaseChatModel
from langchain.schema.runnable import RunnableConfig
from langchain.schema.agent import AgentAction, AgentFinish

from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.entities.agent import Agent
from app.core.entities.execution import ExecutionStep, Command, StepType, CommandStatus, ExecutionResult
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """
    Result of an agent execution.
    """
    output: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentCallback(BaseCallbackHandler):
    """
    Callback handler for agent execution.
    
    This callback handler records agent steps and commands
    to the execution repository.
    """
    
    def __init__(self, execution_id: str, execution_repo: ExecutionRepository):
        """
        Initialize the callback handler.
        
        Args:
            execution_id: The ID of the execution to record steps for
            execution_repo: Repository for execution operations
        """
        self.execution_id = execution_id
        self.execution_repo = execution_repo
        self.tokens_used = 0
    
    async def on_agent_action(
        self, 
        action: AgentAction, 
        run_id: Optional[str] = None, 
        **kwargs
    ) -> None:
        """
        Called when the agent takes an action.
        
        Args:
            action: The action taken by the agent
            run_id: The run ID
            **kwargs: Additional arguments
        """
        # Create a thought step for the action's log
        thought_step = ExecutionStep(
            id=str(uuid.uuid4()),
            execution_id=self.execution_id,
            type=StepType.THOUGHT,
            content=action.log,
            timestamp=datetime.utcnow(),
            metadata={"run_id": run_id}
        )
        await self.execution_repo.add_step(thought_step)
        
        # Create an action step for the tool and input
        action_step = ExecutionStep(
            id=str(uuid.uuid4()),
            execution_id=self.execution_id,
            type=StepType.ACTION,
            content=f"Tool: {action.tool}\nInput: {action.tool_input}",
            timestamp=datetime.utcnow(),
            metadata={
                "tool": action.tool,
                "tool_input": action.tool_input,
                "run_id": run_id
            }
        )
        await self.execution_repo.add_step(action_step)
    
    async def on_agent_finish(
        self, 
        finish: AgentFinish, 
        run_id: Optional[str] = None, 
        **kwargs
    ) -> None:
        """
        Called when the agent finishes.
        
        Args:
            finish: The finish information
            run_id: The run ID
            **kwargs: Additional arguments
        """
        # Create a step for the final output
        output = ""
        metadata = {"run_id": run_id}
        
        if isinstance(finish, str):
            # Handle string output
            output = finish
        else:
            # Handle AgentFinish object
            if hasattr(finish, 'return_values'):
                output = finish.return_values.get("output", "")
                metadata.update(finish.return_values if isinstance(finish.return_values, dict) else {})
            elif hasattr(finish, 'output'):
                output = finish.output
        
        step = ExecutionStep(
            id=str(uuid.uuid4()),
            execution_id=self.execution_id,
            type=StepType.OBSERVATION,
            content=output,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        await self.execution_repo.add_step(step)
    
    async def on_llm_tokens_used(
        self, 
        tokens_used: Dict[str, int], 
        **kwargs
    ) -> None:
        """
        Called when tokens are used by the LLM.
        
        Args:
            tokens_used: Dictionary with keys "prompt_tokens", "completion_tokens", and "total_tokens"
            **kwargs: Additional arguments
        """
        self.tokens_used += tokens_used.get("total_tokens", 0)
    
    async def on_tool_start(
        self, 
        serialized: Dict[str, Any], 
        input_str: str, 
        run_id: Optional[str] = None, 
        **kwargs
    ) -> None:
        """
        Called when a tool is about to be executed.
        
        Args:
            serialized: Serialized tool
            input_str: Tool input
            run_id: The run ID
            **kwargs: Additional arguments
        """
        # For command tools, create a command record
        tool_name = serialized.get("name", "")
        if tool_name == "command" or tool_name.startswith("cmd_"):
            command = Command(
                id=str(uuid.uuid4()),
                execution_id=self.execution_id,
                command=input_str,
                status=CommandStatus.RUNNING,
                timestamp=datetime.utcnow(),
                metadata={"run_id": run_id, "tool": tool_name}
            )
            await self.execution_repo.add_command(command)
    
    async def on_tool_error(
        self, 
        error: Union[Exception, str], 
        run_id: Optional[str] = None, 
        **kwargs
    ) -> None:
        """
        Called when a tool execution results in an error.
        
        Args:
            error: The error that occurred
            run_id: The run ID
            **kwargs: Additional arguments
        """
        # Create a step for the error
        step = ExecutionStep(
            id=str(uuid.uuid4()),
            execution_id=self.execution_id,
            type=StepType.OBSERVATION,
            content=f"Error: {str(error)}",
            timestamp=datetime.utcnow(),
            metadata={"error": True, "run_id": run_id}
        )
        await self.execution_repo.add_step(step)
    
    async def on_tool_end(
        self, 
        output: str, 
        run_id: Optional[str] = None, 
        **kwargs
    ) -> None:
        """
        Called when a tool execution ends.
        
        Args:
            output: The output of the tool
            run_id: The run ID
            **kwargs: Additional arguments
        """
        # Create a step for the tool output
        step = ExecutionStep(
            id=str(uuid.uuid4()),
            execution_id=self.execution_id,
            type=StepType.OBSERVATION,
            content=output,
            timestamp=datetime.utcnow(),
            metadata={"run_id": run_id}
        )
        await self.execution_repo.add_step(step)


class BaseAgent(ABC):
    """
    Base class for all agent implementations.
    """
    
    def __init__(
        self,
        agent: Agent,
        execution_repo: Optional[ExecutionRepository] = None,
        command_client: Optional[CommandClient] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            agent: The agent entity
            execution_repo: Optional repository for execution operations
            command_client: Optional client for command execution
        """
        self.agent = agent
        self.execution_repo = execution_repo
        self.command_client = command_client
        
        # Ensure agent_type is always an enum
        if isinstance(agent.agent_type, str):
            try:
                from app.core.entities.agent import AgentType
                self.agent_type = AgentType(agent.agent_type)
            except (ValueError, ImportError):
                self.agent_type = agent.agent_type
        else:
            self.agent_type = agent.agent_type
        
        # Set up basic agent configuration
        self.llm_config = {
            "model_name": agent.configuration.model_name or settings.DEFAULT_MODEL,
            "temperature": agent.configuration.temperature,
            "max_tokens": agent.configuration.max_tokens or settings.DEFAULT_MAX_TOKENS,
            "streaming": agent.configuration.streaming,
            "openai_api_key": settings.OPENAI_API_KEY,
        }
        
        # Set up command execution configuration
        self.command_config = {
            "execute_commands": agent.permissions.execute_commands,
            "allowed_commands": agent.permissions.allowed_commands,
            "allowed_paths": agent.permissions.allowed_paths,
            "network_access": agent.permissions.network_access,
            "memory_limit": agent.permissions.memory_limit or settings.MAX_MEMORY_MB,
        }
    
    @abstractmethod
    async def run(self, input_text: str, execution_id: Optional[str] = None) -> ExecutionResult:
        """
        Run the agent.
        
        Args:
            input_text: Input text to process
            execution_id: Optional execution ID for tracking
            
        Returns:
            Execution result
        """
        pass
    
    async def _create_callback(self, execution_id: str) -> Tuple[AgentCallback, CallbackManager]:
        """
        Create a callback manager with the agent callback.
        
        Args:
            execution_id: The ID of the execution
            
        Returns:
            Tuple of (AgentCallback, CallbackManager)
        """
        callback = AgentCallback(execution_id, self.execution_repo)
        callback_manager = CallbackManager([callback])
        
        return callback, callback_manager
    
    def _get_runnable_config(self, callbacks: Optional[CallbackManager] = None) -> RunnableConfig:
        """
        Get the runnable configuration.
        
        Args:
            callbacks: Optional callback manager
            
        Returns:
            RunnableConfig for the agent
        """
        config = {"callbacks": callbacks}
        
        # Add tracing configuration if needed
        # config["tags"] = ["agent", self.agent.agent_type.value]
        
        return config 