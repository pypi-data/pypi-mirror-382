# PR Review System - Automated Pull Request Analysis

## Purpose

The **pr-review** system automates pull request feedback processing and task generation. It:
1. **Processes PR feedback** from GitHub pull requests
2. **Generates actionable tasks** from review comments
3. **Routes tasks to appropriate agents** based on complexity
4. **Tracks implementation status** through PR lifecycle

## Key Difference from Other Systems

- **Core system** → Creates GitHub workflows for CI/CD
- **Deployment system** → Creates deployment configs
- **Testing system** → Creates test files
- **PR Review system** → Processes PR feedback into tasks

## Agents Used

- `pr-feedback-router` agent - Routes PR feedback to other agents
- Works with all other agents to implement PR feedback

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
.multiagent/pr-review/
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

## How It Works

### 1. PR Feedback Collection
```bash
# GitHub webhook triggers on PR comment
gh pr view 123 --json comments > pr-feedback.json
```

### 2. Feedback Analysis
- Parses reviewer comments
- Identifies required changes
- Categorizes by type and severity

### 3. Task Generation
- Creates specific tasks from feedback
- Assigns complexity scores
- Determines dependencies

### 4. Task Layering
- Groups tasks by dependencies
- Creates parallel execution layers
- Optimizes for multi-agent work

### 5. Agent Assignment
- Matches tasks to agent capabilities
- Balances workload across agents
- Ensures proper skill alignment

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