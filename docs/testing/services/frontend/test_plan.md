# Frontend Test Plan

This document outlines the testing strategy and approach for the Frontend service in the Ogent Microservices architecture.

## Overview

The Frontend service provides the user interface for the Ogent platform. It is a React-based single-page application that interacts with all backend services through the API Gateway. The Frontend includes:

- User authentication interface
- Command execution management
- Agent configuration and management
- Real-time execution monitoring via WebSockets

## Testing Objectives

1. Verify the Frontend is properly configured and accessible
2. Ensure integration with backend services through the API Gateway
3. Test WebSocket connectivity for real-time updates
4. Validate user authentication flows
5. Verify command execution functionality

## Testing Tools

The following tools have been created to facilitate testing of the Frontend service:

### 1. Frontend Verification Script

**File**: `services/frontend/verify_frontend.sh`

A shell script that verifies the Frontend service's basic functionality:
- Checks if the service is running
- Verifies accessibility at http://localhost:3000
- Tests connectivity to the API Gateway
- Checks connectivity to backend services through the API Gateway
- Verifies environment configuration

### 2. WebSocket Connection Test Tool

**File**: `services/frontend/test_socket_connection.html`

A standalone HTML page that tests WebSocket connectivity:
- Establishes Socket.IO connections to the Socket Service through the API Gateway
- Tests authentication with valid tokens
- Allows joining and leaving execution rooms
- Simulates sending execution status updates
- Displays real-time connection status and received events

## Test Cases

### Basic Functionality Tests

1. **Service Accessibility**
   - Test: Frontend accessibility at http://localhost:3000
   - Expected Result: Frontend loads without errors

2. **API Gateway Connectivity**
   - Test: Connection to the API Gateway
   - Expected Result: API Gateway is accessible

3. **Backend Service Connectivity**
   - Test: Connection to backend services through the API Gateway
   - Expected Result: All backend services are accessible

### User Interface Tests

1. **Login Flow**
   - Test: User authentication process
   - Expected Result: User can log in and obtain a token

2. **Command Execution UI**
   - Test: Command input and execution through the UI
   - Expected Result: Commands can be executed and results displayed

3. **Real-time Updates**
   - Test: Execution status updates in real-time
   - Expected Result: UI displays status updates as they occur

### Integration Tests

1. **Authentication Integration**
   - Test: Token-based authentication with the Auth Service
   - Expected Result: Valid tokens grant access, invalid tokens are rejected

2. **Command Service Integration**
   - Test: Command execution through the API Gateway
   - Expected Result: Commands are executed and status is retrievable

3. **WebSocket Integration**
   - Test: WebSocket connection and event handling
   - Expected Result: Real-time updates are received and displayed

## Test Execution

### Automated Tests

Run the Frontend verification script:

```bash
cd services/frontend
./verify_frontend.sh
```

### Manual Tests

1. Start all services:

```bash
docker-compose up -d
```

2. Access the Frontend:
   - Open http://localhost:3000 in a browser
   - Log in with valid credentials
   - Test command execution functionality
   - Verify real-time updates

3. Test WebSocket connections:
   - Open services/frontend/test_socket_connection.html in a browser
   - Obtain a token by logging in to the Frontend
   - Test WebSocket connectivity and real-time updates

## End-to-End Testing

The Frontend is a critical component in end-to-end testing of the entire system. The following end-to-end test flow is recommended:

1. Log in to the Frontend
2. Create or select an agent
3. Execute a command
4. Verify real-time status updates
5. View command execution results

## Test Environment

- **Development**: Local Docker environment
- **Testing**: Integrated test environment with all services
- **Production**: Production-like environment with real data

## Dependencies

The Frontend testing depends on:

- API Gateway (for routing requests)
- Auth Service (for authentication)
- Command Execution Service (for command execution)
- Socket Service (for real-time updates)
- LangChain Agent Service (for agent management)

## Troubleshooting

Common issues and resolution steps:

1. **Frontend Not Loading**
   - Check if the Frontend container is running
   - Verify network connectivity and port mapping

2. **API Gateway Connection Issues**
   - Ensure the API Gateway is running
   - Check environment variables for correct API URL

3. **WebSocket Connection Failures**
   - Verify Socket Service is running
   - Check authentication token validity
   - Inspect browser console for connection errors

4. **Authentication Problems**
   - Clear browser cache and cookies
   - Check token expiration time
   - Verify correct credentials are being used

## UI Component Testing

The Frontend consists of several key UI components that should be tested:

1. **Login/Registration Forms**
   - Input validation
   - Error handling
   - Success flows

2. **Command Execution Component**
   - Command input
   - Execution control (start, cancel)
   - Status and progress display

3. **Execution Log Display**
   - Real-time updates
   - Formatting of different message types
   - Scrolling and navigation

4. **Agent Management Interface**
   - Agent creation and editing
   - Configuration options
   - Permission controls

## Conclusion

The Frontend testing strategy ensures:

- A functional and accessible user interface
- Proper integration with all backend services
- Reliable real-time communications
- Smooth user authentication and authorization
- Effective command execution and monitoring

These tests help maintain the quality and reliability of the user experience in the Ogent Microservices architecture. 