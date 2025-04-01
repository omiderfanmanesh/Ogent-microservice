# LangChain Agent Service Scripts

This directory contains deployment and maintenance scripts for the LangChain Agent service. These scripts automate common tasks related to deployment, testing, and maintenance of the service.

## Primary Scripts

### Deployment Scripts
- `deploy.sh` - Main deployment script for applying fixes to the agent service
  - Copies necessary files into the Docker container
  - Replaces problematic code with fixed versions
  - Restarts the service to apply changes
  - Runs verification tests to ensure functionality

### Maintenance Scripts
- `run_no_migration.py` - Script to run the service without database migrations
- `cleanup_scripts.sh` - Script to clean up redundant deployment scripts
- `cleanup_fixes.sh` - Script to organize the fixes directory
- `final_cleanup.sh` - Final cleanup script for removing duplicate files

### Testing Scripts
- `run_no_db.py` - Simplified version of the service for testing without database connectivity
  - Provides mock implementations of all API endpoints
  - Useful for testing the API interface without database dependencies
  - Can be used in a standalone Docker container for isolation testing

## Usage Examples

### Deploying the Service

To deploy the latest fixes to the agent service:

```bash
./deploy.sh
```

This will copy all the necessary files to the Docker container, replace problematic code with fixed versions, and restart the service.

### Running Without Migrations

To run the service without performing database migrations:

```bash
python run_no_migration.py
```

This is useful when you want to quickly restart the service without waiting for migrations to complete.

### Testing Without Database

To run a simplified version of the service without database dependencies:

```bash
# Create a test container
docker run -d --name ogent-agent-service-test -p 8002:8000 --entrypoint "python" -v $(pwd):/app ogent-microservice-agent-service /app/scripts/run_no_db.py

# Test the health endpoint
curl -X GET http://localhost:8002/api/health

# Test the agent creation endpoint
curl -X POST http://localhost:8002/api/agents -H "Content-Type: application/json" -d '{"name":"Test Agent", "agent_type":"conversational"}'
```

### Cleaning Up the Repository

To clean up redundant scripts:

```bash
./cleanup_scripts.sh
```

To organize the fixes directory:

```bash
./cleanup_fixes.sh
```

## Best Practices

When working with these scripts:

1. Always make them executable before running: `chmod +x script_name.sh`
2. Test in a development environment before deploying to production
3. Review the script contents to understand what actions will be performed
4. Back up critical files before running potentially destructive scripts

## Script Development Guidelines

When adding new scripts:

1. Include a descriptive shebang line (e.g., `#!/bin/bash`)
2. Add comments explaining what the script does
3. Include error handling with appropriate exit codes
4. Print meaningful status messages
5. Make variables configurable where appropriate
6. Update this README with the new script details
