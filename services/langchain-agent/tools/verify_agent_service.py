#!/usr/bin/env python
"""
Script to verify the agent service.

This script tests the creation and execution of agents.
"""

import logging
import uuid
import json
import asyncio
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_agent_data(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create test agent data.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with agent data
    """
    agent_id = str(uuid.uuid4())
    user_id = user_id or f"test-user-{uuid.uuid4().hex[:8]}"
    
    return {
        "id": agent_id,
        "name": f"Test Agent {uuid.uuid4().hex[:6]}",
        "type": "conversational",
        "description": "A test agent created by the verification script",
        "user_id": user_id,
        "configuration": {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful assistant for testing.",
            "max_iterations": 10
        },
        "permissions": {
            "network_access": False,
            "allowed_commands": [],
            "allowed_paths": []
        },
        "metadata": {
            "test": True,
            "source": "verification_script"
        }
    }


def test_direct_agent_creation():
    """Test creating an agent directly using the domain entities."""
    from app.domain.entities import Agent, AgentConfiguration, AgentPermissions
    
    logger.info("Testing direct agent creation...")
    
    # Create agent data
    agent_data = create_test_agent_data()
    
    try:
        # Method 1: Create using individual parameters
        configuration = AgentConfiguration(
            model=agent_data["configuration"]["model"],
            temperature=agent_data["configuration"]["temperature"],
            system_message=agent_data["configuration"]["system_message"],
            max_iterations=agent_data["configuration"]["max_iterations"]
        )
        
        permissions = AgentPermissions(
            network_access=agent_data["permissions"]["network_access"],
            allowed_commands=agent_data["permissions"]["allowed_commands"],
            allowed_paths=agent_data["permissions"]["allowed_paths"]
        )
        
        agent = Agent(
            id=agent_data["id"],
            name=agent_data["name"],
            type=agent_data["type"],
            description=agent_data["description"],
            user_id=agent_data["user_id"],
            configuration=configuration,
            permissions=permissions,
            metadata=agent_data["metadata"]
        )
        
        logger.info(f"Created agent with ID {agent.id} and name {agent.name}")
        logger.info(f"Agent model: {agent.configuration.model}")
        
        # Method 2: Create using dictionaries for configuration and permissions
        agent2 = Agent(
            id=agent_data["id"],
            name=agent_data["name"],
            type=agent_data["type"],
            description=agent_data["description"],
            user_id=agent_data["user_id"],
            configuration=agent_data["configuration"],
            permissions=agent_data["permissions"],
            metadata=agent_data["metadata"]
        )
        
        logger.info(f"Created agent 2 with ID {agent2.id} and name {agent2.name}")
        logger.info(f"Agent 2 model: {agent2.configuration.model}")
        
        # Access attributes to ensure they work
        logger.info(f"Accessing configuration.model: {agent.configuration.model}")
        logger.info(f"Accessing configuration.temperature: {agent.configuration.temperature}")
        
        # Test accessing permissions
        logger.info(f"Accessing permissions.network_access: {agent.permissions.network_access}")
        logger.info(f"Accessing permissions.allowed_commands: {agent.permissions.allowed_commands}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        return False


async def test_agent_creation_and_execution_async():
    """Test creating and executing an agent asynchronously."""
    try:
        from app.core.agents.conversational_agent import ConversationalAgent
        from app.core.entities.agent import AgentConfiguration, AgentPermissions
        from app.core.clients.command_client import CommandClient
        
        logger.info("Testing agent creation and execution...")
        
        # Create agent data
        agent_data = create_test_agent_data()
        
        # Create a command client
        command_client = CommandClient(execution_timeout=60)
        
        # Create agent
        configuration = AgentConfiguration(
            model=agent_data["configuration"]["model"],
            temperature=agent_data["configuration"]["temperature"],
            system_message=agent_data["configuration"]["system_message"],
            max_iterations=agent_data["configuration"]["max_iterations"]
        )
        
        permissions = AgentPermissions(
            network_access=agent_data["permissions"]["network_access"],
            allowed_commands=agent_data["permissions"]["allowed_commands"],
            allowed_paths=agent_data["permissions"]["allowed_paths"]
        )
        
        # Attempt to create agent
        agent = ConversationalAgent(
            configuration=configuration,
            permissions=permissions,
            command_client=command_client
        )
        
        logger.info(f"Created conversational agent with model {agent.model_name}")
        
        # Execute agent with a simple query
        logger.info("Testing agent execution with a simple query")
        result = await agent.execute("What is 2+2?")
        
        logger.info(f"Agent execution result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing agent: {str(e)}", exc_info=True)
        return False


def test_agent_creation_and_execution():
    """Wrapper for async test function."""
    return asyncio.run(test_agent_creation_and_execution_async())


def main():
    """Main function."""
    logger.info("Starting agent service verification...")
    
    # Test direct agent creation
    if test_direct_agent_creation():
        logger.info("✅ Direct agent creation test passed")
    else:
        logger.error("❌ Direct agent creation test failed")
        return False
    
    # Test agent creation and execution
    if test_agent_creation_and_execution():
        logger.info("✅ Agent creation and execution test passed")
    else:
        logger.error("❌ Agent creation and execution test failed")
        return False
    
    logger.info("✅ All tests passed. Agent service verification completed successfully.")
    return True


if __name__ == "__main__":
    if main():
        print("\n✅ Agent service verification passed!")
    else:
        print("\n❌ Agent service verification failed!")
