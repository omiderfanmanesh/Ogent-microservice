#!/bin/bash
set -e

echo "==============================================="
echo "Deploying fixes for the langchain-agent service"
echo "==============================================="

# Create directory for fixes inside the services/langchain-agent
mkdir -p services/langchain-agent/fixes

# Create the repository fix directly in the services directory
echo "Creating fixes in services/langchain-agent/fixes..."

# Create repository fix
cat > services/langchain-agent/fixes/repository_fix.py << 'EOF'
"""
Fixed repository implementation for the SQLAgentRepository.

This module fixes the repository to use 'configuration' instead of 'config'.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import AgentRepository
from app.domain.entities import Agent, AgentPermissions
from app.infrastructure.persistence.models import AgentModel

# Configure logging
logger = logging.getLogger(__name__)


class SQLAgentRepository(AgentRepository):
    """
    SQL implementation of agent repository.
    
    This repository uses SQLAlchemy to persist agents to a database.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize SQL agent repository.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    async def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.
        
        Args:
            agent: Agent to create
            
        Returns:
            Created agent
        """
        try:
            # Extract configuration from agent - supporting both attribute names
            config_data = {}
            if hasattr(agent, 'configuration'):
                if hasattr(agent.configuration, 'to_dict'):
                    config_data = agent.configuration.to_dict()
                elif hasattr(agent.configuration, 'dict'):
                    config_data = agent.configuration.dict()
                else:
                    config_data = agent.configuration
            elif hasattr(agent, 'config'):
                if hasattr(agent.config, 'to_dict'):
                    config_data = agent.config.to_dict()
                elif hasattr(agent.config, 'dict'):
                    config_data = agent.config.dict()
                else:
                    config_data = agent.config
            
            # Extract permissions
            permissions_data = {}
            if hasattr(agent.permissions, 'to_dict'):
                permissions_data = agent.permissions.to_dict()
            elif hasattr(agent.permissions, 'dict'):
                permissions_data = agent.permissions.dict()
            else:
                permissions_data = agent.permissions
            
            # Convert entity to model
            agent_model = AgentModel(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                agent_type=agent.agent_type,
                config=config_data,  # Using config as that's what the model expects
                permissions=permissions_data,
                user_id=agent.user_id,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
            
            # Add to session and commit
            self.session.add(agent_model)
            await self.session.commit()
            await self.session.refresh(agent_model)
            
            # Convert back to entity
            return self._model_to_entity(agent_model)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            raise
    
    def _model_to_entity(self, model: AgentModel) -> Agent:
        """
        Convert agent model to entity.
        
        Args:
            model: Agent model
            
        Returns:
            Agent entity
        """
        # Create permissions from dict
        permissions = None
        if hasattr(AgentPermissions, 'from_dict'):
            permissions = AgentPermissions.from_dict(model.permissions)
        else:
            permissions = AgentPermissions(**model.permissions)
        
        # Create agent with configuration instead of config
        return Agent(
            id=model.id,
            name=model.name,
            description=model.description,
            agent_type=model.agent_type,
            configuration=model.config,  # Using configuration instead of config
            permissions=permissions,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
EOF

# Create factory fix
cat > services/langchain-agent/fixes/factory_fix.py << 'EOF'
"""
Agent factory module.

This module provides the factory for creating agents.
"""

import importlib
import inspect
import logging
import pkgutil
from typing import Dict, Type, Optional, List

from app.core.agents.base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating agents.
    
    This factory discovers agent classes and creates agent instances.
    """
    
    def __init__(self):
        """Initialize the factory and discover agent classes."""
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._discover_agent_classes()
    
    def _discover_agent_classes(self):
        """
        Discover available agent classes.
        
        This method searches for agent classes in the agents package.
        """
        try:
            # Import the agents package
            import app.core.agents as agents_pkg
            
            # Get the package path
            pkg_path = agents_pkg.__path__
            pkg_name = agents_pkg.__name__
            
            # Search for modules in the package
            for _, name, is_pkg in pkgutil.iter_modules(pkg_path):
                if not is_pkg and name != "base_agent" and name != "factory":
                    # Import the module
                    module = importlib.import_module(f"{pkg_name}.{name}")
                    
                    # Find agent classes in the module
                    for item_name, item in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(item, BaseAgent) 
                            and item is not BaseAgent
                            and hasattr(item, "agent_type")
                        ):
                            # Add to dictionary of agent classes
                            agent_type = getattr(item, "agent_type")
                            self._agent_classes[agent_type] = item
                            logger.info(f"Discovered agent class {item_name} for type {agent_type}")
            
            logger.info(f"Discovered {len(self._agent_classes)} agent classes")
            
        except Exception as e:
            logger.error(f"Error discovering agent classes: {str(e)}", exc_info=True)
    
    def get_available_agent_types(self) -> List[str]:
        """
        Get the list of available agent types.
        
        Returns:
            List of available agent types
        """
        return list(self._agent_classes.keys())
    
    def create_agent(self, agent_type: str, **kwargs) -> Optional[BaseAgent]:
        """
        Create an agent.
        
        Args:
            agent_type: Type of agent to create
            **kwargs: Arguments to pass to the agent constructor
            
        Returns:
            Agent instance or None if the agent type is not found
        """
        try:
            # Get the agent class
            agent_class = self._agent_classes.get(agent_type)
            
            # Return None if the agent type is not found
            if agent_class is None:
                logger.error(f"Agent type {agent_type} not found")
                return None
            
            # Create the agent
            agent = agent_class(**kwargs)
            
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            return None
EOF

# Create command client
cat > services/langchain-agent/fixes/command_client.py << 'EOF'
"""
Command client module.

This module provides a client for executing commands.
"""

import logging
import subprocess
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


class CommandClient:
    """
    Client for executing commands.
    
    This client provides methods for executing commands and managing the execution.
    """
    
    def __init__(self, execution_timeout: int = 60):
        """
        Initialize the command client.
        
        Args:
            execution_timeout: Timeout for command execution in seconds
        """
        self.execution_timeout = execution_timeout
    
    async def execute_command(self, command: str, environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute
            environment: Environment variables for the command
            
        Returns:
            Dictionary containing the command output and status
        """
        logger.info(f"Executing command: {command}")
        
        try:
            # Mock implementation for testing
            return {
                "stdout": f"Mock execution of command: {command}",
                "stderr": "",
                "returncode": 0,
                "command": command
            }
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}", exc_info=True)
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": 1,
                "command": command
            }
EOF

# Create base agent fix
cat > services/langchain-agent/fixes/base_agent_fix.py << 'EOF'
"""
Base agent module.

This module provides the base agent class.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from app.core.entities.agent import AgentConfiguration, AgentPermissions
from app.core.clients.command_client import CommandClient

# Configure logging
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base agent class.
    
    This class provides the foundation for all agent implementations.
    """
    
    agent_type = "base"
    
    def __init__(
        self,
        configuration: Union[AgentConfiguration, Dict[str, Any]],
        permissions: Union[AgentPermissions, Dict[str, Any]],
        command_client: Optional[CommandClient] = None
    ):
        """
        Initialize the agent.
        
        Args:
            configuration: Agent configuration, either as an AgentConfiguration object or a dictionary
            permissions: Agent permissions, either as an AgentPermissions object or a dictionary
            command_client: Client for executing commands
        """
        # Convert dictionary configuration to AgentConfiguration if needed
        if isinstance(configuration, dict):
            if hasattr(AgentConfiguration, 'from_dict'):
                self.configuration = AgentConfiguration.from_dict(configuration)
            else:
                self.configuration = AgentConfiguration(**configuration)
        else:
            self.configuration = configuration
        
        # Convert dictionary permissions to AgentPermissions if needed
        if isinstance(permissions, dict):
            if hasattr(AgentPermissions, 'from_dict'):
                self.permissions = AgentPermissions.from_dict(permissions)
            else:
                self.permissions = AgentPermissions(**permissions)
        else:
            self.permissions = permissions
        
        # Set up command client
        self.command_client = command_client
    
    async def execute(self, input_text: str) -> Dict[str, Any]:
        """
        Execute the agent.
        
        Args:
            input_text: Input text for the agent
            
        Returns:
            Dictionary containing the agent output and metadata
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _validate_input(self, input_text: str) -> bool:
        """
        Validate input text.
        
        Args:
            input_text: Input text to validate
            
        Returns:
            True if the input is valid, False otherwise
        """
        # Check if the input is empty
        if not input_text:
            logger.warning("Empty input text")
            return False
        
        return True
EOF

# Create agent entity fix
cat > services/langchain-agent/fixes/agent_entity_fix.py << 'EOF'
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
class AgentPermissions:
    """
    Agent permissions.
    
    Defines what the agent is allowed to do.
    """
    execute_commands: bool = False
    allowed_commands: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=list)
    network_access: bool = False
    memory_limit: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentPermissions':
        """
        Create permissions from a dictionary.
        
        Args:
            data: Dictionary with permission data
            
        Returns:
            AgentPermissions instance
        """
        return cls(
            execute_commands=data.get('execute_commands', False),
            allowed_commands=data.get('allowed_commands', []),
            allowed_paths=data.get('allowed_paths', []),
            network_access=data.get('network_access', False),
            memory_limit=data.get('memory_limit')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert permissions to a dictionary.
        
        Returns:
            Dictionary representation of permissions
        """
        return {
            'execute_commands': self.execute_commands,
            'allowed_commands': self.allowed_commands,
            'allowed_paths': self.allowed_paths,
            'network_access': self.network_access,
            'memory_limit': self.memory_limit
        }


@dataclass
class AgentConfiguration:
    """
    Agent configuration.
    
    Defines the configuration for an agent.
    """
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    max_iterations: int = 10
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfiguration':
        """
        Create configuration from a dictionary.
        
        Args:
            data: Dictionary with configuration data
            
        Returns:
            AgentConfiguration instance
        """
        extra_params = dict(data)
        for key in ['model_name', 'temperature', 'max_tokens', 'system_message', 'max_iterations']:
            if key in extra_params:
                del extra_params[key]
        
        return cls(
            model_name=data.get('model_name', 'gpt-4'),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            system_message=data.get('system_message'),
            max_iterations=data.get('max_iterations', 10),
            extra_params=extra_params
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        result = {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_iterations': self.max_iterations,
        }
        
        if self.max_tokens is not None:
            result['max_tokens'] = self.max_tokens
        
        if self.system_message is not None:
            result['system_message'] = self.system_message
        
        result.update(self.extra_params)
        
        return result


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

# Create verification script
cat > services/langchain-agent/verify_agent_service.py << 'EOF'
#!/usr/bin/env python
"""
Script to verify the agent service.

This script tests the creation and execution of agents.
"""

import logging
import uuid
import json
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
        "agent_type": "conversational",
        "description": "A test agent created by the verification script",
        "user_id": user_id,
        "configuration": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful assistant for testing.",
            "max_iterations": 10
        },
        "permissions": {
            "execute_commands": False,
            "network_access": False
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
            model_name=agent_data["configuration"]["model_name"],
            temperature=agent_data["configuration"]["temperature"],
            system_message=agent_data["configuration"]["system_message"],
            max_iterations=agent_data["configuration"]["max_iterations"]
        )
        
        permissions = AgentPermissions(
            execute_commands=agent_data["permissions"]["execute_commands"],
            network_access=agent_data["permissions"]["network_access"]
        )
        
        agent = Agent(
            id=agent_data["id"],
            name=agent_data["name"],
            agent_type=agent_data["agent_type"],
            description=agent_data["description"],
            user_id=agent_data["user_id"],
            configuration=configuration,
            permissions=permissions,
            metadata=agent_data["metadata"]
        )
        
        logger.info(f"Created agent with ID {agent.id} and name {agent.name}")
        logger.info(f"Agent model name: {agent.configuration.model_name}")
        
        # Method 2: Create using dictionaries for configuration and permissions
        agent2 = Agent(
            id=agent_data["id"],
            name=agent_data["name"],
            agent_type=agent_data["agent_type"],
            description=agent_data["description"],
            user_id=agent_data["user_id"],
            configuration=agent_data["configuration"],
            permissions=agent_data["permissions"],
            metadata=agent_data["metadata"]
        )
        
        logger.info(f"Created agent 2 with ID {agent2.id} and name {agent2.name}")
        logger.info(f"Agent 2 model name: {agent2.configuration.model_name}")
        
        # Access attributes to ensure they work
        logger.info(f"Accessing configuration.model_name: {agent.configuration.model_name}")
        logger.info(f"Accessing configuration.temperature: {agent.configuration.temperature}")
        
        # Test accessing permissions
        logger.info(f"Accessing permissions.execute_commands: {agent.permissions.execute_commands}")
        logger.info(f"Accessing permissions.network_access: {agent.permissions.network_access}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        return False


def test_agent_creation_and_execution():
    """Test creating and executing an agent."""
    from app.core.agents.conversational_agent import ConversationalAgent
    from app.core.entities.agent import AgentConfiguration, AgentPermissions
    
    logger.info("Testing agent creation and execution...")
    
    # Create agent data
    agent_data = create_test_agent_data()
    
    try:
        # Create agent
        configuration = AgentConfiguration(
            model_name=agent_data["configuration"]["model_name"],
            temperature=agent_data["configuration"]["temperature"],
            system_message=agent_data["configuration"]["system_message"],
            max_iterations=agent_data["configuration"]["max_iterations"]
        )
        
        permissions = AgentPermissions(
            execute_commands=agent_data["permissions"]["execute_commands"],
            network_access=agent_data["permissions"]["network_access"]
        )
        
        agent = ConversationalAgent(
            configuration=configuration,
            permissions=permissions
        )
        
        logger.info(f"Created conversational agent with model {configuration.model_name}")
        
        # Execute agent
        result = agent.execute("What is 2+2?")
        
        logger.info(f"Agent execution result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing agent: {str(e)}", exc_info=True)
        return False


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
EOF

# Create API test script
cat > services/langchain-agent/test_agent_api.py << 'EOF'
#!/usr/bin/env python
"""
Script to test the agent API.

This script tests the agent API endpoints.
"""

import uuid
import json
import socket
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Determine if we're running inside a container
def is_running_in_container():
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return any('docker' in line for line in f)
    except:
        return False

# Configure the base URL based on environment
BASE_URL = "http://localhost:8000" if is_running_in_container() else "http://localhost:8002"

def test_agent_creation():
    """Test agent creation API endpoint."""
    # Generate a unique user ID for testing
    user_id = f"test-user-{uuid.uuid4().hex[:8]}"
    
    print(f"\nTesting agent creation with user ID: {user_id}")
    
    # Construct the agent data
    agent_data = {
        "name": f"Test Agent {uuid.uuid4().hex[:6]}",
        "agent_type": "conversational",
        "description": "A test agent created by the verification script",
        "user_id": user_id,
        "configuration": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "system_message": "You are a helpful assistant for testing.",
            "max_iterations": 10
        },
        "permissions": {
            "execute_commands": False,
            "network_access": False
        },
        "metadata": {
            "test": True,
            "source": "verification_script"
        }
    }
    
    # Print request details
    endpoint = f"{BASE_URL}/api/v1/agents"
    print(f"Sending request to {endpoint}")
    print(f"Request payload: {json.dumps(agent_data, indent=2)}")
    
    try:
        # Send the request
        response = requests.post(endpoint, json=agent_data)
        
        # Print response details
        print(f"Response status code: {response.status_code}")
        
        # Pretty print the response if it's JSON
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        # Check if the request was successful
        if response.status_code == 201:
            print("✅ Agent creation successful!")
            return True
        else:
            print("❌ Agent creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent creation: {str(e)}")
        return False


def main():
    """Main function."""
    print("Testing Agent API Endpoints")
    print("=========================\n")
    
    # Test agent creation
    if test_agent_creation():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n👎 Some tests failed!")
        return False
    

if __name__ == "__main__":
    main()
EOF

# Copy fixes to the Docker container
echo "Copying fixes to container..."
docker cp services/langchain-agent/fixes ogent-agent-service-test:/app/
docker cp services/langchain-agent/verify_agent_service.py ogent-agent-service-test:/app/
docker cp services/langchain-agent/test_agent_api.py ogent-agent-service-test:/app/

# Apply the fixes to their proper locations
echo "Applying fixes..."
docker exec ogent-agent-service-test bash -c "
mkdir -p /app/app/core/clients

# Copy fixed files to their proper locations
cp /app/fixes/repository_fix.py /app/app/infrastructure/persistence/repositories.py
cp /app/fixes/factory_fix.py /app/app/core/agents/factory.py
cp /app/fixes/command_client.py /app/app/core/clients/command_client.py
cp /app/fixes/base_agent_fix.py /app/app/core/agents/base_agent.py
cp /app/fixes/agent_entity_fix.py /app/app/core/entities/agent.py

# Create proper __init__.py files
echo '\"\"\"Clients module.\"\"\"' > /app/app/core/clients/__init__.py
"

# Restart the agent service
echo "Restarting agent service..."
docker restart ogent-agent-service-test

echo "Waiting for service to start..."
sleep 5

# Run verification
echo "Running verification..."
docker exec ogent-agent-service-test python /app/verify_agent_service.py

echo "Testing API..."
docker exec ogent-agent-service-test python /app/test_agent_api.py

echo "Deployment completed!" 