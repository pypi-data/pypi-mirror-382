# MultiAgent Core System Workflow Pattern

## The Real Pattern: How Everything Actually Works

This documents how the MultiAgent Core system ACTUALLY operates - not theoretical patterns, but the real workflow from command to output.

## Foundation: Building on Spec-Kit

**THIS IS THE BIBLE**: MultiAgent is designed to build off Spec-Kit, never duplicate it.

### The Sacred Division of Labor
```
Spec-Kit Provides              MultiAgent Adds
─────────────────              ───────────────
• Specifications              • Infrastructure
• Planning                    • Deployment configs
• Task generation             • Testing suites
• Documentation               • Security setup
• Vision/requirements         • CI/CD workflows
```

### The Fundamental Principle
**Never recreate what Spec-Kit already does**
- Read their outputs, don't regenerate them
- Use their specs as your input
- Build infrastructure from their documentation
- Generate code from their tasks

## Core Philosophy: Separating Mechanical from Intelligence

**The Table-Setting Approach**: When you run a slash command, YOU are the agent executing it. Scripts don't replace you - they set the table for you to do intelligent work.

```
Mechanical Work (Scripts)     →  Intelligence Work (Agent/You)
├── Create directories            ├── Read context & requirements
├── Copy templates                ├── Make technical decisions
├── Set up structure              ├── Customize configurations
└── Validate outputs              └── Adapt to project needs
```

**Building on Spec-Kit Foundation**: Each step reads outputs from Spec-Kit and builds infrastructure:
```
PHASE 1: SPEC-KIT CREATES FOUNDATION
/specify → creates spec.md
/plan → reads spec.md → creates plan.md, data-model.md, contracts/
/tasks → reads spec.md + plan.md → creates tasks.md

PHASE 2: MULTIAGENT BUILDS ON SPEC-KIT
/project-setup → reads ALL Spec-Kit outputs → creates infrastructure
/iterate:tasks → reads tasks.md → creates layered-tasks.md
/deploy-prepare → reads EVERYTHING → creates deployment/
/testing-workflow → reads specs + code → creates tests/
```

**Key Difference from Spec-Kit**: While spec-kit uses templates with step-by-step instructions for direct execution, MultiAgent uses subagents that read templates for context and generate intelligently. See [SPECKIT_VS_MULTIAGENT_PATTERNS.md](./SPECKIT_VS_MULTIAGENT_PATTERNS.md) for detailed comparison.

## The ACTUAL Workflow Pattern

```
User Command → Command File → Orchestration → Subagent Work → Script Tools → Template Context → Generated Output
```

### The Key Insight: The Slash Command IS the Agent

When you run `/project-setup`, you ARE the agent. The workflow is:

1. **Scripts Set the Table** (Mechanical, Consistent)
   - Create directory structure
   - Copy templates to locations
   - Gather context files
   - "Here's your workspace"

2. **Templates Provide the Recipe** (Context, Guidelines)
   - Show expected structure
   - Provide patterns to follow
   - Mark decision points
   - "Here's what you need to create"

3. **You/Agent Cook the Meal** (Intelligence, Adaptation)
   - Read gathered context
   - Make technical decisions
   - Customize for project
   - "I understand and will create"

### Real Example: Deployment System

```
/deploy-prepare specs/002-system-context-we
    ↓
.claude/commands/deployment/deploy-prepare.md (orchestrates)
    ↓
1. PRE-WORK (Command does this):
   - Run scan-mocks.sh (check for test code)
   - Check git status
   - Read ALL spec files (not just spec.md!)
   - Create context file at /tmp/deployment-context.txt
    ↓
2. SUBAGENT WORK (deployment-prep agent):
   - Reads templates to understand expected outputs
   - Gets context from all spec directories
   - Analyzes requirements deeply
   - Makes technical decisions
   - Generates configurations based on templates + specs
    ↓
3. SCRIPT TOOLS (Helper scripts):
   - generate-deployment.sh (bulk generation)
   - detect-stack.sh (pattern matching)
   - Not for step-by-step work - for bulk operations!
    ↓
4. TEMPLATES (Context, not fill-in):
   - Dockerfile.template → Shows structure
   - docker-compose.template → Shows patterns
   - NOT variable replacement (mostly)
   - Templates are GUIDANCE for agents
    ↓
5. DUAL OUTPUT:
   a) SPEC OUTPUT (Documentation):
      specs/002-system/deployment/
      └── deployment-analysis.md

   b) PROJECT OUTPUT (Infrastructure):
      deployment/
      ├── docker/
      ├── k8s/
      └── configs/
```

## System Components & Their REAL Roles

### 1. Commands (.claude/commands/*)
**Purpose**: Orchestration and coordination
**What they do**:
- Parse user input
- Run pre-flight checks
- Decide WHEN to invoke subagents
- Validate outputs
- Report to user

**What they DON'T do**:
- Complex analysis (that's for subagents)
- Bulk generation (that's for scripts)
- Direct file manipulation (use tools)

### 2. Subagents (.claude/agents/*)
**Purpose**: Autonomous, intelligent work
**What they do**:
- Read templates to understand expected outputs
- Get context from spec directories (spec.md, plan.md, tasks.md, etc.)
- Deep analysis of project structure
- Technical decision making
- Multi-step workflows
- Complex generation tasks
- Use their existing tools (Read, Write, Edit, etc.)

**What they DON'T do**:
- Simple file operations (they have tools for that)
- Orchestration (that's the command's job)

### 3. Scripts (.multiagent/*/scripts/)
**Purpose**: Setting the table for agent intelligence
**What they do (MECHANICAL WORK)**:
- Create consistent directory structures
- Copy templates to proper locations
- Gather context into accessible files
- Batch processing (faster than agent Read() 100 times)
- Complex git/GitHub operations
- System operations agents can't do
- Performance-critical scanning

**What they DON'T do**:
- Replace agent intelligence
- Make architectural decisions
- Customize content (that's for agents)

**The Mise en Place Pattern**: Like a chef's preparation, scripts prepare everything the agent needs:
```
Scripts prepare:          Agent then uses:
├── Workspace ready       → Makes decisions
├── Templates copied      → Adapts patterns
├── Context gathered      → Understands requirements
└── Tools available       → Creates intelligently
```

### 4. Templates (.multiagent/*/templates/)
**Purpose**: Context and structure guidance for subagents
**What they do**:
- Show agents the STRUCTURE of expected outputs
- Provide patterns and examples to follow
- Give context about what needs to be generated
- Define the format and organization of outputs
- Sometimes variable replacement (but rarely)

**What they DON'T do**:
- Simple fill-in-the-blank (mostly)
- Replace agent intelligence
- Dictate exact content

### 5. Memory & Logs (.multiagent/*/memory/, logs/)
**Purpose**: State tracking and debugging
**What they do**:
- Track session state
- Store analysis results
- Debug information
- Build on previous runs

## The Dual Output Pattern (MultiAgent Systems)

Unlike spec-kit which outputs only to specs/, MultiAgent systems create TWO outputs:

### 1. Spec Output (Documentation/Reports)
**Location**: `specs/XXX-feature/[system-name]/`
**Purpose**: Track what was done, analysis, decisions
**Examples**:
- `specs/003-security/security/reports/` - Security audit reports
- `specs/001-api/deployment/analysis.md` - Deployment decisions
- `specs/002-auth/testing/coverage-report.md` - Test coverage analysis

### 2. Project Output (Actual Infrastructure)
**Location**: Project root or specific directories
**Purpose**: The actual files the project needs to run
**Examples**:
- `.gitignore` - Security patterns (root)
- `deployment/docker/Dockerfile` - Container config
- `tests/unit/` - Generated test files
- `.github/workflows/` - CI/CD pipelines

### Why This Pattern?

**Separation of Concerns**:
- Specs stay clean - only documentation
- Project gets real files - ready to use
- Clear audit trail - what was generated when

**Example: Security System**
```
/project-setup runs security-auth-compliance agent
    ↓
Creates TWO outputs:
1. specs/003-security/security/compliance-report.md (documentation)
2. .gitignore, .env.example, .git/hooks/ (actual security infrastructure)
```

## Folder Structure Pattern

Every system follows this structure:
```
.multiagent/[system-name]/
├── README.md           # What this system does
├── docs/              # Additional documentation
│   └── KNOWN_ISSUES.md # Bugs and workarounds
├── scripts/           # Helper scripts for bulk ops
│   ├── generate-*.sh  # Generation scripts
│   └── analyze-*.sh   # Analysis scripts
├── templates/         # Context templates
│   ├── structure/     # Show output structure
│   └── patterns/      # Show code patterns
├── memory/           # Session state
│   └── [session].json # Remembers what was done
└── logs/            # Debug information
    └── [session].log  # What happened
```

## How Systems Build on Each Other

### 1. Spec-Kit Foundation (ALWAYS FIRST - THIS IS THE BIBLE)
```
/specify → spec.md (template-driven generation)
    ↓
/plan → plan.md + data-model.md + contracts/ (template instructions)
    ↓
/tasks → tasks.md (template-based task generation)
```
**CRITICAL**: Spec-kit MUST run first - it creates the foundation MultiAgent builds upon
**Note**: Spec-kit commands use templates with step-by-step instructions, no subagents

### 2. Iteration Layer (Subagent-Driven)
```
/iterate:tasks → reads tasks.md → layered-tasks.md (subagent analysis)
    ↓
/iterate:sync → reads all specs → updates ecosystem (subagent coordination)
```
**Transition**: From spec-kit's direct templates to subagent intelligence

### 3. Implementation Layer (Full Subagent Work)
```
/project-setup → reads specs → creates structure (security-auth-compliance agent)
    ↓
/work → reads layered-tasks.md → implements tasks (multiple specialized agents)
    ↓
/testing-workflow → reads implementation → generates tests (backend-tester agent)
```
**Full subagent pattern**: Templates are context, subagents do all work

### 4. Deployment Layer
```
/deploy-prepare → reads EVERYTHING → deployment/
    ↓
/deploy-validate → reads deployment/ → validates
```

### 5. Feedback Loop
```
/pr-review:pr → reads PR → feedback/tasks.md
    ↓
/iterate:sync → reads feedback → updates specs
    ↓
(cycle continues)
```

## Critical Understanding Points

### The Separation of Mechanical from Intelligence

**Mechanical Work (Scripts)**:
- Predictable, repetitive tasks
- Structure creation
- File copying
- Pattern matching
- Bulk operations

**Intelligence Work (Agents)**:
- Decision making
- Context understanding
- Customization
- Adaptation to requirements
- Creative problem solving

### Scripts Set the Table, Agents Cook the Meal
❌ WRONG: Script tells agent step-by-step what to do
✅ RIGHT: Script prepares workspace, agent does intelligent work

Example:
```bash
# Script (Mechanical):
create-structure.sh      # Creates specs/001-feature/ directory
copy-templates.sh        # Copies spec-template.md to location
gather-context.sh        # Collects project info to /tmp/context.txt

# Agent (Intelligence):
- Reads the context gathered by scripts
- Understands project requirements
- Makes technical decisions
- Customizes templates with project-specific content
```

### Templates Are Context, Not Mad Libs
❌ WRONG: `{{VARIABLE}}` everywhere for simple replacement
✅ RIGHT: Show structure and patterns for agent to follow

Example:
```dockerfile
# This is a TEMPLATE showing structure, not variables:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# Agent understands this PATTERN and adapts it
```

### Subagents Are Specialists, Not Executors
❌ WRONG: Subagent just runs scripts
✅ RIGHT: Subagent reads templates for context, analyzes specs, and generates intelligently

Example:
- Command: "Deploy this FastAPI app"
- Subagent workflow:
  1. Reads Dockerfile.template to understand structure
  2. Reads spec.md, plan.md, data-model.md for requirements
  3. Analyzes actual code to detect dependencies
  4. Chooses Python base image based on analysis
  5. Adds Uvicorn because it detected FastAPI
  6. Configures health checks based on API endpoints found
  7. Generates final Dockerfile following template structure but with intelligent adaptations

### Everything Builds on Previous Work
❌ WRONG: Each command starts fresh
✅ RIGHT: Each command reads previous outputs

Example:
- `/deploy-prepare` reads:
  - spec.md (what to build)
  - plan.md (architecture)
  - data-model.md (database needs)
  - layered-tasks.md (components)
  - contracts/ (API endpoints)

## Implementation Checklist for New Systems

When creating a new system, ensure:

### Structure
- [ ] Create `.multiagent/[system-name]/` directory
- [ ] Add comprehensive README.md
- [ ] Create scripts/ for bulk operations
- [ ] Create templates/ for context/patterns
- [ ] Setup memory/ for state tracking
- [ ] Setup logs/ for debugging

### Command Pattern
- [ ] Command in `.claude/commands/[category]/`
- [ ] Command does orchestration, not implementation
- [ ] Pre-work validation and checks
- [ ] Subagent invocation for complex work
- [ ] Post-work validation
- [ ] Clear output location

### Integration
- [ ] Reads previous system outputs
- [ ] Outputs in predictable location
- [ ] Builds on existing work
- [ ] Enables next step in workflow

### Documentation
- [ ] Document in system README
- [ ] Update this pattern doc
- [ ] Add to docs/README.md
- [ ] Track known issues

## Common Anti-Patterns to Avoid

### 1. Scripts Doing Agent Work
❌ Script with 500 lines of logic making decisions
✅ Script that helps agent with bulk operations

### 2. Templates as Code Generators
❌ Template with complex variable substitution
✅ Template showing patterns for agent to follow

### 3. Commands Doing Implementation
❌ Command that generates files directly
✅ Command that orchestrates and invokes specialists

### 4. Ignoring Previous Work
❌ Starting fresh every time
✅ Reading and building on what exists

### 5. Hardcoding Values
❌ Hardcoded usernames, paths, repos
✅ Dynamic detection from environment

## The Golden Rule: Mise en Place

Like a professional kitchen, everything has its place and purpose:

**Scripts** = Prep Cooks (Mechanical)
- Set up workstations
- Prepare ingredients
- Organize tools
- Consistent, repeatable tasks

**Templates** = Recipes (Context)
- Show the dish structure
- Guide preparation
- Suggest techniques
- Provide patterns

**Agents** = Chefs (Intelligence)
- Read the recipes
- Taste and adjust
- Make creative decisions
- Adapt to available ingredients

**Commands** = Head Chef (Orchestration)
- Coordinate the kitchen
- Time the workflow
- Quality control
- Direct the team

When in doubt, ask: "Is this mechanical work (scripts) or intelligence work (agents)?"

## Summary: One Source of Truth

This document is the **single source of truth** for how MultiAgent Core works:
- **BUILDS ON SPEC-KIT**: MultiAgent extends Spec-Kit, never duplicates
- **Mechanical vs Intelligence**: Scripts prepare, agents create
- **Table-Setting Pattern**: Scripts set up workspace for agent intelligence
- **Dual Output**: Specs (documentation) + Project (infrastructure)
- **Building on Foundation**: Each step reads Spec-Kit outputs and builds infrastructure
- **Command = Agent**: When you run a slash command, YOU are the agent

All other pattern documents should reference this as the authoritative guide.

## The Sacred Order of Operations

1. **Spec-Kit Phase** (Foundation): /specify → /plan → /tasks
2. **MultiAgent Phase** (Infrastructure): /project-setup → /deployment → /testing
3. **Never Skip Step 1**: MultiAgent REQUIRES Spec-Kit outputs to function