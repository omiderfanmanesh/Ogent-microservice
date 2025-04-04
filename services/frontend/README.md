# Ogent Frontend Service

## Overview
The frontend service provides the user interface for the Ogent microservice system, following Domain-Driven Design principles to maintain a clean architecture and clear separation of concerns.

## Domain-Driven Design Structure

The frontend code is organized according to DDD principles, with a clear separation between different concerns:

### Domain Layer (`src/domain/`)
Contains the core business concepts of the frontend application, independent of any infrastructure or UI.

- **Entities**: Business objects with identity and lifecycle
  - `User` - User entity with authentication data
  - `Agent` - Agent configuration and details
  - `Execution` - Execution record with status

- **Repositories (Interfaces)**: Define how to access domain entities
  - `UserRepository` - Interface for user data access
  - `AgentRepository` - Interface for agent data access
  - `ExecutionRepository` - Interface for execution data access

- **Services**: Domain business logic
  - `AuthService` - Authentication business rules
  - `ExecutionService` - Execution business rules

### Application Layer (`src/application/`)
Coordinates the domain objects to perform specific application tasks and use cases.

- **Use Cases**: Application-specific business logic
  - `AgentCreationUseCase` - Handle agent creation flow
  - `ExecutionUseCase` - Handle execution flow

- **Composables**: Vue-specific composition functions
  - `useAuth` - Authentication composable
  - `useAgent` - Agent management composable
  - `useExecution` - Execution management composable

### Infrastructure Layer (`src/infrastructure/`)
Implements interfaces defined in the domain layer with specific technologies.

- **API**: Implementation of repositories using API calls
  - `HttpUserRepository` - Implements UserRepository with HTTP
  - `HttpAgentRepository` - Implements AgentRepository with HTTP
  - `HttpExecutionRepository` - Implements ExecutionRepository with HTTP

- **Store**: State management implementations
  - `AuthStore` - Pinia store for authentication
  - `AgentStore` - Pinia store for agent management
  - `ExecutionStore` - Pinia store for execution management

- **Config**: Application configuration
  - `ApiConfig` - API endpoint configuration
  - `AuthConfig` - Authentication configuration

### Presentation Layer (`src/presentation/`)
Contains all UI components, views, and layouts.

- **Components**: Reusable UI components
  - `AgentCard` - Display agent information
  - `ExecutionStatus` - Display execution status
  - `CommandOutput` - Display command output

- **Views**: Page-level components
  - `LoginView` - Login page
  - `AgentView` - Agent management page
  - `ExecutionView` - Execution monitoring page

- **Layouts**: Page layouts
  - `MainLayout` - Main authenticated layout
  - `AuthLayout` - Authentication layout

## Directory Structure
```
/services/frontend
├── public/                # Static assets
├── src/
│   ├── domain/            # Domain layer
│   │   ├── entities/      # Domain entities
│   │   ├── repositories/  # Repository interfaces
│   │   └── services/      # Domain services
│   ├── application/       # Application layer
│   │   ├── use-cases/     # Application use cases
│   │   └── composables/   # Vue composables
│   ├── infrastructure/    # Infrastructure layer
│   │   ├── api/           # API implementations
│   │   ├── store/         # Pinia stores
│   │   └── config/        # Configuration
│   ├── presentation/      # Presentation layer
│   │   ├── components/    # UI components
│   │   ├── views/         # Page components
│   │   └── layouts/       # Layout components
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── tests/                 # Tests
│   ├── unit/              # Unit tests
│   └── e2e/               # End-to-end tests
├── Dockerfile             # Docker configuration
├── nginx.conf             # Nginx configuration
├── package.json           # Package configuration
└── vite.config.js         # Vite configuration
```

## Development

### Prerequisites
- Node.js 16+
- npm or yarn

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production
```bash
# Build the application
npm run build
```

### Docker
```bash
# Build Docker image
docker build -t ogent-frontend .

# Run the container
docker run -p 3000:80 ogent-frontend
```

## Testing
```bash
# Run unit tests
npm run test:unit

# Run e2e tests
npm run test:e2e
``` 