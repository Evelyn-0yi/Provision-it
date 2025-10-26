# Test Package

This directory contains all test-related files and utilities for the Provision-it project.

## Structure

```
test/
├── __init__.py              # Package initialization
├── README.md               # This file
├── test_utils/             # Test utilities and helper functions
│   ├── __init__.py
│   └── database_utils.py   # Database test utilities
├── tests/                  # Actual test files
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── E2E                 # End-to-end Playwright tests
│   ├── Jest                # JavaScript functions unit tests in htmls
│   ├── infrastructure/     # Database tests
└── test_database/          # Database test management
    ├── __init__.py
    ├── manage_test_db.py   # Database setup/teardown script
    ├── manage.py           # Database for programmatic access
    ├── setup_schema.py     # Database schema
    ├── setup.py            # Test database setup utilities
    ├──shared_utils.py      # Database shared utils
    └── init_test_db.py     # Database initialization script
```

## Running Tests

From the project root:

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --unit
python run_tests.py --database
python run_tests.py --integration
python run_tests.py --infrastrcuture
python run_tests.py --Jest
python run_tests.py --e2e --auto-flask

# With coverage
python run_tests.py --unit --coverage

# With details
python run_tests.py --unit --verbose
```

## Test Types

### Unit Tests (`test/tests/unit/`)
- Test individual components in isolation
- Use mocks and fixtures
- Fast execution
- High coverage

### Integration Tests (`test/tests/integration/`)
- Test component interactions
- Use real database connections
- Test API endpoints
- End-to-end workflows

### Database Tests (`test/infrastructure/`)
- Test database schema and setup
- Verify database constraints
- Test data fixtures
- Database isolation

### E2E Tests (`test/tests/E2E/`)
- Test complete user workflows end-to-end
- Use Playwright for browser automation
- Test real user interactions
- Validate full application functionality

### Jest Tests (`test/tests/Jest/`)
- Test JavaScript functions in HTML files
- Unit tests for frontend JavaScript code
- Validate client-side functionality
- Test user interface interactions

## Test Utilities (`test/test_utils/`)

### `database_utils.py`
- Database creation and setup utilities
- Schema management
- Test data seeding
- Database verification functions

## Database Management (`test/test_database/`)

### `manage_test_db.py`
Main script for managing the test database:
- `create` - Create test database
- `drop` - Drop test database
- `reset` - Reset test database (drop + create)
- `full-setup` - Complete setup (schema + sample data)
- `info` - Show database information

### `init_test_db.py`
Database initialization script used by the main management script.

## Configuration

Tests use pytest with the following configuration:
- `pytest.ini` - Main pytest configuration
- `test/tests/conftest.py` - Test fixtures and configuration
- Environment variables from `.env` file

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Tests should clean up after themselves
3. **Fixtures**: Use pytest fixtures for common setup
4. **Mocking**: Mock external dependencies in unit tests
5. **Coverage**: Aim for high test coverage
6. **Naming**: Use descriptive test names
7. **Documentation**: Document complex test scenarios