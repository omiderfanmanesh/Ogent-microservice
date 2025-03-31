# Command Execution Flow (Component-Based View)

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│                                                                     │
│  ┌───────────────┐                                                  │
│  │               │                                                  │
│  │   Frontend    │ React/Redux SPA                                  │
│  │  (React/Nginx)│ Handles user interaction and command display     │
│  │               │                                                  │
│  └───────┬───────┘                                                  │
│          │                                                          │
└──────────┼──────────────────────────────────────────────────────────┘
           │
           │ HTTP/WebSocket
           │
┌──────────┼──────────────────────────────────────────────────────────┐
│          │                     API LAYER                            │
│          ▼                                                          │
│  ┌───────────────┐      JWT Auth       ┌───────────────┐           │
│  │               │◄────────────────────┤               │           │
│  │  API Gateway  │                     │ Auth Service  │           │
│  │   (Node.js)   │────────────────────►│  (Laravel)    │           │
│  │               │                     │               │           │
│  └───────┬───────┘                     └───────────────┘           │
│          │                                                          │
└──────────┼──────────────────────────────────────────────────────────┘
           │
           │ HTTP
           │
┌──────────┼──────────────────────────────────────────────────────────┐
│          │                   SERVICE LAYER                          │
│          ▼                                                          │
│  ┌───────────────┐      WebSocket      ┌───────────────┐           │
│  │               │◄────────────────────┤               │           │
│  │    Command    │      Messages       │Socket Service │           │
│  │   Execution   │────────────────────►│   (Node.js)   │           │
│  │    Service    │                     │               │───┐       │
│  │    (Python)   │                     └───────┬───────┘   │       │
│  │               │                             │           │       │
│  └───────┬───────┘                             │           │       │
│          │                                     │           │       │
│          │                                     │ WebSocket │       │
│          │ SSH                                 │ Events    │       │
│          │                                     │           │       │
└──────────┼─────────────────────────────────────┼───────────┼───────┘
           │                                     │           │
           │                                     │           │
┌──────────┼─────────────────────────────────────┼───────────┼───────┐
│          │                EXECUTION LAYER      │           │       │
│          ▼                                     │           │       │
│  ┌───────────────┐                             │           │       │
│  │               │                             │           │       │
│  │Ubuntu Target  │                             │           │       │
│  │  Container    │                             │           │       │
│  │               │                             │           │       │
│  └───────────────┘                             │           │       │
│                                                │           │       │
└────────────────────────────────────────────────┼───────────┼───────┘
                                                 │           │
                                                 │           │
┌────────────────────────────────────────────────┼───────────┼───────┐
│                                                │           │       │
│                      CLIENT LAYER              │           │       │
│                     (Return Path)              │           │       │
│  ┌───────────────┐                             │           │       │
│  │               │◄────────────────────────────┘           │       │
│  │   Frontend    │◄──────────────────────────────────────────┘     │
│  │  (React/Nginx)│                                                 │
│  │               │                                                 │
│  └───────────────┘                                                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Component Interfaces

### Frontend ↔ API Gateway
- **Interface Type**: RESTful HTTP
- **Endpoints**:
  - `POST /api/command`: Submit a command for execution
  - `GET /api/command/{id}`: Get status/result of a command execution
- **Authentication**: JWT token in Authorization header
- **Payload Format**: JSON

### Frontend ↔ Socket Service
- **Interface Type**: WebSocket
- **Events**:
  - `connect`: Establish connection with execution ID and token
  - `command:output`: Receive real-time command output
  - `command:status`: Receive execution status updates
- **Authentication**: JWT token in connection parameters
- **Payload Format**: JSON

### API Gateway ↔ Auth Service
- **Interface Type**: RESTful HTTP
- **Endpoints**:
  - `POST /api/auth/validate`: Validate token and get user permissions
- **Authentication**: Service API key
- **Payload Format**: JSON

### API Gateway ↔ Command Execution Service
- **Interface Type**: RESTful HTTP
- **Endpoints**:
  - `POST /api/execute`: Submit a command for execution
  - `GET /api/execute/{id}`: Get execution details
- **Authentication**: Service API key
- **Payload Format**: JSON

### Command Execution Service ↔ Socket Service
- **Interface Type**: WebSocket (server-to-server)
- **Events**:
  - `execution:create`: Initialize new execution channel
  - `execution:output`: Push command output
  - `execution:status`: Update execution status
- **Authentication**: Service API key
- **Payload Format**: JSON

### Command Execution Service ↔ Ubuntu Target
- **Interface Type**: SSH
- **Authentication**: SSH key-based
- **Execution**: Commands run in isolated user context
- **Output Capture**: stdout/stderr streams

## Component Responsibilities

### Frontend
- Display command input interface
- Send authenticated command requests
- Establish WebSocket connection for updates
- Display real-time command output
- Show final execution status

### API Gateway
- Validate user authentication
- Check user permissions
- Route command request to execution service
- Return final results to frontend

### Auth Service
- Validate JWT tokens
- Provide user permission details
- Handle role-based access control

### Command Execution Service
- Validate commands against whitelist
- Create execution records
- Establish streaming channel
- Execute commands on target system
- Capture and forward command output
- Track execution status and results

### Socket Service
- Manage WebSocket connections
- Create execution channels
- Stream real-time updates to clients
- Handle connection failures

### Ubuntu Target Container
- Provide isolated execution environment
- Execute commands securely
- Stream output back to execution service

This component-based view highlights the interfaces between services, making it clear how data flows through the system and how each component interacts with others. 