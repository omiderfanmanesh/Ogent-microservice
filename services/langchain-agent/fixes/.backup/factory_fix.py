"""Fixed AgentFactory implementation."""

from typing import Dict, Any, Type, List
import importlib
import inspect
import logging
from enum import Enum

from app.core.clients.command_client import CommandClient
from app.core.entities.agent import AgentType, AgentConfiguration, AgentPermissions
from app.core.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating agents."""

    def __init__(self, command_client: CommandClient):
        """
        Initialize the factory.
        
        Args:
            command_client: Command client
        """
        self.command_client = command_client
        self._agent_classes = self._discover_agent_classes()
        
    def _discover_agent_classes(self) -> Dict[str, Type[BaseAgent]]:
        """
        Discover agent classes.
        
        Returns:
            Dictionary mapping agent types to agent classes
        """
        agent_classes = {}
        
        # Import agent modules
        try:
            from app.core.agents import conversational_agent, command_agent
            
            # Add ConversationalAgent
            if hasattr(conversational_agent, "ConversationalAgent"):
                agent_classes[AgentType.CONVERSATIONAL] = conversational_agent.ConversationalAgent
            
            # Add CommandAgent if available
            if hasattr(command_agent, "CommandAgent"):
                agent_classes[AgentType.COMMAND] = command_agent.CommandAgent
                
        except ImportError as e:
            logger.error(f"Error importing agent modules: {str(e)}")
        
        return agent_classes
        
    def get_available_agent_types(self) -> List[str]:
        """
        Get available agent types.
        
        Returns:
            List of available agent types
        """
        return list(self._agent_classes.keys())
    
    def create_agent(
        self, 
        agent_type: str,
        configuration: AgentConfiguration,
        permissions: AgentPermissions
    ) -> BaseAgent:
        """
        Create an agent.
        
        Args:
            agent_type: Agent type
            configuration: Agent configuration
            permissions: Agent permissions
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If the agent type is not supported
        """
        # Convert agent_type if it's an enum
        if isinstance(agent_type, Enum):
            agent_type = agent_type.value
            
        # Get available agent types as string
        available_types = ", ".join(self.get_available_agent_types())
        
        # Check if agent type is supported
        if agent_type not in self._agent_classes:
            raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {available_types}")
        
        # Get agent class
        agent_class = self._agent_classes[agent_type]
        
        try:
            # Create agent instance
            agent = agent_class(
                configuration=configuration,
                permissions=permissions,
                command_client=self.command_client
            )
            return agent
        except Exception as e:
            logger.error(f"Error creating agent of type {agent_type}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to create agent of type {agent_type}: {str(e)}")
