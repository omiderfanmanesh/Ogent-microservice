# End-to-End Testing Plan

This document outlines the comprehensive end-to-end testing strategy for the Ogent Microservices architecture.

## Overview

End-to-end testing verifies that the entire Ogent system works together as expected, focusing on user workflows that span multiple services. This testing ensures that all microservices integrate correctly and provide a cohesive user experience.

## Testing Objectives

1. Verify all services start and communicate properly
2. Validate key user workflows across the entire system
3. Ensure data flows correctly between services
4. Test authentication and authorization across services
5. Verify real-time communication capabilities
6. Test system resilience and error handling

## End-to-End Test Script

A comprehensive end-to-end test script has been developed to automate key aspects of system verification:

**File**: `end_to_end_test.sh`

This script performs the following tests:

1. **Service Health Checks**
   - Verifies all services are running
   - Checks health endpoints of each service
   - Confirms API Gateway connectivity

2. **Authentication Testing**
   - Tests login functionality
   - Validates token generation and validation
   - Checks authorization for protected resources

3. **Command Execution Workflow**
   - Tests command execution via API
   - Verifies correct status reporting
   - Validates command output

4. **Manual Testing Instructions**
   - Provides step-by-step instructions for manual verification
   - Guides through UI testing workflows
   - Explains WebSocket testing procedures

## Key User Workflows

### 1. User Authentication

Steps:
1. User accesses the Frontend
2. User enters credentials on the login page
3. Auth Service validates credentials and issues a token
4. Frontend stores the token for subsequent requests
5. User is redirected to the dashboard

Expected Results:
- Valid credentials grant access
- Invalid credentials are rejected with appropriate error message
- Authentication token is properly stored
- Protected routes require authentication

### 2. Command Execution

Steps:
1. User navigates to the command execution page
2. User enters a command in the input field
3. Command is sent to the Command Execution service via API Gateway
4. Command is validated and executed
5. Real-time updates are sent via the Socket Service
6. Frontend displays execution progress and results

Expected Results:
- Allowed commands are executed successfully
- Disallowed commands are rejected with appropriate message
- Real-time status updates are displayed
- Command output is shown correctly
- Execution history is properly maintained

### 3. Agent Management

Steps:
1. User navigates to the agent management page
2. User creates a new agent with specific configuration
3. Agent is stored in the LangChain Agent service
4. User executes a prompt with the agent
5. Agent response is returned to the Frontend

Expected Results:
- Agent is created with specified configuration
- Agent can be retrieved and displayed
- Agent can process prompts correctly
- Agent execution is properly logged

## Testing Methods

### Automated Testing

Run the end-to-end test script:

```bash
./end_to_end_test.sh
```

The script will perform automated checks and provide instructions for manual verification steps.

### Manual Testing

1. Start all services:

```bash
docker-compose up -d
```

2. Follow the manual testing workflow:
   - Open http://localhost:3000 in a browser
   - Complete the authentication flow
   - Test each primary workflow (command execution, agent management)
   - Verify real-time updates via WebSocket

### Browser-based WebSocket Testing

For specialized WebSocket testing:
1. Open `services/frontend/test_socket_connection.html` in a browser
2. Log in to obtain an authentication token
3. Test WebSocket connectivity and real-time updates

## Test Environment Setup

### Prerequisites

- Docker and Docker Compose installed
- Git repository cloned locally
- Ports 3000, 8080, 8081 available

### Service Configuration

The end-to-end tests depend on proper configuration of all services in the `docker-compose.yml` file:

```yaml
# Key configurations for testing
environment:
  - AUTH_SERVICE_URL=http://ogent-auth-service:5000
  - COMMAND_SERVICE_URL=http://ogent-command-service:5001
  - AGENT_SERVICE_URL=http://ogent-agent-service:8000
  - SOCKET_SERVICE_URL=http://ogent-socket-service:3002
```

## Testing Matrix

| Test Area | Automated | Manual | Priority |
|-----------|-----------|--------|----------|
| Service Health | ✅ | ❌ | High |
| Authentication | ✅ | ✅ | High |
| Command Execution | ✅ | ✅ | High |
| Agent Management | ❌ | ✅ | Medium |
| WebSocket Connectivity | ✅ | ✅ | High |
| UI Functionality | ❌ | ✅ | Medium |
| Error Handling | ✅ | ✅ | Medium |
| Performance | ❌ | ❌ | Low |

## Service Dependencies

The following diagram illustrates the service dependencies for end-to-end testing:

```
Frontend → API Gateway → Auth Service
                       → Command Execution Service → Socket Service
                       → LangChain Agent Service
                       → Socket Service
```

Each service must be operational for complete end-to-end testing.

## Troubleshooting

Common issues and resolution steps:

1. **Service Unavailable**
   - Check Docker container status
   - Verify network connectivity between services
   - Check service logs for errors

2. **Authentication Failures**
   - Verify Auth Service is running
   - Check token format and expiration
   - Ensure correct credentials are being used

3. **Command Execution Issues**
   - Check Command Execution service logs
   - Verify command allowlist configuration
   - Ensure proper permissions are set

4. **WebSocket Connection Problems**
   - Verify Socket Service is running
   - Check browser console for connection errors
   - Ensure authentication token is valid

## Test Report Format

Test results should be documented with:

- Date and time of test execution
- Environment details
- Test cases executed
- Pass/fail status for each case
- Issues encountered
- Screenshots or logs where applicable

## Conclusion

The end-to-end testing strategy ensures that the Ogent Microservices architecture functions correctly as an integrated system. By validating key user workflows across all services, we can ensure a smooth user experience and reliable system operation.

Regular execution of these tests helps identify integration issues early and maintain the quality of the overall system. 