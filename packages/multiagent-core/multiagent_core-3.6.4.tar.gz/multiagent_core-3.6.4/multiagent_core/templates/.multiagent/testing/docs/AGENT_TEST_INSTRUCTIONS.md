# Agent Test Instructions

## Finding Your Tests

When you are assigned a task (e.g., T020), your test already exists!

### Quick Find Command:
```bash
# Find your test by task ID
find tests -name "T020*"
```

### Test Structure:
```
tests/
├── backend/           # Python/API tests
│   ├── api/          # API endpoints (T020, T023, T025)
│   ├── auth/         # Security (T022, T024, T050, T051)
│   ├── services/     # Integrations (T029, T032)
│   └── utils/        # Utilities (T002, T011, T012, T021)
└── frontend/         # JavaScript/UI tests
    ├── pages/        # Workflows (T001, T003)
    └── services/     # Frontend services (T052)
```

## Your Workflow:

1. **Get assigned task**: e.g., "T020 Create FastAPI feedback endpoint"

2. **Find your test**:
   ```bash
   find tests -name "T020*"
   # Output: tests/backend/api/T020_claude_create_fastapi_feedback_endpoint.test.py
   ```

3. **Read the test**:
   ```bash
   cat tests/backend/api/T020_*.py
   ```

4. **Run the test** (it will fail - that's expected!):
   ```bash
   pytest tests/backend/api/T020_*.py
   ```

5. **Implement your code** to make the test pass

6. **Verify test passes**:
   ```bash
   pytest tests/backend/api/T020_*.py -v
   ```

## Important Notes:

- **Tests are pre-generated** - DO NOT recreate them
- **Tests use templates** - They have proper structure
- **Tests include TODOs** - Add specific test cases as needed
- **TDD approach** - Make the existing test pass first

## Test Naming Convention:
`T{TASK_ID}_{description}.test.{ext}`

Examples:
- `T020_claude_create_fastapi_feedback_endpoint.test.py`
- `T001_claude_setup_github_actions_workflows.test.js`

## Running All Tests:
```bash
# Backend tests
pytest tests/backend/

# Frontend tests
npm test tests/frontend/

# Specific category
pytest tests/backend/api/
```