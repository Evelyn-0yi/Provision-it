# Frontend Unit Tests

Unit tests for embedded JavaScript functions in frontend HTML files.

## Setup

1. Install Node.js dependencies:
```bash
cd test/tests/frontend_unit
npm install
```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run tests with coverage
```bash
npm run test:coverage
```

### Run tests in verbose mode
```bash
npm run test:verbose
```

## Test Files

- `login.test.js` - Tests for login.html JavaScript functions
- `signup.test.js` - Tests for signup.html JavaScript functions
- `dashboard.test.js` - Tests for dashboard.html JavaScript functions
- `portfolio.test.js` - Tests for portfolio.html JavaScript functions
- `common.test.js` - Tests for browsing.html, trading.html, and profile.html JavaScript functions

## Test Utilities

- `test-utils.js` - Helper functions for loading HTML files, setting up DOM, and mocking
- `jest.setup.js` - Global setup for Jest, including mocks for fetch, sessionStorage, etc.

## Coverage

Test coverage reports are generated in the `coverage/` directory when running with `--coverage` flag.

## Integration with CI/CD

These tests are automatically run by the GitHub Actions workflow and can also be executed via:
```bash
python run_tests.py --frontend
```

