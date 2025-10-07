---
allowed-tools: Task(judge-architect)
description: Analyze Claude Code PR review and generate actionable feedback in spec directory
argument-hint: "PR number (e.g., 9)"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/judge` in the triggering message **is** the PR number. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

# Invoke Judge Architect Subagent

**Purpose**: Use the judge-architect subagent to evaluate PR review feedback and provide cost-benefit analysis for implementation decisions.

**Subagent Responsibilities**:
- Analyze Claude Code's PR review feedback against original SpecKit requirements
- Assess business impact vs. development effort
- Provide APPROVE/DEFER/REJECT recommendations with confidence scoring
- Generate human-readable decision summaries

**Instructions**:

Invoke the judge-architect subagent with the PR number:

```
PR number: $ARGUMENTS

Evaluate the PR review feedback and determine implementation worthiness:

1. Determine spec directory from PR branch name (e.g., branch "005-documentation-management-system" → spec "005")
2. Fetch Claude Code's GitHub review using `gh pr view "$ARGUMENTS" --json reviews,comments`
3. Read the original SpecKit specification from the spec directory (spec.md, plan.md, data-model.md)
4. Apply the judge-architect analysis framework to evaluate:
   - Feedback alignment with original specs
   - Cost-benefit analysis (effort estimates vs. business value)
   - Technical risk assessment
   - Implementation priority scoring
5. **CRITICAL - Output Location**: Generate all feedback artifacts in `specs/{spec-number}/pr-feedback/session-{timestamp}/`:
   - judge-summary.md (recommendation with confidence score, NO tasks)
   - review-tasks.md (ONLY actionable tasks with agent assignments)
   - future-enhancements.md (long-term deferred improvements)
   - plan.md (implementation roadmap)
6. **DO NOT** use `.multiagent-feedback/`, `.multiagent/pr-review/sessions/`, or `.multiagent/pr-review/logs/`
7. Post summary comment to PR using `gh pr comment`

The subagent will:
- Run `.multiagent-feedback/scripts/github/find-pr-spec-directory.sh` to locate spec context
- Read original specifications to understand requirements
- Fetch PR review data from GitHub
- Apply cost-benefit decision framework
- Generate complete feedback analysis with confidence scores
- Create all required feedback artifacts

Return the recommendation (APPROVE/DEFER/REJECT), confidence score, and feedback directory location.
```

This command delegates all analysis and decision-making to the specialized judge-architect subagent.