"""
Agent factory.

This module provides the agent factory for creating instances of different agent types.
"""

import logging
from typing import Dict, List, Optional, Type, Any

from app.core.agents.base_agent import BaseAgent
from app.core.agents.conversational_agent import ConversationalAgent
from app.core.agents.command_agent import CommandAgent
from app.infrastructure.adapters.command_client import CommandClient
from app.core.domain.entities import AgentPermissions

# Configure logging
logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Agent factory.
    
    This class is responsible for creating agent instances based on their type.
    """
    
    def __init__(self, command_client: CommandClient):
        """
        Initialize agent factory.
        
        Args:
            command_client: Command client for executing commands
        """
        self.command_client = command_client
        self.agent_types: Dict[str, Type[BaseAgent]] = {}
        self._register_agent_types()
    
    def _register_agent_types(self):
        """Register available agent types."""
        self.agent_types = {
            "conversational": ConversationalAgent,
            "command": CommandAgent,
        }
    
    def get_available_agent_types(self) -> List[str]:
        """
        Get available agent types.
        
        Returns:
            List of available agent type names
        """
        return list(self.agent_types.keys())
    
    def create_agent(
        self,
        agent_type: str,
        config: Dict[str, Any],
        permissions: Optional[AgentPermissions] = None,
    ) -> BaseAgent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Agent configuration
            permissions: Optional agent permissions
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If the agent type is not supported
        """
        if agent_type not in self.agent_types:
            available_types = ", ".join(self.agent_types.keys())
            raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {available_types}")
        
        # Create default permissions if none provided
        if not permissions:
            permissions = AgentPermissions(
                execute_commands=False,
                allowed_commands=[],
                allowed_paths=[],
                memory_limit=None,
                network_access=False
            )
        
        # Create agent instance
        agent_class = self.agent_types[agent_type]
        
        try:
            agent = agent_class(
                config=config,
                permissions=permissions,
                command_client=self.command_client
            )
            return agent
        except Exception as e:
            logger.error(f"Error creating agent of type {agent_type}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create agent of type {agent_type}: {str(e)}") 