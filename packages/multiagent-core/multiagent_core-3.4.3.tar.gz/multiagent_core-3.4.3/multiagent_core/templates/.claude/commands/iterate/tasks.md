---
allowed-tools: Task(task-layering)
description: Phase 1 - Apply task layering to create non-blocking parallel structure
argument-hint: "Spec directory (e.g., 002-system-context-we or just 005)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/iterate:tasks` in the triggering message **is** the spec directory name or number. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

# Phase 1: Invoke Task Layering Subagent

**Purpose**: Use the task-layering subagent to intelligently organize and assign ALL tasks to agents.

**Subagent Responsibilities**:
- Analyze original tasks.md for complexity and grouping
- Organize tasks into functional phases (Foundation, Implementation, Testing, Integration)
- Assign tasks to agents based on realistic workload distribution
- Generate complete layered-tasks.md following 002 structure pattern

**Instructions**:

Invoke the task-layering subagent with the spec directory:

```
Spec directory: $ARGUMENTS

Transform the sequential tasks in specs/$ARGUMENTS/tasks.md into a layered, non-blocking parallel structure in specs/$ARGUMENTS/agent-tasks/layered-tasks.md.

Follow the pattern from specs/002-system-context-we/agent-tasks/layered-tasks.md:
1. Organize tasks into functional phases (Foundation, Implementation, Testing)
2. Group tasks by logical area within each phase
3. Assign tasks to agents based on complexity and specialization
4. Apply realistic workload distribution (Claude 45-55%, Codex 30-35%, Qwen 15-20%, Copilot 10-15%, Gemini 0-5%)
5. Include clear dependencies and coordination protocol

The subagent will:
- Run .multiagent/iterate/scripts/layer-tasks.sh to create directory structure
- Read original tasks.md to understand all tasks
- Read agent-responsibilities.yaml to understand agent capabilities
- Analyze task complexity and organize into logical sections
- Write complete layered-tasks.md with all tasks assigned and organized

Return the final task distribution and confirm all tasks have been organized and assigned.
```

This command delegates all intelligence and decision-making to the specialized task-layering subagent.