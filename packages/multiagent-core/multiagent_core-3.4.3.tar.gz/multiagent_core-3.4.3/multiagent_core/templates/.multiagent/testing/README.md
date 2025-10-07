# Testing System - Automated Test Generation

## Purpose

The **testing** system generates comprehensive test suites based on project specifications and implementation. It:
1. **Analyzes project code** to understand what needs testing
2. **Generates test files** appropriate for the tech stack (Jest, Pytest, etc.)
3. **Creates mock implementations** for external dependencies
4. **Sets up test configurations** (jest.config.js, pytest.ini)

## Key Difference from Other Systems

- **Core system** → Creates GitHub workflows for CI/CD
- **Deployment system** → Creates Docker, K8s configs
- **Testing system** → Creates actual test files and test runners

## Agents Used

- `testing-workflow` agent - Main test generation agent
- `test-generator` agent - Creates comprehensive tests for production readiness
- Invoked via `/testing-workflow --generate` command

## Commands

### Primary Commands
- `/testing-workflow --generate` - Generate test structure
- `/test --create` - Create tests for specific files
- `/test-generate --unit` - Generate unit tests
- `/test-generate --e2e` - Generate end-to-end tests

### Integration Points
- Called by `/project-setup` during initial setup
- Used by `/test-prod` for production readiness validation

## Directory Structure

```
.multiagent/testing/
├── scripts/
│   ├── generate-tests.sh          # Main test generation
│   ├── generate-mocks.sh          # Mock creation for dependencies
│   ├── generate-tests-ai.sh       # AI-enhanced test generation
│   └── test-coverage.sh           # Coverage reporting
├── templates/
│   ├── jest/                      # Jest test templates
│   ├── pytest/                    # Pytest test templates
│   └── mocks/                     # Mock templates
├── memory/                        # Session state
└── logs/                          # Generation logs
```

## Outputs

### 1. Test Directory Structure (`tests/`)

Generated based on project type:

```
tests/
├── unit/                          # Unit tests
│   ├── api/                      # API endpoint tests
│   ├── services/                 # Service layer tests
│   └── utils/                    # Utility function tests
├── integration/                   # Integration tests
│   ├── database/                 # DB integration tests
│   └── external/                 # External API tests
├── e2e/                          # End-to-end tests
│   ├── flows/                    # User flow tests
│   └── scenarios/                # Business scenarios
└── fixtures/                      # Test data
```

### 2. Test Files Generated

| Language | Test Framework | File Pattern | Example |
|----------|---------------|--------------|---------|
| JavaScript | Jest | `*.test.js` | `api.test.js` |
| TypeScript | Jest | `*.test.ts` | `service.test.ts` |
| Python | Pytest | `test_*.py` | `test_api.py` |
| Go | Go test | `*_test.go` | `api_test.go` |

### 3. Test Configurations

| File | Purpose | When Created |
|------|---------|--------------|
| `jest.config.js` | Jest configuration | Node.js projects |
| `pytest.ini` | Pytest configuration | Python projects |
| `.coveragerc` | Coverage settings | Python projects |
| `vitest.config.js` | Vitest config | Vite projects |

### 4. Mock Files (`tests/mocks/`)

| Type | Purpose | Example |
|------|---------|---------|
| API mocks | Mock external APIs | `github-api.mock.js` |
| Database mocks | Mock DB operations | `db.mock.py` |
| Service mocks | Mock services | `auth-service.mock.ts` |

## How It Works

### 1. Project Analysis
```bash
# Script analyzes project structure
./scripts/generate-tests.sh specs/001-*
```

### 2. Stack Detection
- Reads `package.json` or `requirements.txt`
- Identifies test framework to use
- Selects appropriate templates

### 3. Test Generation
- Creates test files matching source structure
- Generates assertions based on function signatures
- Adds mock implementations for dependencies

### 4. Configuration
- Sets up test runner config
- Configures coverage thresholds
- Adds test scripts to package.json

## Template Variables

Templates use placeholders:
- `{{MODULE_NAME}}` - Module being tested
- `{{FUNCTION_NAME}}` - Function under test
- `{{TEST_FRAMEWORK}}` - Jest, Pytest, etc.
- `{{MOCK_TYPE}}` - Type of mock needed

## Example Generated Test

### JavaScript (Jest)
```javascript
describe('UserService', () => {
  let userService;
  let mockDatabase;

  beforeEach(() => {
    mockDatabase = createMockDatabase();
    userService = new UserService(mockDatabase);
  });

  describe('createUser', () => {
    it('should create a new user', async () => {
      const userData = { name: 'Test User' };
      const result = await userService.createUser(userData);

      expect(result).toHaveProperty('id');
      expect(mockDatabase.insert).toHaveBeenCalledWith('users', userData);
    });
  });
});
```

### Python (Pytest)
```python
import pytest
from unittest.mock import Mock, patch
from src.services.user_service import UserService

class TestUserService:
    @pytest.fixture
    def mock_database(self):
        return Mock()

    @pytest.fixture
    def user_service(self, mock_database):
        return UserService(database=mock_database)

    def test_create_user(self, user_service, mock_database):
        user_data = {"name": "Test User"}
        result = user_service.create_user(user_data)

        assert "id" in result
        mock_database.insert.assert_called_with("users", user_data)
```

## Integration with CI/CD

Tests are automatically run by GitHub workflows created by the core system:

1. **On Push**: Run unit tests
2. **On PR**: Run all tests + coverage
3. **Pre-deploy**: Run integration tests
4. **Post-deploy**: Run e2e tests

## Coverage Requirements

Default thresholds set in generated configs:
- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

## Running Generated Tests

### Node.js Projects
```bash
npm test              # Run all tests
npm run test:unit     # Unit tests only
npm run test:e2e      # E2E tests only
npm run test:coverage # With coverage
```

### Python Projects
```bash
pytest                      # Run all tests
pytest tests/unit          # Unit tests only
pytest tests/integration   # Integration tests
pytest --cov=src           # With coverage
```

## Troubleshooting

### Tests Not Generated
```bash
# Re-run generation with spec
.multiagent/testing/scripts/generate-tests.sh specs/001-*
```

### Missing Mocks
```bash
# Generate mocks for external dependencies
.multiagent/testing/scripts/generate-mocks.sh
```

### Coverage Too Low
```bash
# Check coverage report
npm run test:coverage
# or
pytest --cov=src --cov-report=html
```

## Key Points

- **Testing owns tests/** - All test files in `tests/`
- **Stack-appropriate** - Jest for JS, Pytest for Python
- **Comprehensive** - Unit, integration, and E2E tests
- **Mock-ready** - Generates mocks for external dependencies
- **CI/CD integrated** - Works with GitHub workflows from core