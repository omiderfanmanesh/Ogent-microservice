# Agent Integration Tests

This directory contains integration tests for the LangChain Agent service. These tests verify the functionality of the agent service components in isolation and as a complete system.

## Available Tests

### API Tests
- `test_agent_api.py` - Comprehensive test for the agent API endpoints
  - Tests agent creation through the API
  - Tests agent retrieval through the API
  - Tests agent execution through the API
  - Verifies proper error handling for invalid requests

### Agent Creation Tests
- `test_create_agent.py` - Focused test for agent creation functionality
  - Tests creation of different agent types
  - Validates agent configuration parameters
  - Tests error handling for invalid configurations

### Agent Execution Tests
- `test_agent_execution.py` - Tests agent execution functionality
  - Tests prompt execution with different agent types
  - Verifies proper response formatting
  - Tests handling of execution errors

### Direct Agent Tests
- `test_agent_direct.py` - Tests direct agent functionality (bypassing API)
- `test_direct_agent.py` - Alternative approach for direct agent testing
- `direct_test.py` - Simplified direct testing script
- `test_agent.py` - Basic agent functionality test

## Running Tests

### Running All Tests

To run all agent integration tests:

```bash
python -m pytest tests/integration/agent
```

### Running Specific Tests

To run a specific test:

```bash
python -m pytest tests/integration/agent/test_agent_api.py
```

### Running Tests with Verbosity

For more detailed output:

```bash
python -m pytest tests/integration/agent -v
```

## Test Requirements

These tests require:
1. A running agent service or a mock service (provided by `scripts/run_no_db.py`)
2. Proper environment variables (see `.env.example`)

## Writing New Tests

When adding new tests:

1. Follow the naming convention `test_*.py`
2. Include proper docstrings explaining the test purpose
3. Organize tests into logical test cases
4. Use appropriate assertions to verify results
5. Update this README when adding significant new test files
