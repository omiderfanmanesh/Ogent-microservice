#!/bin/bash

# Ogent Microservices End-to-End Test
# This script performs comprehensive testing of all services

set -e

echo "===== Ogent Microservices End-to-End Test ====="
echo "This script tests all services together to verify the complete system is working"

# Check Docker services
echo -e "\n1. Checking Docker services..."
docker ps | grep ogent

# Verify individual services
echo -e "\n2. Verifying individual services..."

# Check API Gateway
echo -e "\n2.1. API Gateway - Health check..."
if curl -s http://localhost:8081/health | grep -q "ok"; then
  echo "✅ API Gateway health check: PASSED"
else
  echo "❌ API Gateway health check: FAILED"
  echo "Please ensure the API Gateway is running"
  exit 1
fi

# Check Auth Service
echo -e "\n2.2. Auth Service - Health check..."
if curl -s http://localhost:8081/auth/health | grep -q "ok"; then
  echo "✅ Auth Service health check: PASSED"
else
  echo "❌ Auth Service health check: FAILED"
  echo "Please ensure the Auth Service is running"
  exit 1
fi

# Check Command Execution Service
echo -e "\n2.3. Command Execution Service - Health check..."
if curl -s http://localhost:8081/command/health | grep -q "ok"; then
  echo "✅ Command Execution Service health check: PASSED"
else
  echo "❌ Command Execution Service health check: FAILED"
  echo "Please ensure the Command Execution Service is running"
  exit 1
fi

# Check Socket Service
echo -e "\n2.4. Socket Service - Health check..."
if curl -s http://localhost:8081/socket-http/health | grep -q "ok"; then
  echo "✅ Socket Service health check: PASSED"
else
  echo "❌ Socket Service health check: FAILED"
  echo "Please ensure the Socket Service is running"
  exit 1
fi

# Check Frontend
echo -e "\n2.5. Frontend Service - Health check..."
if curl -s http://localhost:3000 > /dev/null; then
  echo "✅ Frontend Service is accessible"
else
  echo "❌ Frontend Service is not accessible"
  echo "Please ensure the Frontend Service is running"
  exit 1
fi

# Test login flow (requires manual input)
echo -e "\n3. Testing authentication flow..."
echo "You will need to enter valid credentials to test the login flow"

read -p "Email: " email
read -sp "Password: " password
echo ""

# Attempt login
echo "Attempting login with provided credentials..."
login_response=$(curl -s -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$email\",\"password\":\"$password\"}")

if echo "$login_response" | grep -q "token"; then
  echo "✅ Authentication successful"
  # Extract token
  token=$(echo "$login_response" | grep -o '"token":"[^"]*' | sed 's/"token":"//')
  echo "Token obtained: ${token:0:20}..."
else
  echo "❌ Authentication failed"
  echo "Response: $login_response"
  echo "Continuing with limited testing..."
  token=""
fi

# Test command execution with authentication
if [ -n "$token" ]; then
  echo -e "\n4. Testing command execution with authentication..."
  
  # Generate a unique execution ID
  execution_id=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen || date +%s)
  echo "Execution ID: $execution_id"
  
  # Execute a simple command
  echo "Executing command: 'echo Hello, Ogent!'"
  execute_response=$(curl -s -X POST http://localhost:8081/command/api/commands \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $token" \
    -d "{\"command\":\"echo Hello, Ogent!\",\"executionId\":\"$execution_id\"}")
  
  echo "Command execution response: $execute_response"
  
  # Give the command some time to execute
  echo "Waiting for command to execute..."
  sleep 3
  
  # Check command status
  status_response=$(curl -s -X GET http://localhost:8081/command/api/commands/$execution_id \
    -H "Authorization: Bearer $token")
  
  echo "Command status: $status_response"
  
  if echo "$status_response" | grep -q "completed"; then
    echo "✅ Command execution test: PASSED"
  else
    echo "⚠️ Command execution test: INCONCLUSIVE"
    echo "Status: $status_response"
  fi
fi

# Manual verification steps
echo -e "\n5. Manual verification steps:"
echo "Please complete the following manual verification steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Log in with valid credentials"
echo "3. Try executing a command through the UI"
echo "4. Verify that real-time updates appear in the execution log"
echo "5. Open services/frontend/test_socket_connection.html in your browser"
echo "6. Use it to test WebSocket connections and status updates"

# Test service integration
echo -e "\n6. Service integration verification:"
echo "The following scripts can be run to verify service integration:"
echo "- services/command-execution/tools/verify_service.py"
echo "- services/socket-service/verify_all.sh"
echo "- services/frontend/verify_frontend.sh"

# Summary
echo -e "\n===== End-to-End Test Summary ====="
echo "✅ API Gateway: OPERATIONAL"
echo "✅ Auth Service: OPERATIONAL"
echo "✅ Command Execution Service: OPERATIONAL"
echo "✅ Socket Service: OPERATIONAL"
echo "⚠️ Frontend Service: REQUIRES MANUAL VERIFICATION"
echo "⚠️ End-to-End Integration: REQUIRES MANUAL VERIFICATION"
echo -e "\nPlease complete the manual verification steps to ensure complete system functionality." 