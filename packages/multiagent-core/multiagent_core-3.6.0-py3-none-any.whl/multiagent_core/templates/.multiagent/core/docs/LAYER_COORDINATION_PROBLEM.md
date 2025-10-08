# Layer Coordination Problem - CRITICAL ISSUE

**Created**: 2025-10-03
**Status**: ⚠️ BLOCKING ISSUE - Needs Resolution Before Layering Works
**Discovered By**: User feedback on agent task visibility

---

## The Problem

**Layered tasks with blocking dependencies don't work if agents can't see real-time progress.**

### Current Broken Flow

```
1. /iterate:tasks creates layered-tasks.md:
   ┌─────────────────────────────────────────┐
   │ Layer 1: Foundation (BLOCKS Layer 2)   │
   │ - T031 @claude RunRecord model         │
   │ - T032 @claude StepRecord model        │
   │ - T033 @copilot Configuration model    │
   └─────────────────────────────────────────┘
   ┌─────────────────────────────────────────┐
   │ Layer 2: Infrastructure (needs Layer 1) │
   │ - T038 @claude HTTP client             │
   │ - T039 @copilot Retry logic            │
   └─────────────────────────────────────────┘

2. @claude creates worktree, starts T031

3. @claude completes T031, commits to branch agent-claude-001

4. @claude creates PR for review

5. @copilot wants to start T038 (Layer 2)

6. ❌ Problem: T038 depends on T031, but PR not merged yet!

7. @copilot reads layered-tasks-main.md (symlink to main)

8. Main repo still shows T031 incomplete (PR pending)

9. @copilot BLOCKED - can't start Layer 2

10. ❌ Entire layering system fails!
```

---

## Root Causes

### Issue 1: PR Merge Latency
- Agents complete tasks in worktrees
- Create PRs for review
- **But PRs take time to merge** (CI, review, approval)
- During this time, main repo shows task incomplete
- Dependent agents are blocked unnecessarily

### Issue 2: Symlink Points to Main (Stale State)
```bash
# Worktree symlink
layered-tasks-main.md → ../../../main-repo/specs/001/agent-tasks/layered-tasks.md

# This shows PR-pending state, not work-complete state
# Agents see tasks as incomplete even when work is done
```

### Issue 3: No Cross-Worktree Visibility
```bash
# @claude worktree
specs/001/layered-tasks.md       ← T031 marked [x] locally

# @copilot worktree
specs/001/layered-tasks-main.md  ← Still shows T031 [ ] (from main)

# @copilot CAN'T SEE @claude's completed work until PR merges
```

---

## Possible Solutions

### Option A: Shared Progress File (Immediate Visibility)

**Concept**: Separate real-time progress tracking outside of layered-tasks.md

**Implementation**:
```bash
# Main repo has both:
specs/001/agent-tasks/layered-tasks.md        ← Task definitions (immutable)
specs/001/agent-tasks/.progress.json          ← Live progress (agents update)

# .progress.json structure:
{
  "last_updated": "2025-10-03T14:32:15Z",
  "layers": {
    "1": {
      "status": "in_progress",
      "completed": 5,
      "total": 8,
      "blocking_layer_2": true
    },
    "2": {
      "status": "blocked",
      "waiting_for": "layer_1",
      "completed": 0,
      "total": 11
    }
  },
  "tasks": {
    "T031": {
      "status": "completed",
      "agent": "claude",
      "worktree": "agent-claude-001",
      "pr": "#123",
      "pr_status": "pending_review",
      "completed_at": "2025-10-03T14:15:00Z"
    },
    "T032": {
      "status": "in_progress",
      "agent": "claude",
      "worktree": "agent-claude-001",
      "started_at": "2025-10-03T14:30:00Z"
    },
    "T033": {
      "status": "available",
      "dependencies": [],
      "assigned_to": "copilot"
    },
    "T038": {
      "status": "blocked",
      "dependencies": ["T031", "T032", "T033"],
      "assigned_to": "claude"
    }
  }
}
```

**Agent Workflow**:
```bash
# 1. Agent checks which tasks are available
orbit-agent check-available-tasks 001

# Reads .progress.json, finds tasks where:
# - status = "available" OR "assigned to me"
# - all dependencies have status = "completed"

# 2. Agent marks task started
orbit-agent start-task T031
# Updates .progress.json: T031 status → "in_progress"

# 3. Agent completes work, commits
git commit -m "feat: Complete T031 RunRecord model"

# 4. Agent marks task complete (even before PR merge!)
orbit-agent complete-task T031 --pr 123
# Updates .progress.json: T031 status → "completed"

# 5. Other agents see update immediately
# @copilot checks T038 dependencies:
# - T031: completed ✅
# - T032: in_progress ⏳
# - T033: available ⏸️
# Result: T038 still blocked (needs all 3)
```

**Pros**:
- ✅ Real-time visibility across all agents
- ✅ No waiting for PR merges
- ✅ Atomic updates (JSON file changes)
- ✅ Can track PR status separately from work status
- ✅ `/supervisor:mid` can read this to check progress

**Cons**:
- ❌ Two sources of truth (layered-tasks.md + .progress.json)
- ❌ Potential race conditions if multiple agents update simultaneously
- ❌ Requires new CLI commands (check-available-tasks, start-task, complete-task)

---

### Option B: Layer Branches (Sequential Merging)

**Concept**: Create branches per layer, merge layers sequentially

**Implementation**:
```bash
# Main repo has layer branches
main
├── layer-1-foundation     (base: main)
├── layer-2-infrastructure (base: layer-1-foundation) ← blocked until layer-1 merged
├── layer-3-adapters       (base: layer-2-infrastructure)
├── layer-4-wrappers       (base: layer-3-adapters)
└── layer-5-integration    (base: layer-4-wrappers)

# Agent workflow:
1. @claude creates worktree from layer-1-foundation
   git worktree add -b agent-claude-layer1 ../project-claude layer-1-foundation

2. @claude completes T031, T032, commits to layer-1-foundation
   git commit -m "feat: Complete Layer 1 models"
   git push origin layer-1-foundation

3. When ALL Layer 1 tasks complete:
   - Merge layer-1-foundation → main
   - This UNBLOCKS layer-2-infrastructure

4. @copilot creates worktree from layer-2-infrastructure
   git worktree add -b agent-copilot-layer2 ../project-copilot layer-2-infrastructure
   # This branch now has ALL Layer 1 work automatically
```

**Pros**:
- ✅ Natural blocking (can't start layer-2 branch until layer-1 merged)
- ✅ Git enforces dependencies
- ✅ Clean merge history (one merge per layer)
- ✅ Works with existing worktree system

**Cons**:
- ❌ Requires ALL layer tasks complete before next layer starts (strict waterfall)
- ❌ Can't have partial layer completion
- ❌ Complicates worktree setup (need to track base branches)
- ❌ What if one task in Layer 1 is blocked? Entire Layer 2 stuck

---

### Option C: Dependency-Only (No Strict Layers)

**Concept**: Forget layers, just track task dependencies

**Implementation**:
```bash
# layered-tasks.md simplified:
- [ ] T031 @claude RunRecord model
      Dependencies: None

- [ ] T038 @claude HTTP client
      Dependencies: T034, T037
      Blocks: T051, T052, T053, T054

- [ ] T051 @copilot CATS adapter
      Dependencies: T038, T044, T039
      Blocks: T058

# Agent picks any task where dependencies are complete
# No concept of "layers" - just dependency graph
```

**Agent Workflow**:
```bash
# Agent queries available tasks
orbit-agent list-available --for claude

# Returns:
Available for @claude:
- T031 (no dependencies)
- T032 (no dependencies)

Blocked for @claude:
- T038 (waiting for T034, T037)

# Agent starts work
orbit-agent start T031

# Agent completes, marks in progress file
orbit-agent complete T031

# Other agents see T031 complete, can start dependent tasks
```

**Pros**:
- ✅ Maximum parallelism (no artificial layer boundaries)
- ✅ Handles partial completions gracefully
- ✅ Simpler mental model (just dependencies)
- ✅ More resilient (one blocked task doesn't block entire layer)

**Cons**:
- ❌ Harder to visualize progress (no clear phases)
- ❌ Agents might pick tasks in wrong order
- ❌ Still needs shared progress file

---

### Option D: Optimistic Merging (Trust + Verify)

**Concept**: Trust agents completed work before PR merges, verify in CI

**Implementation**:
```bash
# Agent completes task, updates shared file immediately
1. @claude completes T031
2. @claude updates main repo's .progress.json directly:
   git checkout main
   # Update .progress.json
   git commit -m "chore: Mark T031 complete"
   git push origin main

3. @claude creates worktree PR with actual code
   # PR #123 still pending review

4. @copilot sees T031 marked complete in .progress.json
5. @copilot starts T038 (depends on T031)

6. CI runs on both PRs:
   - Validates T031 code exists and passes tests
   - Validates T038 can import from T031

7. If T031 PR fails → reject T038 PR (dependency broken)
8. If T031 PR passes → approve both
```

**Pros**:
- ✅ No blocking on PR merges
- ✅ Agents work in parallel immediately
- ✅ CI catches integration issues

**Cons**:
- ❌ Risk: Agent marks complete but PR fails review
- ❌ Wasted work if dependency PR rejected
- ❌ Requires robust CI to catch issues

---

## Recommended Solution: Hybrid (A + C)

**Combine**:
- **Option A** (Shared Progress File) for real-time coordination
- **Option C** (Dependency-Only) for flexibility

**Implementation**:

### 1. Layered-Tasks Structure (Soft Layers for Organization)
```markdown
# layered-tasks.md

## Layer 1: Foundation (Informational - Not Blocking)
These are high-priority tasks with no dependencies

- [ ] T031 @claude RunRecord model
      Dependencies: None
      Blocks: T038, T047, T058

- [ ] T032 @claude StepRecord model
      Dependencies: None
      Blocks: T047

## Layer 2: Infrastructure
Wait for Layer 1 ONLY if your task depends on it

- [ ] T038 @claude HTTP client
      Dependencies: T034, T037 (REQUIRED before starting)
      Blocks: T051, T052, T053, T054
```

**Key Change**: "Layers" are organizational hints, not hard blocks

### 2. Shared Progress File
```bash
specs/001/agent-tasks/.progress.json

# Updated atomically by agents
# Read by all agents to check dependencies
```

### 3. Agent CLI Commands
```bash
# Check what I can work on
orbit-agent available-tasks 001 --agent claude

# Start task (marks in progress)
orbit-agent start T031

# Complete task (marks done, even before PR merge)
orbit-agent complete T031 --pr 123

# Check layer status
orbit-agent layer-status 001
```

### 4. /supervisor:mid Integration
```bash
# Supervisor reads .progress.json
/supervisor:mid 001

# Reports:
Layer 1: 6/8 complete (75%) - @claude finishing T032
Layer 2: 0/11 started - Blocked on T034, T037
Stuck tasks: T037 (no activity for 2 hours)
```

---

## Implementation Checklist

To make layering work, we need:

- [ ] **Create .progress.json schema** - Define structure
- [ ] **Create orbit-agent CLI** - Commands for task coordination
  - [ ] `available-tasks` - List tasks I can start
  - [ ] `start` - Mark task in progress
  - [ ] `complete` - Mark task done
  - [ ] `layer-status` - Show progress per layer
- [ ] **Update /iterate:tasks** - Generate both layered-tasks.md AND .progress.json
- [ ] **Update /supervisor:mid** - Read .progress.json for monitoring
- [ ] **Update agent CLAUDE.md** - Teach agents to use orbit-agent commands
- [ ] **Add locking** - Prevent race conditions on .progress.json updates
- [ ] **Test coordination** - Run 3 agents in parallel, verify no conflicts

---

## Decision Needed

**Which solution do we implement?**

**Recommendation**: **Hybrid (A + C)**
- Shared progress file for coordination
- Soft layers (organizational) with hard dependencies
- Agents work on any task where dependencies complete
- No blocking on PR merges

**Why**:
- Balances structure (layers) with flexibility (dependencies)
- Maximum parallelism
- Real-time visibility
- Resilient to individual task delays

**Alternative**: If we want strict waterfall, use **Option B** (Layer Branches)

---

## Questions for User

1. **Should layers be hard blocks** (can't start Layer 2 until ALL Layer 1 done)?
   - OR soft guidelines (start Layer 2 tasks when dependencies met)?

2. **When should tasks be marked complete**?
   - Immediately after work done (before PR merge)?
   - OR only after PR merged to main?

3. **How do we handle race conditions** on shared .progress.json?
   - File locking?
   - Atomic commits with retry?
   - Database (overkill)?

4. **Should we create orbit-agent CLI** or reuse existing tools?
   - New CLI for task coordination?
   - OR extend /supervisor commands?

---

## Impact on Existing Work

**TASK_LAYERING_PRINCIPLES.md** needs update:
- Add section on "Layer Coordination"
- Explain soft vs hard layers
- Document .progress.json structure
- Show agent workflow with orbit-agent commands

**WORKTREE_BRANCHING_ARCHITECTURE.md** needs update:
- Explain how agents check dependencies
- Show .progress.json usage
- Update agent workflow examples

**Agent CLAUDE.md templates** need update:
- Add orbit-agent command usage
- Teach agents to check dependencies before starting
- Teach agents to mark progress

---

## Next Steps (Tomorrow)

1. **Decide on solution** (Hybrid A+C recommended)
2. **Design .progress.json schema**
3. **Create orbit-agent CLI spec**
4. **Update /iterate:tasks to generate .progress.json**
5. **Test with Orbit spec** (small 30-task version)
6. **Validate 3 agents can work in parallel without conflicts**
