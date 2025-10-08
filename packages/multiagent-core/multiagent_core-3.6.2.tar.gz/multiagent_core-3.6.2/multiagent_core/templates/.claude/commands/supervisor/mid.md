---
allowed-tools: Task(supervisor-mid)
description: Mid-work agent progress and compliance monitoring
argument-hint: "Spec directory (e.g., 002-system-context-we)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

# Invoke Supervisor Mid Subagent

**Purpose**: Use the supervisor-mid subagent to monitor agent progress during work and ensure compliance with task assignments.

**Subagent Responsibilities**:
- Track task completion status per agent
- Monitor commit activity and progress velocity
- Detect blocked or stuck agents
- Validate compliance with layered-tasks.md assignments
- Identify cross-agent dependency issues

**Instructions**:

Invoke the supervisor-mid subagent with the spec directory:

```
Spec directory: $ARGUMENTS

Monitor agent progress and detect issues:

1. Run `.multiagent/supervisor/scripts/mid-verification.sh "$ARGUMENTS"` to analyze progress
2. Parse script output for:
   - Commit activity per agent worktree
   - Task completion percentage vs. assignments
   - Time since last activity (staleness detection)
   - File changes vs. assigned task scope
3. Assess agent status:
   - Making good progress (recent commits, tasks complete)
   - Potentially stuck (no recent activity, tasks incomplete)
   - Off-track (commits don't match assignments)
   - Blocked on dependencies (waiting for other agents)
4. Validate compliance:
   - Agents working on assigned tasks only
   - File changes align with task descriptions
   - No unauthorized cross-agent modifications
5. Generate progress report showing:
   - Task completion stats per agent (X/Y complete, Z%)
   - Recent activity summary (last commit time)
   - Agents needing attention (stale, blocked, off-track)
   - Cross-agent blockers (dependency issues)
6. Provide intervention recommendations:
   - Contact commands for stuck agents
   - Dependency resolution steps
   - Task reassignment suggestions if needed
   - Timeline adjustments based on velocity

The subagent will:
- Execute `.multiagent/supervisor/scripts/mid-verification.sh`
- Analyze git history across all agent worktrees
- Read layered-tasks.md to validate compliance
- Detect staleness using configurable thresholds
- Generate actionable progress report with recommendations

Return progress summary, agents needing attention, and intervention steps.
```

This command delegates all mid-work monitoring to the specialized supervisor-mid subagent.