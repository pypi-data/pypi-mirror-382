# PR Review Workflow Improvements

**Created**: 2025-09-30
**Status**: Planning

## Issues Identified

1. **Judge reading from wrong location**: Currently reads from `.multiagent/github/pr-review/sessions/` but should read directly from GitHub Claude Code review
2. **Output location incorrect**: Putting analysis in `.multiagent/` instead of spec directory where work originated
3. **Manual invocation**: Judge should automatically trigger when Claude Code review is ready
4. **Session setup redundant**: pr-session-setup creates unnecessary intermediate files
5. **Task assignment**: Judge is creating tasks, not task-assignment-router subagent

## Streamlining Tasks

### Phase 1: Fix Output Location
- [ ] T1.1 Update judge to output to spec directory instead of `.multiagent/github/pr-review/sessions/`
  - Output path should be: `specs/{spec-number}/pr-feedback/session-{timestamp}/`
  - Keep session structure but move to spec directory
  - **Effort**: 1 hour
  - **Priority**: HIGH

- [ ] T1.2 Update all PR review scripts to use spec-based paths
  - Modify path resolution in judge-architect.md
  - Update session setup to create in spec directory
  - **Effort**: 30 minutes
  - **Priority**: HIGH

### Phase 2: Direct GitHub Integration
- [ ] T2.1 Remove pr-session-setup dependency
  - Judge should read directly from GitHub API using `gh pr view`
  - No intermediate session files needed
  - **Effort**: 1 hour
  - **Priority**: MEDIUM

- [ ] T2.2 Judge auto-detection of Claude Code reviews
  - Monitor for Claude Code bot comments on PRs
  - Auto-trigger judge when review appears
  - Use GitHub webhooks or polling
  - **Effort**: 2-3 hours
  - **Priority**: MEDIUM

### Phase 3: Task Assignment Router
- [ ] T3.1 Fix task-assignment-router to actually route tasks
  - Currently judge creates tasks directly
  - Router should analyze judge output and assign to agents
  - **Effort**: 1-2 hours
  - **Priority**: LOW

- [ ] T3.2 Integrate with worktree automation
  - When tasks created, auto-create worktrees for assigned agents
  - Link to layered-tasks system
  - **Effort**: 2 hours
  - **Priority**: LOW (wait for worktree systemization)

### Phase 4: Workflow Automation (Future)
- [ ] T4.1 GitHub Action integration
  - Trigger on Claude Code review posted
  - Run judge automatically
  - Post results as PR comment
  - **Effort**: 3-4 hours
  - **Priority**: DEFERRED

- [ ] T4.2 Agent auto-assignment
  - Based on judge output, automatically assign agents to worktrees
  - Create GitHub issues or tasks for each agent
  - **Effort**: 2-3 hours
  - **Priority**: DEFERRED

## Architecture Changes

### Current Flow (Broken)
```
PR created → Manual: /pr-review:pr → pr-session-setup → Creates session in .multiagent/
→ Manual: /pr-review:judge → Reads from session → Outputs to wrong location
→ Manual: /pr-review:tasks → task-assignment-router (doesn't work, judge already did it)
```

### Target Flow (Streamlined)
```
PR created → Claude Code reviews → Judge auto-detects review
→ Judge reads directly from GitHub → Analyzes against spec
→ Outputs to specs/{spec-number}/pr-feedback/
→ task-assignment-router assigns to agents → Auto-creates worktrees
→ Agents pick up work from their worktrees
```

## Implementation Order

1. **Immediate** (Fix critical issues):
   - T1.1, T1.2: Fix output location to spec directory

2. **Short-term** (Streamline workflow):
   - T2.1: Remove session setup, read from GitHub directly
   - T3.1: Fix task-assignment-router

3. **Medium-term** (Automation):
   - T2.2: Auto-trigger judge on Claude Code review
   - T3.2: Integrate with worktree system

4. **Long-term** (Full automation):
   - T4.1, T4.2: GitHub Actions integration

## Notes

- **Don't break working parts**: System overall works well, just needs refinement
- **Wait for worktree systemization**: Some improvements depend on consistent branch/worktree setup
- **Impressive results**: Judge output quality is excellent, just needs better integration
- **Spec-centric**: All feedback should live in spec directory, not global `.multiagent/`

---
*This is a working document to track PR review workflow improvements*
