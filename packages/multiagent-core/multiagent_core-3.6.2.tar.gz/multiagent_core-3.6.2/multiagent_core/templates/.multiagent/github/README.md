# GitHub Subsystem

**Purpose**: Manage GitHub interactions - PR reviews, issue triage, discussions, and releases.

**Subsystem Components:**
- `pr-review/` - Pull request feedback automation
- `issue-review/` - Issue triage and spec generation (contributor-only)

---

## 📋 Overview

The GitHub subsystem provides tools for managing the full GitHub workflow from incoming issues to PR reviews and releases.

### For Users (Ships to Projects)

**PR Review Automation** (`pr-review/`):
- `/github:pr-review <PR#>` - Analyze Claude Code PR reviews
- Generate actionable feedback in spec directories
- Route feedback to appropriate agents
- Track implementation progress

**Issue Management**:
- `/github:create-issue` - Create GitHub issues with templates
- `/github:discussions` - Manage GitHub Discussions

### For Contributors (Framework Only)

**Issue Triage** (`issue-review/`):
- `/github:issue-review` - Review incoming issues from users
- Categorize and prioritize issues
- Generate specs from approved requests
- Link related issues

---

## 🔄 Workflow: From Issue to Deployed Feature

```
1. User Reports Issue
   ↓
2. Contributor runs /github:issue-review
   - Categorizes issue
   - Assesses priority
   - Checks completeness
   ↓
3. Creates spec/XXX-feature-name/
   - Generates spec.md from issue
   - Uses /planning:plan to add details
   - Uses /planning:tasks to generate tasks
   ↓
4. Development
   - Agent completes tasks
   - Creates PR
   ↓
5. User runs /github:pr-review <PR#>
   - Analyzes PR feedback
   - Routes to judge-architect agent
   - Generates improvement tasks
   ↓
6. Refinement & Merge
   - Agent addresses feedback
   - PR merged
   ↓
7. Release & Close Issue
   - Feature deployed
   - Issue closed with resolution
```

---

## 📁 Directory Structure

```
.multiagent/github/
├── README.md                    # This file
│
├── pr-review/                   # PR Review Subsystem (SHIPS TO USERS)
│   ├── README.md               # PR review documentation
│   ├── templates/              # PR feedback templates
│   │   ├── judge-output-review.md
│   │   └── feedback-routing.md
│   └── scripts/                # PR processing scripts
│       └── process-pr-feedback.sh
│
└── issue-review/               # Issue Review Subsystem (CONTRIBUTOR-ONLY)
    ├── templates/              # Issue analysis templates
    │   ├── bug-report.md
    │   ├── feature-request.md
    │   └── spec-generation.md
    └── scripts/                # Issue processing scripts
        └── create-spec-from-issue.sh
```

---

## 🎯 Commands by Phase

### Phase 4: PR Review & Feedback

**Available to all users:**

```bash
# Analyze PR review feedback
/github:pr-review 123

# Create issues for tracking
/github:create-issue --bug "Title"
/github:create-issue --feature "Title"

# Manage discussions
/github:discussions "Topic"
```

**Spawns subagents:**
- `judge-architect` - Analyzes PR feedback, creates task breakdown

### Contributor Workflow (Pre-Phase 1)

**Contributor-only commands:**

```bash
# Triage incoming issues
/github:issue-review

# Review specific issue
/github:issue-review 42

# Review by label
/github:issue-review --label=bug
/github:issue-review --label=enhancement

# Create spec from issue
/github:issue-review 42 --create-spec
```

**Spawns subagents:**
- `issue-reviewer` - Categorizes issues, generates specs

---

## 🔧 Configuration

### PR Review (`pr-review/`)

**Required:**
- GitHub CLI (`gh`) installed and authenticated
- PR must be in same repository

**Optional:**
- Custom feedback templates in `pr-review/templates/`
- Custom routing rules in `pr-review/scripts/`

### Issue Review (`issue-review/` - Contributor-only)

**Required:**
- GitHub CLI (`gh`) installed and authenticated
- Write access to repository

**Optional:**
- Custom issue templates in `issue-review/templates/`
- Custom spec templates for auto-generation

---

## 📊 Templates

### PR Review Templates

**judge-output-review.md** - Format for PR feedback analysis:
```markdown
# PR Review Analysis

**PR Number**: #123
**Author**: @agent
**Review Type**: Code Quality | Architecture | Security

## Issues Identified
[List of issues from PR review]

## Recommended Actions
[Specific tasks for addressing feedback]

## Priority Assessment
[Critical/High/Medium/Low with rationale]
```

### Issue Review Templates (Contributor-only)

**bug-report.md** - Bug report analysis template
**feature-request.md** - Feature request analysis template
**spec-generation.md** - Auto-generated spec template

---

## 🚀 Usage Examples

### Example 1: User Receives PR Feedback

```bash
# User's PR #123 got feedback from Claude Code review
user@project$ /github:pr-review 123

Analyzing PR #123...
Found 5 issues in review comments.

Spawning judge-architect subagent...

✅ Analysis Complete

High Priority (2 issues):
- Security: Exposed API keys in config
- Architecture: Database queries in view layer

Medium Priority (3 issues):
- Code quality: Unused imports
- Documentation: Missing function docstrings
- Testing: No edge case coverage

Created tasks in specs/003-authentication/feedback/pr-123-tasks.md

Would you like to start addressing these? [y/n]
```

### Example 2: Contributor Triages Issues

```bash
# Contributor reviews incoming issues
contributor@multiagent-core$ /github:issue-review

Fetching open issues... found 12

High Priority (3):
- #42: TypeScript support (Feature) → Create spec
- #38: Better error messages (Enhancement) → Add to spec
- #35: Installation fails on Windows (Bug) → Needs info

Medium Priority (5):
[...]

Low Priority (4):
[...]

Detailed report? [y/n] y

[Shows full analysis with recommendations]

Execute recommended actions? [y/n] y

✅ Created specs/007-typescript-support/
✅ Added task to specs/003-error-handling/
✅ Commented on #35 requesting info
✅ Linked related issues #42, #38, #29
```

---

## 🎓 Best Practices

### For PR Review (Users)

1. **Run after every PR review** - Don't ignore feedback
2. **Prioritize security issues** - Address immediately
3. **Create tracking tasks** - Use generated tasks.md files
4. **Learn from patterns** - Common issues indicate training needs

### For Issue Review (Contributors)

1. **Review regularly** - Check issues weekly
2. **Be responsive** - Comment within 48 hours
3. **Group similar issues** - One spec can solve multiple problems
4. **Maintain roadmap** - Keep ROADMAP.md current
5. **Set expectations** - Be honest about timelines

---

## 🔗 Integration Points

**Integrates with:**
- `/planning:plan-generate` - Generate specs from issues
- `/planning:tasks` - Generate tasks from specs
- `/iterate:tasks` - Layer tasks for parallel work
- `/supervisor:start` - Verify agent readiness
- `/deployment:prod-ready` - Check before release

**Upstream:** User issues, PR reviews from Claude Code
**Downstream:** Specs, tasks, agent assignments, releases

---

## 📈 Metrics

Track effectiveness with:
- Issue response time (target: < 48 hours)
- Issue-to-spec conversion rate
- PR feedback implementation rate
- Time from issue to deployed fix

---

## 🛠️ Troubleshooting

### PR Review

**Error: "gh not found"**
```bash
# Install GitHub CLI
# macOS: brew install gh
# Ubuntu: sudo apt install gh
# Windows: winget install GitHub.cli

# Authenticate
gh auth login
```

**Error: "Cannot access PR #123"**
- Verify PR number exists
- Check you have read access to repository
- Ensure gh CLI is authenticated

### Issue Review

**Error: "Permission denied"**
- You need write access to create specs
- Verify you're in the multiagent-core repository
- Check gh authentication: `gh auth status`

**No issues found**
- Check you're in correct repository
- Verify issue state (open vs closed)
- Try without label filter

---

## 📝 Development

### Adding New Issue Categories

Edit `.claude/agents/issue-reviewer.md` to add new category:

```markdown
6. **Performance** ⚡
   - Keywords: "slow", "lag", "memory", "cpu"
   - Priority: High
   - Action: Profile and optimize
```

### Adding New PR Patterns

Edit `.multiagent/github/pr-review/templates/` to add new templates.

---

## 🎯 Success Criteria

**PR Review Success:**
- ✅ All PR feedback addressed within 48 hours
- ✅ Security issues fixed immediately
- ✅ Tasks tracked in spec directories
- ✅ PR approved and merged

**Issue Review Success:**
- ✅ All issues categorized and prioritized
- ✅ High-priority issues have specs
- ✅ Incomplete issues have info requests
- ✅ Users feel heard and informed
- ✅ Roadmap reflects community needs

---

**Remember**: GitHub subsystem bridges users and development - make every interaction count!
