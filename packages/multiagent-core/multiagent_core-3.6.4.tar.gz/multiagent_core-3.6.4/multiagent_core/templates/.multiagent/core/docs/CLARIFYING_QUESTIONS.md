# Clarifying Questions - Architectural Issues to Resolve

**Created**: 2025-10-03
**Status**: Needs Resolution
**Purpose**: Document architectural questions and concerns discovered during E2E testing setup

---

## 1. Command System Architecture

### Q1.1: How does layered command execution actually work?
**Context**: README says commands are "layered" and invoke each other
**Questions**:
- Which commands invoke which other commands?
- What's the dependency graph?
- Is it: `project-setup` → `deploy-prepare` → `test-generate` → `docs:init`?
- Or are they independent commands you run manually in sequence?
- How do we prevent circular dependencies?

**Current State**: ⚠️ Still needs testing - theory documented but not validated

**Related**: See also Q4.1 (task layering) which has been answered with TASK_LAYERING_PRINCIPLES.md

### Q1.2: What is the actual status of `/core:project-setup`?
**Context**: Found 5+ `@claude` questions in the code
**Questions Found in Code**:
- Line 8: "@claude are we not invoking a subagent to do this..."
- Line 45: "@claude don't we already have workflows as templates..."
- Line 90: "@claude look how the projects initialize git hooks..."
- Line 98: "@claude there is wholp process that needs to be run through here..."
- Line 113: "@claude not sure about this part either..."

**Questions**:
- Is this command production-ready or incomplete?
- Should it orchestrate other commands or is it standalone?
- Should we finish it, scrap it, or mark it as "future enhancement"?
- What was the original design intent?

**Current State**: Not production-ready, has never been tested end-to-end

### Q1.3: Do we have too many command categories?
**Context**: 8 different command categories deployed with every project
**Categories**:
1. `/core:*` - Core setup
2. `/docs:*` - Documentation
3. `/deployment:*` - Deployment
4. `/testing:*` - Testing
5. `/iterate:*` - Iteration
6. `/github:*` - GitHub integration
7. `/supervisor:*` - Supervision
8. `/planning:*` - Planning

**Questions**:
- Is 8 categories too complex for typical projects?
- Should we consolidate some categories?
- Are all these commands tested and working?
- Which commands are actually used vs "nice to have"?

**Current State**: All deployed, unclear which work, unclear which are essential

---

## 2. Testing Infrastructure

### Q2.1: How does test generation vs agent test creation work?
**Context**: Potential duplication between `/testing:test-generate` and agent tasks
**Scenario**:
- `/testing:test-generate` reads `tasks.md` and creates test files
- `tasks.md` has tasks like "Create tests for authentication module" assigned to agents
- Agent creates tests... but test infrastructure already created tests?

**Questions**:
- Does `/testing:test-generate` work?
- If it works, should agents skip test creation tasks?
- If it doesn't work, should we remove it or fix it?
- What's the rule: "Agents create tests" OR "Test infrastructure creates tests, agents run them"?

**Current State**: Untested, potential duplication, unclear rules

### Q2.2: What test frameworks do we support?
**Context**: Projects can use different test frameworks
**Questions**:
- Does `/testing:test-generate` detect framework from package.json/pyproject.toml?
- What frameworks are supported? (pytest, jest, vitest, playwright, etc.)
- What if a project uses multiple frameworks (backend + frontend)?
- Does it generate intelligent test structure or just placeholders?

**Current State**: Unknown - command never tested

---

## 3. Deployment Strategy

### Q3.1: Should we deploy everything or have profiles?
**Context**: Currently deploy all `.multiagent/` and `.claude/` to every project
**Current Approach**: Deploy ~25 slash commands, all agent configs, all workflows, all scripts

**Alternative Approaches**:
```
Option A (Current): Deploy everything, use what you need
- Pro: Consistent across all projects
- Con: Overhead for simple projects

Option B: Deployment Profiles
- `--backend-heavy`: Skip frontend scaffolding (already implemented)
- `--minimal`: Core commands only (project-setup, docs, testing)
- `--full-stack`: Everything (current behavior)
- Pro: Smaller footprint for focused projects
- Con: More complexity, harder to maintain

Option C: Modular Installation
- Base: Core commands only
- Add-ons: Install `/deployment:*`, `/github:*` etc. as needed
- Pro: Maximum flexibility
- Con: Much more complex, dependency management nightmare
```

**Questions**:
- Is the current "deploy everything" approach acceptable?
- Do users complain about too many commands?
- Should we add more `--backend-heavy`-style flags?
- What's the maintenance burden of profiles vs deploy-all?

**Current State**: Deploy-all works, but maybe too heavy

### Q3.2: What's the minimum viable deployment?
**Context**: What files are absolutely required?
**Questions**:
- Can a project work with JUST `.multiagent/README.md` and core commands?
- Are agent configs (CLAUDE.md, etc.) mandatory or optional?
- Are workflows mandatory or can projects skip GitHub Actions?
- What's the smallest possible MultiAgent deployment?

**Current State**: Unknown - never tested minimal deployment

---

## 4. Specification Handoff

### Q4.1: How should `/iterate:tasks` layer tasks properly? ✅ ANSWERED
**Context**: `/iterate:tasks` transforms tasks.md into layered-tasks.md
**Answer**: Created comprehensive guide in `TASK_LAYERING_PRINCIPLES.md`

**Key Principles**:
1. **Infrastructure First**: Models → Infrastructure → Adapters → Wrappers → Integration
2. **Use Before Build**: Prefer battle-tested libraries (httpx, tenacity, fastmcp) over custom code
3. **Critical Path Blocking**: Identify tasks that block entire layers (HTTP client blocks all adapters)
4. **Proper Layer Assignment**:
   - Layer 1: Foundation (models, protocols) - BLOCKS everything
   - Layer 2: Infrastructure (HTTP, retry, auth, state) - BLOCKS adapters
   - Layer 3: Adapters (business logic) - BLOCKS wrappers
   - Layer 4: Wrappers (MCP/CLI/API) - Can run in parallel
   - Layer 5: Integration & Polish

**Implementation**:
- Command analyzes dependencies from "Depends on: T###" clauses
- Builds dependency graph
- Assigns layers based on blocking relationships
- Distributes tasks across agents per layer
- Includes "Use Before Build Decisions" documenting library choices
- Adds blocking notes explaining why Layer N+1 must wait for Layer N

**Status**: ✅ Documented, needs implementation in `/iterate:tasks` command

### Q4.2: Is the Specify → MultiAgent handoff one-way or bi-directional?
**Context**: Specify creates tasks.md, MultiAgent reads it
**Flow**:
1. Specify creates `tasks.md` (110 tasks)
2. MultiAgent init deploys infrastructure
3. `/iterate:tasks` creates `layered-tasks.md` (from tasks.md)
4. Agents complete tasks
5. **WHO UPDATES tasks.md vs layered-tasks.md?**

**Questions**:
- Do agents mark tasks complete in `tasks.md`? (`[ ]` → `[x]`)
- Or do agents only work in their worktrees and never touch main tasks.md?
- Is `layered-tasks.md` the new source of truth after layering?
- Is `tasks.md` the single source of truth or just initial input?
- What happens if user updates spec and re-runs `/tasks`?

**Current State**: Unclear - agents have TodoWrite but relationship to tasks.md undefined

### Q4.3: How do agents coordinate on shared tasks.md?
**Context**: Multiple agents working in parallel
**Scenario**:
- Agent A completes T010 in worktree `agent-claude-architecture`
- Agent B completes T025 in worktree `agent-copilot-impl`
- Both need to mark tasks complete in main repo's `tasks.md` or `layered-tasks.md`

**Questions**:
- Do agents sync back to main `tasks.md` or work independently?
- Is there a "task completion" webhook/script agents run?
- Does `layered-tasks.md` replace `tasks.md` as source of truth?
- How do we prevent merge conflicts on `tasks.md` / `layered-tasks.md`?

**Current State**: Worktree docs mention symlinks but actual coordination unclear

---

## 5. Production Readiness

### Q5.1: What must work for v1.0?
**Context**: Define minimum viable production readiness
**Critical Path**:
1. ✅ `multiagent init` deploys structure
2. ❓ Run **which commands** to set up project?
3. ❓ Agents complete **which types** of tasks?
4. ❓ What **must pass** before agents can work?
5. ❓ What **must pass** before deployment?

**Questions**:
- Which commands are absolutely required vs nice-to-have?
- What's the happy path: Specify → MultiAgent → Agents → Deploy?
- What's the minimum test coverage needed?
- What edge cases must be handled vs deferred?

**Current State**: No clear definition of "production ready"

### Q5.2: What's the testing strategy for the framework itself?
**Context**: MultiAgent is a framework - how do we test it?
**Questions**:
- Do we have E2E tests for MultiAgent itself?
- How do we test slash commands work?
- How do we test agent coordination works?
- Should we have a "reference project" that exercises everything?
- What's the CI/CD strategy for MultiAgent core?

**Current State**: No framework tests, only manual testing so far

---

## 6. Scale and Performance

### Q6.1: How big should specs be?
**Context**: Orbit spec has 110 tasks - too big for testing
**Questions**:
- What's the recommended task count? 20? 50? 100?
- Should specs be split into milestones/phases?
- How do agents handle large task lists without context overflow?
- Should we recommend "max 30 tasks per spec" as best practice?

**Current State**: No guidance, users could create 500-task specs

### Q6.2: How many agents can work in parallel?
**Context**: Worktree architecture supports parallel agent work
**Questions**:
- Is there a practical limit? (3 agents? 5? 10?)
- What's the merge conflict strategy when agents touch shared files?
- How do we prevent agents from duplicating work?
- Should task assignment prevent overlapping file changes?

**Current State**: Unknown - never tested with multiple agents

---

## 7. Documentation and Guidance

### Q7.1: What documentation is missing?
**Current Documentation**:
- ✅ `.multiagent/README.md` - Workflow guide (created today, untested)
- ✅ `.multiagent/core/docs/agent-workflows/` - Worktree, git hooks, etc.
- ❌ Command reference guide (what each command does)
- ❌ Troubleshooting guide (common issues and fixes)
- ❌ Best practices guide (spec size, task assignment, etc.)

**Questions**:
- Should we create command reference docs?
- Should we add troubleshooting flowcharts?
- Should we have video walkthroughs?
- What do users actually need to be productive?

**Current State**: Minimal documentation, assumes user knows the system

### Q7.2: How do we keep docs in sync with reality?
**Context**: Docs can drift from actual behavior
**Questions**:
- Should we have automated tests that verify docs match behavior?
- Should commands have `--help` text that matches slash command .md files?
- How do we ensure README workflow matches actual command execution?
- Who maintains documentation when commands change?

**Current State**: No sync mechanism, manual updates only

---

## 8. Error Handling and Recovery

### Q8.1: What happens when commands fail?
**Context**: Slash commands can fail mid-execution
**Scenarios**:
- `/testing:test-generate` fails reading tasks.md
- `/deployment:deploy-prepare` fails detecting framework
- `/iterate:tasks` fails creating worktrees
- `/docs:init` fails due to missing templates

**Questions**:
- Do commands have rollback mechanisms?
- Are failures logged centrally?
- How does user know what went wrong and how to fix?
- Should we have a `/debug:doctor` command to check system health?

**Current State**: Unknown error handling - never tested failure scenarios

### Q8.2: What happens when agents get stuck?
**Context**: Agents working in worktrees might hit issues
**Scenarios**:
- Agent can't complete task due to missing dependency
- Agent creates broken code that fails tests
- Agent conflicts with another agent's work
- Agent loses context mid-task

**Questions**:
- Is there a supervisor pattern to detect stuck agents?
- Do agents have a "help" mechanism to request clarification?
- How do we restart agent work without losing progress?
- Should there be a `/supervisor:rescue` command?

**Current State**: `/supervisor:*` commands exist but never tested

---

## Resolution Strategy

**Proposed Approach for Tomorrow**:

### Phase 1: Fix Critical Issues (2-3 hours)
1. Reduce Orbit spec from 110 to ~30-40 tasks
2. Test each command individually (docs:init, deploy-prepare, test-generate, iterate:tasks)
3. Document what works vs what's broken
4. Fix or remove `/core:project-setup`

### Phase 2: Validate Workflow (2-3 hours)
5. Follow `.multiagent/README.md` workflow step-by-step
6. Update README with actual tested reality
7. Document required vs optional commands
8. Create troubleshooting guide for common issues

### Phase 3: Answer Architectural Questions (1-2 hours)
9. Define test infrastructure strategy (generate vs agent-create)
10. Define task.md update strategy (one-way vs bi-directional)
11. Define production readiness criteria
12. Update documentation with decisions

### Phase 4: Production Hardening (2-3 hours)
13. Add error handling to critical commands
14. Create `/debug:doctor` health check command
15. Add command `--help` text
16. Test with second clean project to validate

**Total Estimated Time**: 7-11 hours of focused work

---

## Success Criteria

**We can call MultiAgent "production ready" when**:
1. ✅ We can drop it in a fresh project
2. ✅ Follow the README start to finish
3. ✅ All documented commands work as described
4. ✅ Agents complete at least 5 real tasks in parallel
5. ✅ Tests pass and project is deployable
6. ✅ Error messages are clear and actionable
7. ✅ Documentation matches reality

**We're NOT there yet, but we know the path forward.**

---

## Notes for Future

**Defer to v1.1+**:
- Deployment profiles (`--minimal`, `--full-stack`)
- Advanced agent coordination (10+ agents)
- Framework self-tests and CI/CD
- Video walkthroughs and tutorials
- Plugin system for custom commands

**Focus v1.0 on**:
- Core workflow works reliably
- Documentation matches reality
- Error messages are helpful
- Can ship real projects with it
