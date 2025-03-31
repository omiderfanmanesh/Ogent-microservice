# Installation and Setup Guide

This guide provides step-by-step instructions for setting up the Ogent platform on your system.

## Prerequisites

Before installing Ogent, ensure your system meets the following requirements:

- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 2.0.0 or higher
- **Git**: For cloning the repository
- **OpenAI API Key**: For LangChain agent functionality
- **Minimum System Requirements**:
  - 4GB RAM
  - 2 CPU cores
  - 20GB free disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ogent.git
cd ogent
```

### 2. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit the `.env` file to set the following required variables:

```
# Application Settings
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your_secret_key_here

# Database Settings
DATABASE_URL=postgresql://postgres:postgres@db:5432/langchain_agent

# OpenAI API Settings
OPENAI_API_KEY=your_openai_api_key
DEFAULT_LLM_MODEL=gpt-3.5-turbo

# Command Service
COMMAND_SERVICE_URL=http://command-execution:5000
```

### 3. Configure Database Settings

If you're using a custom database configuration, update the following files:

- For the Agent Service: `services/langchain-agent/.env`
- For the Auth Service: `services/auth-service/.env`

### 4. Run the Setup Script

The setup script will initialize the project and prepare the environment:

```bash
./setup.sh
```

This script performs the following actions:
- Checks for required dependencies
- Creates necessary Docker volumes
- Generates security keys
- Prepares the initial configuration

### 5. Build and Start the Services

```bash
docker-compose build
docker-compose up -d
```

This will start all services in detached mode. The first build might take several minutes.

### 6. Initialize the Databases

```bash
docker-compose exec agent-service alembic upgrade head
docker-compose exec auth-service php artisan migrate --seed
```

This will:
- Run all PostgreSQL migrations for the Agent Service
- Run all MySQL migrations for the Auth Service
- Seed the databases with initial data (including an admin user)

### 7. Verify Installation

Once all services are running, verify the installation by accessing:

- Frontend interface: http://localhost:8080
- API Gateway: http://localhost:8080/api
- Swagger API Documentation: http://localhost:8080/api/docs

### 8. Default Login Credentials

Use these credentials to log in to the system for the first time:

```
Email: admin@example.com
Password: password
```

**Important**: Change the default password immediately after first login.

## Docker Services

The `docker-compose.yml` file defines the following services:

| Service | Description | Ports |
|---------|-------------|-------|
| nginx | Web server and reverse proxy | 8080 |
| frontend | React frontend application | - |
| api-gateway | API Gateway service | - |
| auth-service | Authentication service | - |
| auth-db | MySQL database for auth service | - |
| agent-service | LangChain agent service | 8002 |
| db | PostgreSQL database for agent service | - |
| socket-service | WebSocket service | - |
| command-execution | Command execution service | 5001 |
| ubuntu-target | Ubuntu container for command execution | 2222 (SSH) |

## Configuration Options

### Environment Variables

The system can be configured with the following environment variables:

#### General Settings
- `ENVIRONMENT`: Set to `development`, `testing`, or `production`
- `DEBUG`: Set to `true` to enable debug mode
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

#### Security Settings
- `SECRET_KEY`: Secret key for JWT signing
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

#### Database Settings
- `DATABASE_URL`: PostgreSQL connection string
- `DB_CONNECTION`: MySQL connection type for auth service
- `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`: MySQL connection details

#### LangChain Settings
- `OPENAI_API_KEY`: Your OpenAI API key
- `DEFAULT_LLM_MODEL`: Default language model to use
- `DEFAULT_EMBEDDING_MODEL`: Default embedding model to use

## Production Deployment

For production deployments, follow these additional steps:

1. Use the production Docker Compose file:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. Set up HTTPS with proper SSL certificates:
   ```bash
   # Generate certificates or use Let's Encrypt
   # Update the Nginx configuration to use SSL
   cp services/nginx/ssl.conf services/nginx/default.conf
   ```

3. Configure a proper firewall to restrict access to essential ports only.

4. Set up monitoring and logging (Prometheus, Grafana, ELK stack).

5. Configure regular database backups.

## Troubleshooting

### Common Issues

1. **Services not starting properly**
   - Check logs with `docker-compose logs [service-name]`
   - Ensure all required environment variables are set
   - Verify port availability (no conflicts)

2. **Database connection errors**
   - Check that database containers are running
   - Verify database credentials in .env files
   - Ensure migrations have been applied

3. **API Gateway routing issues**
   - Check API Gateway logs
   - Verify service hostnames match the docker-compose configuration
   - Test individual services directly if accessible

4. **Authentication problems**
   - Verify the JWT secret key is set correctly
   - Check that auth-service is running
   - Ensure user exists in the database

### Support

If you encounter issues not covered in this guide, please:
1. Check the project issues on GitHub
2. Review the logs for specific error messages
3. Contact support at support@ogent.example.com

## Updating the System

To update to the latest version:

```bash
git pull
docker-compose build
docker-compose down
docker-compose up -d
docker-compose exec agent-service alembic upgrade head
docker-compose exec auth-service php artisan migrate
```

Always back up your data before updating! 