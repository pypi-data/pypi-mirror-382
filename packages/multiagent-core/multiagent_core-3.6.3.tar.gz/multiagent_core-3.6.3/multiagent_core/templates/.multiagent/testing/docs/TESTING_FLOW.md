# Testing System Flow

## Correct Pattern: Command → Script → Template → Output

### 1. Command (.claude/commands/testing/testing-workflow.md)
- Orchestrates the workflow
- NO inline code
- Tells ME when to:
  - Run helper scripts for analysis
  - Invoke subagents for generation
  - Verify outputs

### 2. Scripts (.multiagent/testing/scripts/)
These are TOOLS that:
- Set up directory structure
- Read spec files
- Apply templates
- Generate output

**Key Scripts:**
- `test-coverage.sh` - Analyzes current test coverage
- `generate-tests.sh` - PRIMARY: Creates test structure using templates with backend/frontend detection
- `generate-mocks.sh` - Creates mock implementations
- `archive/` - Archived experimental variants (not used)

### 3. Templates (.multiagent/testing/templates/)
These are ACTUAL FILE TEMPLATES with placeholders:
- `backend_template.test.py` - Python test template
- `frontend_template.test.js` - JavaScript test template
- `integration_template.test.js` - Integration test template
- NOT markdown documentation files

### 4. Subagent (.claude/agents/test-structure-generator.md)
The subagent:
- Reads the ENTIRE spec folder (especially layered-tasks.md)
- Understands what's being built
- Runs the scripts with appropriate parameters
- Uses templates to generate tests

### 5. Output (/tests in project root)
```
/tests/
├── backend/
│   ├── api/
│   ├── auth/
│   ├── services/
│   └── models/
└── frontend/
    ├── components/
    ├── pages/
    └── hooks/
```

## The Flow in Action

1. **User runs**: `/testing-workflow --generate`

2. **Command orchestrates**:
   - Runs `test-coverage.sh` to check current state
   - Invokes test-structure-generator subagent

3. **Subagent executes**:
   - Reads specs/*/agent-tasks/layered-tasks.md
   - Runs `generate-tests.sh specs/001-build-a-complete tests`
   - Script detects backend/frontend, uses templates to create actual test files

4. **Script does the work**:
   - Creates directory structure
   - Reads tasks from layered-tasks.md
   - For each task, fills template with task info
   - Outputs to /tests directory

5. **Verification**:
   - Command checks /tests was created
   - Reports success to user

## Why This Pattern Works

- **Commands** are generic orchestrators
- **Scripts** are reusable tools
- **Templates** are actual file templates (not docs)
- **Subagents** understand context and use the tools
- **Output** goes to project root, not .multiagent

## Current Issues to Fix

1. Some scripts have inline test generation instead of using templates
2. Templates directory has some .md files that are docs, not templates
3. Scripts need to be callable by subagents, not just manually

## Success Criteria

✅ Running `/testing-workflow` generates tests in /tests
✅ Tests are based on layered-tasks.md content
✅ Uses actual code templates, not hardcoded strings
✅ Works through command → subagent → script flow
✅ Outputs to project root, not .multiagent subdirectory