---
allowed-tools: Bash(*), Read(*), Write(*), Glob(*), TodoWrite(*)
description: Phase 2 - Sync entire spec ecosystem to match layered tasks
argument-hint: "Spec directory (e.g., 002-system-context-we)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/iterate-sync` in the triggering message **is** the spec directory name. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

# Phase 2: Spec Ecosystem Sync

**Purpose**: Update the entire spec ecosystem to match the organized tasks from Phase 1.

## Instructions

Given that spec directory, do this:

1. Run the script `.multiagent/iterate/scripts/phase2-ecosystem-sync.sh "$ARGUMENTS"` to sync the spec ecosystem.
2. Report completion with updated files and next steps.

Note: The script updates plan.md, quickstart.md, and creates iteration tracking.

## What This Does

- Reads layered tasks from Phase 1
- Updates plan.md with layering status
- Updates quickstart.md with agent coordination info
- Creates current-tasks.md symlink to latest iteration
- Tracks changes in iteration-log.md

This is Phase 2 of the iterate system - keeps all specs coherent.