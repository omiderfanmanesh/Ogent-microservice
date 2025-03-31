"""
Agent factory for creating different types of LangChain agents.
"""

from typing import Dict, Any, Optional, Type

from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.agents.base_agent import BaseAgent
from app.core.config import settings


class AgentFactory:
    """
    Factory for creating different types of agents.
    
    This factory manages the creation of various agent types based on
    configuration and agent type.
    """
    
    def __init__(
        self,
        execution_repo: ExecutionRepository,
        command_client: CommandClient
    ):
        """
        Initialize the agent factory.
        
        Args:
            execution_repo: Repository for saving execution data
            command_client: Client for executing commands
        """
        self.execution_repo = execution_repo
        self.command_client = command_client
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
    
    def register_agent_type(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent type with the factory.
        
        Args:
            agent_type: Type identifier for the agent
            agent_class: The agent class to instantiate for this type
        """
        self._agent_types[agent_type] = agent_class
    
    def get_agent_types(self) -> Dict[str, Type[BaseAgent]]:
        """
        Get all registered agent types.
        
        Returns:
            Dictionary of agent types and their class implementations
        """
        return self._agent_types.copy()
    
    def create_agent(
        self,
        agent_type: str,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            agent_config: Optional configuration for the agent
        
        Returns:
            Instantiated agent of the requested type
            
        Raises:
            ValueError: If agent type is not registered
        """
        if agent_type not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Get agent class for this type
        agent_class = self._agent_types[agent_type]
        
        # Configure agent parameters
        config = agent_config or {}
        model_name = config.get("model_name", settings.MODEL_SETTINGS["model_name"])
        temperature = config.get("temperature", settings.MODEL_SETTINGS["temperature"])
        max_tokens = config.get("max_tokens", settings.MODEL_SETTINGS["max_tokens"])
        streaming = config.get("streaming", False)
        
        # Create and return the agent
        return agent_class(
            execution_repo=self.execution_repo,
            command_client=self.command_client,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming
        ) 