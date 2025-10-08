# GitHub Commands - Issue & PR Management

## Overview

The github subsystem provides 3 commands for GitHub integration:

| Command | Purpose | When to Use | Invokes |
|---------|---------|-------------|---------|
| `/github:create-issue` | Create issues with templates and auto-assignment | Planning features, documenting bugs, creating tasks | GitHub API (MCP) |
| `/github:discussions` | Manage GitHub Discussions | Exploring ideas, gathering feedback | GitHub API (MCP) |
| `/github:pr-review` | Analyze PR review feedback | After Claude Code reviews PR | judge-architect agent |

## Command Details

### 1. `/github:create-issue [--feature\|--bug\|--task\|--hotfix\|--simple] "title"`

**Purpose**: Create GitHub issues with proper templates and automatic agent assignment.

**Modes**:
- **Simple Mode** (--simple, --task, --hotfix): Use GitHub templates, no complexity estimation
- **Complex Mode** (--feature, --bug): Full workflow with agent routing

**Auto-Assignment Logic**:
```javascript
// Copilot gets: Complexity ≤2 AND Size ≤S (BOTH conditions)
// Claude gets: Everything else
```

**What It Does**:

**Simple Mode**:
1. Check for existing similar issues
2. Select issue type (bug/feature/task/hotfix)
3. Fill GitHub template
4. Create issue with appropriate labels
5. No agent assignment

**Complex Mode**:
1. Check for existing similar issues
2. Determine complexity (1-5) and size (XS/S/M/L/XL)
3. Load appropriate template
4. Fill template with metadata
5. Create issue
6. **Auto-assign Copilot** if complexity ≤2 AND size ≤S
7. Otherwise assign to Claude Code agents
8. Optionally create sub-issues
9. Set milestone and priority

**Usage**:
```bash
# Simple mode
/github:create-issue --task "Add error handling to API"
/github:create-issue --bug "Fix login redirect"
/github:create-issue --hotfix "Critical payment bug"

# Complex mode with auto-assignment
/github:create-issue --feature "User dashboard redesign"
/github:create-issue --bug "Memory leak in background service"
```

**Copilot Auto-Assignment**:
When both conditions are met (complexity ≤2 AND size ≤S):
- Copilot assigned immediately via MCP
- Copilot receives task instructions
- Branch created automatically: `copilot/{type}-{number}`
- Expected timeline:
  - Acknowledgment: ~5 seconds
  - Branch created: ~30 seconds
  - Draft PR: ~1 minute
  - Implementation: 10-15 minutes
  - PR ready: ~17 minutes

**Claude Code Assignment**:
When complexity >2 OR size >M OR has blocking labels:
- Requires `/work #[number]` to start
- Full MCP tool access
- Agent orchestration available

**Templates Location**: `templates/local_dev/`
- `feature-template.md`
- `bug-template.md`
- `task-template.md`
- `enhancement-template.md`

---

### 2. `/github:discussions [topic or discussion number]`

**Purpose**: Create and manage GitHub Discussions for idea exploration.

**Smart Argument Detection**:
- **No arguments** → Show menu
- **Number** (e.g., "125") → View Discussion #125
- **Text** (e.g., "branching strategy") → Create discussion

**What It Does**:

**Menu Options**:
1. Create new discussion
2. List existing discussions
3. View specific discussion
4. Find similar/overlapping discussions
5. Consolidate multiple discussions

**Create Discussion**:
1. Quick overlap check (avoid duplicates)
2. Select category (Ideas, General, Q&A, etc.)
3. Use idea template structure
4. Create with GraphQL mutation
5. Return discussion number and URL

**Find Similar Content**:
1. Search existing issues (limit 10)
2. Search recent discussions (limit 20)
3. Identify overlapping topics
4. Suggest consolidation or linking

**Consolidate Discussions**:
1. Check if existing issue covers topic
2. Select multiple discussions
3. Create unified issue with combined requirements
4. Link discussions to issue
5. Add status comments

**Usage**:
```bash
/github:discussions                           # Show menu
/github:discussions "milestone planning"      # Create discussion
/github:discussions 42                        # View discussion #42
```

**Discussion Lifecycle Labels**:
- `discussion:exploring` - Initial state
- `discussion:approved` - Ready for implementation
- `discussion:in-progress` - Being implemented
- `discussion:implemented` - Completed
- `discussion:declined` - Won't implement
- `discussion:blocked` - Waiting on dependencies

**Status Comment Format**:
```
📍 Status: In Progress
🔗 Issue: #123
📅 Started: 2025-01-15
```

**Key Principles**:
- No code blocks in discussions (keep readable)
- GitHub native (use API, not local files)
- Clean codebase (no temp files)
- Team visibility (all ideas in GitHub)
- Comment-based tracking (labels restricted)

**Efficiency**:
- Don't list ALL issues (use targeted search)
- Limit results to 5-10 most relevant
- Check issues first (prevent duplicates)

---

### 3. `/github:pr-review [PR number]`

**Purpose**: Analyze Claude Code's PR review feedback and generate actionable recommendations.

**What It Does**:
1. Determine spec directory from PR branch name
2. Fetch Claude Code's review from GitHub
3. Read original SpecKit specification
4. Apply cost-benefit analysis framework:
   - Feedback alignment with specs
   - Effort vs. business value
   - Technical risk assessment
   - Implementation priority scoring
5. Generate feedback artifacts in `specs/{spec-number}/pr-feedback/session-{timestamp}/`:
   - `judge-summary.md` - Recommendation with confidence score
   - `review-tasks.md` - Actionable tasks with agent assignments
   - `future-enhancements.md` - Deferred improvements
   - `plan.md` - Implementation roadmap
6. Post summary comment to PR

**Output Location**:
```
specs/005-feature/pr-feedback/session-20250115-143022/
├── judge-summary.md          # APPROVE/DEFER/REJECT with confidence
├── review-tasks.md           # Tasks with agent assignments
├── future-enhancements.md    # Long-term improvements
└── plan.md                   # Implementation roadmap
```

**Usage**:
```bash
/github:pr-review 9
```

**Recommendations**:
- **APPROVE** - High value, low effort, aligned with specs
- **DEFER** - Low priority or requires dependencies
- **REJECT** - Not aligned with specs or too costly

**Confidence Scores**:
- 90-100%: Very confident in recommendation
- 70-89%: Confident but some uncertainty
- 50-69%: Uncertain, needs discussion
- <50%: Requires human decision

**Invokes**: judge-architect agent

---

## Typical GitHub Workflow

### Feature Planning
```bash
1. /github:discussions "user profile redesign"  # Explore idea
2. # Gather feedback, refine concept
3. /github:create-issue --feature "User profile redesign"
4. # Copilot auto-assigned if simple (complexity ≤2, size ≤S)
5. # Or use /work #[number] for complex features
```

### Bug Tracking
```bash
1. /github:create-issue --bug "Login redirect broken"
2. # Auto-assigned to Copilot if simple bug
3. # Copilot creates PR within ~17 minutes
4. /github:pr-review [PR#]  # Analyze PR review
5. # Implement feedback tasks from review-tasks.md
```

### Idea Management
```bash
1. /github:discussions "multi-agent coordination"
2. # Select option 4 to find similar discussions
3. # Consolidate overlapping discussions
4. # Create unified issue when approved
```

## Subsystem Integration

- **Core System**: Issues created during `/core:project-setup`
- **Iterate System**: Task assignments reference issue numbers
- **Testing System**: Test coverage tracked in issues
- **Deployment System**: Deployment issues created for releases
- **Supervisor System**: Validates issue compliance

## Troubleshooting

### "gh CLI not configured"
Run `gh auth login` to authenticate GitHub CLI.

### "Discussion not found"
Ensure GitHub Discussions are enabled in repository Settings → Features.

### "Similar issue already exists"
Review existing issues before creating duplicates. Use `/github:discussions` for exploration first.

### "Copilot not auto-assigned"
Check both conditions: complexity ≤2 AND size ≤S. Missing either condition requires Claude Code.

### "PR review feedback not found"
Ensure PR has been reviewed by Claude Code before running `/github:pr-review`.

## Related Documentation

- PR review subsystem: `.multiagent/pr-review/README.md`
- Judge architect agent: `.claude/agents/judge-architect.md`
- Issue templates: `templates/local_dev/`
- Discussion templates: `templates/idea-template.md`
- GitHub workflows: `.github/workflows/`
