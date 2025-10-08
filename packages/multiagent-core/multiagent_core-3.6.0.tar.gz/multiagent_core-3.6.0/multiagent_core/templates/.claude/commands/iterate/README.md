# Iterate Commands - Task Organization & Ecosystem Sync

## Overview

The iterate subsystem provides 3 sequential commands for organizing tasks and maintaining spec ecosystem coherence:

| Command | Phase | Purpose | When to Use |
|---------|-------|---------|-------------|
| `/iterate:tasks` | Phase 1 | Apply task layering and agent assignment | After initial tasks.md creation |
| `/iterate:sync` | Phase 2 | Sync spec ecosystem to match layered tasks | After `/iterate:tasks` completes |
| `/iterate:adjust` | Phase 3 | Handle live development adjustments | During development when changes occur |

## Command Details

### 1. `/iterate:tasks [spec-directory]`

**Phase**: 1 - Task Layering
**Purpose**: Transform sequential tasks into layered, non-blocking parallel structure.

**What It Does**:
- Analyzes original `tasks.md` for complexity and logical grouping
- Organizes tasks into functional phases:
  - Foundation (setup, core infrastructure)
  - Implementation (features, business logic)
  - Testing (unit, integration, E2E tests)
  - Integration (deployment, documentation)
- Assigns tasks to agents based on:
  - Task complexity and specialization
  - Realistic workload distribution (Claude 45-55%, Codex 30-35%, Qwen 15-20%, Copilot 10-15%, Gemini 0-5%)
  - Agent capabilities from `agent-responsibilities.yaml`
- Generates `specs/[spec-dir]/agent-tasks/layered-tasks.md`

**Usage**:
```bash
/iterate:tasks 002-system-context-we
/iterate:tasks 005                      # Can use just the number
```

**Output**:
- Creates `specs/[spec-dir]/agent-tasks/` directory
- Generates `layered-tasks.md` with organized task structure
- Shows task distribution by agent

**Invokes**: task-layering subagent

---

### 2. `/iterate:sync [spec-directory]`

**Phase**: 2 - Ecosystem Sync
**Purpose**: Update entire spec ecosystem to match organized tasks from Phase 1.

**What It Does**:
- Reads layered tasks from Phase 1
- Updates `plan.md` with layering status and metadata
- Updates `quickstart.md` with agent coordination info
- Creates `current-tasks.md` symlink to latest iteration
- Tracks changes in `iteration-log.md`
- Ensures all spec files reference correct task structure

**Usage**:
```bash
/iterate:sync 002-system-context-we
```

**Output**:
- Updated `plan.md` with iteration metadata
- Updated `quickstart.md` with agent assignments
- Created `current-tasks.md` symlink
- Appended to `iteration-log.md`

**Script**: `.multiagent/iterate/scripts/phase2-ecosystem-sync.sh`

---

### 3. `/iterate:adjust [spec-directory]`

**Phase**: 3 - Development Adjustments
**Purpose**: Handle live changes during development while maintaining spec coherence.

**What It Does**:
- Incorporates feedback from:
  - PR reviews
  - Manual task changes
  - New requirements discovered during development
- Re-runs Phase 1 + Phase 2 with updated requirements
- Creates new iteration file (`iteration-N-tasks.md`)
- Updates entire spec ecosystem to match changes
- Maintains development audit trail
- Preserves history of all iterations

**Usage**:
```bash
/iterate:adjust 002-system-context-we
```

**Output**:
- New iteration file (`iteration-2-tasks.md`, `iteration-3-tasks.md`, etc.)
- Updated `layered-tasks.md` with new assignments
- Re-synced spec ecosystem files
- Updated `iteration-log.md` with change summary

**Script**: `.multiagent/iterate/scripts/phase3-development-adjust.sh`

---

## Typical Iterate Workflow

### Initial Task Organization (After Spec Creation)
```bash
1. Create specs/005-feature/tasks.md     # Sequential task list
2. /iterate:tasks 005                    # Phase 1: Organize and assign
3. /iterate:sync 005                     # Phase 2: Sync ecosystem
4. # Agents begin parallel work
```

### Development Adjustments (During Development)
```bash
1. # PR review identifies new requirements
2. # Edit specs/005-feature/agent-tasks/layered-tasks.md
3. /iterate:adjust 005                   # Phase 3: Re-organize and sync
4. # Agents continue with updated assignments
```

### Iteration History
```
specs/005-feature/agent-tasks/
├── layered-tasks.md              # Current active tasks
├── iteration-1-tasks.md          # First iteration (from Phase 1)
├── iteration-2-tasks.md          # After first adjust
├── iteration-3-tasks.md          # After second adjust
├── current-tasks.md -> layered-tasks.md
└── iteration-log.md              # Change history
```

## Agent Workload Distribution

The task-layering subagent follows these distribution guidelines:

| Agent | Percentage | Task Types |
|-------|-----------|------------|
| **@claude** | 45-55% | Architecture, integration, complex features, security |
| **@codex** | 30-35% | Implementation, API development, business logic |
| **@qwen** | 15-20% | Optimization, algorithm refinement, performance |
| **@copilot** | 10-15% | Simple implementation, boilerplate, utilities |
| **@gemini** | 0-5% | Research, documentation, analysis |

## Task Organization Pattern

Tasks are organized into functional phases, following the 002 pattern:

```markdown
# Phase 1: Foundation
## Authentication Core
- [ ] T001 @claude Design authentication architecture
- [ ] T002 @codex Implement JWT middleware
- [ ] T003 @qwen Optimize token validation

## Database Infrastructure
- [ ] T010 @claude Design database schema
- [ ] T011 @codex Implement database models
- [ ] T012 @copilot Create database migrations

# Phase 2: Implementation
## User Management
- [ ] T020 @codex Create user CRUD endpoints
- [ ] T021 @copilot Add input validation
- [ ] T022 @qwen Optimize user queries

# Phase 3: Testing
## Unit Tests
- [ ] T030 @codex Write authentication tests
- [ ] T031 @copilot Write user management tests

# Phase 4: Integration
## Documentation
- [ ] T040 @gemini Write API documentation
- [ ] T041 @claude Review and approve
```

## Subsystem Integration

- **Core System**: Invokes `/iterate:tasks` during `/core:project-setup`
- **Supervisor System**: Validates task assignments in `/supervisor:start`
- **GitHub System**: References task structure in PR reviews
- **Testing System**: Uses task phases to organize test generation

## Troubleshooting

### "spec directory not found"
Ensure you're using the correct spec directory name (e.g., `002-system-context-we` or just `005`).

### "layered-tasks.md missing"
Run `/iterate:tasks [spec-dir]` first before running `/iterate:sync`.

### "agent assignment seems unbalanced"
The task-layering subagent analyzes complexity. Review `agent-responsibilities.yaml` to ensure capabilities are correctly defined.

### "iteration-N-tasks.md not created"
Ensure you made actual changes to `layered-tasks.md` before running `/iterate:adjust`.

## Related Documentation

- Iterate subsystem: `.multiagent/iterate/README.md`
- Task-layering agent: `.claude/agents/task-layering.md`
- Agent responsibilities: `.multiagent/iterate/config/agent-responsibilities.yaml`
- Workflow phases: `.multiagent/README.md` (Subsystem Integration Reference)
