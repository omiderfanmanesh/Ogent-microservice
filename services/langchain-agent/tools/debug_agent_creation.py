#!/usr/bin/env python3
"""
Debug script for agent creation.

This script directly tests agent creation to help debug the issue with 
'dict' object has no attribute 'model_name'.
"""

import asyncio
import json
import sys
from typing import Dict, Any

def debug_dict_access(d, attribute):
    """Debug dictionary access issues."""
    print(f"Debugging access to '{attribute}' in dictionary:")
    print(f"  Dictionary type: {type(d)}")
    print(f"  Dictionary content: {json.dumps(d, indent=2)}")
    print(f"  Has attribute method: {hasattr(d, attribute)}")
    print(f"  Has key: {attribute in d}")
    
    if isinstance(d, dict) and attribute in d:
        print(f"  Value: {d[attribute]}")
    elif hasattr(d, attribute):
        print(f"  Value: {getattr(d, attribute)}")
    else:
        print(f"  Cannot access attribute/key '{attribute}'")

async def main():
    """Main function to test agent creation."""
    try:
        # Import needed classes inside the docker container
        from app.core.entities.agent import Agent, AgentConfiguration, AgentPermissions
        from app.core.agents.factory import AgentFactory
        from app.infrastructure.adapters.command_client import CommandClient
        
        # Create test configuration
        config_dict = {
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful AI assistant.",
            "max_iterations": 10
        }
        
        # Create command client
        command_client = CommandClient()
        
        # Create factory
        factory = AgentFactory(command_client=command_client)
        
        print("\n===== TESTING AGENT CREATION =====")
        print(f"Configuration dictionary: {json.dumps(config_dict, indent=2)}")
        
        # Method 1: Create directly with dictionary
        print("\nMethod 1: Create agent directly with dictionary")
        try:
            agent1 = factory.create_agent(
                agent_type="conversational",
                configuration=config_dict
            )
            print(f"✅ Success! Agent created with model: {agent1.model_name}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            # Debug the dictionary
            debug_dict_access(config_dict, "model_name")
            
        # Method 2: Create AgentConfiguration first
        print("\nMethod 2: Create with AgentConfiguration instance")
        try:
            agent_config = AgentConfiguration(**config_dict)
            agent2 = factory.create_agent(
                agent_type="conversational",
                configuration=agent_config
            )
            print(f"✅ Success! Agent created with model: {agent2.model_name}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            # Debug the configuration
            debug_dict_access(agent_config, "model_name")
            
        # Method 3: Use from_dict
        print("\nMethod 3: Use from_dict method")
        try:
            agent_config = AgentConfiguration.from_dict(config_dict)
            agent3 = factory.create_agent(
                agent_type="conversational",
                configuration=agent_config
            )
            print(f"✅ Success! Agent created with model: {agent3.model_name}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        # Method 4: Create via Agent entity
        print("\nMethod 4: Create via Agent entity")
        try:
            agent_entity = Agent(
                name="Test Agent",
                user_id="test-user",
                agent_type="conversational",
                configuration=config_dict
            )
            print(f"Agent entity configuration type: {type(agent_entity.configuration)}")
            
            # Access model_name from the agent's configuration
            model_name = agent_entity.configuration.model_name
            print(f"Model name from agent entity: {model_name}")
            
            # Create agent from factory using the agent entity's configuration
            agent4 = factory.create_agent(
                agent_type="conversational",
                configuration=agent_entity.configuration
            )
            print(f"✅ Success! Agent created with model: {agent4.model_name}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            # Debug the configuration
            if hasattr(agent_entity, 'configuration'):
                debug_dict_access(agent_entity.configuration, "model_name")
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 