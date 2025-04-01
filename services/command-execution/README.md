# Command Execution Service

The Command Execution Service is a critical microservice in the Ogent platform that securely executes system commands on behalf of agents and users.

## Overview

This service provides a secure API for executing system commands in a controlled environment. It includes:

- Command execution with real-time status updates
- Command validation against an allowlist
- Path restrictions for security
- Authentication and authorization
- Command cancellation

## API Endpoints

### Health Check
- `GET /health` - Check service health

### Command Execution
- `POST /api/execute` - Execute a command
- `GET /api/execution/{execution_id}` - Get execution status
- `POST /api/execution/{execution_id}/cancel` - Cancel an execution

## Configuration

The service is configured using environment variables:

- `PORT` - Port to run the service on (default: 5000)
- `SOCKET_SERVICE_URL` - URL for the socket service
- `AUTH_SERVICE_URL` - URL for the auth service
- `ALLOWED_COMMANDS_PATH` - Path to the allowed commands configuration
- `MAX_EXECUTION_TIME` - Maximum execution time in seconds
- `EXECUTION_DIR` - Directory for command execution

## Security

The service implements several security measures:

1. **Command Allowlist**: Only approved commands can be executed
2. **Path Restrictions**: Commands can only access approved paths
3. **Authentication**: Token-based authentication with JWT
4. **Authorization**: Role-based permissions for command execution
5. **Execution Isolation**: Each command runs in its own workspace

## Directory Structure

- `/` - Main service code
  - `app.py` - Main application file
  - `Dockerfile` - Docker container definition
  - `requirements.txt` - Python dependencies
  - `allowed_commands.json` - Allowed commands configuration
- `/tools` - Verification and monitoring tools
- `/tests` - Service tests

## Development Setup

### Prerequisites
- Python 3.9+
- Flask
- Docker (for containerized usage)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
4. Run the service:
   ```bash
   python app.py
   ```

## Docker Setup

Build and run the Docker container:

```bash
docker build -t command-execution-service .
docker run -p 5001:5000 --env-file .env command-execution-service
```

## Testing

Run tests using the unittest framework:

```bash
python -m unittest discover -s tests
```

For verification tools:

```bash
python tools/verify_service.py
```

## Integration

The Command Execution Service integrates with:

- **Agent Service**: For executing commands as part of agent workflows
- **Auth Service**: For authentication and authorization
- **Socket Service**: For real-time status updates

## License

This project is licensed under the MIT License. 