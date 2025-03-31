# Development Guide

This guide provides information for developers who want to contribute to the Ogent platform.

## Development Environment Setup

### Local Development Prerequisites

- **Docker and Docker Compose**: Required for running the services
- **Git**: For version control
- **Node.js**: v16+ for frontend and API gateway development
- **PHP**: 8.1+ with Composer for auth service development
- **Python**: 3.9+ with Poetry for agent service development
- **IDE**: VS Code (recommended) with Docker, Python, PHP, and React extensions

### Setting Up for Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ogent.git
   cd ogent
   ```

2. **Install development dependencies**
   ```bash
   # For frontend and API gateway
   cd services/frontend
   npm install
   cd ../api-gateway
   npm install
   
   # For auth service
   cd ../auth-service
   composer install
   
   # For agent service
   cd ../langchain-agent
   pip install -r requirements.txt
   ```

3. **Set up environment for local development**
   ```bash
   # Copy example environment files
   cp .env.example .env
   cp services/langchain-agent/.env.example services/langchain-agent/.env
   cp services/auth-service/.env.example services/auth-service/.env
   
   # Edit .env files with your local settings
   ```

4. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

5. **Initialize databases**
   ```bash
   docker-compose exec agent-service alembic upgrade head
   docker-compose exec auth-service php artisan migrate --seed
   ```

## Project Structure

The project is organized as a microservices architecture:

```
ogent/
├── services/
│   ├── api-gateway/          # Node.js API gateway
│   ├── auth-service/         # Laravel authentication service
│   ├── command-execution/    # Python command execution service
│   ├── frontend/             # React frontend
│   ├── langchain-agent/      # FastAPI agent service
│   ├── nginx/                # Nginx configuration
│   └── socket-service/       # Node.js WebSocket service
├── docker-compose.yml        # Production Docker Compose
├── docker-compose.dev.yml    # Development Docker Compose
├── setup.sh                  # Setup script
└── docs/                     # Documentation
```

### Key Components

#### Frontend (React)
- Located in `services/frontend/`
- Uses React with Redux for state management
- Communicates with backend via API Gateway
- Real-time updates via WebSockets

#### API Gateway (Node.js)
- Located in `services/api-gateway/`
- Provides a unified API entry point
- Routes requests to appropriate services
- Handles authentication verification

#### Auth Service (Laravel)
- Located in `services/auth-service/`
- Manages users, roles, and permissions
- Generates and validates JWT tokens
- Uses MySQL database

#### Agent Service (FastAPI/LangChain)
- Located in `services/langchain-agent/`
- Implements AI agent capabilities
- Uses LangChain for natural language processing
- Uses PostgreSQL database

#### Command Execution Service (Python)
- Located in `services/command-execution/`
- Executes system commands securely
- Provides real-time command output
- Connects to Ubuntu target container

#### Socket Service (Node.js)
- Located in `services/socket-service/`
- Handles WebSocket connections
- Provides real-time updates to clients
- Communicates with other services

## Development Workflow

### Git Workflow

We follow the GitHub Flow model:

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. **Push changes and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

4. **Code review and merge**
   - All PRs require at least one review
   - CI must pass before merging
   - Use squash merging for cleaner history

### Running Tests

Each service has its own test suite:

```bash
# Frontend tests
cd services/frontend
npm test

# API Gateway tests
cd services/api-gateway
npm test

# Auth Service tests
cd services/auth-service
php artisan test

# Agent Service tests
cd services/langchain-agent
pytest

# Command Execution Service tests
cd services/command-execution
pytest
```

### Code Style and Linting

We enforce code style with linters:

- **JavaScript/TypeScript**: ESLint with Prettier
  ```bash
  cd services/frontend
  npm run lint
  ```

- **PHP**: PHP_CodeSniffer with PSR-12
  ```bash
  cd services/auth-service
  composer lint
  ```

- **Python**: Black and flake8
  ```bash
  cd services/langchain-agent
  black app
  flake8 app
  ```

## Service Development Guidelines

### Frontend Development

1. **Component Structure**
   - Use functional components with hooks
   - Organize by feature, not by type
   - Follow atomic design principles

2. **State Management**
   - Use Redux for global state
   - Use local state for component-specific state
   - Use context for theme and authentication

3. **API Communication**
   - Use Axios for HTTP requests
   - Define API services in `src/services/`
   - Handle errors consistently

### Backend Development

1. **API Endpoints**
   - Follow RESTful conventions
   - Document with OpenAPI/Swagger
   - Implement proper validation
   - Use consistent response formats

2. **Database**
   - Write migrations for schema changes
   - Use repositories for data access
   - Implement proper indexing
   - Write automated tests for repositories

3. **Authentication**
   - Use JWT tokens
   - Implement role-based access control
   - Validate permissions for each action

### Agent Service Development

1. **LangChain Integration**
   - Follow LangChain best practices
   - Abstract model-specific code
   - Implement caching for efficiency

2. **Agent Configuration**
   - Make agents configurable
   - Use dependency injection
   - Document configuration options

### Command Execution Development

1. **Security**
   - Sanitize all inputs
   - Restrict command execution
   - Implement resource limits
   - Use isolation mechanisms

2. **Output Streaming**
   - Use asynchronous I/O
   - Implement buffering when needed
   - Handle command timeouts

## Architecture Decisions

When making architecture decisions, consider:

1. **Scalability**
   - Will this solution scale horizontally?
   - How will it handle increased load?

2. **Security**
   - What are the security implications?
   - How is user data protected?
   - Are there potential vulnerabilities?

3. **Maintainability**
   - Is the code easy to understand?
   - Is it well-documented?
   - Does it follow project conventions?

4. **Performance**
   - Are there performance bottlenecks?
   - How can we optimize?

## Documentation

All code should be documented:

- **Inline Comments**: For complex logic
- **Function/Method Comments**: Purpose, parameters, return values
- **API Documentation**: Using OpenAPI/Swagger
- **README Files**: For each service
- **Architecture Documentation**: For major components
- **Diagrams**: For visualizing complex interactions

## Debugging

### Debug Mode

Enable debug mode in your environment:

```
DEBUG=true
LOG_LEVEL=DEBUG
```

### Accessing Container Logs

```bash
# View logs for a specific service
docker-compose logs -f service-name

# Tail the last 100 lines
docker-compose logs -f --tail=100 service-name
```

### Interactive Debugging

- **Frontend**: Use React DevTools and Redux DevTools
- **Node.js Services**: Use `--inspect` flag and connect with Chrome DevTools
- **PHP**: Use Xdebug with your IDE
- **Python**: Use pdb or an IDE like PyCharm

## Deployment

### Development Deployment

For testing new features in a dev environment:

```bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

### Staging Deployment

Update the staging environment:

```bash
git checkout staging
git merge main
git push origin staging
# CI/CD will handle the rest
```

### Production Deployment

Production deployments are handled via CI/CD pipeline:

1. Merge to `main` branch
2. CI/CD runs tests
3. If tests pass, build and push Docker images
4. Deploy to production environment
5. Run database migrations
6. Update documentation

## Contribution Guidelines

1. **Discuss First**: Open an issue before making significant changes
2. **Follow Conventions**: Adhere to project coding standards
3. **Write Tests**: Include tests for new features
4. **Update Documentation**: Keep documentation in sync with code
5. **Review Others' Work**: Participate in code reviews
6. **Be Respectful**: Follow the code of conduct

By following these guidelines, you'll help maintain high-quality code and a productive development environment. 