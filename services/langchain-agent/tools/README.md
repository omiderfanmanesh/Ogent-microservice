# LangChain Agent Service Tools

This directory contains operational utility tools for the LangChain Agent service. These tools help with verification, debugging, and monitoring of the service.

## Available Tools

### Verification Tools
- `verify_agent_service.py` - Comprehensive script to verify the agent service functionality
- `verify_service.py` - Tests overall service health and API endpoints

### Debugging Tools
- `debug_agent_creation.py` - Helps identify issues in the agent creation process
- `debug_agent_structure.py` - Examines the agent object structure for debugging

## Usage Examples

### Verifying Service Functionality

To verify the agent service:

```bash
python tools/verify_agent_service.py
```

### Debugging Agent Creation

To debug issues with agent creation:

```bash
python tools/debug_agent_creation.py
```

## When to Use

- **After Deployment**: Use verification tools to confirm that the service is working correctly in the production environment
- **During Troubleshooting**: When issues arise, use the debugging tools to identify the root cause

## Adding New Tools

When adding new tools to this directory:

1. Ensure the tool serves an operational purpose (verification, debugging, monitoring)
2. Include proper error handling and logging
3. Add descriptive comments
4. Update this README with information about the new tool

## Note

This directory is for operational tools only. Test files belong in the `/tests` directory.
