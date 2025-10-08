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
4. **Layers organize work logically** - not sequential blocking, just smart grouping

### Layering Philosophy: Infrastructure First + Use Before Build

**Infrastructure First**: Foundation before things that depend on it
- Layer 1: Models, protocols, base types (everyone imports these)
- Layer 2: Infrastructure services (HTTP, retry, cache, auth)
- Layer 3: Business logic (adapters, domain code)
- Layer 4: Wrappers (MCP tools, CLI commands, API endpoints)
- Layer 5: Integration (tests, docs, polish)

**Use Before Build**: Prefer battle-tested libraries over custom code
- ✅ USE httpx (not custom HTTP client)
- ✅ USE tenacity (not custom retry logic)
- ✅ USE FastMCP (not custom MCP protocol)
- ✅ USE Click (not custom CLI parser)
- ✅ USE SQLAlchemy (not custom ORM)
- ❌ BUILD only domain-specific logic (your secret sauce)

**Result**: All layers start immediately because infrastructure ALREADY EXISTS!

### Agent Specializations (Realistic Workload)
- **@claude**: Primary workhorse (45-55%) - Complex architecture, models, coordination
- **@codex**: Secondary workhorse (30-35%) - Scripts, templates, testing infrastructure
- **@qwen**: Third workhorse (15-20%) - Implementation, validation, optimization
- **@copilot**: Straightforward tasks (10-15%) - Data models, simple adapters
- **@gemini**: Minimal use (0-5%) - Large-scale analysis (rarely needed)

---

## Layer 1: Foundation (Models, Protocols, Base Types)

**Purpose**: Core types that everything else imports - NO blocking, just logical organization!

**Why This Layer**: Models/protocols/configs are imported by infrastructure and adapters
**Can Start Now**: All different files, all agents start immediately

**Use Before Build Decisions for This Layer**:
- ✅ USE Pydantic v2 for all models (validation, JSON schema, FastAPI integration)
- ✅ USE platformdirs for OS-native config directories
- ✅ USE standard Python protocols (typing.Protocol)

### @claude Foundation Tasks (Models & Core Types)
- [ ] TXXX @claude [Task description with file path]
- [ ] TXXX @claude [Task description with file path]

**Example**: `- [ ] T031 @claude RunRecord model in orbit/sdk/state/models.py`

### @codex Foundation Tasks (Configuration & Setup)
- [ ] TXXX @codex [Task description with file path]
- [ ] TXXX @codex [Task description with file path]

### @copilot Foundation Tasks (Supporting Models)
- [ ] TXXX @copilot [Task description with file path]

**Note**: All tasks in Layer 1 can start NOW - different files, no waiting!

---

## Layer 2: Infrastructure (HTTP, Retry, Cache, Auth)

**Purpose**: Shared services that adapters consume - NO blocking, all start now!

**Why This Layer**: Provides services (HTTP client, retry, auth) for business logic
**Can Start Now**: All different files, all agents start immediately

**Use Before Build Decisions for This Layer**:
- ✅ USE httpx for HTTP client (async, pooling, timeouts) - just wrap with telemetry
- ✅ USE tenacity for retry logic (exponential backoff, jitter, predicates)
- ✅ USE cachetools for caching (TTL, LRU built-in)
- ✅ USE SQLAlchemy + Alembic for state manager (ORM + migrations)
- ❌ BUILD AuthProvider protocol (vendor auth varies: API key vs OAuth2)

### @claude Infrastructure Tasks (HTTP, State, Protocols)
- [ ] TXXX [P] @claude [Task description with file path]
- [ ] TXXX [P] @claude [Task description with file path]

**Example**: `- [ ] T038 [P] @claude HTTP client with telemetry in orbit/sdk/core/http.py`

**Note**: [P] = truly parallel (different files, no dependencies)

### @codex Infrastructure Tasks (Retry, Cache, Auth)
- [ ] TXXX [P] @codex [Task description with file path]
- [ ] TXXX [P] @codex [Task description with file path]

### @copilot Infrastructure Tasks (Auth Implementations)
- [ ] TXXX [P] @copilot [Task description with file path]

**Note**: All Layer 2 tasks can start NOW - infrastructure libs already exist!

---

## Layer 3: Business Logic (Adapters, Domain Code)

**Purpose**: Domain-specific logic using Layer 1 models + Layer 2 infrastructure

**Why This Layer**: Core business value - vendor integrations, workflows, etc.
**Can Start Now**: All different files (different vendors/domains)

**Use Before Build Decisions for This Layer**:
- ❌ BUILD all adapters (CATS, Dayforce, Email, SMS) - domain-specific, custom logic
- ✅ USE adapters consume httpx, tenacity, AuthProvider from Layer 2

### @copilot Business Logic Tasks (Adapters)
- [ ] TXXX [P] @copilot [Task description with file path]
- [ ] TXXX [P] @copilot [Task description with file path]

**Example**: `- [ ] T051 [P] @copilot CATS adapter in orbit/sdk/ats/cats.py`

### @gemini Business Logic Tasks (Additional Adapters)
- [ ] TXXX [P] @gemini [Task description with file path]

**Note**: All adapters parallel - different vendor APIs, different files!

---

## Layer 4: Wrappers (MCP Tools, CLI Commands, API Endpoints)

**Purpose**: Expose SDK via different interfaces - thin delegation only!

**Why This Layer**: Presentation layers with NO business logic
**Can Start Now**: All different files, completely independent streams

**Use Before Build Decisions for This Layer**:
- ✅ USE FastMCP for MCP server (official framework, handles protocol)
- ✅ USE Click for CLI (standard, completion support)
- ✅ USE FastAPI for API (async, validation, OpenAPI docs)
- ❌ BUILD thin wrappers only - all delegate to SDK adapters

### @qwen Wrapper Tasks (MCP Tools)
- [ ] TXXX [P] @qwen [Task description with file path]
- [ ] TXXX [P] @qwen [Task description with file path]

**Example**: `- [ ] T057 [P] @qwen MCP search_candidates tool`

### @copilot Wrapper Tasks (CLI Commands)
- [ ] TXXX [P] @copilot [Task description with file path]

### @gemini Wrapper Tasks (API Endpoints)
- [ ] TXXX [P] @gemini [Task description with file path]

**Note**: MCP/CLI/API can ALL work in parallel - completely independent!

---

## Layer 5: Integration & Polish

**Purpose**: End-to-end tests, documentation, performance validation

**Why This Layer**: Validate integrated system works as whole
**Can Start Now**: All different test/doc files

### @codex Integration Tasks (Testing)
- [ ] TXXX [P] @codex [Task description with file path]
- [ ] TXXX [P] @codex [Task description with file path]

**Example**: `- [ ] T096 [P] @codex Integration test: CLI → MCP → SDK flow`

### @gemini Polish Tasks (Documentation)
- [ ] TXXX [P] @gemini [Task description with file path]

**Note**: Tests and docs can all run in parallel!

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