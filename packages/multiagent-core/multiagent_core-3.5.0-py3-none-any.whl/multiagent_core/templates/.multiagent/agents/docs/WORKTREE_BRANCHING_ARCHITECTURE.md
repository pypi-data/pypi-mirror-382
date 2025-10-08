# Git Worktree Branching Architecture

> **How MultiAgent enables parallel agent development with isolated worktrees, symlinked task visibility, and safe merge workflows**

## Overview

MultiAgent uses **git worktrees** to enable multiple AI agents to work simultaneously on different features without conflicts. Each agent gets an isolated environment with visibility into shared task progress via symlinks.

## Table of Contents
- [Core Concepts](#core-concepts)
- [Worktree Structure](#worktree-structure)
- [Symlink Strategy](#symlink-strategy)
- [Branching Strategy](#branching-strategy)
- [Setup Automation](#setup-automation)
- [Specify Integration](#specify-integration)
- [Safe Git Operations](#safe-git-operations)
- [Cleanup Workflow](#cleanup-workflow)

---

## Core Concepts

### Git Worktrees Explained

**Traditional Git Workflow:**
```bash
# Switching branches changes files in current directory
git checkout feature-a    # Files change
git checkout feature-b    # Files change again
# Can only work on one branch at a time
```

**Worktree Workflow:**
```bash
# Each worktree is a separate directory
git worktree add ../project-claude agent-claude-feature
# multiagent-core/ stays on main
# project-claude/ is on agent-claude-feature
# Both exist simultaneously!
```

**Key Benefits:**
- ✅ **Parallel Development**: Multiple agents work simultaneously
- ✅ **No Branch Conflicts**: Each agent isolated in own directory
- ✅ **Main Stays Clean**: Original repo never leaves main branch
- ✅ **Fast PR Reviews**: One agent = one worktree = one PR
- ✅ **Easy Rollback**: Delete worktree without affecting main

---

## Worktree Structure

### Directory Layout

```
parent-directory/
├── multiagent-core/              # Main repository (always on main)
│   ├── specs/
│   │   └── 005-doc-system/
│   │       └── agent-tasks/
│   │           └── layered-tasks.md    # SOURCE OF TRUTH
│   ├── .multiagent/
│   └── .claude/
│
├── project-claude/               # @claude's worktree
│   ├── specs/
│   │   └── 005-doc-system/
│   │       ├── layered-tasks.md        # Local copy (agent edits)
│   │       └── layered-tasks-main.md   # Symlink → main's version
│   └── [on branch: agent-claude-005]
│
├── project-qwen/                 # @qwen's worktree
│   ├── specs/
│   │   └── 005-doc-system/
│   │       ├── layered-tasks.md        # Local copy
│   │       └── layered-tasks-main.md   # Symlink → main
│   └── [on branch: agent-qwen-005]
│
└── project-codex/                # @codex's worktree
    ├── specs/
    │   └── 005-doc-system/
    │       ├── layered-tasks.md        # Local copy
    │       └── layered-tasks-main.md   # Symlink → main
    └── [on branch: agent-codex-005]
```

### Branch Naming Convention

```bash
agent-{agent-name}-{spec-number}

# Examples:
agent-claude-005      # @claude working on spec 005
agent-qwen-005        # @qwen working on spec 005
agent-gemini-012      # @gemini working on spec 012
agent-codex-003       # @codex working on spec 003
agent-copilot-007     # @copilot working on spec 007
```

**Why This Format:**
- **Predictable**: Easy to identify agent and spec
- **Unique**: Prevents branch name conflicts
- **Filterable**: Easy to find all branches for a spec
- **PR-Friendly**: Clear attribution in GitHub

---

## Symlink Strategy

### The Problem: Task Visibility

Without symlinks, agents can't see each other's progress:
```
@claude checks off T001 in their worktree
↓
@qwen doesn't see this change
@qwen also starts T001
↓
CONFLICT! Both agents working on same task
```

### The Solution: Symlinked Main Tasks

Each worktree has a **symlink** to main's layered-tasks.md:

```bash
# In worktree: project-claude/specs/005-doc-system/
layered-tasks-main.md → ../../../multiagent-core/specs/005-doc-system/agent-tasks/layered-tasks.md
```

**How It Works:**
1. Agents check `layered-tasks-main.md` (symlink) to see latest progress
2. Agents edit their local `layered-tasks.md` to mark tasks complete
3. When PR merges, local changes update main's file
4. All other agents' symlinks instantly show the update

### Symlink Creation Script

**Location**: `.multiagent/iterate/scripts/setup-worktree-symlinks.sh`

```bash
# Automatically called during worktree setup
./setup-worktree-symlinks.sh 005-documentation-management-system

# Creates symlink
ln -sf $MAIN_REPO/specs/005-.../layered-tasks.md \
       $WORKTREE/specs/005-.../layered-tasks-main.md
```

**Result**:
```bash
# In any worktree
cat layered-tasks-main.md    # See latest from main (real-time)
vim layered-tasks.md          # Edit your local copy
```

### Visibility Flow

```
┌─────────────────────────────────────────────────┐
│ Main Repo: multiagent-core/                    │
│ specs/005-doc-system/agent-tasks/               │
│ ├── layered-tasks.md (SOURCE OF TRUTH)         │
│ ├── T001 [ ] @claude Setup infrastructure      │
│ ├── T002 [ ] @qwen Optimize queries            │
│ └── T003 [ ] @codex Build frontend             │
└─────────────────┬───────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ @claude  │ │ @qwen    │ │ @codex   │
│ worktree │ │ worktree │ │ worktree │
│          │ │          │ │          │
│ tasks.md │ │ tasks.md │ │ tasks.md │ ← Local edits
│ ──────   │ │ ──────   │ │ ──────   │
│ *symlink*│ │ *symlink*│ │ *symlink*│ ← Real-time view
│ to main  │ │ to main  │ │ to main  │
└──────────┘ └──────────┘ └──────────┘
```

---

## Branching Strategy

### Workflow Phases

**Phase 1: Setup** (From main repo)
```bash
cd /home/user/Projects/multiagent-core
git branch --show-current  # Verify: main

# Create worktrees (automated by setup-spec-worktrees.sh)
git worktree add -b agent-claude-005 ../project-claude main
git worktree add -b agent-qwen-005 ../project-qwen main
git worktree add -b agent-codex-005 ../project-codex main
```

**Phase 2: Development** (In agent worktree)
```bash
cd ../project-claude
git branch --show-current  # Shows: agent-claude-005

# Configure safety (prevent rebases)
git config --local pull.rebase false
git config --local pull.ff only

# Check task visibility
cat specs/005-doc-system/layered-tasks-main.md  # See all agents' progress

# Work on tasks
vim src/feature.py
git commit -m "[WORKING] feat: Implement feature @claude"

# Sync with main (safe merge, NO rebase)
git fetch origin main && git merge origin/main
```

**Phase 3: PR Creation** (Ready for review)
```bash
# Final commit with @claude (triggers review)
git commit -m "[COMPLETE] feat: Feature complete @claude

All assigned tasks implemented and tested."

# Push and create PR
git push origin agent-claude-005
gh pr create --title "feat: Documentation system from @claude" \
             --body "Summary of changes..."
```

**Phase 4: Cleanup** (After PR merge)
```bash
# MANDATORY: Return to main repo
cd /home/user/Projects/multiagent-core

# Update main
git checkout main && git pull origin main

# Remove worktree
git worktree remove ../project-claude

# Delete branches
git push origin --delete agent-claude-005  # Remote
git branch -d agent-claude-005              # Local
```

### Parallel Development Flow

```
Main Repo (main branch - never changes)
    │
    ├─────────────────────────────────────┐
    │                                     │
    ▼                                     ▼
Worktree: @claude                    Worktree: @qwen
Branch: agent-claude-005             Branch: agent-qwen-005
│                                    │
├─ Commit: [WORKING] feat: Setup    ├─ Commit: [WORKING] perf: Optimize
├─ Commit: [WORKING] feat: Tests    ├─ Commit: [WORKING] perf: Cache
├─ Commit: [COMPLETE] @claude       ├─ Commit: [COMPLETE] @qwen
│                                    │
└─> PR #42 → Merge                  └─> PR #43 → Merge
         │                                   │
         └───────────┬───────────────────────┘
                     ▼
             Main Repo Updated
         (Both agents' work merged)
```

---

## Setup Automation

### Automated Worktree Creation

**Script**: `.multiagent/iterate/scripts/setup-spec-worktrees.sh`

**What It Does:**
1. Reads `layered-tasks.md`
2. Detects which agents have tasks (`@claude`, `@qwen`, etc.)
3. Creates worktrees ONLY for agents with work
4. Sets up symlinks automatically
5. Reports setup status

**Usage:**
```bash
# After running /iterate:tasks 005
./multiagent/iterate/scripts/setup-spec-worktrees.sh 005-documentation-management-system

# Output:
📋 Analyzing layered-tasks.md to detect agents with work...
   ✓ @claude has 12 tasks
   ✓ @qwen has 8 tasks
   ○ @gemini has no tasks (skipping worktree)

📁 Creating worktrees for 2 agents with tasks...
   @claude → /home/user/Projects/project-claude [agent-claude-005]
   @qwen → /home/user/Projects/project-qwen [agent-qwen-005]

🔗 Setting up task visibility symlinks...
   ✅ @claude: symlink created
   ✅ @qwen: symlink created

✅ Worktree Setup Complete
```

### Safety Features

**1. Branch Validation**
```bash
# Script verifies you're on main before creating worktrees
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "ERROR: Must be on main branch"
    exit 1
fi
```

**2. Path Traversal Protection**
```bash
# Prevents malicious spec names
if [[ "$SPEC_NAME" =~ \.\. ]] || [[ "$SPEC_NAME" =~ / ]]; then
    echo "ERROR: Invalid spec name (security violation)"
    exit 1
fi
```

**3. Git Config Safety**
```bash
# Prevents destructive rebases
git config --local pull.rebase false
git config --local pull.ff only
```

---

## Specify Integration

### How Worktrees Enhance Specify

```
Specify Workflow          →  Worktree Enhancement
─────────────────────        ──────────────────────────
/specify → spec.md       →  /iterate:tasks → layered-tasks.md
                         →  setup-spec-worktrees.sh
                         →  Each agent gets isolated environment

/plan → plan.md          →  Agents read plan in their worktrees
                         →  Work proceeds in parallel

/tasks → tasks.md        →  Layered tasks distributed across agents
                         →  Symlinks provide progress visibility
```

### Task Distribution Example

**After Specify creates tasks.md:**
```markdown
- [ ] T001 Setup API endpoints
- [ ] T002 Create database schema
- [ ] T003 Build frontend components
- [ ] T004 Write integration tests
- [ ] T005 Optimize performance
```

**After /iterate:tasks layers them:**
```markdown
## Layer 1: Foundation (@claude @qwen)
- [ ] T001 @claude Setup API endpoints
- [ ] T002 @claude Create database schema

## Layer 2: Implementation (@codex)
- [ ] T003 @codex Build frontend components

## Layer 3: Testing (@claude)
- [ ] T004 @claude Write integration tests

## Layer 4: Optimization (@qwen)
- [ ] T005 @qwen Optimize performance
```

**Worktree Setup:**
```bash
# Automatically creates:
../project-claude  # Has T001, T002, T004
../project-codex   # Has T003
../project-qwen    # Has T002, T005
```

---

## Safe Git Operations

### ❌ NEVER Use Rebases

**Why Rebases Are Dangerous:**
- Rewrites commit history
- Can destroy completed work
- Resets task checkboxes in layered-tasks.md
- Causes conflicts between agents

**Wrong:**
```bash
git pull origin main --rebase        # ❌ Destroys work
git rebase origin/main               # ❌ Resets tasks.md
git pull --rebase                    # ❌ Dangerous
```

### ✅ ALWAYS Use Merge

**Correct:**
```bash
# Safe sync pattern
git fetch origin main && git merge origin/main

# Why it's safe:
# 1. fetch downloads changes
# 2. merge preserves both histories
# 3. task completions stay intact
# 4. conflicts are transparent
```

### Git Config Protection

**Required in every worktree:**
```bash
git config --local pull.rebase false  # Disable rebase
git config --local pull.ff only       # Only fast-forward merges
```

**What This Does:**
- `pull.rebase false`: Uses merge instead of rebase
- `pull.ff only`: Fails if merge would create commits (forces manual review)

---

## Cleanup Workflow

### Why Cleanup Matters

Worktrees persist on disk even after PR merge:
- Takes up disk space
- Clutters `git worktree list`
- Old branches confuse future work

### Mandatory Cleanup Steps

**After Your PR Merges:**
```bash
# 1. Go to MAIN repo (not your worktree!)
cd /home/user/Projects/multiagent-core

# 2. Ensure you're on main
git checkout main

# 3. Update main with merged changes
git pull origin main

# 4. Remove your worktree
git worktree remove ../project-claude

# 5. Delete local branch
git branch -d agent-claude-005

# 6. Delete remote branch (if not auto-deleted)
git push origin --delete agent-claude-005
```

### Cleanup Verification

```bash
# Check all worktrees
git worktree list

# Should only show main repo:
/home/user/Projects/multiagent-core  abcdef1 [main]

# If stale worktrees exist:
git worktree prune
```

### Common Cleanup Issues

**Issue: "worktree has uncommitted changes"**
```bash
# Solution: Commit or stash first
cd ../project-claude
git commit -am "WIP: Final changes"
# OR
git stash save "WIP"

# Then remove worktree
cd ../multiagent-core
git worktree remove ../project-claude
```

**Issue: "Cannot remove worktree"**
```bash
# Solution: Force removal
git worktree remove --force ../project-claude
git worktree prune
```

---

## Best Practices

### 1. One Worktree = One Feature

```
✅ GOOD:
agent-claude-005 → Work on spec 005 documentation system
agent-claude-007 → Work on spec 007 authentication

❌ BAD:
agent-claude-mixed → Work on specs 005 + 007 simultaneously
```

### 2. Check Symlink Before Starting

```bash
# Always verify task visibility
cd ../project-claude
cat specs/005-doc-system/layered-tasks-main.md

# If symlink broken:
./.multiagent/iterate/scripts/setup-worktree-symlinks.sh 005-documentation-management-system
```

### 3. Sync Frequently

```bash
# Sync at start of each work session
git fetch origin main && git merge origin/main

# Sync before final commit
git fetch origin main && git merge origin/main
git commit -m "[COMPLETE] feat: Work complete @claude"
```

### 4. Clean Up Immediately

```bash
# As soon as PR merges:
cd /path/to/multiagent-core
git worktree remove ../project-claude
git branch -d agent-claude-005

# Don't wait - prevents future conflicts
```

---

## Integration with Commands

### Commands That Use Worktrees

**Analysis Commands** (Read-only, worktree-safe):
```bash
/specify:analyze specs/005    # Reads files in worktree
/docs:validate                # Validates docs in worktree
/review:code src/             # Reviews code in worktree
```

**Output Commands** (Create files in worktree):
```bash
/docs:init                         # Creates docs in worktree
/deployment:deploy-prepare 005     # Outputs to worktree
/testing:test-generate 005         # Generates tests in worktree
```

**Orchestration Commands** (Coordinate across main):
```bash
/iterate:tasks 005            # Runs in main, creates layered-tasks.md
/iterate:sync 005             # Syncs all spec files
/core:project-setup 001       # Initial setup (main only)
```

---

## Troubleshooting Guide

### "Symlink not found"

```bash
# Recreate symlink
cd /path/to/worktree
./.multiagent/iterate/scripts/setup-worktree-symlinks.sh 005-doc-system
```

### "Branch already exists"

```bash
# Delete old branch first
git branch -D agent-claude-005
git worktree add -b agent-claude-005 ../project-claude main
```

### "Merge conflicts"

```bash
# Resolve manually
git fetch origin main
git merge origin/main
# Fix conflicts in editor
git add .
git commit -m "resolve: Merge conflicts with main"
```

### "Lost track of worktrees"

```bash
# List all worktrees
git worktree list

# Prune stale references
git worktree prune
```

---

## Summary

### Key Takeaways

✅ **Worktrees enable parallel agent development**
✅ **Symlinks provide real-time task visibility**
✅ **Safe merge-only strategy prevents data loss**
✅ **Automated setup reduces manual errors**
✅ **Proper cleanup keeps repository clean**

### Quick Command Reference

```bash
# Create worktree
git worktree add -b agent-name-005 ../project-name main

# Configure safety
git config --local pull.rebase false
git config --local pull.ff only

# Sync safely
git fetch origin main && git merge origin/main

# Check tasks
cat specs/005-.../layered-tasks-main.md

# Commit work
git commit -m "[WORKING] feat: Description @agent"

# Final commit
git commit -m "[COMPLETE] feat: Complete @claude"

# Clean up
cd /path/to/main
git worktree remove ../project-name
git branch -d agent-name-005
```

---

## Related Documentation

- [Git Worktree Guide](./GIT_WORKTREE_GUIDE.md)
- [Agent Branch Protocol](./AGENT_BRANCH_PROTOCOL.md)
- [Slash Command Patterns](./SLASH_COMMAND_DESIGN_PATTERN.md)
- [Task Layering](../../.multiagent/iterate/README.md)

---

**Last Updated:** 2025-10-03
**Version:** 3.2.0+
**Status:** Production
