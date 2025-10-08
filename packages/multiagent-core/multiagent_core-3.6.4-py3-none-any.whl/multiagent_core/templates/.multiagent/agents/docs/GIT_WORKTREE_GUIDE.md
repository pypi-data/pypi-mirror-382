# Git Worktree Management Guide

## 🚨 CRITICAL SAFETY RULES

### ❌ NEVER USE REBASES
- **Rebases can destroy completed work and reset tasks.md**
- **ALWAYS use `git merge` instead of rebase**
- **Required git config prevents rebases:**

```bash
# MANDATORY configuration for all agents
git config --local pull.rebase false
git config --local pull.ff only
```

### ✅ SAFE Git Operations
```bash
# CORRECT: Sync with main safely
git fetch origin main && git merge origin/main

# WRONG: Dangerous rebase operations
git rebase origin/main              # ❌ Can destroy work
git pull origin main --rebase      # ❌ Can reset tasks.md
```

## 6-Phase Worktree Workflow

### Phase 1: Setup & Context Reading
1. **Read your specific agent MD file** - Understand your role and specializations
2. **Configure safe git behavior** - Prevent destructive operations:
   ```bash
   git config --local pull.rebase false
   git config --local pull.ff only
   ```

### Phase 2: Worktree Setup & Environment Preparation
3. **Verify current location** - `git branch --show-current` (should be main)
4. **Create agent worktree** - Isolate your work environment:
   ```bash
   # Each agent creates their own isolated worktree
   git worktree add -b agent-claude-feature ../project-claude main
   git worktree add -b agent-qwen-optimize ../project-qwen main
   git worktree add -b agent-gemini-docs ../project-gemini main
   git worktree add -b agent-codex-frontend ../project-codex main
   git worktree add -b agent-copilot-backend ../project-copilot main
   ```
5. **Navigate to worktree** - `cd ../project-[agent]`
6. **Verify isolation** - `git branch --show-current` (should show your agent branch)
7. **Set up task visibility symlink** - Link to main's layered-tasks.md:
   ```bash
   cd specs/[spec-number]-[spec-name]/agent-tasks
   ./setup-worktree-symlinks.sh
   # Creates: specs/[spec]/layered-tasks-main.md -> main repo's layered-tasks.md
   ```
8. **Sync with main** - `git fetch origin main && git merge origin/main`

## Directory Structure After Setup

```
parent-directory/
├── multiagent-core/             # Original repository (main branch)
├── project-claude/              # Claude's worktree (agent-claude-feature)
├── project-qwen/                # Qwen's worktree (agent-qwen-optimize)
├── project-gemini/              # Gemini's worktree (agent-gemini-docs)
├── project-codex/               # Codex's worktree (agent-codex-frontend)
└── project-copilot/             # Copilot's worktree (agent-copilot-backend)
```

## Phase 3: Task Discovery & Planning

8. **Find your tasks** - `grep "@[agent]" specs/*/tasks.md`
9. **Use TodoWrite tool** - Track tasks internally:
   ```json
   [
     {"content": "Implement feature X (T001)", "status": "pending", "activeForm": "Implementing feature X"},
     {"content": "Add tests for X (T002)", "status": "pending", "activeForm": "Adding tests for X"}
   ]
   ```
10. **Plan implementation** - Review existing structure and dependencies

## Phase 4: Implementation & Development Work

11. **Start tasks** - Mark `in_progress` in TodoWrite, then implement
12. **Make regular commits** - **NO @claude during work**:
    ```bash
    git commit -m "[WORKING] feat: Implement feature
    
    @[agent] working in isolated worktree"
    ```
13. **Complete dual tracking** - Update TodoWrite AND tasks.md:
    - **Internal**: `{"status": "completed"}`
    - **External**: `- [x] T001 @agent Feature complete ✅`

## Phase 5: PR Creation & Review Integration

14. **Final commit with @claude** - Triggers review integration:
    ```bash
    git commit -m "[COMPLETE] feat: Implementation complete @claude
    
    All tasks completed and ready for automated review."
    ```
15. **Push and create PR**:
    ```bash
    git push origin agent-[name]-feature
    gh pr create --title "feat: Updates from @[agent]" --body "Summary of changes"
    ```

## Phase 6: Post-Merge Cleanup - MANDATORY

16. **After PR merge** - Clean up immediately:
    ```bash
    # Go to main project directory (not your worktree!)
    cd /home/vanman2025/Projects/multiagent-core
    
    # Update main branch
    git checkout main && git pull origin main
    
    # Remove your worktree (MANDATORY!)
    git worktree remove ../project-[agent]
    
    # Delete local branch
    git branch -d agent-[agent]-feature
    ```

## Daily Sync Pattern

```bash
# From your agent worktree directory
cd ../project-[agent]

# Configure safety (run once per worktree)
git config --local pull.rebase false
git config --local pull.ff only

# Sync with main safely (NO REBASE)
git fetch origin main && git merge origin/main

# Continue work...
```

## Worktree Management Commands

```bash
# List all worktrees
git worktree list

# Remove worktree safely
git worktree remove ../project-[agent]

# Prune stale references
git worktree prune

# Check worktree status
git status --porcelain
```

## Branch Naming Convention

- **Agent worktrees**: `agent-[name]-[feature]`
- **Examples**:
  - `agent-claude-architecture`
  - `agent-qwen-optimization`  
  - `agent-gemini-documentation`
  - `agent-codex-frontend`
  - `agent-copilot-backend`

## Pull Request Best Practices

### PR Title Format
```
feat: [Agent] Description of changes
```

### PR Body Template
```markdown
## Summary
- Brief description of changes
- Key features implemented

## Agent Worktree
- Branch: agent-[name]-feature
- Worktree: ../project-[agent]

## Tasks Completed
- [x] T001 @agent Feature implementation ✅
- [x] T002 @agent Testing complete ✅

## Testing
- [x] Local smoke tests pass
- [x] No merge conflicts with main
- [x] All TodoWrite tasks completed

@[agent] work complete - ready for review
```

## Common Issues and Solutions

### Issue: "Branch already exists"
```bash
# Solution: Remove existing branch first
git branch -D agent-name-feature
git worktree add -b agent-name-feature ../project-name main
```

### Issue: "Worktree has uncommitted changes"
```bash
# Solution: Commit or stash changes first
cd ../project-name
git stash save "WIP: Saving work"
# OR
git commit -am "WIP: Temporary commit"
```

### Issue: "Can't remove worktree"  
```bash
# Solution: Force removal if needed
git worktree remove --force ../project-name
git worktree prune
```

### Issue: Merge conflicts during sync
```bash
# Solution: Resolve conflicts manually
git fetch origin main
git merge origin/main
# Resolve conflicts in editor
git add .
git commit -m "resolve: Merge conflicts with main"
```

## Integration with Agent Templates

### TodoWrite Tool Integration
Each agent uses TodoWrite for internal task tracking:
```bash
# Mark task in progress
TodoWrite: {"content": "Fix bug X", "status": "in_progress", "activeForm": "Fixing bug X"}

# Mark task complete
TodoWrite: {"content": "Fix bug X", "status": "completed", "activeForm": "Fixed bug X"}
```

### Dual Task Tracking
- **Internal**: TodoWrite tool for session management
- **External**: tasks.md checkboxes for team coordination
- **Both required**: Internal tracking AND external visibility

## Automated Testing Integration

### GitHub Actions Workflow
```yaml
name: Agent Worktree Tests
on:
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize ]

jobs:
  test-agent-work:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Identify Agent
        run: |
          if [[ "${{ github.head_ref }}" == agent-* ]]; then
            echo "Agent: ${{ github.head_ref }}"
          fi
      - name: Run Tests
        run: npm test
```

## Workflow Benefits

1. **Parallel Development**: Each agent works independently
2. **Conflict Prevention**: Isolated worktrees prevent interference  
3. **Clean PRs**: One agent = one PR = manageable review
4. **Safe Operations**: No destructive rebases or branch switching
5. **Clear Attribution**: Easy to track which agent made what changes
6. **Automated Testing**: CI/CD runs on each agent's work
7. **Easy Rollback**: Individual PRs can be reverted safely

## Quick Reference Commands

```bash
# Create worktree (safe - doesn't affect current directory)
git worktree add -b agent-name-feature ../project-name main

# Navigate to your worktree
cd ../project-name

# Configure safety
git config --local pull.rebase false
git config --local pull.ff only

# Sync safely (no rebase!)
git fetch origin main && git merge origin/main

# Work commits (no @claude)
git commit -m "[WORKING] feat: Description @agent"

# Final commit (with @claude for review)
git commit -m "[COMPLETE] feat: Work done @claude"

# Create PR
gh pr create --title "feat: Description" --body "Summary"

# Clean up after merge
cd /path/to/main/project
git worktree remove ../project-name
git branch -d agent-name-feature
```

## Remember: Worktrees + Safe Git = Parallel Success!

- ✅ **Each agent = isolated worktree**
- ✅ **Merge instead of rebase**
- ✅ **@claude integration for review**
- ✅ **TodoWrite for task tracking**
- ✅ **Clean up after merge**

---

## Related Documentation

For detailed architecture and design:
- [Worktree Branching Architecture](./WORKTREE_BRANCHING_ARCHITECTURE.md) - Comprehensive worktree design
- [Git Hooks System](./GIT_HOOKS_SYSTEM.md) - Hook architecture and integration
- [Agent Branch Protocol](./AGENT_BRANCH_PROTOCOL.md) - Branch naming and workflow
- [Agent Coordination Guide](./AGENT_COORDINATION_GUIDE.md) - Multi-agent coordination