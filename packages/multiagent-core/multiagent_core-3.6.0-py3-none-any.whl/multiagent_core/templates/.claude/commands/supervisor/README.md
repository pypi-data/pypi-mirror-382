# Supervisor Commands - Agent Progress Monitoring

## Overview

The supervisor subsystem provides 3 commands for monitoring agent work at different stages:

| Command | Phase | Purpose | When to Use |
|---------|-------|---------|-------------|
| `/supervisor:start` | Pre-work | Verify agent setup and readiness | Before agents begin work on spec |
| `/supervisor:mid` | Mid-work | Monitor progress and compliance | During active development |
| `/supervisor:end` | Pre-PR | Verify completion and PR readiness | Before creating PRs |

## Command Details

### 1. `/supervisor:start [spec-directory]`

**Phase**: Pre-work verification
**Purpose**: Verify agent setup before starting work on a spec.

**What It Does**:
1. Check worktree configuration
2. Verify task assignments in layered-tasks.md
3. Ensure agents can begin work without conflicts
4. Validate spec directory structure
5. Check for missing dependencies
6. Verify environment setup

**Checks Performed**:
- ✅ Worktree properly configured
- ✅ Task assignments valid
- ✅ No conflicting agent assignments
- ✅ Spec directory complete
- ✅ Dependencies available
- ✅ Environment variables set

**Usage**:
```bash
/supervisor:start specs/002-system-context-we
/supervisor:start 005
```

**Output**: Setup report with:
- Agent readiness status
- Worktree configuration
- Task distribution
- Blockers (if any)
- Green light to proceed (or issues to fix)

**Invokes**: supervisor-start subagent

---

### 2. `/supervisor:mid [spec-directory]`

**Phase**: Mid-work monitoring
**Purpose**: Monitor agent progress during work on a spec.

**What It Does**:
1. Check task completion status
2. Validate compliance with layered-tasks.md
3. Identify agents that are stuck or off-track
4. Detect scope creep or deviations
5. Validate code quality standards
6. Check for integration issues

**Checks Performed**:
- 📊 Task completion progress
- ✅ Tasks marked complete match actual work
- ⚠️ Agents stuck on tasks
- 🔄 Inter-agent dependencies
- 📝 Code quality compliance
- 🔗 Integration points validated

**Usage**:
```bash
/supervisor:mid specs/002-system-context-we
```

**Output**: Progress report with:
- Completion percentage by agent
- Tasks completed vs. remaining
- Agents off-track or stuck
- Recommendations for intervention
- Estimated completion time

**Invokes**: supervisor-mid subagent

---

### 3. `/supervisor:end [spec-directory]`

**Phase**: Pre-PR verification
**Purpose**: Verify agent work completion before creating PRs.

**What It Does**:
1. Check that all tasks are complete
2. Verify code quality standards met
3. Ensure tests pass
4. Validate documentation updated
5. Check PRs are ready for review
6. Verify no uncommitted work

**Checks Performed**:
- ✅ All assigned tasks completed
- ✅ Tests passing
- ✅ Code quality standards met
- ✅ Documentation updated
- ✅ No uncommitted changes
- ✅ PR templates followed
- ✅ CI/CD ready

**Usage**:
```bash
/supervisor:end specs/002-system-context-we
```

**Output**: Completion report with:
- All tasks completion status
- Test results
- Code quality metrics
- Documentation status
- PR readiness checklist
- Go/No-go decision

**Invokes**: supervisor-end subagent

---

## Typical Supervisor Workflow

### Starting New Work
```bash
1. /iterate:tasks 005                  # Organize tasks
2. /supervisor:start 005               # Verify setup
3. # Agents begin work in worktrees
```

### During Development
```bash
1. # Agents working on assigned tasks
2. /supervisor:mid 005                 # Check progress
3. # Identify and unblock stuck agents
4. # Continue development
```

### Before PR Creation
```bash
1. # Agents signal work complete
2. /supervisor:end 005                 # Verify completion
3. # Fix any issues identified
4. # Create PRs
```

## Validation Rules

### Compliance Checks
- Tasks match spec requirements
- Code follows project patterns
- Tests achieve coverage thresholds
- Documentation is current
- No mock implementations in production code

### Quality Standards
- Lint and typecheck pass
- All tests pass
- No security vulnerabilities
- API contracts maintained
- Performance benchmarks met

## Automation Behavior

The supervisor system can be configured for:

**Manual Mode** (default):
- User runs supervisor commands explicitly
- Provides progress reports on demand
- User decides when to proceed

**Automated Mode** (optional):
- Runs automatically at workflow checkpoints
- Blocks progression if issues detected
- Integrates with CI/CD pipelines

## Subsystem Integration

- **Core System**: Invoked during `/core:project-setup`
- **Iterate System**: Validates task layering compliance
- **Testing System**: Checks test coverage and quality
- **Deployment System**: Ensures deployment readiness
- **GitHub System**: Validates PR requirements

## Troubleshooting

### "Worktree not configured"
Run `git worktree list` to check configuration. Create worktree if missing.

### "Tasks not assigned"
Run `/iterate:tasks [spec-dir]` to assign tasks before starting work.

### "Agent stuck on task"
Use `/supervisor:mid` to identify stuck agents. Review task complexity or reassign.

### "Tests failing"
Ensure all agents have run tests locally. Check CI/CD logs for specific failures.

### "Documentation outdated"
Run `/docs:update` to update documentation based on code changes.

## Related Documentation

- Supervisor subsystem: `.multiagent/supervisor/README.md`
- Supervisor-start agent: `.claude/agents/supervisor-start.md`
- Supervisor-mid agent: `.claude/agents/supervisor-mid.md`
- Supervisor-end agent: `.claude/agents/supervisor-end.md`
- Compliance rules: `.multiagent/supervisor/memory/compliance-rules.md`
