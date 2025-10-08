# Testing Commands - Test Generation & Execution

## Overview

| Command | Purpose | When to Use | Token Usage |
|---------|---------|-------------|-------------|
| `/testing:test` | Run existing tests or create new ones | During development, before commits | Low (--quick) / High (--create) |
| `/testing:test-generate` | Generate test structure from tasks | After task organization | Medium |
| `/testing:test-prod` | Validate production readiness | Before production deployment | Medium-High |

## Command Details

### 1. `/testing:test [--quick\|--create\|--frontend\|--backend\|--unit\|--e2e]`

**Purpose**: Unified testing with intelligent project detection and agent routing.

**Token-Efficient Design**:
- **NO FLAGS or --quick**: Run existing tests (~50 tokens)
- **--create or --update**: Use agents to create/update tests (~5000+ tokens)

**Flags**:
- `--quick` - Run existing tests without agents (default if tests exist)
- `--create` - Force creation of new tests using agents
- `--update` - Update existing tests using agents
- `--mock` - Use mock API responses (fast, no DB needed)
- `--frontend` - Run only frontend tests
- `--backend` - Run only backend tests
- `--unit` - Run only unit tests
- `--e2e` - Run only E2E tests
- `--ci` - Trigger CI pipeline tests

**Usage**:
```bash
/testing:test                  # Auto-detect and run existing tests
/testing:test --quick          # Run existing tests
/testing:test --create         # Create new tests (high tokens)
/testing:test --frontend       # Run only frontend tests
/testing:test --backend --unit # Run backend unit tests only
```

**Invokes**: test-generator agent (only with --create or --update)

---

### 2. `/testing:test-generate [spec-directory]`

**Purpose**: Generate intelligent test structure from task specifications.

**What It Does**:
1. Read tasks from `{spec-dir}/agent-tasks/layered-tasks.md`
2. Read template files from `.multiagent/testing/templates/`
3. Analyze task types and layers
4. Generate bash script with test structure commands
5. Save script to `.multiagent/testing/memory/generated-tests-{timestamp}.sh`
6. Execute script to create actual test files in `tests/`

**Output**: Test directory structure based on project type:
- **Backend only**: `tests/backend/` (unit, integration, e2e)
- **Frontend only**: `tests/frontend/` (unit, integration, e2e)
- **Full-stack**: Both `tests/backend/` and `tests/frontend/`

**Usage**:
```bash
/testing:test-generate specs/001-authentication
/testing:test-generate 005
```

**Invokes**: test-generator agent

---

### 3. `/testing:test-prod [--verbose] [--fix]`

**Purpose**: Validate production readiness and identify mock implementations.

**What It Does**:
1. Run `multiagent devops` CLI for deployment readiness:
   - `--deploy-check --environment production`
   - `--mock-detection --spec-path /specs/`
   - `--security-scan --production-ready`
2. Fallback to mock detector if CLI unavailable:
   - `python .claude/scripts/mock_detector.py --verbose`
3. Categorize issues by priority:
   - **Critical**: Payment, auth, database mocks
   - **High**: External APIs, configuration
   - **Medium**: Logging, monitoring, performance
4. If `--fix`: Implement real replacements for critical mocks
5. Validate fixes with scans and production tests
6. Generate prioritized remediation checklist

**Flags**:
- `--verbose` - Detailed analysis output
- `--fix` - Auto-fix critical mock implementations

**Usage**:
```bash
/testing:test-prod              # Standard scan
/testing:test-prod --verbose    # Detailed output
/testing:test-prod --fix        # Scan and fix critical issues
```

**Production Tests Location**: `testing/backend-tests/production/`

**Invokes**: production-specialist agent

---

## Test Structure Generated

### Backend Tests (`tests/backend/`)
```
tests/backend/
├── unit/
│   ├── api/              # API endpoint tests
│   ├── services/         # Service layer tests
│   ├── models/           # Database model tests
│   └── middleware/       # Middleware tests
├── integration/
│   ├── database/         # DB integration tests
│   └── external/         # External API tests
└── e2e/
    └── workflows/        # API workflow tests
```

### Frontend Tests (`tests/frontend/`)
```
tests/frontend/
├── unit/
│   ├── components/       # Component tests
│   ├── hooks/            # React hooks tests
│   └── utils/            # Utility tests
├── integration/
│   └── services/         # Service integration tests
└── e2e/
    ├── flows/            # User flow tests
    └── scenarios/        # Business scenarios
```

## Typical Testing Workflow

### Development Testing
```bash
1. /testing:test --quick           # Run existing tests
2. # Make code changes
3. /testing:test --quick           # Verify changes
4. git commit                      # Commit if tests pass
```

### New Feature Testing
```bash
1. # Complete feature implementation
2. /testing:test --create          # Generate tests (if none exist)
3. /testing:test --quick           # Run new tests
4. # Fix any failing tests
5. git commit                      # Commit with passing tests
```

### Production Deployment
```bash
1. /testing:test-prod --verbose    # Check readiness
2. /testing:test-prod --fix        # Fix critical mocks
3. /testing:test --quick           # Verify all tests pass
4. # Deploy to production
```

## Subsystem Integration

- **Core System**: Generates test configs during `/core:project-setup`
- **Deployment System**: Runs tests before deployment
- **GitHub System**: CI/CD runs tests on PRs
- **Supervisor System**: Validates test coverage

## Related Documentation

- Testing subsystem: `.multiagent/testing/README.md`
- Test generator agent: `.claude/agents/test-generator.md`
- Production specialist agent: `.claude/agents/production-specialist.md`
- Test templates: `.multiagent/testing/templates/`
