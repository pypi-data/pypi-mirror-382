# Layered Tasks: {{SPEC_NAME}}

**Generated**: {{TIMESTAMP}}
**Source**: Original tasks.md transformed for non-blocking parallel execution
**Usage**: Agents read from this file instead of tasks.md for parallel coordination

<!--
IMPORTANT FOR TASK-LAYERING AGENT:
This template has TXXX placeholders that MUST be replaced with actual task numbers FROM tasks.md.

DO NOT INVENT NEW NUMBERS - USE EXISTING TASK IDS:
1. Read specs/{{SPEC_NAME}}/tasks.md to see all existing tasks with their IDs
2. Group and organize those tasks by functional phase and agent
3. Keep the ORIGINAL task numbers (T001, T002, T012, etc.) from tasks.md
4. Just reorganize them into layers - don't renumber anything

Example from tasks.md:
  "- [ ] T012 Create docs-init subagent"
Becomes in layered-tasks.md:
  "- [ ] T012 @claude Create docs-init subagent in .claude/agents/"

PRESERVE ALL ORIGINAL TASK NUMBERS - only add organization and agent assignments.
-->

## Non-Blocking Parallel Architecture

**Core Principle**: ALL agents work simultaneously in isolated worktrees - ZERO blocking dependencies.

### How It Works
1. **Every agent starts immediately** - no waiting for other agents
2. **Work in parallel worktrees** - complete isolation, no conflicts
3. **Integrate via Git PRs** - merge when ready, {{COORDINATOR_AGENT}} resolves conflicts
4. **No sequential layers** - all work happens concurrently

### Agent Specializations (Realistic Workload)
- **@claude**: Primary workhorse (45-55%) - Complex subagents, commands, coordination
- **@codex**: Secondary workhorse (30-35%) - Scripts, templates, testing
- **@qwen**: Third workhorse (15-20%) - Templates, validation, implementation
- **@copilot**: Straightforward backend (10-15%) - JSON state, simple data
- **@gemini**: Minimal use (0-5%) - Large-scale analysis (rarely needed)

---

## Layer 1: Foundation & Setup

**Purpose**: Foundation setup before implementation begins.

### Phase 1.1: Foundation Tasks

#### @claude Foundation Tasks
- [ ] TXXX @claude [Task description with file path]
- [ ] TXXX @claude [Task description with file path]

**Format Example**: `- [ ] T012 @claude Create documentation-manager subagent in .claude/agents/`

#### @codex Foundation Tasks
- [ ] TXXX @codex [Task description with file path]
- [ ] TXXX @codex [Task description with file path]

#### @copilot Foundation Tasks
- [ ] TXXX @copilot [Task description with file path]

---

## Layer 2: Core Implementation

**Purpose**: Parallel implementation - all agents work simultaneously.

### Phase 2.1: Parallel Implementation

#### @claude Implementation Tasks
- [ ] TXXX [P] @claude [Task description with file path]
- [ ] TXXX [P] @claude [Task description with file path]
- [ ] TXXX [P] @claude [Task description with file path]

**Format Example**: `- [ ] T016 [P] @claude Implement spec reading logic in subagent`

**Note**: [P] indicates truly parallel tasks (different files, no dependencies)

#### @codex Implementation Tasks
- [ ] TXXX [P] @codex [Task description with file path]
- [ ] TXXX [P] @codex [Task description with file path]
- [ ] TXXX [P] @codex [Task description with file path]

#### @qwen Implementation Tasks
- [ ] TXXX [P] @qwen [Task description with file path]
- [ ] TXXX [P] @qwen [Task description with file path]

#### @copilot Implementation Tasks
- [ ] TXXX [P] @copilot [Task description with file path]
- [ ] TXXX [P] @copilot [Task description with file path]

---

## Layer 3: Testing & Integration

**Purpose**: Validate complete system functionality.

### Phase 3.1: Testing & Validation

#### @claude Testing Tasks
- [ ] TXXX @claude [Task description with file path]
- [ ] TXXX @claude [Task description with file path]

#### @codex Testing Tasks
- [ ] TXXX @codex [Task description with file path]
- [ ] TXXX @codex [Task description with file path]

#### @qwen Testing Tasks
- [ ] TXXX @qwen [Task description with file path]

---

## Agent Coordination Protocol

### Contract-Driven Development
1. **Foundation first**: Complete Layer 1 foundation tasks
2. **Parallel implementation**: All agents work simultaneously in Layer 2
3. **No cross-dependencies**: Layer 2 tasks have no dependencies on each other
4. **Clean integration**: Layer 3 validates everything works together

### Communication Through Structure
- **All coordination** happens through layered structure
- **Layer changes** require re-running /iterate:tasks command
- **Implementation isolation**: Agents work independently
- **Integration points** clearly defined in Layer 3

### Worktree Protocol
1. **Create your worktree**: `git worktree add -b agent-[name]-[feature] ../project-[name] main`
2. **Start your tasks immediately** - don't wait for anyone
3. **Work in isolation** - your worktree is yours alone
4. **Commit frequently** - track your progress
5. **Push and PR when ready** - merge when your work is complete

### Integration via Git
- **No blocking** - agents never wait for each other
- **PRs merge independently** - GitHub Actions validates each PR
- **Conflicts resolved by {{COORDINATOR_AGENT}}** - CTO-level coordination when needed
- **Continuous integration** - work flows in as it completes

### Task Status Tracking
- **[ ]**: Task pending, ready for work
- **[x] ✅**: Task completed successfully
- **Dependencies**: Check layer dependencies and (depends on...) annotations

### Agent Specializations Summary
- **@claude**: Strategic architecture, SDK integration, complex coordination
- **@copilot**: Data models, straightforward implementation
- **@codex**: Scripts, automation, documentation, testing infrastructure
- **@qwen**: Performance optimization, validation testing
- **@gemini**: Research, analysis, documentation (when needed)

### Benefits
1. **Eliminates blocking**: After foundation, implementation is fully parallel
2. **Clear boundaries**: Each layer has distinct purpose and dependencies
3. **Independent work**: No need to coordinate during implementation
4. **Testable interfaces**: Layer 3 defines exact validation criteria
5. **Clean integration**: Components fit together by structural design

**Last Updated**: {{TIMESTAMP}}
**Refresh**: Run `/iterate:tasks {{SPEC_NAME}}` to regenerate