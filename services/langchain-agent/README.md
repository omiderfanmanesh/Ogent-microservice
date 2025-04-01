# LangChain Agent Service

This service provides an API for creating, managing, and executing agents built with LangChain. The agents can be used for various tasks such as conversation, executing commands, and more.

## Directory Structure

- **app/** - Core application code
  - **core/** - Core functionality including agents, entities, and services
  - **api/** - API endpoints and controllers
  - **infrastructure/** - Database models, repositories, and other infrastructure

- **fixes/** - Fixes for various components of the service
  - Contains implementations for the agent entities, factory, repository, and more

- **scripts/** - Deployment and maintenance scripts
  - `deploy.sh` - Main deployment script for applying fixes to the service

- **tools/** - Testing, verification, and debugging tools
  - `verify_agent_service.py` - Tool for verifying agent functionality
  - `test_agent_api.py` - Tool for testing the agent API

## Getting Started

### Deploying Fixes

To deploy the latest fixes to the service:

```bash
cd services/langchain-agent/scripts
./deploy.sh
```

### Verification

After deploying, you can verify the service using:

```bash
cd services/langchain-agent/tools
python verify_agent_service.py
```

## API Endpoints

The service exposes the following API endpoints:

- **GET /api/v1/agents** - List all agents
- **POST /api/v1/agents** - Create a new agent
- **GET /api/v1/agents/{agent_id}** - Get a specific agent
- **DELETE /api/v1/agents/{agent_id}** - Delete an agent
- **POST /api/v1/agents/{agent_id}/execute** - Execute an agent with input

## Docker Container

The service runs in a Docker container named `ogent-agent-service-test`. The container exposes port 8000, which is mapped to port 8002 on the host.

## Recent Fixes

The fixes in this repository address several issues:

1. Fixed parameter naming inconsistencies between `configuration`/`config` and `model_name`/`model`
2. Added missing `AgentCallback` class to the base agent implementation
3. Corrected entity class fields to match Pydantic model expectations
4. Improved error handling and logging in the agent service

## Development

When making changes to the service, ensure that:

1. Tests pass using the verification tools
2. Naming conventions are consistent across the codebase
3. Documentation is updated to reflect any changes
4. The deployment script is updated if necessary 