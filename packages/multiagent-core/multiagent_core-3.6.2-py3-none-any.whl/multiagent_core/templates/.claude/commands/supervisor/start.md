---
allowed-tools: Task(supervisor-start)
description: Pre-work agent setup and readiness verification
argument-hint: "Spec directory (e.g., 002-system-context-we)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

# Invoke Supervisor Start Subagent

**Purpose**: Use the supervisor-start subagent to verify agents are properly configured before starting work on a spec.

**Subagent Responsibilities**:
- Validate worktree setup for all assigned agents
- Check that layered-tasks.md exists and is readable
- Verify task assignments are clear and non-conflicting
- Ensure no agents are working in main branch
- Validate git state is clean for parallel work

**Instructions**:

Invoke the supervisor-start subagent with the spec directory:

```
Spec directory: $ARGUMENTS

Verify agents are ready to begin work:

1. Run `.multiagent/supervisor/scripts/start-verification.sh "$ARGUMENTS"` to check pre-work setup
2. Parse script output for:
   - Worktree status per agent (created, branch name, clean state)
   - layered-tasks.md existence and readability
   - Task assignment clarity (no conflicts, all agents have tasks)
   - Main branch sync status with origin
   - Git working directory cleanliness
3. Identify any blockers:
   - Agents missing worktrees
   - Task assignment conflicts
   - Out of sync git state
   - Uncommitted changes
4. Generate readiness report showing:
   - Agent status (ready/blocked per agent)
   - Task assignment summary
   - Git state health
   - Blockers preventing work from starting
5. If blockers found, provide exact resolution commands:
   - Worktree creation: `git worktree add -b agent-{name}-{feature} ../project-{name} main`
   - Git sync: `git fetch origin && git checkout main && git merge origin/main`
   - Task clarification guidance if assignments unclear

The subagent will:
- Execute `.multiagent/supervisor/scripts/start-verification.sh`
- Read layered-tasks.md to understand assignments
- Check worktree configuration across all agents
- Validate git state is ready for parallel development
- Generate comprehensive readiness report with resolutions

Return readiness status (READY/BLOCKED), blockers found, and resolution steps.
```

This command delegates all pre-work verification to the specialized supervisor-start subagent.