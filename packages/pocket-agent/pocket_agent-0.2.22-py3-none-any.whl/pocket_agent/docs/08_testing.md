# Testing

Pocket Agent includes a comprehensive test suite covering all core functionality. The tests are designed to be fast and reliable using in-memory FastMCP servers and mocked LLM responses.

## Running Tests

The easiest way to run tests is using the provided test runner script:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run with coverage reporting (Coverage reports are generated in `htmlcov/`)
python run_tests.py --coverage

# Run quick subset for development
python run_tests.py --quick
```
