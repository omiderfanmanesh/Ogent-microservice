# API Overview

## Introduction
The Ogent API provides programmatic access to the Ogent platform functionality. This document provides an overview of the API, including authentication methods, request formats, response formats, and error handling.

## API Endpoints

The Ogent API is organized around REST principles. It uses standard HTTP verbs, returns JSON responses, and uses standard HTTP status codes to indicate errors.

### Base URL
```
https://api.ogent.example.com/v1
```

### API Versioning
The API is versioned through the URL path. The current version is `v1`.

## API Categories

| Category | Description | Base Path |
|----------|-------------|-----------|
| Authentication | User authentication and token management | `/auth` |
| Users | User management and profiles | `/users` |
| Notifications | Notification management | `/notifications` |

## Request Format

### Headers
All API requests should include the following headers:

```
Content-Type: application/json
Authorization: Bearer <token>
```

### Request Body
For POST, PUT, and PATCH requests, the request body should be a valid JSON object.

```json
{
  "property1": "value1",
  "property2": "value2"
}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "data": {
    // Response data
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request:

| Status Code | Description |
|-------------|-------------|
| 200 | OK - The request was successful |
| 201 | Created - The resource was successfully created |
| 400 | Bad Request - The request was invalid |
| 401 | Unauthorized - Authentication is required |
| 403 | Forbidden - The authenticated user does not have permission |
| 404 | Not Found - The requested resource does not exist |
| 422 | Validation Error - The request data is invalid |
| 500 | Internal Server Error - An error occurred on the server |

### Error Response Format

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error": {
    "code": "ERROR_CODE",
    "description": "Detailed error description"
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits are applied on a per-user basis:

- 100 requests per minute for authenticated users
- 30 requests per minute for unauthenticated users

Rate limit information is included in the response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

## Further Reading

- [Authentication](authentication.md): Detailed information about authentication
- [API Endpoints](endpoints/): Documentation for specific API endpoints
- [API Versioning](versioning.md): Information about API versioning

# API Reference Documentation

This document provides a comprehensive reference for all API endpoints available in the Ogent platform.

## Authentication Service API

### Authentication

#### Login
- **Endpoint:** `POST /api/auth/login`
- **Description:** Authenticate a user and receive an access token
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** 
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "name": "User Name",
      "email": "user@example.com",
      "roles": ["admin"]
    }
  }
  ```

#### Register
- **Endpoint:** `POST /api/auth/register`
- **Description:** Register a new user
- **Request Body:**
  ```json
  {
    "name": "New User",
    "email": "newuser@example.com",
    "password": "password123",
    "password_confirmation": "password123"
  }
  ```
- **Response:** 
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": 2,
      "name": "New User",
      "email": "newuser@example.com"
    }
  }
  ```

#### Logout
- **Endpoint:** `POST /api/auth/logout`
- **Description:** Invalidate the current user's token
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

### User Management

#### Get User Profile
- **Endpoint:** `GET /api/users/profile`
- **Description:** Get the current user's profile information
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "roles": ["admin"],
    "permissions": ["execute_commands", "manage_agents"]
  }
  ```

#### Update User Profile
- **Endpoint:** `PUT /api/users/profile`
- **Description:** Update the current user's profile
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "name": "Updated Name",
    "email": "updated@example.com"
  }
  ```
- **Response:** 
  ```json
  {
    "message": "Profile updated successfully",
    "user": {
      "id": 1,
      "name": "Updated Name",
      "email": "updated@example.com"
    }
  }
  ```

### Roles & Permissions

#### List Roles
- **Endpoint:** `GET /api/roles`
- **Description:** Get all available roles
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "roles": [
      {
        "id": 1,
        "name": "admin",
        "permissions": ["execute_commands", "manage_agents", "manage_users"]
      },
      {
        "id": 2,
        "name": "user",
        "permissions": ["execute_commands"]
      }
    ]
  }
  ```

#### Assign Role
- **Endpoint:** `POST /api/users/{userId}/roles`
- **Description:** Assign a role to a user
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "role_id": 2
  }
  ```
- **Response:** 
  ```json
  {
    "message": "Role assigned successfully"
  }
  ```

## Agent Service API

### Agents

#### List Agents
- **Endpoint:** `GET /api/agents`
- **Description:** Get all available agents
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "agents": [
      {
        "id": "agt_123456789",
        "name": "Command Executor",
        "description": "Agent for executing system commands",
        "type": "command",
        "created_at": "2023-03-28T12:00:00Z",
        "created_by": "user@example.com"
      }
    ]
  }
  ```

#### Get Agent
- **Endpoint:** `GET /api/agents/{agentId}`
- **Description:** Get details for a specific agent
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "id": "agt_123456789",
    "name": "Command Executor",
    "description": "Agent for executing system commands",
    "type": "command",
    "configuration": {
      "model": "gpt-3.5-turbo",
      "temperature": 0.7
    },
    "permissions": {
      "users": ["*"],
      "roles": ["admin", "user"]
    },
    "meta_data": {
      "version": "1.0.0"
    },
    "created_at": "2023-03-28T12:00:00Z",
    "updated_at": "2023-03-28T12:00:00Z",
    "created_by": "user@example.com"
  }
  ```

#### Create Agent
- **Endpoint:** `POST /api/agents`
- **Description:** Create a new agent
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "name": "New Agent",
    "description": "A new command execution agent",
    "type": "command",
    "configuration": {
      "model": "gpt-3.5-turbo",
      "temperature": 0.7
    },
    "permissions": {
      "users": ["*"],
      "roles": ["admin"]
    }
  }
  ```
- **Response:** 
  ```json
  {
    "message": "Agent created successfully",
    "agent": {
      "id": "agt_987654321",
      "name": "New Agent",
      "description": "A new command execution agent",
      "type": "command",
      "created_at": "2023-03-28T14:30:00Z",
      "created_by": "user@example.com"
    }
  }
  ```

#### Update Agent
- **Endpoint:** `PUT /api/agents/{agentId}`
- **Description:** Update an existing agent
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "name": "Updated Agent Name",
    "description": "Updated description",
    "configuration": {
      "model": "gpt-4",
      "temperature": 0.5
    }
  }
  ```
- **Response:** 
  ```json
  {
    "message": "Agent updated successfully",
    "agent": {
      "id": "agt_123456789",
      "name": "Updated Agent Name",
      "description": "Updated description",
      "type": "command",
      "updated_at": "2023-03-28T15:00:00Z"
    }
  }
  ```

#### Delete Agent
- **Endpoint:** `DELETE /api/agents/{agentId}`
- **Description:** Delete an agent
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "message": "Agent deleted successfully"
  }
  ```

### Executions

#### Execute Command
- **Endpoint:** `POST /api/executions`
- **Description:** Execute a command using a specific agent
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "agent_id": "agt_123456789",
    "input": "ls -la",
    "parameters": {
      "timeout": 30
    }
  }
  ```
- **Response:** 
  ```json
  {
    "execution_id": "exec_abcdef123",
    "status": "pending",
    "socket_channel": "execution_exec_abcdef123"
  }
  ```

#### Get Execution
- **Endpoint:** `GET /api/executions/{executionId}`
- **Description:** Get details for a specific execution
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "id": "exec_abcdef123",
    "agent_id": "agt_123456789",
    "user_id": "user@example.com",
    "status": "completed",
    "input": "ls -la",
    "output": "total 24\ndrwxr-xr-x  6 user  staff  192 Mar 28 12:00 .\n...",
    "tokens_used": 125,
    "created_at": "2023-03-28T15:30:00Z",
    "started_at": "2023-03-28T15:30:01Z",
    "completed_at": "2023-03-28T15:30:05Z"
  }
  ```

#### List Executions
- **Endpoint:** `GET /api/executions`
- **Description:** Get all executions for the current user
- **Headers:** `Authorization: Bearer {token}`
- **Query Parameters:**
  - `agent_id` (optional): Filter by agent ID
  - `status` (optional): Filter by status (pending, running, completed, failed)
  - `limit` (optional): Limit number of results (default: 20)
  - `offset` (optional): Pagination offset (default: 0)
- **Response:** 
  ```json
  {
    "executions": [
      {
        "id": "exec_abcdef123",
        "agent_id": "agt_123456789",
        "status": "completed",
        "input": "ls -la",
        "created_at": "2023-03-28T15:30:00Z",
        "completed_at": "2023-03-28T15:30:05Z"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  }
  ```

## Command Execution Service API

### Commands

#### Execute Direct Command
- **Endpoint:** `POST /api/command`
- **Description:** Execute a command directly on the target system
- **Headers:** `Authorization: Bearer {token}`
- **Request Body:**
  ```json
  {
    "command": "ls -la",
    "timeout": 30
  }
  ```
- **Response:** 
  ```json
  {
    "execution_id": "cmd_123456789",
    "status": "pending",
    "socket_channel": "command_cmd_123456789"
  }
  ```

#### Command Status
- **Endpoint:** `GET /api/command/{commandId}`
- **Description:** Get status of a command execution
- **Headers:** `Authorization: Bearer {token}`
- **Response:** 
  ```json
  {
    "id": "cmd_123456789",
    "status": "completed",
    "exit_code": 0,
    "output": "total 24\ndrwxr-xr-x  6 user  staff  192 Mar 28 12:00 .\n...",
    "execution_time": 0.35,
    "created_at": "2023-03-28T16:00:00Z",
    "completed_at": "2023-03-28T16:00:00Z"
  }
  ```

## Socket Service API

### WebSocket Connections

#### Command Output Stream
- **Connection URL:** `ws://socket-service/command/{commandId}`
- **Authentication:** Query parameter `token={jwt_token}`
- **Events:**
  - `connection`: Initial connection established
  - `command:output`: New output available
    ```json
    {
      "output": "drwxr-xr-x  6 user  staff  192 Mar 28 12:00 .\n",
      "timestamp": "2023-03-28T16:00:00.123Z"
    }
    ```
  - `command:status`: Status change
    ```json
    {
      "status": "running",
      "timestamp": "2023-03-28T16:00:00.100Z"
    }
    ```
  - `command:complete`: Command execution completed
    ```json
    {
      "status": "completed",
      "exit_code": 0,
      "execution_time": 0.35,
      "timestamp": "2023-03-28T16:00:00.350Z"
    }
    ```
  - `command:error`: Error during execution
    ```json
    {
      "status": "failed",
      "error": "Command timed out after 30 seconds",
      "timestamp": "2023-03-28T16:00:30.000Z"
    }
    ```

## API Gateway Routes

The API Gateway routes requests to the appropriate service based on the URL path:

| Path Pattern | Service |
|--------------|---------|
| `/api/auth/*` | Auth Service |
| `/api/users/*` | Auth Service |
| `/api/roles/*` | Auth Service |
| `/api/agents/*` | Agent Service |
| `/api/executions/*` | Agent Service |
| `/api/command/*` | Command Execution Service |
| `/socket/*` | Socket Service |

## Error Responses

All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "authentication_failed",
    "message": "Invalid credentials provided",
    "status": 401
  }
}
```

Common error codes:
- `authentication_failed`: Authentication issues (401)
- `permission_denied`: Authorization issues (403)
- `resource_not_found`: Requested resource doesn't exist (404)
- `validation_error`: Request validation failed (422)
- `server_error`: Internal server error (500)

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

Responses will include headers:
- `X-RateLimit-Limit`: Total requests allowed per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when the rate limit resets 