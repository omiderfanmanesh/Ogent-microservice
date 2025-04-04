# Ogent Microservices Project Structure

## Root Directory

The root directory should contain only:

- `README.md` - Main project documentation
- `LICENSE` - Project license
- `docker-compose.yml` - Main Docker Compose file
- `docker-compose.override.yml` - Docker Compose override for development
- `docker-compose.prod.yml` - Docker Compose for production
- `Dockerfile` - Main Dockerfile (if applicable)
- `Makefile` - Make targets for common operations
- `.gitignore` - Git ignore file
- `.env.example` - Example environment file
- `.env.prod.example` - Example production environment file
- `/services` - Directory containing all microservices
- `/scripts` - Directory containing utility scripts
- `/docs` - Directory containing documentation

## Services Directory

Each service in the `/services` directory should follow a consistent structure:

```
/services
  /auth-service
    /app
      /domain
      /infrastructure
      /api
    /tests
    README.md
    docker-compose.yml
    Dockerfile
  
  /langchain-agent
    /app
      /domain
      /infrastructure
      /api
    /tests
    README.md
    docker-compose.yml
    Dockerfile
  
  /command-execution
    ...
  
  /socket-service
    ...
  
  /api-gateway
    ...
  
  /frontend
    ...
  
  /nginx
    ...
```

## Scripts Directory

The scripts directory contains utility scripts for development, deployment, and maintenance:

```
/scripts
  setup.sh - Initial setup script
  docker.sh - Docker utility functions
  migrate-docs.sh - Documentation migration script
  update_nginx_config.sh - Nginx configuration updater
  end_to_end_test.sh - End-to-end testing script
```

## Documentation Directory

The documentation directory contains comprehensive docs:

```
/docs
  /architecture
    domain_driven_design.md - DDD principles
    service_boundaries.md - Service boundary documentation
    data_flow.md - Data flow diagrams
  
  /api
    auth-service.md - Auth service API documentation
    langchain-agent.md - Agent service API documentation
    command-execution.md - Command service API documentation
  
  service_readme_template.md - Template for service READMEs
  project_structure.md - This document
```

## Docker Files

Docker Compose files follow this convention:

- `docker-compose.yml` - Base configuration for all environments
- `docker-compose.override.yml` - Development overrides
- `docker-compose.prod.yml` - Production configuration
- `docker-compose.agent-test.yml` - Testing specific configuration 