# Workflow Generation Architecture

**Last Updated**: 2025-09-29
**Status**: Active Pattern

## Overview

GitHub workflows are NOT copied during `multiagent init`. Instead, they are intelligently generated during `/project-setup` based on the actual project requirements discovered from specifications.

## The Problem We Solved

Previously, all workflows were blindly copied to new projects, resulting in:
- Python projects getting Node.js workflows
- Local-only tools getting deployment workflows
- Backend-only APIs getting frontend build workflows
- Unnecessary CI/CD for projects that don't need it

## The Solution: Context-Aware Generation

### Phase 1: Init (No Workflows)

```bash
multiagent init my-project
```

**What gets copied**:
```
.github/
├── ISSUE_TEMPLATE/         ✅ Universal templates
├── copilot-instructions.md ✅ Agent instructions
└── labels.yml             ✅ Standard labels
```

**What does NOT get copied**:
```
.github/
├── workflows/             ❌ Generated later
├── prompts/              ❌ Already in .specify
└── WORKFLOW_CONFIGURATION.md ❌ Moved to docs
```

### Phase 2: Specification

```bash
/specify "Build task management API with FastAPI"
/plan
/tasks
```

**Now we know**:
- Language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL
- Deployment: AWS Lambda
- Testing: pytest, coverage

### Phase 3: Project Setup (Workflow Generation)

```bash
/project-setup specs/001-task-api
```

**What happens**:
1. **Validation Script** checks existing config
2. **Core agent** reads specifications
3. **Determines needed workflows**:
   - Python → pytest workflow
   - API → security scanning
   - AWS → deployment workflow
4. **Generates from templates**
5. **Writes to .github/workflows/**

## Template Structure

### Base Templates Location
```
.multiagent/
├── security/templates/workflows/
│   └── security-scan.yml.template
├── testing/templates/workflows/
│   ├── python-test.yml.template
│   ├── node-test.yml.template
│   └── integration-test.yml.template
└── deployment/templates/workflows/
    ├── deploy-aws.yml.template
    ├── deploy-vercel.yml.template
    └── deploy-local.yml.template
```

### Template Variables
```yaml
# python-test.yml.template
name: Python Tests - {{PROJECT_NAME}}
on:
  push:
    branches: [{{DEFAULT_BRANCH}}]
jobs:
  test:
    runs-on: {{RUNNER_OS}}
    strategy:
      matrix:
        python-version: [{{PYTHON_VERSIONS}}]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r {{REQUIREMENTS_FILE}}
          pip install {{TEST_DEPENDENCIES}}
      - name: Run tests
        run: {{TEST_COMMAND}}
```

## Generation Logic

### The Validation Script
```bash
# check-project-config.sh
detect_project_type() {
    # Read spec.md and plan.md
    # Detect: python|node|go|rust|etc
}

check_existing_files() {
    # Check if workflows already exist
    # Don't overwrite without confirmation
}
```

### The Generation Process
```python
def generate_workflows(spec_context):
    workflows = []

    # Language-specific workflows
    if spec_context.language == "python":
        workflows.append("python-test.yml")
        workflows.append("python-lint.yml")
    elif spec_context.language == "javascript":
        workflows.append("node-test.yml")
        workflows.append("eslint.yml")

    # Feature-specific workflows
    if spec_context.has_api:
        workflows.append("security-scan.yml")

    if spec_context.deployment_target:
        workflows.append(f"deploy-{spec_context.deployment_target}.yml")

    # Generate each
    for workflow in workflows:
        template = read_template(workflow + ".template")
        filled = fill_template(template, spec_context)
        write(f".github/workflows/{workflow}", filled)
```

## Examples: Different Projects, Different Workflows

### Example 1: Python CLI Tool (Local Only)
```yaml
# Generated workflows:
.github/workflows/
├── python-test.yml      # Unit tests with pytest
└── python-lint.yml      # Ruff and black formatting
```

### Example 2: Full-Stack Application
```yaml
# Generated workflows:
.github/workflows/
├── frontend-test.yml    # Jest, React Testing Library
├── frontend-build.yml   # Next.js build
├── backend-test.yml     # Pytest, API tests
├── integration.yml      # E2E with Playwright
├── security-scan.yml    # TruffleHog, Bandit
└── deploy-vercel.yml    # Frontend deployment
└── deploy-aws.yml       # Backend deployment
```

### Example 3: Microservice
```yaml
# Generated workflows:
.github/workflows/
├── test.yml            # Service tests
├── docker-build.yml    # Container build
├── trivy-scan.yml      # Container security
└── deploy-k8s.yml      # Kubernetes deployment
```

## The Table-Setting Pattern

This follows our core philosophy:

1. **Scripts** (Mechanical Work):
   - Check what exists
   - Copy template files
   - Create directories

2. **Templates** (Context):
   - Show workflow structure
   - Provide patterns
   - Define variables

3. **Agents** (Intelligence):
   - Read specifications
   - Decide what's needed
   - Customize templates
   - Write final workflows

## Benefits

### 1. No Waste
- Only workflows you need
- No unused CI/CD running

### 2. Correct Configuration
- Python project gets Python tools
- Node project gets npm/yarn commands
- Local tools don't get deployment

### 3. Fast Generation
- Takes 10-15 minutes
- Well-documented patterns
- Agents know the templates

### 4. Maintainable
- Templates in one place
- Easy to update
- Version controlled

## Integration Points

### With project-setup Command
```markdown
## Step 7: Generate Workflows
Based on project analysis:
1. Run validation script
2. Determine needed workflows
3. Read templates from .multiagent/[system]/templates/workflows/
4. Fill templates with project context
5. Write to .github/workflows/
```

### With Config Validation
```bash
# After checking config files
if project_needs_workflows; then
    generate_workflows_for_project
fi
```

## Future Enhancements

### Smart Conditionals
Instead of separate workflows, use GitHub Actions conditionals:
```yaml
- name: Python Tests
  if: hashFiles('**/*.py')
  run: pytest

- name: Node Tests
  if: hashFiles('package.json')
  run: npm test
```

### Workflow Composition
Combine smaller workflow fragments:
```yaml
workflows = compose(
    base_workflow,
    language_steps,
    deployment_steps,
    security_steps
)
```

### Registry-Based Templates
Fetch templates from a registry:
```bash
fetch_template("python-fastapi-aws")
```

## Troubleshooting

### Workflow Not Generated
1. Check spec.md has clear technology indicators
2. Verify plan.md includes technical details
3. Run validation script manually
4. Check template exists

### Wrong Workflow Generated
1. Spec may be ambiguous
2. Update detection patterns
3. Manually specify in project-setup

### Workflow Fails
1. Check generated variables
2. Verify dependencies exist
3. Test locally first

## Summary

Workflows are generated intelligently based on project needs, not blindly copied. This ensures each project gets exactly the CI/CD it needs, when it needs it, configured correctly for its technology stack.