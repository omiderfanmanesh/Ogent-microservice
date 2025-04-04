# Socket Service Test Plan

This document outlines the testing strategy and approach for the Socket Service in the Ogent Microservices architecture.

## Overview

The Socket Service is responsible for real-time communication between the server and clients using WebSockets. It provides functionality for:

- Real-time execution status updates
- Client subscription to specific execution events
- Authenticated WebSocket connections
- Integration with the Command Execution service

## Testing Objectives

1. Verify the Socket Service is operational and accessible
2. Ensure WebSocket connections can be established with proper authentication
3. Test execution status update functionality
4. Verify client subscription and event broadcasting
5. Confirm integration with the Command Execution service

## Testing Tools

The following tools have been created to facilitate testing of the Socket Service:

### 1. WebSocket Client (Browser-based)

**File**: `services/socket-service/websocket_test.html`

A browser-based WebSocket client that allows testing Socket.IO connections:
- Establish authenticated WebSocket connections
- Join/leave execution rooms
- Receive real-time execution updates
- Test connection handling and error scenarios

### 2. Execution Status Simulation

**File**: `services/socket-service/simulation_test.py`

A Python script that simulates execution status updates:
- Generates a unique execution ID
- Sends sequential status updates to the Socket Service
- Simulates different execution states (queued, running, completed, failed)
- Provides progress updates and sample output

### 3. Command Integration Test

**File**: `services/socket-service/command_integration_test.py`

A script that tests the integration between the Command Execution service and Socket Service:
- Notifies the Socket Service about a new execution
- Schedules a command via the Command Execution service
- Polls for execution status updates
- Sends final status to the Socket Service

### 4. Authentication Testing

**File**: `services/socket-service/auth_test.py`

A script for testing the Socket Service with authentication:
- Authenticates with the Auth Service to obtain a token
- Uses the token to access Socket Service APIs
- Tests various authenticated API endpoints
- Verifies authorization requirements

### 5. Comprehensive Verification Script

**File**: `services/socket-service/verify_all.sh`

A shell script that performs comprehensive verification of the Socket Service:
- Checks service health and availability
- Tests API endpoints with sample data
- Provides instructions for manual WebSocket testing
- Verifies integration with other services

## Test Cases

### API Tests

1. **Health Check**
   - Endpoint: `GET /health`
   - Expected Result: Returns status "ok"

2. **Execution Status Update**
   - Endpoint: `POST /api/execution-status`
   - Input: Execution ID, status, progress, output
   - Expected Result: Status update is broadcast to connected clients

3. **Start Execution**
   - Endpoint: `POST /api/start-execution`
   - Input: Execution ID, agent info, command
   - Expected Result: Execution start event is broadcast

### WebSocket Tests

1. **Connection Authentication**
   - Test: Connect with and without valid authentication token
   - Expected Result: Connection succeeds with valid token, fails without

2. **Room Subscription**
   - Test: Join and leave execution rooms
   - Expected Result: Client receives updates for joined rooms only

3. **Real-time Updates**
   - Test: Send status updates while clients are connected
   - Expected Result: Updates are received in real-time by subscribed clients

### Integration Tests

1. **Command Execution Integration**
   - Test: Execute a command and verify status updates
   - Expected Result: Socket Service receives and broadcasts updates

2. **Authentication Integration**
   - Test: Verify token validation with Auth Service
   - Expected Result: Invalid tokens are rejected

## Test Execution

### Automated Tests

Run the comprehensive verification script:

```bash
cd services/socket-service
./verify_all.sh
```

### Manual Tests

1. Start the Socket Service and other required services:

```bash
docker-compose up -d
```

2. Open the WebSocket test client in a browser:

```
services/socket-service/websocket_test.html
```

3. Log in to obtain an authentication token

4. Test WebSocket connections and real-time updates

## Test Environment

- **Development**: Local Docker environment
- **Testing**: Integrated test environment
- **Production**: Production-like staging environment

## Dependencies

The Socket Service testing depends on:

- Auth Service (for authentication tokens)
- Command Execution Service (for integration testing)
- API Gateway (for routing requests)

## Troubleshooting

Common issues and resolution steps:

1. **Connection Refused**
   - Ensure Socket Service is running
   - Check the correct hostname/port is being used

2. **Authentication Failures**
   - Verify token format and expiration
   - Check Auth Service connectivity

3. **Missing Updates**
   - Confirm client has joined the correct execution room
   - Verify Command Execution service is sending updates

## Conclusion

The Socket Service testing strategy ensures:

- Reliable real-time communication
- Proper authentication and authorization
- Successful integration with other services
- Consistent event broadcasting to subscribed clients

These tests help maintain the reliability and performance of the real-time aspects of the Ogent Microservices architecture. 