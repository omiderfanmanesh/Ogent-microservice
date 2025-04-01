#!/bin/bash
# Script to deploy langchain-agent service fixes

set -e
echo "Deploying fixes for the langchain-agent service..."

# Copy fixed files to Docker container
echo "Copying fix for agent_result.py..."
docker cp fixes/agent_result.py ogent-agent-service-test:/app/app/core/agents/agent_result.py

echo "Copying fix for factory.py..."
docker cp fixes/factory.py ogent-agent-service-test:/app/app/core/agents/factory.py

# Fix agent_service.py
echo "Applying fix for agent_service.py..."
AGENT_SERVICE_FILE=$(docker exec ogent-agent-service-test cat /app/app/core/services/agent_service.py)
FIXED_CREATE_AGENT=$(cat fixes/agent_service.py)

# Extract the method definition
METHOD_START="async def create_agent"
METHOD_END="return created_agent"

# Create a temporary file with the entire content
TMP_FILE=$(mktemp)
echo "$AGENT_SERVICE_FILE" > $TMP_FILE

# Replace the create_agent method with our fixed version
# This is a simplistic approach - in a real scenario, we might use sed with proper capture groups
awk -v method_start="$METHOD_START" -v method_end="$METHOD_END" -v replacement="$FIXED_CREATE_AGENT" '
BEGIN {
    in_method = 0
    matched = 0
}
{
    if ($0 ~ method_start) {
        print replacement
        in_method = 1
        matched = 1
        next
    }
    
    if (in_method) {
        if ($0 ~ method_end) {
            in_method = 0
            next
        }
        next
    }
    
    print
}
END {
    if (!matched) {
        print "Error: Could not find method to replace"
        exit 1
    }
}
' $TMP_FILE > agent_service.py.fixed

docker cp agent_service.py.fixed ogent-agent-service-test:/app/app/core/services/agent_service.py
rm -f agent_service.py.fixed

# Fix conversational_agent.py
echo "Applying fix for conversational_agent.py..."
CONV_AGENT_FILE=$(docker exec ogent-agent-service-test cat /app/app/core/agents/conversational_agent.py)
FIXED_RUN_METHOD=$(cat fixes/conversational_agent.py)

# Extract the method definition
METHOD_START="async def run"
METHOD_END="return AgentResult"

# Create a temporary file with the entire content
TMP_FILE=$(mktemp)
echo "$CONV_AGENT_FILE" > $TMP_FILE

# Replace the run method with our fixed version
awk -v method_start="$METHOD_START" -v method_end="$METHOD_END" -v replacement="$FIXED_RUN_METHOD" '
BEGIN {
    in_method = 0
    matched = 0
}
{
    if ($0 ~ method_start) {
        print replacement
        in_method = 1
        matched = 1
        next
    }
    
    if (in_method) {
        if ($0 ~ method_end) {
            in_method = 0
            next
        }
        next
    }
    
    print
}
END {
    if (!matched) {
        print "Error: Could not find method to replace"
        exit 1
    }
}
' $TMP_FILE > conversational_agent.py.fixed

docker cp conversational_agent.py.fixed ogent-agent-service-test:/app/app/core/agents/conversational_agent.py
rm -f conversational_agent.py.fixed

# Restart the service to apply changes
echo "Restarting the agent service..."
docker restart ogent-agent-service-test

echo "Fixes deployed successfully! Waiting for service to start..."
sleep 5
echo "Done. The service should now be functioning correctly." 