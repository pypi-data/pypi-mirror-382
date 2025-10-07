---
allowed-tools: Task(supervisor-end)
description: Pre-PR agent completion and readiness verification
argument-hint: "Spec directory (e.g., 002-system-context-we)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

# Invoke Supervisor End Subagent

**Purpose**: Use the supervisor-end subagent to verify agent work completion before creating PRs.

**Subagent Responsibilities**:
- Validate all tasks are 100% complete per layered-tasks.md
- Check code quality standards are met (lint, format, tests)
- Verify PR readiness criteria (proper commits, no conflicts)
- Validate cross-agent integration points work correctly
- Provide exact PR creation commands for ready agents

**Instructions**:

Invoke the supervisor-end subagent with the spec directory:

```
Spec directory: $ARGUMENTS

Verify agents are ready to create PRs:

1. Run `.multiagent/supervisor/scripts/end-verification.sh "$ARGUMENTS"` to validate completion
2. Parse script output for:
   - Task completion status (all tasks marked complete in layered-tasks.md)
   - Code quality checks (lint, format, typecheck passing)
   - Test coverage (tests exist and pass for new functionality)
   - PR readiness (commits, branch names, no merge conflicts)
3. Assess completion status per agent:
   - All tasks complete and quality checks pass (READY)
   - Incomplete tasks or failing checks (BLOCKED)
   - Quality issues requiring fixes (WARNING)
4. Validate integration points:
   - Dependencies between agent tasks resolved
   - Interfaces between agent code compatible
   - No conflicts between agent implementations
5. Generate completion report showing:
   - Task completion status per agent (X/Y complete, percentage)
   - Code quality results (lint, tests, typecheck status)
   - PR readiness per agent (ready/blocked with reasons)
   - Integration validation results
6. For ready agents, provide PR creation commands:
   - Final commit: `git commit -m "[COMPLETE] feat: Feature name @agent"`
   - Push branch: `git push origin agent-{name}-{feature}`
   - Create PR: `gh pr create --title "..." --body "..."`
7. For blocked agents, provide exact fix commands:
   - Complete remaining tasks (specific task IDs)
   - Fix quality issues (lint errors, missing tests)
   - Resolve merge conflicts
   - Add missing commits

The subagent will:
- Execute `.multiagent/supervisor/scripts/end-verification.sh`
- Read layered-tasks.md to verify 100% completion
- Run code quality checks across all agent worktrees
- Validate integration between agent implementations
- Generate comprehensive readiness report with PR commands

Return completion status (READY/BLOCKED per agent), blockers found, and PR creation commands.
```

This command delegates all completion verification to the specialized supervisor-end subagent.