#!/bin/bash

# Frontend Verification Script
# This script checks the frontend's connection to all required backend services

echo "===== Frontend Service Verification ====="

# Check if Docker is running
echo "Checking if Docker is running..."
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker first."
  exit 1
fi

# Check if the frontend container is running
echo "Checking if the frontend container is running..."
if ! docker ps | grep -q "ogent-frontend"; then
  echo "❌ Frontend container is not running. Start it with 'docker-compose up -d'."
  exit 1
fi

# Check if the frontend is accessible
echo "Checking if the frontend is accessible..."
if ! curl -s http://localhost:3000 > /dev/null; then
  echo "❌ Frontend is not accessible at http://localhost:3000"
  exit 1
else
  echo "✅ Frontend is accessible at http://localhost:3000"
fi

# Check API Gateway connection
echo "Checking API Gateway connection..."
if ! curl -s http://localhost:8081/health > /dev/null; then
  echo "❌ API Gateway is not accessible at http://localhost:8081"
else
  echo "✅ API Gateway is accessible"
fi

# Check Auth Service connection
echo "Checking Auth Service connection..."
if ! curl -s http://localhost:8081/auth/health > /dev/null; then
  echo "❌ Auth Service is not accessible through the API Gateway"
else
  echo "✅ Auth Service is accessible through the API Gateway"
fi

# Check Command Execution Service connection
echo "Checking Command Execution Service connection..."
if ! curl -s http://localhost:8081/command/health > /dev/null; then
  echo "❌ Command Execution Service is not accessible through the API Gateway"
else
  echo "✅ Command Execution Service is accessible through the API Gateway"
fi

# Check Socket Service connection
echo "Checking Socket Service connection..."
if ! curl -s http://localhost:8081/socket-http/health > /dev/null; then
  echo "❌ Socket Service is not accessible through the API Gateway"
else
  echo "✅ Socket Service is accessible through the API Gateway"
fi

# Check if the frontend environment variables are set correctly
echo "Checking frontend environment variables..."
FRONTEND_ENV=$(docker exec $(docker ps | grep ogent-frontend | awk '{print $1}') env | grep REACT_APP)
echo "Frontend environment variables:"
echo "$FRONTEND_ENV"

echo -e "\n===== Verification Summary ====="
echo "To complete the frontend verification:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Login with a valid user account"
echo "3. Try executing a command and verify that real-time updates are received"
echo "4. Check that all services can be accessed through the frontend UI"
echo -e "\nEnd of verification" 