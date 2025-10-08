# Spec-Kit vs MultiAgent Patterns: Key Differences

## Executive Summary

**Spec-Kit**: Direct template filling with step-by-step instructions in templates
**MultiAgent**: Subagent-driven with templates as context/guidance

## The Fundamental Difference

### Spec-Kit Pattern (Direct Execution)
```
Command → Script → Template (with instructions) → Direct Output
```
- **Templates contain execution flow**: Step-by-step instructions
- **No subagents**: Claude directly follows template instructions
- **Scripts do setup**: Create directories, check prerequisites
- **Output**: Directly to specs/001-feature-name/

### MultiAgent Pattern (Subagent Intelligence)
```
Command → Orchestration → Subagent (reads templates for context) → Intelligent Output
```
- **Templates show structure**: Examples and patterns, not instructions
- **Subagents do the work**: Autonomous, intelligent generation
- **Scripts for bulk ops**: Things agents can't easily do
- **Output**: Various locations (deployment/, tests/, etc.)

## Detailed Comparison

### 1. Templates

#### Spec-Kit Templates (.specify/templates/)
```markdown
## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
2. Extract: tech stack, libraries, structure
3. Generate tasks by category
4. Apply task rules
5. Number tasks sequentially
```
```
**Purpose**: Step-by-step instructions for direct execution
**Who reads**: Claude directly (no subagent)
**Content**: Procedural instructions with error handling

#### MultiAgent Templates (.multiagent/*/templates/)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
```
**Purpose**: Show expected output structure
**Who reads**: Subagents for context
**Content**: Examples and patterns to follow

### 2. Commands

#### Spec-Kit Commands (.github/prompts/)
```markdown
1. Run script `.specify/scripts/bash/create-new-feature.sh`
2. Load `.specify/templates/spec-template.md`
3. Write specification to SPEC_FILE using template
4. Report completion
```
**Direct execution**: Claude follows these steps exactly

#### MultiAgent Commands (.claude/commands/)
```markdown
1. PRE-WORK: Run scan-mocks.sh
2. SUBAGENT: Invoke deployment-prep agent
3. POST-WORK: Verify outputs
```
**Orchestration**: Commands coordinate, subagents implement

### 3. Scripts

#### Spec-Kit Scripts (.specify/scripts/bash/)
- `create-new-feature.sh`: Creates branch and directory
- `check-prerequisites.sh`: Validates environment
- `setup-plan.sh`: Initializes plan structure
- `update-agent-context.sh`: Updates agent files

**Purpose**: Essential setup Claude can't do (no subagents to help)

#### MultiAgent Scripts (.multiagent/*/scripts/)
- `scan-mocks.sh`: Scan 100+ files (bulk operation)
- `find-pr-spec-directory.sh`: Complex GitHub API piping

**Purpose**: Only what subagents CAN'T efficiently do

**Key Difference**: MultiAgent subagents replace most scripts with their tools (Read, Write, Bash), keeping only performance-critical or system-integration scripts.

### 4. Execution Flow & Output Patterns

#### Spec-Kit Flow (Single Output Location)
```
/specify "User authentication"
    ↓
.specify/templates/ → Provide structure/format
    ↓
Commands fill templates directly
    ↓
Output: specs/001-user-authentication/
        ├── spec.md (from spec-template.md)
        ├── plan.md (from plan-template.md)
        └── tasks.md (from tasks-template.md)
```
**Single output**: Everything goes in the spec folder

#### MultiAgent Flow (Dual Output Pattern)
```
/project-setup → Invokes security-auth-compliance subagent
    ↓
.multiagent/security/ → System infrastructure (stays in repo)
├── templates/ → Context/structure for subagent
├── scripts/ → Bulk operation tools
    ↓
Subagent reads templates, analyzes project, makes decisions
    ↓
DUAL OUTPUT:

1. SPEC OUTPUT (Documentation & Reports):
   specs/003-security-setup/security/
   ├── reports/
   │   ├── security-setup-report.md
   │   └── compliance-check.md
   ├── docs/
   │   ├── SECRET_MANAGEMENT.md
   │   └── SECURITY_CHECKLIST.md
   └── configs/
       └── security-config.json

2. PROJECT OUTPUT (Actual Infrastructure):
   project-root/
   ├── .gitignore (deployed security patterns)
   ├── .env.example (safe template)
   └── .git/hooks/ (secret scanning)
```

#### Another Example: Deployment System
```
/deploy-prepare specs/001-user-authentication
    ↓
DUAL OUTPUT:

1. SPEC OUTPUT (Analysis & Decisions):
   specs/001-user-authentication/deployment/
   ├── analysis-report.md
   └── deployment-decisions.md

2. PROJECT OUTPUT (Actual Configs):
   deployment/
   ├── docker/
   │   └── Dockerfile
   ├── k8s/
   │   └── deployment.yaml
   └── configs/
       └── .env.production
```

### 5. Intelligence Location

#### Spec-Kit
**Intelligence in templates**: Templates contain logic and decision trees
```markdown
## Execution Flow (main)
→ If not found: ERROR "No implementation plan found"
→ Extract: tech stack, libraries, structure
→ Different files = mark [P] for parallel
```

#### MultiAgent
**Intelligence in subagents**: Templates are just examples
```yaml
# Subagent sees this pattern and adapts intelligently
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
```

## Key Pattern Differences

### Building on Previous Work

#### Both Follow Same Pattern
```
/specify → spec.md
    ↓
/plan → reads spec.md → plan.md
    ↓
/tasks → reads spec.md + plan.md → tasks.md
```

### But Execution Differs

#### Spec-Kit
- Direct template execution
- Step-by-step instructions
- Error handling in templates
- No autonomous decisions

#### MultiAgent
- Subagent autonomy
- Templates as guidance
- Intelligent adaptation
- Complex decision making

## When to Use Each Pattern

### Use Spec-Kit Pattern When:
- Output is highly structured (specs, plans, tasks)
- Process is deterministic
- Steps are well-defined
- No complex analysis needed

### Use MultiAgent Pattern When:
- Output requires analysis (deployment configs)
- Process needs intelligence (security setup)
- Adaptation required (different tech stacks)
- Complex decisions needed (test generation)

## Migration Path

To convert spec-kit style to multiagent:

### 1. Extract Instructions from Templates
Move execution flow from templates to subagent instructions

### 2. Convert Templates to Examples
Change from instructions to structural examples

### 3. Create Subagents
Add subagents for intelligent work

### 4. Update Commands
Change from direct execution to orchestration + subagent invocation

## The Golden Rule

**Spec-Kit**: Templates tell you WHAT TO DO
**MultiAgent**: Templates show you WHAT IT LOOKS LIKE

## Examples in Practice

### Spec-Kit: Creating a Spec
```markdown
Template says: "Extract key concepts from description"
Claude does: Extracts key concepts directly
```

### MultiAgent: Creating Deployment
```markdown
Template shows: Example Dockerfile structure
Subagent does: Analyzes project, chooses base image, adds dependencies
```

## Output Pattern Summary

### Spec-Kit: Single Output
- **Location**: specs/XXX-feature-name/
- **Content**: Documentation only (spec.md, plan.md, tasks.md)
- **Purpose**: Planning and specification

### MultiAgent: Dual Output
- **Spec Output**: specs/XXX-feature/[system-name]/ - Reports, documentation, analysis
- **Project Output**: Project root or specific directories - Actual infrastructure/configs
- **Purpose**: Both documentation AND implementation

### Why Dual Output?

MultiAgent systems need to:
1. **Document what they did** (spec output) - for tracking and review
2. **Deploy actual infrastructure** (project output) - for the project to use

This separation keeps:
- Specs clean and focused on documentation
- Project structure organized with actual configs
- Clear audit trail of what was generated

## Summary

The fundamental differences:
- **Spec-Kit** = Template-driven direct execution, single output location
- **MultiAgent** = Subagent-driven intelligent generation, dual output pattern

Both patterns work well for their use cases. Spec-kit excels at structured document generation. MultiAgent excels at complex, adaptive generation requiring both documentation and actual implementation.