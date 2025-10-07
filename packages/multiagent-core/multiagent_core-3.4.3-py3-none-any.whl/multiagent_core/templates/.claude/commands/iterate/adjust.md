---
allowed-tools: Bash(*), Read(*), Write(*), Glob(*), TodoWrite(*)
description: Phase 3 - Live development adjustments with ecosystem sync
argument-hint: "Spec directory (e.g., 002-system-context-we)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/iterate-adjust` in the triggering message **is** the spec directory name. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

# Phase 3: Development Adjustments

**Purpose**: Handle live changes during development while maintaining spec ecosystem coherence.

## Instructions

Given that spec directory, do this:

1. Run the script `.multiagent/iterate/scripts/phase3-development-adjust.sh "$ARGUMENTS"` to handle development adjustments.
2. Report completion with new iteration and updated ecosystem.

Note: The script incorporates changes and re-syncs the entire spec ecosystem.

## What This Does

- Incorporates feedback from PR reviews or manual changes
- Re-runs Phase 1 + Phase 2 with new requirements
- Creates new iteration file (iteration-N-tasks.md)
- Updates entire spec ecosystem to match changes
- Maintains development audit trail

This is Phase 3 of the iterate system - handles live development changes.