"""
Agent factory implementation.

This module provides the agent factory for creating different types of agents.
"""

import logging
from typing import Dict, Type, Optional

from app.domain.repositories.execution_repository import ExecutionRepository
from app.infrastructure.adapters.command_client import CommandClient
from app.core.entities.agent import Agent, AgentType
from app.core.agents.base_agent import BaseAgent
from app.core.agents.command_agent import CommandAgent
from app.core.agents.sql_agent import SQLAgent
from app.core.agents.custom_agent import CustomAgent
from app.infrastructure.persistence.database import get_session

# Configure logging
logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating different types of agents.
    """
    
    def __init__(
        self,
        execution_repo: ExecutionRepository,
        command_client: CommandClient
    ):
        """
        Initialize the agent factory.
        
        Args:
            execution_repo: Repository for execution operations
            command_client: Client for command execution
        """
        self.execution_repo = execution_repo
        self.command_client = command_client
    
    async def create_agent(self, agent: Agent) -> BaseAgent:
        """
        Create an agent instance based on the agent type.
        
        Args:
            agent: Agent entity
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If the agent type is not supported
        """
        if agent.agent_type == AgentType.COMMAND:
            return CommandAgent(
                agent=agent,
                execution_repo=self.execution_repo,
                command_client=self.command_client
            )
        elif agent.agent_type == AgentType.SQL:
            db_session = await anext(get_session())
            return SQLAgent(agent=agent, db_session=db_session)
        elif agent.agent_type == AgentType.CUSTOM:
            return CustomAgent(agent=agent)
        else:
            valid_types = ", ".join([t.value for t in AgentType])
            raise ValueError(f"Unsupported agent type: {agent.agent_type}. Valid types are: {valid_types}")
    
    def register_agent_type(self, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """
        Register a new agent type.
        
        Args:
            agent_type: The agent type to register
            agent_class: The agent class to use for the type
        """
        # This method is not used in the new implementation
        pass
    
    def get_available_agent_types(self) -> Dict[str, str]:
        """
        Get available agent types and their descriptions.
        
        Returns:
            Dictionary of agent types and descriptions
        """
        return {
            AgentType.COMMAND.value: "Agent that can execute system commands",
            AgentType.SQL.value: "Agent that can execute SQL queries",
            AgentType.CUSTOM.value: "Agent that can execute custom Python code"
        } 