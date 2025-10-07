# Agent Coordination Guide

## 🎯 Purpose

This guide explains how multiple agents coordinate work in parallel using isolated worktrees while maintaining team visibility and managing dependencies.

## 🔄 Dual Tracking System

### Internal Tracking: TodoWrite Tool
Each agent tracks their session work internally using the TodoWrite tool:

```json
{
  "content": "Implement user authentication (T015)",
  "status": "in_progress",
  "activeForm": "Implementing user authentication"
}
```

**Benefits:**
- Real-time progress within agent session
- Detailed task breakdown
- Session-specific organization
- No external conflicts

### External Tracking: tasks.md + Checkboxes
Team coordination through shared task visibility:

```markdown
- [x] T015 @copilot Implement user authentication ✅
```

**Benefits:**
- Team-wide visibility
- Dependency tracking
- Historical record
- Integration with automation

## 🏗️ Agent Specialization Strategy

### Role-Based Assignment
- **@claude**: Architecture, integration, security, strategic decisions (CTO-level)
- **@qwen**: Performance optimization, algorithms, database efficiency
- **@gemini**: Documentation, research, analysis (simple tasks only)
- **@codex**: Frontend development, UI/UX, React components
- **@copilot**: Backend implementation, API development, database operations

### Task Dependencies
```markdown
# Typical dependency flow:
- [x] T001 @claude Design authentication architecture ✅
    ↓ (architecture complete - implementation can start)
- [ ] T002 @copilot Implement auth backend (depends on T001)
- [ ] T003 @qwen Optimize auth queries (depends on T002)
- [ ] T004 @codex Create auth UI (depends on T002)
- [ ] T005 @gemini Document auth API (depends on T002)
```

## 📋 Coordination Workflow

### Phase 1: Setup & Assignment Discovery
All agents simultaneously:

```bash
# Each agent finds their assignments
grep "@claude" specs/*/tasks.md
grep "@qwen" specs/*/tasks.md
grep "@gemini" specs/*/tasks.md
grep "@codex" specs/*/tasks.md
grep "@copilot" specs/*/tasks.md
```

### Phase 2: Task Planning
Each agent in their worktree:

```bash
cd ../project-[agent]

# Set up TodoWrite tracking
TodoWrite: [
  {"content": "Feature X (T001)", "status": "pending", "activeForm": "Implementing feature X"},
  {"content": "Tests for X (T002)", "status": "pending", "activeForm": "Adding tests for X"}
]

# Review dependencies
grep -B5 -A5 "T001" specs/tasks.md
```

### Phase 3: Parallel Implementation
All agents work simultaneously in isolation:

```bash
# Each agent makes regular commits in their worktree
git commit -m "[WORKING] feat: Implement feature @[agent]"

# Update internal tracking
TodoWrite: {"content": "Task X", "status": "completed"}

# NO interference between agents
# NO shared branches or conflicts
```

### Phase 4: Sequential PR Integration
**Recommended merge order for dependencies:**

1. **@claude** - Architecture foundation first
2. **@copilot** - Core backend implementation
3. **@qwen** - Performance optimizations
4. **@codex** - Frontend implementation
5. **@gemini** - Documentation polish

### Phase 5: Post-Merge Synchronization
After PR merge, dependent agents sync:

```bash
# After @copilot's PR merges, dependent agents update
cd ../project-qwen
git fetch origin main && git merge origin/main  # Gets backend changes

cd ../project-codex
git fetch origin main && git merge origin/main  # Gets backend changes

# Both can now work on their dependent tasks
```

## 🔗 Communication Channels

### 1. tasks.md Files
- **Purpose**: Task assignment and dependency tracking
- **Update**: Via PR merge (external visibility)
- **Format**: `- [x] T001 @agent Description ✅`

### 2. TodoWrite Tool
- **Purpose**: Internal session tracking
- **Update**: Real-time during work
- **Format**: `{"content": "Task X", "status": "completed"}`

### 3. PR Descriptions
- **Purpose**: Document integration points and dependencies
- **Update**: During PR creation
- **Format**: Reference task numbers and dependent work

### 4. Git Commit Messages
- **Purpose**: Progress tracking and attribution
- **Update**: Regular during work
- **Format**: `[WORKING] feat: Description @agent`

## 🚫 Conflict Prevention

### Structural Conflicts (Prevented By Design)
- **Agent specializations** prevent work overlap
- **Sequential dependencies** provide clear order
- **Isolated worktrees** eliminate file conflicts
- **One agent = one PR** keeps changes focused

### Integration Conflicts (Resolved Through Sync)
- **Later agents sync with main** to get earlier work
- **Dependency tracking** in tasks.md shows requirements
- **@claude coordination** resolves complex integration issues
- **Small, focused PRs** make conflicts manageable

## 📊 Coordination Patterns

### Sequential Dependencies
```markdown
# Architecture → Implementation → Optimization
- [x] T001 @claude Design system architecture ✅
    ↓ (architecture complete - backends can start)
- [ ] T002 @copilot Implement API endpoints (depends on T001)
- [ ] T003 @copilot Implement data models (depends on T001)
    ↓ (implementation complete - optimization can start)
- [ ] T004 @qwen Optimize database queries (depends on T002, T003)
```

### Parallel Development
```markdown
# After architecture, multiple agents work simultaneously:
- [x] T001 @claude Design auth architecture ✅
    ↓ (enables parallel work)
- [ ] T002 @copilot Auth backend     } Parallel
- [ ] T003 @codex Auth frontend      } Development
- [ ] T004 @gemini Auth documentation} Phase
```

### Integration Coordination
```markdown
# Final integration after parallel work:
- [x] T002 @copilot Auth backend ✅
- [x] T003 @codex Auth frontend ✅
- [ ] T005 @claude Integration testing (depends on T002, T003)
- [ ] T006 @qwen Performance testing (depends on T005)
```

## 🔍 Monitoring & Status

### Central Coordination View
```bash
# From main repo, check all agent status
cd /home/vanman2025/Projects/multiagent-core

# See all active worktrees
git worktree list

# Check task completion status
grep -r "@\(claude\|qwen\|gemini\|codex\|copilot\)" specs/*/tasks.md

# See recent progress
git log --oneline --grep="@" -10
```

### Agent Status Checking
```bash
# Quick status of all active agents
for agent in claude qwen gemini codex copilot; do
  if [ -d "../project-$agent" ]; then
    echo "$agent: $(cd ../project-$agent && git log -1 --oneline)"
  fi
done
```

## ⚠️ Common Issues and Solutions

### Issue: "Multiple agents assigned same task"
```markdown
# WRONG: Multiple agents assigned same task
- [ ] T001 @copilot @codex Implement auth ❌

# CORRECT: Single agent responsibility
- [ ] T001 @copilot Implement auth backend
- [ ] T002 @codex Implement auth frontend
```

### Issue: "Agent blocked by missing dependency"
```bash
# Check if prerequisites are complete before starting
if ! grep -q "\[x\] T001" specs/tasks.md; then
  echo "ERROR: T001 must be complete before starting T002"
  exit 1
fi
```

### Issue: "Integration conflicts between agents"
```bash
# When multiple agents' work conflicts
# 1. Later agent syncs with main to get earlier work
cd ../project-codex
git fetch origin main && git merge origin/main

# 2. Resolve conflicts understanding both implementations
# 3. Escalate complex conflicts to @claude
git commit -m "[COMPLETE] feat: Work complete @claude

Integration conflicts resolved with @copilot's implementation."
```

## ✅ Best Practices

### 1. Clear Task Assignment
- **One task = one agent**
- **Clear dependencies in tasks.md**
- **Specific, actionable descriptions**

### 2. Regular Synchronization
```bash
# Daily sync routine for all agents
cd ../project-[agent]
git fetch origin main && git merge origin/main
```

### 3. Proactive Communication
```bash
# Update status before blocking others
git commit -m "[PROGRESS] feat: Auth 80% complete @copilot

Backend endpoints implemented, testing in progress."
```

### 4. Dependency Management
- **Check prerequisites before starting**
- **Update dependents when complete**
- **Document integration requirements in PR**

### 5. Escalation Protocol
```bash
# When stuck, escalate to @claude
git commit -m "[BLOCKED] feat: Need architecture decision @claude

Database schema unclear for user roles."
```

## 🎯 Quick Reference

### For Agents Starting Work
```bash
# 1. Find your tasks
grep "@[agent]" specs/*/tasks.md

# 2. Check dependencies
grep -B5 -A5 "T00X" specs/tasks.md

# 3. Set up tracking
TodoWrite: [{"content": "Task X", "status": "pending"}]

# 4. Start work in worktree
cd ../project-[agent]
```

### For Agents Completing Work
```bash
# 1. Mark internal tracking complete
TodoWrite: [{"content": "Task X", "status": "completed"}]

# 2. Final commit with @claude
git commit -m "[COMPLETE] feat: Work complete @claude"

# 3. Create PR (updates tasks.md via PR)
gh pr create --title "feat: [agent] Description"

# 4. Dependent agents notified via PR merge
```

### For Monitoring Progress
```bash
# Check all agent status
git worktree list
grep -r "\[x\]" specs/*/tasks.md

# See dependency chain
grep -A10 -B10 "@agent" specs/tasks.md
```

## 📈 Success Metrics

- **Task Visibility**: All agents can see current status
- **Dependency Tracking**: Clear prerequisite relationships
- **Attribution**: Easy to identify who did what
- **Conflict Rate**: Minimal integration issues
- **Coordination Overhead**: < 10% of development time

**Remember: Isolation enables parallelism, coordination ensures success!**