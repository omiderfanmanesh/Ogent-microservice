#!/bin/bash
set -e

echo "==============================================="
echo "Deploying fixes for the langchain-agent service"
echo "==============================================="

# Create directory for fixes in the Docker container
echo "Setting up directories in container..."
docker exec ogent-agent-service-test bash -c "mkdir -p /app/fixes /app/app/core/clients"

# Copy fixes to the Docker container
echo "Copying fixes to container..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

docker cp "$ROOT_DIR/fixes/repository.py" ogent-agent-service-test:/app/fixes/
docker cp "$ROOT_DIR/fixes/factory.py" ogent-agent-service-test:/app/fixes/
docker cp "$ROOT_DIR/fixes/command_client.py" ogent-agent-service-test:/app/fixes/
docker cp "$ROOT_DIR/fixes/base_agent.py" ogent-agent-service-test:/app/fixes/
docker cp "$ROOT_DIR/fixes/agent_entity.py" ogent-agent-service-test:/app/fixes/

# Copy verification tools
docker cp "$ROOT_DIR/tools/verify_agent_service.py" ogent-agent-service-test:/app/
docker cp "$ROOT_DIR/tools/test_agent_api.py" ogent-agent-service-test:/app/

# Apply the fixes to their proper locations
echo "Applying fixes..."
docker exec ogent-agent-service-test bash -c "
# Copy fixed files to their proper locations
cp /app/fixes/repository.py /app/app/infrastructure/persistence/repositories.py
cp /app/fixes/factory.py /app/app/core/agents/factory.py
cp /app/fixes/command_client.py /app/app/core/clients/command_client.py
cp /app/fixes/base_agent.py /app/app/core/agents/base_agent.py
cp /app/fixes/agent_entity.py /app/app/core/entities/agent.py

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