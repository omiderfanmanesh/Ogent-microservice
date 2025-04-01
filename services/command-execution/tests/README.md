# Command Execution Service Tests

This directory contains tests for the Command Execution Service to verify its functionality.

## Available Tests

### API Tests
- `test_command_api.py` - Tests the Command Execution Service API
  - Tests the health endpoint
  - Tests simple command execution
  - Tests command execution with arguments
  - Tests complex commands with pipes
  - Tests command cancellation
  - Tests disallowed commands

## Running Tests

### Running All Tests

To run all tests:

```bash
cd services/command-execution
python -m unittest discover -s tests
```

### Running a Specific Test

To run a specific test:

```bash
cd services/command-execution
python -m unittest tests.test_command_api
```

## Environment Variables

These tests use the following environment variables:

- `COMMAND_SERVICE_URL` - URL of the command execution service (default: http://localhost:5001)

You can set these variables before running the tests:

```bash
export COMMAND_SERVICE_URL=http://command-execution:5000
python -m unittest tests.test_command_api
```

## Test Requirements

These tests require:
1. A running command execution service
2. Network access to the service API

## Writing New Tests

When adding new tests:

1. Follow the naming convention `test_*.py`
2. Use the `unittest` framework for test structure
3. Include docstrings explaining the test purpose
4. Organize tests into test cases
5. Use appropriate assertions to verify results
6. Update this README when adding significant new test files

## Note

These tests are for verification and quality assurance. For operational tools and service verification, see the `/tools` directory. 