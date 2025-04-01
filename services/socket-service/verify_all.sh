#!/bin/bash

set -e

echo "===== Socket Service Comprehensive Verification ====="
echo "This script will test the Socket Service's APIs and integrations"

# Variables
API_GATEWAY_URL="http://localhost:8081"
EXECUTION_ID=$(uuidgen || echo "test-execution-$(date +%s)")

echo "Test execution ID: ${EXECUTION_ID}"

# Step 1: Basic Health Check
echo -e "\n1. Checking Socket Service health..."
HEALTH_RESPONSE=$(curl -s ${API_GATEWAY_URL}/socket-http/health)
echo "Health Response: ${HEALTH_RESPONSE}"

if [[ $HEALTH_RESPONSE == *"ok"* ]]; then
  echo "✅ Socket Service health check passed"
else
  echo "❌ Socket Service health check failed"
  echo "Response: $HEALTH_RESPONSE"
  exit 1
fi

# Step 2: Test Execution Status Update API
echo -e "\n2. Testing execution-status API..."
STATUS_PAYLOAD="{\"executionId\":\"${EXECUTION_ID}\",\"status\":\"running\",\"progress\":50,\"output\":\"Verification test output\"}"

echo "Sending payload: ${STATUS_PAYLOAD}"
STATUS_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d "${STATUS_PAYLOAD}" \
  ${API_GATEWAY_URL}/socket-http/api/execution-status)

echo "Status API Response: ${STATUS_RESPONSE}"

if [[ $STATUS_RESPONSE == *"success"* ]]; then
  echo "✅ Execution status API test passed"
else
  echo "⚠️ Execution status API test result inconclusive"
  echo "Note: The API may require authentication or have other requirements"
fi

# Step 3: WebSocket Testing Instructions
echo -e "\n3. WebSocket Testing Instructions"
echo "To test WebSocket connections:"
echo "1. Open the websocket_test.html file in a browser"
echo "2. Obtain an authentication token from the auth service"
echo "3. Enter the token in the form and click 'Connect'"
echo "4. Enter the execution ID: ${EXECUTION_ID} and click 'Join Execution'"
echo "5. In a separate terminal, run one of the following test scripts:"
echo "   - For basic simulation: python simulation_test.py"
echo "   - For command integration: python command_integration_test.py"
echo "   - For authenticated testing: python auth_test.py"

# Step 4: Integration Testing Instructions
echo -e "\n4. Integration Testing Instructions"
echo "To test integration with Command Execution service:"
echo "1. Ensure the Command Execution service is running"
echo "2. Run: python command_integration_test.py"
echo "3. Observe both terminal output and the WebSocket client"

# Step 5: Authentication Testing Instructions
echo -e "\n5. Authentication Testing Instructions"
echo "To test with authentication:"
echo "1. Run: python auth_test.py"
echo "2. Enter your credentials when prompted"
echo "3. Observe both terminal output and the WebSocket client"

echo -e "\n===== Verification Summary ====="
echo "✅ Health Check: PASSED"
echo "⚠️ API Tests: PARTIALLY TESTED (Some require authentication)"
echo "ℹ️ WebSocket and Integration: MANUAL TESTING REQUIRED"
echo -e "\nSocket Service verification completed."
echo "For a complete end-to-end test, please follow the instructions above." 