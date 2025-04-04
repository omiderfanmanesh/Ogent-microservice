# Command Execution Service Test Plan

This document outlines the testing strategy and approach for the Command Execution Service in the Ogent Microservices architecture.

## Overview

The Command Execution Service is responsible for securely executing system commands with proper permissions and security constraints. It provides a controlled environment for running commands and tracking their execution status in real-time.

## Testing Objectives

1. Verify the Command Execution Service is operational
2. Test execution of allowed commands
3. Ensure disallowed commands are properly rejected
4. Validate command cancellation functionality
5. Test complex commands with arguments and pipes
6. Verify execution timeouts and resource limits
7. Confirm integration with the Socket Service for real-time updates

## Testing Tools

The following tools have been created to facilitate testing of the Command Execution Service:

### 1. Service Verification Script

**File**: `services/command-execution/tools/verify_service.py`

A Python script that performs comprehensive verification of the Command Execution Service:
- Checks service health and accessibility
- Tests execution of allowed commands
- Verifies rejection of disallowed commands
- Tests complex command execution with pipes and redirects
- Validates timeout handling

### 2. Test API Script

**File**: `services/command-execution/tests/test_command_api.py`

A Python script that tests the Command Execution Service API:
- Tests API endpoints using pytest
- Validates request/response formats
- Tests edge cases and error handling
- Verifies execution ID format and consistency

### 3. Integration Test Script

**File**: `services/command-execution/tools/verify_integration.py`

A script that tests integration with other services:
- Tests authentication integration with Auth Service
- Verifies real-time updates with Socket Service
- Validates agent execution with LangChain Agent Service

## Test Cases

### Health Check Tests

1. **Basic Health Check**
   - Endpoint: `GET /health`
   - Expected Result: Returns status "ok"

### Command Execution Tests

1. **Execute Allowed Command**
   - Endpoint: `POST /api/commands`
   - Input: `{"command": "echo 'Hello, World!'", "executionId": "test-id"}`
   - Expected Result: Command executes successfully with output "Hello, World!"

2. **Execute Disallowed Command**
   - Endpoint: `POST /api/commands`
   - Input: `{"command": "rm -rf /", "executionId": "test-id"}`
   - Expected Result: Command is rejected with appropriate error

3. **Execute Complex Command**
   - Endpoint: `POST /api/commands`
   - Input: `{"command": "echo 'Test' | grep Test", "executionId": "test-id"}`
   - Expected Result: Command executes successfully with piped output

4. **Execute Long-Running Command**
   - Endpoint: `POST /api/commands`
   - Input: `{"command": "sleep 10", "executionId": "test-id"}`
   - Expected Result: Command execution status shows "running" initially, then "completed"

### Execution Status Tests

1. **Get Execution Status**
   - Endpoint: `GET /api/commands/:executionId`
   - Expected Result: Returns current status, output, and metadata

2. **Track Status Changes**
   - Process: Execute command, check status repeatedly
   - Expected Result: Status transitions from "scheduled" to "running" to "completed"

### Cancellation Tests

1. **Cancel Execution**
   - Endpoint: `POST /api/commands/:executionId/cancel`
   - Expected Result: Running command is cancelled, status changes to "cancelled"

### Security Tests

1. **Command Injection Prevention**
   - Input: Commands with injection attempts (e.g., `echo 'test' && rm -rf /`)
   - Expected Result: Injection attempts are detected and rejected

2. **User Permission Validation**
   - Test: Attempt to execute commands with different user permissions
   - Expected Result: Commands respect user permission levels

## Test Execution

### Automated Tests

Run the verification script:

```bash
cd services/command-execution/tools
python verify_service.py
```

Run the API tests:

```bash
cd services/command-execution
pytest tests/test_command_api.py
```

### Manual Tests

1. Start the Command Execution Service:

```bash
docker-compose up -d command-execution
```

2. Send test requests using curl:

```bash
curl -X POST http://localhost:8081/command/api/commands \
  -H "Content-Type: application/json" \
  -d '{"command": "echo Hello", "executionId": "test-123"}'
```

3. Check execution status:

```bash
curl http://localhost:8081/command/api/commands/test-123
```

## Integration Testing

The Command Execution Service integrates with several other services:

1. **Auth Service**: For validating user permissions
2. **Socket Service**: For real-time status updates
3. **LangChain Agent Service**: For agent-initiated commands

Test these integrations using the integration verification script:

```bash
cd services/command-execution/tools
python verify_integration.py
```

## Test Environment

- **Development**: Local Docker environment
- **Testing**: CI/CD pipeline tests
- **Staging**: Pre-production environment tests

## Dependencies

The Command Execution Service testing depends on:

- Docker for containerization
- Python for test scripts
- pytest for API testing
- curl for manual API testing

## Troubleshooting

Common issues and resolution steps:

1. **Service Unavailable**
   - Check if the Docker container is running
   - Verify network connectivity
   - Check service logs for errors

2. **Command Not Allowed**
   - Verify the command against the allowlist in the configuration
   - Check for syntax issues in the command

3. **Socket Updates Not Working**
   - Ensure Socket Service is running
   - Check connection configuration
   - Verify the execution ID format

4. **Permission Issues**
   - Check user permissions configuration
   - Verify authentication token
   - Check file system permissions in the container

## Best Practices

1. Always test with unique execution IDs to avoid conflicts
2. Verify commands are in the allowlist before testing
3. Test edge cases like empty commands, long-running commands, and commands with special characters
4. Check both success and failure scenarios
5. Monitor resource usage during command execution tests

## Conclusion

The Command Execution Service testing strategy ensures:

- Commands are executed securely and properly
- Security constraints are enforced
- Performance and reliability meets requirements
- Integration with other services functions correctly

Regular execution of these tests helps maintain the reliability and security of the command execution functionality in the Ogent Microservices architecture. 