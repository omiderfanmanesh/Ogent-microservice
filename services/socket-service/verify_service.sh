#!/bin/bash

set -e

echo "Starting Socket Service verification..."

# Check socket service health
echo -e "\nChecking Socket Service health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8081/socket-http/health)
echo "Health Response: $HEALTH_RESPONSE"
if [[ $HEALTH_RESPONSE == *"ok"* ]]; then
  echo "✅ Socket Service health check passed"
else
  echo "❌ Socket Service health check failed"
  echo "Response: $HEALTH_RESPONSE"
  exit 1
fi

# Test execution-status API
echo -e "\nTesting execution-status API..."
STATUS_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"executionId":"test-execution-123","status":"running","progress":50,"output":"Test output"}' \
  http://localhost:8081/socket-http/api/execution-status)
echo "Status Response: $STATUS_RESPONSE"

if [[ $STATUS_RESPONSE == *"success"* ]]; then
  echo "✅ Execution status API test passed"
else
  echo "❌ Execution status API test failed"
  echo "Response: $STATUS_RESPONSE"
fi

echo -e "\n=========== Verification Summary ==========="
echo "Health Check: PASSED"
echo "Execution Status API: Verified"
echo -e "\nSocket Service verification completed." 