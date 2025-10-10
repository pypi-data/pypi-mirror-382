# Lightwheel SDK Tests

This directory contains the unit tests for the Lightwheel SDK.

## Test Structure

```text
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_client.py           # Tests for LightwheelClient
├── test_exception.py        # Tests for ApiException
├── test_login.py            # Tests for Login class
├── test_object_loader.py    # Tests for ObjectLoader and RegistryQuery
├── test_cli.py              # Tests for CLI commands
└── README.md                # This file
```

## Running Tests

### Prerequisites

Install the test dependencies:

```bash
pip install -e .[test]
```

### Running All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py

# With verbose output
python run_tests.py --verbose

# With coverage report
python run_tests.py --coverage
```

### Running Specific Tests

```bash
# Run a specific test file
python run_tests.py --path tests/test_client.py

# Run a specific test class
pytest tests/test_client.py::TestLightwheelClient

# Run a specific test method
pytest tests/test_client.py::TestLightwheelClient::test_init_with_default_host
```

### Test Markers

The test suite uses pytest markers to categorize tests:

- `unit`: Unit tests (fast, isolated)
- `integration`: Integration tests (slower, may require external services)
- `slow`: Tests that take a long time to run

```bash
# Run only unit tests
python run_tests.py --markers "unit"

# Skip slow tests
python run_tests.py --markers "not slow"
```

## Test Coverage

To generate a coverage report:

```bash
python run_tests.py --coverage
```

This will generate:
- Terminal coverage report
- HTML coverage report in `htmlcov/` directory

## Writing New Tests

### Test File Naming

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Fixtures

Common fixtures are available in `conftest.py`:

- `mock_client`: Mock LightwheelClient instance
- `mock_requests`: Mock requests.post and requests.get
- `sample_api_response`: Sample successful API response
- `sample_error_response`: Sample error API response
- `temp_cache_dir`: Temporary directory for cache files

### Example Test

```python
def test_example_function(mock_client, mock_requests):
    """Test example function."""
    mock_post, _ = mock_requests
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_post.return_value = mock_response
    
    # Your test code here
    result = some_function()
    
    assert result is not None
    mock_post.assert_called_once()
```

## Mocking Guidelines

### HTTP Requests

Use the `mock_requests` fixture to mock HTTP calls:

```python
def test_api_call(mock_requests):
    mock_post, mock_get = mock_requests
    
    # Mock POST response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_post.return_value = mock_response
    
    # Your test code
```

### File System Operations

Use `patch` to mock file system operations:

```python
from unittest.mock import patch, mock_open

def test_file_operation():
    with patch('builtins.open', mock_open()) as mock_file:
        # Your test code that writes/reads files
        pass
```

### Environment Variables

Use `patch.dict` to mock environment variables:

```python
import os
from unittest.mock import patch

def test_env_variable():
    with patch.dict(os.environ, {'LW_API_ENDPOINT': 'https://test.api.com'}):
        # Your test code
        pass
```

## Continuous Integration

The test suite is designed to run in CI environments:

- All tests should be deterministic
- No external network calls (use mocks)
- No file system dependencies (use temporary directories)
- Fast execution time

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the package is installed in development mode: `pip install -e .`

2. **Missing Dependencies**: Install test dependencies: `pip install -e .[test]`

3. **Test Failures**: Run with verbose output to see detailed error messages: `pytest -v`

4. **Coverage Issues**: Make sure all code paths are tested and mocks are properly configured

### Debug Mode

To run tests in debug mode:

```bash
pytest --pdb
```

This will drop into the Python debugger on test failures.
