# Ogent Microservices

A modern microservices architecture for intelligent agent execution and command management.

## System Overview

Ogent is a distributed system composed of several microservices that work together to provide:
- User authentication and authorization
- AI agent creation and management
- Secure command execution
- Real-time updates via WebSockets
- Frontend UI for interacting with the system

## Architecture

The system follows a microservice architecture with the following components:

- **API Gateway**: Routes requests to appropriate services and handles cross-cutting concerns
- **Auth Service**: Manages user authentication and authorization
- **LangChain Agent Service**: Creates and manages AI agents
- **Command Execution Service**: Safely executes system commands
- **Socket Service**: Provides real-time updates via WebSockets
- **Frontend**: React-based UI for interacting with the system

![Architecture Diagram](./docs/architecture.png)

## Services

### API Gateway
- Entry point for all client requests
- Routes requests to appropriate services
- Handles authentication validation
- Provides a unified API endpoint

### Auth Service
- User registration and authentication
- JWT token generation and validation
- Role-based authorization
- User profile management

### LangChain Agent Service
- Creates AI agents using LangChain
- Manages agent configurations
- Handles agent execution requests
- Integrates with Command Execution service

### Command Execution Service
- Securely executes system commands
- Implements execution permission controls
- Command execution status tracking
- Real-time command output streaming

### Socket Service
- Real-time WebSocket connections
- Execution status updates
- Supports client subscription to specific executions
- Integration with Command Execution service

### Frontend
- React-based single-page application
- User authentication interface
- Command execution and monitoring UI
- Real-time updates via WebSocket

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 16+
- Python 3.9+

### Running the System

1. Clone the repository:
```
git clone https://github.com/omiderfanmanesh/Ogent-microservice.git
cd Ogent-microservice
```

2. Start all services using Docker Compose:
```
docker-compose up -d
```

3. Access the application:
- Frontend UI: http://localhost:3000
- API Gateway: http://localhost:8081

### Service URLs

| Service | Internal URL | External URL |
|---------|--------------|-------------|
| Frontend | http://ogent-frontend:80 | http://localhost:3000 |
| API Gateway | http://ogent-api-gateway:8081 | http://localhost:8081 |
| Auth Service | http://ogent-auth-service:5000 | via API Gateway |
| LangChain Agent | http://ogent-agent-service:8000 | via API Gateway |
| Command Execution | http://ogent-command-service:5001 | via API Gateway |
| Socket Service | http://ogent-socket-service:3002 | via API Gateway |

## Testing

The project includes comprehensive testing tools for each service:

### Individual Service Testing
- Auth Service: `services/auth-service/verify_service.py`
- Command Execution: `services/command-execution/tools/verify_service.py`
- Socket Service: `services/socket-service/verify_all.sh`
- Frontend: `services/frontend/verify_frontend.sh`

### End-to-End Testing
Run the end-to-end test script:
```
./end_to_end_test.sh
```

This script verifies that all services are operational and properly integrated.

### Manual Testing
For WebSocket and real-time functionality testing:
1. Open `services/frontend/test_socket_connection.html` in a browser
2. Log in to obtain an authentication token
3. Test WebSocket connections and real-time updates

## Configuration

Each service can be configured using environment variables defined in the `docker-compose.yml` file.

Key configuration options:
- `JWT_SECRET`: Secret key for JWT token generation
- `AUTH_SERVICE_URL`: URL for the Auth Service
- `COMMAND_SERVICE_URL`: URL for the Command Execution Service
- `AGENT_SERVICE_URL`: URL for the LangChain Agent Service
- `SOCKET_SERVICE_URL`: URL for the Socket Service

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for AI agent capabilities
- Socket.IO for real-time functionality
- Express.js and Nginx for API Gateway
- React and Material UI for frontend implementation 