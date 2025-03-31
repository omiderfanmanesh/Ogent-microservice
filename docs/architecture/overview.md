# Project Overview: Ogent

Ogent is a microservices-based application that provides AI agent capabilities, authentication, and command execution across multiple services.

## Services Architecture

1. **Agent Service (LangChain-based)**
   - Language: Python (FastAPI framework)
   - Database: PostgreSQL
   - Purpose: Manages AI agents using LangChain for NLP tasks
   - Key features: Agent creation, execution history, conversation management

2. **Auth Service**
   - Language: PHP (Laravel framework)
   - Database: MySQL
   - Purpose: Handles authentication, user management, roles and permissions
   - Key features: JWT auth, role-based access control, user registration

3. **Command Execution Service**
   - Language: Python
   - Purpose: Executes system commands in a controlled environment
   - Features: Command validation, secure execution, output streaming

4. **Socket Service**
   - Language: Node.js
   - Purpose: Provides real-time communication capabilities
   - Features: Websocket connections, event broadcasting

5. **API Gateway**
   - Language: Node.js
   - Purpose: Central entry point for all API requests
   - Features: Request routing, service discovery, rate limiting

6. **Frontend**
   - Language: JavaScript (React framework)
   - Purpose: User interface for the application

7. **Nginx**
   - Purpose: Web server and reverse proxy
   - Features: Static file serving, load balancing, SSL termination

## Database Structure

### PostgreSQL (for Agent Service)
- **Database Name**: langchain_agent
- **Tables**:
  - `agents`: Stores agent configurations and metadata
  - `executions`: Records execution history of agent interactions

### MySQL (for Auth Service)
- **Database Name**: ogent_auth
- **Tables**:
  - `users`: User data including credentials
  - `roles`: Role definitions for access control
  - `permissions`: Granular permissions
  - `role_permissions`: Junction table for roles and permissions
  - `user_roles`: Junction table for users and roles

## System Requirements
- Docker and Docker Compose for containerization
- OpenAI API key for LangChain functionality
- Modern web browser for frontend access

## Network Communication
The services communicate with each other through a Docker network (ogent_network), with the API Gateway serving as the central coordination point. The Nginx server handles external HTTP requests and routes them to the appropriate services.

## Security Features
- JWT-based authentication
- Role-based access control
- Secure command execution in isolated container
- Parameterized database queries for SQL injection prevention

## Container Structure
- **ogent-agent-service**: LangChain agent service (Python/FastAPI)
- **ogent-auth-service**: Laravel authentication service (PHP)
- **ogent-db**: PostgreSQL database for agent service
- **ogent-auth-db**: MySQL database for auth service
- **ogent-api-gateway**: API gateway service (Node.js)
- **ogent-frontend**: React frontend
- **ogent-nginx**: Nginx web server
- **ogent-socket-service**: Socket service for real-time communication
- **ogent-command-execution**: Command execution service
- **ogent-ubuntu-target**: Ubuntu container for secure command execution

This architecture allows for scalable, maintainable development with clear separation of concerns between services. Each service can be developed, tested, and deployed independently. 