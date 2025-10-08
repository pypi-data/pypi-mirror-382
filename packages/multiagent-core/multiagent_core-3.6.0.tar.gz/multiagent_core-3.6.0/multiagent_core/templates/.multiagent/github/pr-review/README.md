# PR Review System - Automated Pull Request Analysis

## Purpose

Analyzes PR review feedback from Claude Code and evaluates it against original SpecKit requirements. Generates cost-benefit analysis with APPROVE/DEFER/REJECT recommendations.

## What It Does

1. **Fetches PR review** - Gets Claude Code's review comments via GitHub API
2. **Analyzes against spec** - Compares feedback to original requirements in specs/*/
3. **Cost-benefit analysis** - Estimates implementation effort vs business value
4. **Generates recommendation** - Creates APPROVE/DEFER/REJECT summary with confidence score
5. **Creates tasks** - Breaks down approved changes into agent-assigned tasks

## Agents Used

- **@claude/judge-architect** - Evaluates PR feedback against SpecKit requirements
- **No other dedicated agents** - Python orchestrator handles API calls and analysis

## Commands

### Primary Commands
- `/pr-review:pr <PR-number>` - Process PR feedback
- `/pr-review:tasks <session-ID>` - Generate tasks from PR
- `/pr-review:plan <session-ID>` - Create implementation plan
- `/pr-review:judge <PR-number>` - Generate approval summary

### Integration Points
- Triggered by GitHub webhooks on PR comments
- Coordinates with all agent systems for fixes

## Directory Structure

```
.multiagent/github/pr-review/
├── scripts/
│   ├── layer-tasks.sh            # Task layering for parallel work
│   ├── process-pr-feedback.sh    # PR feedback processor
│   └── generate-pr-tasks.sh      # Task generation from PR
├── templates/
│   ├── task-layers/              # Layered task templates
│   └── feedback/                 # Feedback processing templates
├── sessions/                     # PR analysis sessions
└── logs/                         # Processing logs
```

## Outputs

### 1. PR Session Files (`sessions/`)

Generated for each PR analysis:

```
sessions/
└── pr-8-20250926-192003/
    ├── pr-data.json              # Raw PR data
    ├── analysis.md               # Feedback analysis
    ├── tasks.md                  # Generated tasks
    └── implementation-plan.md    # Execution plan
```

### 2. Layered Task Files

| File | Purpose | Content |
|------|---------|---------|
| `layer-1-independent.md` | Parallel tasks | Tasks with no dependencies |
| `layer-2-dependent.md` | Sequential tasks | Tasks that depend on layer 1 |
| `layer-3-integration.md` | Integration tasks | Final integration work |

### 3. Agent Assignments

Tasks are assigned based on complexity and type:

| Agent | Task Types | Complexity |
|-------|------------|------------|
| @copilot | Simple fixes, typos | Low (1-2) |
| @qwen | Performance optimization | Medium (3) |
| @gemini | Documentation, research | Low-Medium |
| @claude | Architecture, security | High (4-5) |

## Complete Workflow (Following SpecKit Pattern)

### Phase 1: Slash Command - Main Agent Setup
**Command**: `/github:pr-review <PR_NUMBER>`

**Main agent (Claude Code) executes mechanically**:
1. Get PR branch: `gh pr view <PR> --json headRefName`
2. Extract spec from branch (pattern: `agent-{agent}-{spec}`)
3. Create session directory: `specs/{spec}/pr-feedback/session-{timestamp}/`
4. Copy templates from `.multiagent/github/pr-review/templates/` to session
5. Create `pr-context.json` in session with: `{"pr_number": "X", "branch": "...", "spec": "..."}`
6. Invoke judge-architect subagent with session directory path

### Phase 2: Subagent Intelligence Work
**Subagent**: @claude/judge-architect
**Receives**: Session directory path (e.g., `specs/005/pr-feedback/session-20250930-134756/`)

**Subagent workflow**:
1. Read `pr-context.json` for PR number, branch, spec
2. Load execution flow from `judge-output-review.md` template
3. **Follow execution flow step-by-step**:
   - Extract spec number from branch name
   - Read original spec: `specs/{spec}/spec.md`
   - Fetch Claude Code review: `gh pr view {pr} --json reviews,comments`
   - Parse priority markers (🚨 critical, ⚠️ high, 📋 medium)
   - Estimate effort (<1h, 1-4h, 4-8h, >1day) for each item
   - Assess value (low/medium/high) against spec requirements
   - Calculate decision matrix scores (quality, cost, value, risk)
4. Fill template placeholders with analysis results
5. Generate recommendation (APPROVE/DEFER/REJECT)
6. Create review-tasks.md with agent assignments

### Phase 3: Outputs Created
**Location**: `specs/{spec}/pr-feedback/session-{timestamp}/`

**Files generated**:
- `judge-output-review.md` - Filled template with complete analysis
- `review-tasks.md` - Actionable tasks with agent assignments
- `future-enhancements.md` - Long-term deferred improvements
- `plan.md` - Implementation roadmap

## Key Architecture Pattern

**SpecKit Pattern Applied**:
1. **Slash Command** → Tells main agent what mechanical steps to do
2. **Main Agent** → Runs scripts, creates structure, copies templates
3. **Main Agent** → Invokes subagent with session path
4. **Subagent** → Reads templates to understand execution flow
5. **Subagent** → Fills templates with intelligence/analysis
6. **Templates** → Guide subagent with execution flow + placeholders

## Example Workflow

### PR Comment → Task
```markdown
# PR Comment:
"The authentication middleware needs rate limiting"

# Generated Task:
- [ ] T025 @claude Add rate limiting to authentication middleware (Complexity: 4)
  - Implement token bucket algorithm
  - Add configuration for limits
  - Write tests for rate limiting
```

### Task Layering Example
```markdown
# Layer 1 (Parallel)
- [ ] T010 @copilot Fix typo in README
- [ ] T011 @gemini Update API documentation
- [ ] T012 @qwen Optimize database queries

# Layer 2 (After Layer 1)
- [ ] T020 @claude Integrate optimized queries with API

# Layer 3 (Final)
- [ ] T030 @claude Run integration tests
```

## GitHub Workflows

### PR Feedback Automation (`.github/workflows/`)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pr-feedback-automation.yml` | PR comment | Process feedback |
| `claude-code-review.yml` | PR opened | Initial review |
| `claude-feedback-router.yml` | Review submitted | Route to agents |

## Integration with AgentSwarm

The PR review system integrates with AgentSwarm for:
1. **Automatic task routing** to appropriate agents
2. **Progress tracking** across multiple agents
3. **Coordination** of parallel work
4. **Final integration** of all changes

## Session Management

Each PR creates a session:
```bash
# Session naming: pr-<number>-<date>-<time>
pr-8-20250926-192003/
```

Sessions track:
- Original PR data
- All feedback received
- Tasks generated
- Implementation status
- Final resolution

## Manual Usage

### Process a PR
```bash
/pr-review:pr 123
```

### Generate Tasks from Session
```bash
/pr-review:tasks pr-123-20250926-192003
```

### Get Implementation Plan
```bash
/pr-review:plan pr-123-20250926-192003
```

## Automation

PR review is fully automated via GitHub Actions:
1. **PR opened** → Initial analysis
2. **Review comment** → Task generation
3. **Tasks complete** → Update PR
4. **All tasks done** → Request re-review

## Key Points

- **PR Review owns feedback processing** - Not implementation
- **Coordinates all agents** - Routes work appropriately
- **Parallel execution** - Layers tasks for efficiency
- **GitHub integrated** - Works with PR workflow
- **Session-based** - Tracks entire PR lifecycle