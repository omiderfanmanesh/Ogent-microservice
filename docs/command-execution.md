# Command Execution Service

The Command Execution Service is responsible for securely executing system commands in the Ogent Microservice system. It provides a controlled environment for running commands with proper permissions and security constraints.

## Overview

The Command Execution Service is implemented using Python (Flask) and provides the following functionality:

- **Secure Command Execution**: Executes system commands in a sandboxed environment
- **Permission Controls**: Enforces fine-grained permissions for command execution
- **Execution Status Tracking**: Tracks the status and output of command executions
- **Real-time Output Streaming**: Provides real-time updates on command execution progress

## Security Features

The Command Execution Service includes several security features:

1. **Command Allowlist**: Only pre-approved commands can be executed
2. **Execution Sandboxing**: Commands are executed in a controlled environment
3. **User Permission Checks**: Commands can only be executed by authorized users
4. **Input Sanitization**: Command inputs are sanitized to prevent injection attacks
5. **Resource Limits**: CPU, memory, and execution time limits are enforced

## API Endpoints

### Health Check

```
GET /health
```

Returns the health status of the service.

Response:
```json
{
  "status": "ok"
}
```

### Execute Command

```
POST /api/commands
```

Executes a system command.

Request:
```json
{
  "command": "echo 'Hello, World!'",
  "executionId": "unique-execution-id"
}
```

Response:
```json
{
  "executionId": "unique-execution-id",
  "status": "scheduled"
}
```

### Get Execution Status

```
GET /api/commands/:executionId
```

Retrieves the status of a command execution.

Response:
```json
{
  "executionId": "unique-execution-id",
  "status": "completed",
  "command": "echo 'Hello, World!'",
  "output": "Hello, World!",
  "exitCode": 0,
  "startTime": "2023-03-15T12:34:56Z",
  "endTime": "2023-03-15T12:34:57Z"
}
```

### Cancel Execution

```
POST /api/commands/:executionId/cancel
```

Cancels a running command execution.

Response:
```json
{
  "executionId": "unique-execution-id",
  "status": "cancelled"
}
```

## Command Permissions

The Command Execution Service uses a comprehensive permission system:

1. **Global Allowlist**: A list of generally allowed commands (e.g., `ls`, `echo`, `cat`)
2. **User-specific Permissions**: Additional commands allowed for specific users
3. **Protected Directories**: Restrictions on accessing sensitive directories
4. **Protected Operations**: Restrictions on potentially harmful operations

## Configuration

The Command Execution Service is configured using environment variables:

```yaml
services:
  command-execution:
    build:
      context: ./services/command-execution
    environment:
      - ALLOWED_COMMANDS=ls,echo,cat,grep,find,pwd
      - MAX_EXECUTION_TIME=60
      - AUTH_SERVICE_URL=http://ogent-auth-service:5000
      - SOCKET_SERVICE_URL=http://ogent-socket-service:3002
```

## Integration with Socket Service

The Command Execution Service integrates with the Socket Service to provide real-time updates:

1. When a command execution starts, it notifies the Socket Service
2. During execution, it sends progress updates
3. Upon completion, it sends the final status and output

## Execution Workflow

1. The service receives a command execution request
2. It validates the command against the allowlist
3. It creates an execution record with a unique ID
4. It spawns a separate process to execute the command
5. It monitors the process and captures output in real-time
6. It sends status updates to the Socket Service
7. Upon completion, it records the final status and output

## Testing

You can test the Command Execution Service using the included verification script:

```bash
cd services/command-execution/tools
python verify_service.py
```

This script performs several tests to ensure that the service is functioning correctly:

1. Health check
2. Execution of allowed commands
3. Rejection of disallowed commands
4. Command cancellation
5. Complex command handling
6. Execution timeouts

## Logs

Logs for the Command Execution Service can be viewed with:

```bash
docker logs ogent-command-service
```

## Common Issues

1. **Command Not Allowed**: The command is not in the allowlist. Check the `ALLOWED_COMMANDS` environment variable.

2. **Execution Timeout**: The command exceeded the maximum execution time. Adjust the `MAX_EXECUTION_TIME` environment variable if necessary.

3. **Socket Service Connection**: Ensure the Socket Service is running and the `SOCKET_SERVICE_URL` is correctly configured.

4. **Permission Denied**: The command attempted to access a protected resource. Check the execution logs for details.

5. **Invalid Execution ID**: The execution ID doesn't exist or belongs to another user. Verify the execution ID. 