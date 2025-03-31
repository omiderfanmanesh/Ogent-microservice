"""
Agents module.

This module contains the agent implementations for the application.
"""

from app.core.agents.base_agent import BaseAgent, AgentResult, AgentCallback
from app.core.agents.conversational_agent import ConversationalAgent
from app.core.agents.command_agent import CommandAgent
from app.core.agents.factory import AgentFactory

# Export public API
__all__ = [
    "BaseAgent", 
    "AgentResult",
    "AgentCallback",
    "ConversationalAgent",
    "CommandAgent",
    "AgentFactory"
]


def get_agent_factory(
    execution_repo,
    command_client
) -> AgentFactory:
    """
    Get a configured agent factory with all available agent types registered.
    
    Args:
        execution_repo: Repository for saving execution data
        command_client: Client for executing commands
        
    Returns:
        Configured agent factory
    """
    factory = AgentFactory(
        execution_repo=execution_repo,
        command_client=command_client
    )
    
    # Register available agent types
    factory.register_agent_type("conversational", ConversationalAgent)
    factory.register_agent_type("command", CommandAgent)
    
    return factory 