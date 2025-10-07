# Agent Branch Protocol - Worktree Isolation

## 🚨 CRITICAL: Worktree-Based Agent Isolation

### The Problem (OLD WAY)
Multiple agents working on the same branch creates:
- Massive, unreviewable PRs (22,700+ lines)
- Mixed agent work that's impossible to track
- Merge conflicts and attribution problems
- Coordination chaos

### The Solution: Isolated Agent Worktrees

Each agent works in their own **completely isolated worktree** with their own branch.

## Worktree Creation Rules

### 1. Each Agent Creates Their Own Worktree
```bash
# From main project directory, each agent creates isolation:

# @claude - Architecture and integration
git worktree add -b agent-claude-architecture ../project-claude main

# @qwen - Performance optimization  
git worktree add -b agent-qwen-optimization ../project-qwen main

# @gemini - Documentation and research
git worktree add -b agent-gemini-documentation ../project-gemini main

# @codex - Frontend development
git worktree add -b agent-codex-frontend ../project-codex main

# @copilot - Backend implementation
git worktree add -b agent-copilot-backend ../project-copilot main
```

### 2. Directory Isolation Structure
```
parent-directory/
├── multiagent-core/             # Original repo (main branch)
│   ├── specs/                   # Task specifications
│   └── .multiagent/             # Agent templates
├── project-claude/              # Claude's isolated workspace
├── project-qwen/                # Qwen's isolated workspace  
├── project-gemini/              # Gemini's isolated workspace
├── project-codex/               # Codex's isolated workspace
└── project-copilot/             # Copilot's isolated workspace
```

### 3. Branch Naming Convention
```
agent-[name]-[specialization]
```

Examples:
- `agent-claude-architecture`
- `agent-qwen-optimization`
- `agent-gemini-documentation`
- `agent-codex-frontend`
- `agent-copilot-backend`

## Safe Git Configuration

### MANDATORY Git Safety Settings
```bash
# EVERY agent MUST configure this in their worktree:
cd ../project-[agent]
git config --local pull.rebase false  # Prevents destructive rebases
git config --local pull.ff only       # Only allows safe fast-forwards
```

### Safe Sync Operations
```bash
# CORRECT: Safe sync with main
git fetch origin main && git merge origin/main

# WRONG: Dangerous rebase operations
git rebase origin/main              # ❌ Can destroy work
git pull origin main --rebase      # ❌ Can reset tasks.md
```

## 6-Phase Worktree Workflow

### Phase 1: Setup & Context Reading (Steps 1-8)
1. **Read agent MD file** - Understand your role
2. **Configure git safety** - Set rebase=false, pull.ff=only
3. **Verify location** - Should be on main branch
4. **Find assignments** - `grep "@[agent]" specs/*/tasks.md`

### Phase 2: Worktree Setup (Steps 9-13)
5. **Create worktree** - `git worktree add -b agent-[name]-feature ../project-[name] main`
6. **Navigate** - `cd ../project-[name]`
7. **Verify isolation** - `git branch --show-current`
8. **Sync with main** - `git fetch origin main && git merge origin/main`

### Phase 3: Task Planning (Steps 14-19)
9. **Use TodoWrite** - Track tasks internally
10. **Plan implementation** - Review structure and dependencies

### Phase 4: Implementation (Steps 20-26)
11. **Work commits** - `[WORKING] feat: Description @[agent]`
12. **Dual tracking** - TodoWrite + tasks.md checkboxes
13. **NO @claude during work** - Only in final commit

### Phase 5: PR Creation (Steps 27-31)
14. **Final commit** - `[COMPLETE] feat: Work done @claude`
15. **Push and create PR** - One agent = One PR

### Phase 6: Cleanup (Steps 32-33)
16. **Mandatory cleanup** - Remove worktree after merge
17. **Verify cleanup** - `git worktree list` should not show your worktree

## Pull Request Protocol

### One Agent = One PR Rule
- **Each agent creates exactly ONE PR**
- **Max 1,000 lines per PR** (split if larger)
- **Clear agent attribution in title**

### PR Title Format
```
feat: [Agent] Brief description of changes
```

Examples:
```
feat: [claude] Architecture and security implementation
feat: [qwen] Database query optimization and caching
feat: [gemini] API documentation and usage examples
feat: [codex] Responsive dashboard components
feat: [copilot] User authentication backend
```

### PR Body Template
```markdown
## Summary
Brief description of what was implemented.

## Agent Worktree Details
- **Agent**: @[agent]
- **Branch**: agent-[name]-feature
- **Worktree**: ../project-[name]

## Tasks Completed
- [x] T001 @agent Feature implementation ✅
- [x] T002 @agent Testing complete ✅
- [x] T003 @agent Documentation updated ✅

## TodoWrite Status
All internal tasks marked as completed.

## Testing
- [x] Local smoke tests pass
- [x] No merge conflicts with main
- [x] Agent-specific tests pass

## Integration Points
List any dependencies or integration requirements.

@[agent] work complete - ready for review
```

## Merge Strategy & Order

### Recommended Merge Order
1. **@claude** - Architecture and integration (foundation)
2. **@copilot** - Backend implementation (core functionality)
3. **@qwen** - Performance optimization (efficiency layer)
4. **@codex** - Frontend implementation (user interface)
5. **@gemini** - Documentation (final polish)

### Integration Dependencies
- Later agents must sync with earlier merged work
- Use `git fetch origin main && git merge origin/main` to integrate
- Resolve conflicts by understanding both implementations

## Task Coordination

### Dual Tracking System
**Internal Tracking (TodoWrite)**:
```json
{
  "content": "Implement user authentication (T015)",
  "status": "completed",
  "activeForm": "Implementing user authentication"
}
```

**External Tracking (tasks.md)**:
```markdown
- [x] T015 @copilot Implement user authentication ✅
```

### Task Dependency Management
```markdown
# Example dependency chain:
- [x] T010 @claude Design authentication architecture ✅
- [ ] T015 @copilot Implement auth backend (depends on T010)
- [ ] T020 @codex Create auth UI components (depends on T015)
- [ ] T025 @qwen Optimize auth queries (depends on T015)
- [ ] T030 @gemini Document auth API (depends on T015)
```

## Prevention Checklist

### Before Starting Work
- [ ] In main project directory
- [ ] Git safety configured (rebase=false)
- [ ] Created your own worktree
- [ ] Navigated to your worktree directory
- [ ] Verified you're on YOUR agent branch

### Before Each Commit
- [ ] Confirm you're in your worktree directory
- [ ] Check you're on YOUR agent branch
- [ ] Verify only YOUR work is included
- [ ] Use proper commit format

### Before Creating PR
- [ ] All TodoWrite tasks completed
- [ ] All tasks.md checkboxes checked
- [ ] Final @claude commit made
- [ ] PR size < 1,000 lines
- [ ] Only your agent's work included

### After PR Merge
- [ ] Returned to main project directory
- [ ] Updated main branch
- [ ] Removed your worktree
- [ ] Deleted your local branch
- [ ] Verified cleanup with `git worktree list`

## Common Issues and Solutions

### Issue: "Multiple agents on same branch"
**Solution**: Each agent creates their own worktree
```bash
# WRONG: Multiple agents sharing branch
git checkout shared-feature-branch  # ❌

# CORRECT: Each agent in own worktree
git worktree add -b agent-claude-feature ../project-claude main  # ✅
```

### Issue: "Massive PRs with mixed work"
**Solution**: One agent = One worktree = One PR
```bash
# Each agent's PR should be manageable size
# If too large, split into multiple features
```

### Issue: "Can't track who did what"
**Solution**: Clear agent attribution
```bash
# Commit format shows agent clearly
git commit -m "[WORKING] feat: Add auth @copilot"

# PR title shows agent clearly
"feat: [copilot] User authentication backend"
```

### Issue: "Merge conflicts everywhere"
**Solution**: Sync regularly with main
```bash
# Daily sync in your worktree
git fetch origin main && git merge origin/main
```

## Monitoring & Enforcement

### Git Hooks (pre-commit)
```bash
#!/bin/bash
# Check if agent is in correct worktree
CURRENT_DIR=$(pwd)
AGENT_NAME=$(git branch --show-current | cut -d'-' -f2)

if [[ ! "$CURRENT_DIR" =~ project-$AGENT_NAME ]]; then
    echo "ERROR: Agent $AGENT_NAME should work in project-$AGENT_NAME directory"
    echo "Current directory: $CURRENT_DIR"
    exit 1
fi
```

### Branch Protection
- Main branch requires PR review
- No direct pushes to main
- Status checks must pass
- Branch must be up to date

## Workflow Benefits

1. **Complete Isolation**: No interference between agents
2. **Clean Attribution**: Clear responsibility for each change
3. **Manageable PRs**: One agent = one focused PR
4. **Parallel Development**: All agents work simultaneously
5. **Safe Operations**: No destructive rebases or conflicts
6. **Easy Rollback**: Individual agent work can be reverted
7. **Clear History**: Git log shows agent contributions clearly

## Emergency Recovery

### If Agents Mixed on Same Branch
```bash
# 1. Each agent creates new clean worktree
git worktree add -b agent-[name]-recovery ../project-[name]-clean main

# 2. Cherry-pick only their commits
cd ../project-[name]-clean
git cherry-pick <their-commit-hash>
git cherry-pick <another-their-commit>

# 3. Create new PR from clean worktree
git push origin agent-[name]-recovery
gh pr create --title "feat: [agent] Cleaned work"

# 4. Close the messy mixed PR
gh pr close <mixed-pr-number>
```

## Quick Reference

```bash
# Setup worktree isolation
git worktree add -b agent-[name]-feature ../project-[name] main
cd ../project-[name]
git config --local pull.rebase false
git config --local pull.ff only

# Daily sync (safe)
git fetch origin main && git merge origin/main

# Work commits
git commit -m "[WORKING] feat: Description @[agent]"

# Final commit
git commit -m "[COMPLETE] feat: Work done @claude"

# Create PR
gh pr create --title "feat: [agent] Description"

# Cleanup after merge
cd /path/to/main/project
git worktree remove ../project-[name]
git branch -d agent-[name]-feature
```

## Golden Rules

1. **Each agent = isolated worktree**
2. **One agent = one PR** 
3. **Merge, never rebase**
4. **@claude in final commit only**
5. **Clean up after merge**
6. **TodoWrite + tasks.md tracking**
7. **Safe git configuration always**

**Remember**: Isolation prevents chaos, coordination enables success!