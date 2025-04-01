# Command Execution Service Tools

This directory contains operational utility tools for the Command Execution Service. These tools help with verification, debugging, and monitoring of the service.

## Available Tools

### Comprehensive Verification
- `verify_all.py` - Master script to run all verification tests
  - Runs both service verification and integration verification
  - Provides a consolidated summary of test results
  - Supports optional arguments to customize testing

### Verification Tools
- `verify_service.py` - Comprehensive script to verify the service functionality
  - Tests the health endpoint
  - Tests basic command execution
  - Verifies command validation (allowed vs. disallowed commands)
  - Tests complex commands with pipes

### Integration Tools
- `verify_integration.py` - Script to verify integration with the Agent Service
  - Tests the integration between command execution and agent services
  - Creates a command agent
  - Tests executing commands through the agent
  - Verifies results are correctly passed back

## Usage Examples

### Running All Verification Tests

To run all verification tests:

```bash
python tools/verify_all.py
```

To run only the service verification (skip integration tests):

```bash
python tools/verify_all.py --skip-integration
```

### Verifying Service Functionality

To verify just the command execution service:

```bash
python tools/verify_service.py
```

### Verifying Integration with Agent Service

To verify just the integration with the agent service:

```bash
python tools/verify_integration.py
```

## Environment Variables

These tools use the following environment variables:

- `COMMAND_SERVICE_URL` - URL of the command execution service (default: http://localhost:5001)
- `AGENT_SERVICE_URL` - URL of the agent service (default: http://localhost:8002)

You can set these variables before running the tools:

```bash
export COMMAND_SERVICE_URL=http://command-execution:5000
export AGENT_SERVICE_URL=http://langchain-agent:8000
python tools/verify_all.py
```

## When to Use

- **After Deployment**: Use verification tools to confirm that the service is working correctly
- **During Integration Testing**: Use integration tools to verify that services work together
- **During Troubleshooting**: When issues arise, use these tools to identify the root cause
- **CI/CD Pipeline**: Use verify_all.py in your continuous integration pipeline

## Note

These tools are for operational purposes. Test files for unit and functional testing can be found in the `/tests` directory. 