# API Gateway Service

The API Gateway serves as the central entry point for all client requests to the Ogent Microservice system. It routes requests to the appropriate backend services and handles cross-cutting concerns such as authentication, rate limiting, and request logging.

## Overview

The API Gateway is implemented using Express.js and provides the following functionality:

- **Request Routing**: Directs incoming requests to the appropriate service
- **Authentication Validation**: Validates JWT tokens for protected routes
- **Request/Response Transformation**: Adapts requests and responses as needed
- **Health Checking**: Provides health status of the overall system
- **Error Handling**: Standardizes error responses across services

## Architecture

The API Gateway acts as a reverse proxy that sits between clients and backend services:

```
Client → API Gateway → Backend Services
```

All client requests are sent to the API Gateway, which then forwards them to the appropriate service based on the URL path.

## Configuration

The API Gateway is configured using environment variables in the `docker-compose.yml` file:

```yaml
services:
  api-gateway:
    build:
      context: ./services/api-gateway
    ports:
      - "8081:8081"
    environment:
      - PORT=8081
      - AUTH_SERVICE_URL=http://ogent-auth-service:5000
      - AGENT_SERVICE_URL=http://ogent-agent-service:8000
      - COMMAND_SERVICE_URL=http://ogent-command-service:5001
      - SOCKET_SERVICE_URL=http://ogent-socket-service:3002
```

## Service Routes

The API Gateway maps routes to backend services as follows:

| Path Pattern | Service | Description |
|--------------|---------|-------------|
| `/auth/*` | Auth Service | Authentication and user management endpoints |
| `/agents/*` | LangChain Agent Service | Agent creation and management endpoints |
| `/command/*` | Command Execution Service | Command execution and status endpoints |
| `/socket-http/*` | Socket Service (HTTP) | HTTP endpoints for the Socket Service |
| `/socket` | Socket Service (WebSocket) | WebSocket connection endpoint |
| `/health` | API Gateway | System health check endpoint |

## Health Check

The API Gateway provides a health check endpoint that verifies the health of all backend services:

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "services": {
    "auth": "ok",
    "agent": "ok",
    "command": "ok",
    "socket": "ok"
  }
}
```

## Authentication

The API Gateway validates JWT tokens for protected routes by forwarding the `Authorization` header to the Auth Service. If the token is invalid, the gateway returns a 401 Unauthorized response.

## WebSocket Support

The API Gateway supports WebSocket connections for real-time updates by proxying WebSocket connections to the Socket Service.

## Rate Limiting

To prevent abuse, the API Gateway implements rate limiting based on client IP addresses:

- 100 requests per minute for standard routes
- 5 requests per minute for sensitive operations

## Error Handling

The API Gateway standardizes error responses across all services:

```json
{
  "error": "Error message",
  "status": 400,
  "path": "/path/to/resource"
}
```

## Logs

The API Gateway logs all requests and responses for monitoring and debugging purposes. Logs can be viewed using:

```bash
docker logs ogent-api-gateway
```

## Debugging

To debug the API Gateway service, you can use:

```bash
cd /services/api-gateway
node debug.js
```

This will start the service in debug mode with more verbose logging.

## Testing

You can test the API Gateway's basic functionality with:

```bash
curl http://localhost:8081/health
```

A successful response indicates that the gateway is operational.

## Common Issues

1. **Connection Refused**: Ensure that all backend services are running and properly configured in the `docker-compose.yml` file.

2. **Invalid JWT Token**: Check that the JWT token is properly formatted and not expired.

3. **Service Unavailable**: Verify that all services are healthy by checking the `/health` endpoint.

4. **Proxy Error**: Ensure that service URLs are correctly configured in the environment variables. 