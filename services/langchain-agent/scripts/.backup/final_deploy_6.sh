#!/bin/bash
set -e

echo "==============================================="
echo "Deploying fixes for the langchain-agent service"
echo "==============================================="

# Create directory for fixes inside the services/langchain-agent
mkdir -p services/langchain-agent/fixes

# Copy the existing fixes to the Docker container
echo "Copying fixes to container..."
docker cp services/langchain-agent/fixes/repository_fix.py ogent-agent-service-test:/app/fixes/
docker cp services/langchain-agent/fixes/factory_fix.py ogent-agent-service-test:/app/fixes/
docker cp services/langchain-agent/fixes/command_client.py ogent-agent-service-test:/app/fixes/
docker cp services/langchain-agent/fixes/base_agent_fix.py ogent-agent-service-test:/app/fixes/
docker cp services/langchain-agent/fixes/agent_entity_fix.py ogent-agent-service-test:/app/fixes/
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

# Make sure we have the proper __init__.py files
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