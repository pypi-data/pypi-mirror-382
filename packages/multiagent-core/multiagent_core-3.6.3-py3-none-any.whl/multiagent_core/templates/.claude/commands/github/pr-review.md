---
allowed-tools: Task(judge-architect)
description: Analyze Claude Code PR review and generate actionable feedback in spec directory
argument-hint: "PR number (e.g., 9)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/github:pr-review` in the triggering message **is** the PR number.

Given the PR number, do this:

1. Get PR branch name using `gh pr view "$ARGUMENTS" --json headRefName --jq '.headRefName'`
2. Extract spec number from branch name (pattern: `agent-{agent}-{spec}` → extract the spec number)
3. Find the spec directory in `specs/` that matches (e.g., `specs/002-system-context-we/`)
4. Invoke the judge-architect subagent with:
   - PR number: $ARGUMENTS
   - Spec directory path found in step 3

The subagent will read templates from `.multiagent/github/pr-review/templates/` to understand the execution flow and output directly to `specs/{spec}/feedback/`