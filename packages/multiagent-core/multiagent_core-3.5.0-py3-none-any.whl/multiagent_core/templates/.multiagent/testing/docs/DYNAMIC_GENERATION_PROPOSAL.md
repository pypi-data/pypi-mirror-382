# Notes: Universal Dynamic Folder Generation Framework

**Date**: 2025-09-28  
**Context**: Building a dynamic folder structure generation system for ALL outputs instead of pre-existing static directories

## Universal Pattern: Task-Driven Folder Generation

This framework can be applied to ANY folder structure that needs to be generated based on tasks and project patterns.

## Current Observation

Instead of having a pre-existing static `/tests/` directory structure like:
```
tests/
├── backend/
├── frontend/ 
├── e2e/
├── integration/
└── unit/
```

## Proposed Solution: Dynamic Test Generation

### Philosophy: Command → Script → Template → Test Structure

Following the established pattern:
1. **Command**: `/test-generate 00X-project-name`
2. **Script**: Analyzes tasks.md to identify test patterns
3. **Templates**: Test guidance templates for different test types
4. **Output**: Generated `.multiagent/tests/` directory structure (clean, organized, avoids root duplication)

### Task Pattern Recognition

The script should analyze `specs/00X-project-name/tasks.md` and detect:

#### Frontend Tasks → Frontend Test Structure
```markdown
- [ ] T015 @codex Create responsive dashboard component
- [ ] T045 @codex Implement user login form
```
**Generates**:
```
.multiagent/tests/frontend/
├── components/
│   ├── dashboard/
│   │   ├── README.md        # Test guidance for dashboard component
│   │   └── dashboard.test.js # Generated test skeleton
│   └── login/
│       ├── README.md        # Test guidance for login form
│       └── login.test.js    # Generated test skeleton
└── README.md               # Frontend testing strategy
```

#### Backend Tasks → Backend Test Structure
```markdown
- [ ] T020 @copilot Create user authentication API
- [ ] T030 @copilot Implement data validation middleware
```
**Generates**:
```
.multiagent/tests/backend/
├── api/
│   ├── auth/
│   │   ├── README.md           # API test guidance
│   │   └── auth.test.py        # Generated API test skeleton
│   └── validation/
│       ├── README.md           # Middleware test guidance
│       └── validation.test.py  # Generated middleware test skeleton
└── README.md                  # Backend testing strategy
```

#### Integration Tasks → Integration Test Structure
```markdown
- [ ] T055 @claude Coordinate API integration testing
- [ ] T060 @claude Validate end-to-end user workflows
```
**Generates**:
```
.multiagent/tests/integration/
├── api-integration/
│   ├── README.md              # Integration test guidance
│   └── api-integration.test.js # Generated integration test skeleton
├── e2e/
│   ├── user-workflows/
│   │   ├── README.md           # E2E test guidance
│   │   └── workflows.test.js   # Generated E2E test skeleton
└── README.md                  # Integration testing strategy
```

### Template System

#### Test Guidance Templates
Located in `.multiagent/test-generate/templates/`:

1. **`component-test-guidance.md`** - How to test React/Vue components
2. **`api-test-guidance.md`** - How to test API endpoints
3. **`integration-test-guidance.md`** - How to test service integration
4. **`e2e-test-guidance.md`** - How to test user workflows
5. **`test-strategy.md`** - Overall testing approach

#### Test Skeleton Templates
1. **`component.test.template.js`** - Basic component test structure
2. **`api.test.template.py`** - Basic API test structure
3. **`integration.test.template.js`** - Basic integration test structure
4. **`e2e.test.template.js`** - Basic E2E test structure

### Script Logic Flow

1. **Parse Tasks**: Read `specs/00X-project-name/tasks.md`
2. **Categorize Tasks**: Group by test type (frontend, backend, integration, e2e)
3. **Generate Structure**: Create appropriate directory structure
4. **Apply Templates**: Fill templates with task-specific information
5. **Create Guidance**: Generate README files with testing guidance
6. **Generate Skeletons**: Create test file skeletons based on task patterns

### Command Structure

Following the established pattern:

```
/.claude/commands/testing/generate.md
```

**Script**: `.multiagent/test-generate/scripts/analyze-and-generate.sh`

**Templates**: `.multiagent/test-generate/templates/`

**Output**: Dynamic `.multiagent/tests/` directory (clean structure, updates/adds each run, avoids root duplication)

### Benefits of This Approach

1. **No Wasted Structure**: Only creates test directories for tasks that actually exist
2. **Task-Specific Guidance**: Each test guidance is tailored to the specific component/feature
3. **Agent-Ready**: Generated README files tell agents exactly what to test in clean `.multiagent/tests/`
4. **Pattern Recognition**: Learns from task patterns to suggest appropriate test types
5. **Consistent with Framework**: Follows the same Command → Script → Template → Output pattern
6. **Iterative Updates**: Each new spec run updates the same `.multiagent/tests/` folder structure 
7. **Clean Organization**: Avoids the duplication and mess of root `tests/`, keeps structure organized in framework
8. **No E2E Duplication**: Prevents creating multiple e2e directories like current root structure

### Integration with Agent Workflow

In the 45-step process, this becomes Step 3:

**Step 3: Generate Test Framework**
- **Action**: Create proactive test structure
- **Command**: `/test-generate 00X-project-name` 
- **Output**: `.multiagent/tests/unit/`, `.multiagent/tests/integration/`, `.multiagent/tests/e2e/`, guidance files
- **Purpose**: Prepare clean testing scaffold based on task patterns (avoids root duplication)
- **Status Check**: ✅ Test directories created in `.multiagent/tests/` with guidance files

## Key Pattern Note

**Framework Location**: Scripts and templates in `.multiagent/test-generate/`
**Output Location**: Generated structure in `.multiagent/tests/`
**Regeneration**: Each new spec updates the same clean `.multiagent/tests/` structure
**Agent Usage**: Agents reference `.multiagent/tests/` for their testing work

### Key Differences from Static Structure

- **Static**: Pre-existing directories that may be unused
- **Dynamic**: Generated directories based on actual requirements
- **Static**: Generic guidance for all projects
- **Dynamic**: Task-specific guidance for current project
- **Static**: Manual creation of test files
- **Dynamic**: Generated test skeletons ready for implementation

### Implementation Priority

This system should be implemented as part of Step 3 in the 45-step process, right after task layering but before agent development begins. This ensures agents have proper testing guidance when they start their work.

### Universal Application Examples

This same pattern can be applied to:

#### 1. Test Structure Generation
**Command**: `/test-generate 00X-project-name`
**Output**: Dynamic `tests/` directories based on task patterns

#### 2. Documentation Structure Generation  
**Command**: `/docs-generate 00X-project-name`
**Output**: Dynamic `docs/` directories based on features and APIs

#### 3. Source Code Structure Generation
**Command**: `/src-generate 00X-project-name`
**Output**: Dynamic `src/` directories based on architecture tasks

#### 4. Configuration Structure Generation
**Command**: `/config-generate 00X-project-name`
**Output**: Dynamic `config/` directories based on deployment tasks

#### 5. Scripts Structure Generation
**Command**: `/scripts-generate 00X-project-name`
**Output**: Dynamic `scripts/` directories based on automation tasks

### Universal Framework Benefits

1. **Task-Driven**: All structure based on actual requirements, not assumptions
2. **Zero Waste**: No unused directories or files
3. **Agent-Ready**: Generated guidance tells agents exactly what to work on
4. **Scalable**: Grows with project complexity
5. **Consistent**: Same Command → Script → Template → Output pattern everywhere
6. **Flexible**: Can generate any folder structure for any purpose

### Pattern Consistency

This maintains the proven Command → Script → Template → Output pattern while providing dynamic, task-driven folder generation that scales with ANY project output requirement, not just testing.