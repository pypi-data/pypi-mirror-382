# MultiAgent Framework

**Intelligent development framework orchestrating specialized AI subagents through slash commands.**

## 🏗️ Architecture: How The Layers Work Together

### The 3-Layer Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: USER & MAIN AGENT (@claude, @qwen, etc.)              │
│ - User provides high-level goals                                │
│ - Main agent plans and coordinates                              │
│ - Executes slash commands to invoke subagents                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: SLASH COMMANDS (Subsystem Orchestrators)              │
│ /docs:init          → Spawns docs-init subagent                │
│ /testing:test       → Spawns backend-tester subagent           │
│ /deployment:prepare → Spawns deployment-prep subagent          │
│ /github:pr-review   → Spawns judge-architect subagent          │
│ /iterate:tasks      → Spawns task-layering subagent            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: SUBAGENTS (Specialized Workers)                       │
│ - docs-init: Reads templates, fills content, writes docs       │
│ - deployment-prep: Analyzes specs, generates configs           │
│ - backend-tester: Writes tests, validates APIs                 │
│ - judge-architect: Reviews PRs, generates feedback             │
│ - test-generator: Creates test structure from tasks            │
│                                                                 │
│ Subagents use subsystem resources:                             │
│ - .multiagent/{subsystem}/templates/                           │
│ - .multiagent/{subsystem}/scripts/                             │
│ - .multiagent/{subsystem}/docs/                                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principle: Subagents Handle Complexity

**Old Pattern (Deprecated):**
```bash
# Scripts did the work directly
.multiagent/deployment/scripts/generate-deployment.sh
```

**New Pattern (Current):**
```bash
# Main agent runs slash command
/deployment:deploy-prepare 001

# Slash command spawns subagent
→ deployment-prep subagent activated

# Subagent handles complexity
→ Reads .multiagent/deployment/templates/
→ Analyzes specs/001-*/spec.md
→ Generates deployment configs
→ Creates .github/workflows/deploy.yml
→ May call scripts as utilities
```

**Why This Works:**
- Main agent stays focused on coordination
- Subagents have specialized knowledge
- Slash commands provide consistent interface
- Scripts become utilities, not primary logic

## 📋 The 4 Development Phases

MultiAgent organizes work into clear phases, each with specific commands and subagents.

### Phase 1-2: SETUP (Spec Creation)

**Who:** User + Main Agent + Spec-Kit
**Output:** Specification documents

```bash
# 1. Initialize project with SpecKit
specify init --here --ai claude

# 2. Create feature specification
/specify                    # → specs/001-feature-name/spec.md

# 3. Create technical plan
/plan                       # → plan.md, data-model.md

# 4. Generate sequential tasks
/tasks                      # → tasks.md

# ✓ Spec directory ready for MultiAgent
```

### Phase 3: PROJECT SETUP (Infrastructure Deployment)

**Who:** Main Agent + Setup Subagents
**Output:** Project infrastructure and initial configs

#### Step 1: Deploy Framework
```bash
multiagent init
# ✓ Deploys .multiagent/, .claude/, .github/, .vscode/
```

#### Step 2: Initialize Documentation
```bash
/docs:init [--project-type <type>]

# Spawns: docs-init subagent
# Reads templates from:
#   - .multiagent/documentation/templates/
#   - .multiagent/security/templates/docs/
# Writes to: docs/
# Creates: ARCHITECTURE.md, SECURITY.md, README.md, etc.
```

#### Step 3: Generate Deployment Configs
```bash
/deployment:deploy-prepare 001

# Spawns: deployment-prep subagent
# Reads templates from: .multiagent/deployment/templates/
# Analyzes: specs/001-*/spec.md, plan.md
# Writes to: deployment/, .github/workflows/deploy.yml
# Creates: Dockerfile, docker-compose.yml, k8s manifests
```

#### Step 4: Generate Test Structure
```bash
/testing:test-generate 001

# Spawns: test-generator subagent
# Reads templates from: .multiagent/testing/templates/
# Analyzes: specs/001-*/tasks.md
# Writes to: tests/, .github/workflows/ci.yml
# Creates: Test files organized by task complexity
```

#### Step 5: Layer Tasks for Parallel Work
```bash
/iterate:tasks 001

# Spawns: task-layering subagent
# Reads: specs/001-*/tasks.md
# Analyzes: Dependencies, complexity, agent skills
# Writes to: specs/001-*/agent-tasks/layered-tasks.md
# Organizes: Foundation → Implementation → Testing layers
# Assigns: Tasks to specific agents (@claude, @qwen, etc.)
```

#### Step 6: Setup Agent Worktrees (Optional)
```bash
.multiagent/iterate/scripts/setup-spec-worktrees.sh 001

# Creates isolated worktrees for each assigned agent
# ✓ ../project-claude (agent-claude-001)
# ✓ ../project-codex (agent-codex-001)
# ✓ ../project-qwen (agent-qwen-001)
```

**✓ Project Setup Complete** - Ready for development

---

### Phase 4: DEVELOPMENT (Feature Implementation)

**Who:** Multiple Agents Working in Parallel
**Output:** Feature implementation in isolated branches

#### Continuous Development Commands

```bash
# Update documentation as code evolves
/docs:update [--check-patterns]
# Spawns: docs-update subagent
# Detects code changes and updates docs in-place

# Run tests during development
/testing:test [--quick|--create|--backend|--frontend]
# Spawns: backend-tester or frontend-playwright-tester subagent
# Intelligently routes to correct test framework

# Sync spec ecosystem after changes
/iterate:sync 001
# Spawns: ecosystem-sync subagent
# Propagates spec changes to related files

# Adjust tasks during development
/iterate:adjust 001
# Spawns: live-adjust subagent
# Updates task assignments based on progress
```

#### Agent Workflow in Development
```bash
# Each agent in their worktree:
1. cd ../project-[agent]
2. grep "@[agent]" specs/001-*/agent-tasks/layered-tasks.md
3. Implement assigned tasks
4. Commit work regularly
5. Push to branch when complete
6. Create PR
```

#### Progress Monitoring
```bash
# Check mid-development compliance
/supervisor:mid 001

# Spawns: supervisor-mid subagent
# Validates: Task completion, code quality, standards
# Reports: Progress, blockers, recommendations
```

**✓ Development Phase** - Agents work in parallel, main agent coordinates

---

### Phase 4.5: PR REVIEW & FEEDBACK (Quality Gates)

**Who:** Main Agent + Judge Subagent
**Output:** PR analysis, feedback tasks, approval decisions

```bash
# 1. Agent creates PR from worktree
gh pr create --title "feat: implement auth system"

# 2. Analyze PR review feedback
/github:pr-review 123

# Spawns: judge-architect subagent
# Reads: GitHub PR #123 review comments
# Analyzes: Against specs/001-*/spec.md requirements
# Writes to: specs/001-*/feedback/
# Creates:
#   - judge-summary.md (APPROVE/DEFER/REJECT decision)
#   - tasks.md (actionable feedback items)
#   - future-enhancements.md
#   - plan.md (if architecture changes needed)

# 3. Create GitHub issues from feedback
/github:create-issue --feature "title"

# Spawns: github-issue subagent
# Creates properly formatted issues with templates

# 4. Pre-PR completion check
/supervisor:end 001

# Spawns: supervisor-end subagent
# Validates: All tasks complete, tests pass, ready for merge
# Blocks: If requirements not met
```

**Human Decision Point:**
- **APPROVE** → `gh pr merge 123`
- **DEFER** → Implement feedback tasks, iterate
- **REJECT** → Major changes needed, create new tasks

**✓ PR Review Complete** - Quality gates passed

---

### Phase 5: DEPLOYMENT (Production Readiness & Launch)

**Who:** Main Agent + Production Subagents
**Output:** Validated, secure, production-ready deployment

#### Pre-Deployment Validation

```bash
# 1. Validate production test coverage
/testing:test-prod [--fix] [--verbose]

# Spawns: production-test-validator subagent
# Scans: All code for remaining mocks
# Validates: Production APIs configured
# Reports: Mock locations, replacement suggestions
# Optionally: Auto-generates production replacements

# 2. Comprehensive production readiness scan
/deployment:prod-ready [--fix] [--verbose]

# Spawns: production-specialist subagent
# Checks:
#   - Security vulnerabilities (secrets, dependencies)
#   - Environment variables configured
#   - Production configs valid
#   - Build processes work
#   - Health checks pass
# Generates: Detailed readiness report
# Optionally: Auto-fixes common issues

# 3. Validate deployment configuration
/deployment:deploy-validate

# Spawns: deployment-validator subagent
# Validates:
#   - Dockerfile syntax
#   - docker-compose configuration
#   - Environment files complete
#   - K8s manifests valid
# Reports: Configuration issues

# 4. Validate documentation completeness
/docs:validate [--strict]

# Spawns: docs-validator subagent
# Checks:
#   - All placeholders filled
#   - Cross-document consistency
#   - Required sections present
# Reports: Documentation gaps
```

#### Local Deployment Testing

```bash
# 5. Test deployment locally
/deployment:deploy-run up

# Spawns: deployment-runner subagent
# Actions:
#   - Builds Docker images
#   - Starts containers via docker-compose
#   - Runs health checks
#   - Validates services running
# Commands: up, down, restart, logs, status

# Check deployment logs
/deployment:deploy-run logs

# Stop local deployment
/deployment:deploy-run down
```

#### Cloud Deployment

```bash
# 6. Deploy to preview environment
/deployment:deploy preview [--platform=vercel|aws|railway]

# Spawns: cloud-deployer subagent
# Actions:
#   - Builds production bundle
#   - Configures platform
#   - Deploys to preview URL
#   - Runs smoke tests
# Reports: Preview URL, deployment status

# 7. Deploy to production
/deployment:deploy production [--platform=vercel|aws|railway]

# Spawns: cloud-deployer subagent
# Requires: All validation checks passed
# Actions:
#   - Final security scan
#   - Production build
#   - Deploy to production
#   - Run health checks
#   - Monitor initial metrics
# Reports: Production URL, deployment summary
```

**✓ Deployment Complete** - Live in production

---

### Phase 6: END (Cleanup & Maintenance)

**Who:** Main Agent + Cleanup Utilities
**Output:** Clean workspace, archived work

```bash
# After PR merge - Clean up worktrees
cd /path/to/main/project
git checkout main && git pull

# Remove agent worktrees
git worktree remove ../project-claude
git worktree remove ../project-codex
git worktree remove ../project-qwen

# Delete branches
git branch -d agent-claude-001
git branch -d agent-codex-001
git branch -d agent-qwen-001

# Verify cleanup
git worktree list  # Should show only main project

# Continue monitoring
/deployment:prod-ready  # Periodic production health checks
/docs:update            # Keep docs current with code changes
```

**✓ Cycle Complete** - Ready for next feature

---

## 🎯 Subsystem Overview

MultiAgent has 8 specialized subsystems. Each owns its templates, scripts, and documentation.

| Subsystem | Subagents | Primary Commands | Templates Location |
|-----------|-----------|------------------|-------------------|
| **Agents** | N/A | Coordination infrastructure | `.multiagent/agents/templates/` |
| **Core** | project-setup orchestrator | `/core:project-setup` | `.multiagent/core/` |
| **Deployment** | deployment-prep, deployment-validator, deployment-runner, production-specialist | `/deployment:*` | `.multiagent/deployment/templates/` |
| **Documentation** | docs-init, docs-update, docs-validator | `/docs:*` | `.multiagent/documentation/templates/` |
| **Testing** | test-generator, backend-tester, frontend-tester | `/testing:*` | `.multiagent/testing/templates/` |
| **Iterate** | task-layering, ecosystem-sync, live-adjust | `/iterate:*` | `.multiagent/iterate/templates/` |
| **PR Review** | judge-architect, github-integration | `/github:*` | `.multiagent/github/pr-review/templates/` |
| **Security** | security-scanner, compliance-checker | Auto-runs via hooks | `.multiagent/security/templates/` |
| **Supervisor** | supervisor-start, supervisor-mid, supervisor-end | `/supervisor:*` | `.multiagent/supervisor/templates/` |

## 📚 Complete Directory Structure

```
.multiagent/
│
├── agents/                         # Agent Coordination Infrastructure
│   ├── docs/                       # Agent workflow guides
│   ├── templates/                  # Agent behavior templates (CLAUDE.md, etc.)
│   ├── prompts/                    # User prompt templates
│   └── hooks/                      # Git hooks (post-commit guidance)
│
├── core/                           # Project Setup Orchestrator
│   ├── scripts/                    # Setup automation utilities
│   └── docs/                       # Setup documentation
│
├── deployment/                     # Deployment Configuration
│   ├── templates/                  # Dockerfile, K8s, compose templates
│   │   └── workflows/             # deploy.yml.template
│   ├── scripts/                   # Deployment utilities
│   └── logs/                      # Deployment execution logs
│
├── documentation/                  # Documentation Generation
│   ├── templates/                  # ARCHITECTURE.md, README.md templates
│   ├── scripts/                   # Doc generation utilities
│   └── memory/                    # Doc state tracking
│
├── iterate/                        # Task Organization
│   ├── templates/                  # layered-tasks.md.template
│   ├── scripts/                   # Task layering utilities
│   └── logs/                      # Task layering logs
│
├── pr-review/                      # PR Analysis & Feedback
│   ├── templates/                  # judge-output-review.md templates
│   ├── scripts/                   # GitHub API integration
│   └── logs/                      # PR review logs
│
├── security/                       # Security Enforcement
│   ├── templates/
│   │   ├── docs/                  # SECURITY.md.template
│   │   └── github-workflows/     # security-scan.yml.template
│   ├── hooks/                     # pre-push (secret scanning)
│   └── scripts/                   # Security utilities
│
├── supervisor/                     # Agent Compliance Monitoring
│   ├── templates/                  # compliance-report.md.template
│   ├── scripts/                   # Compliance validation
│   └── memory/                    # Compliance rules
│
└── testing/                        # Test Generation & Execution
    ├── templates/                  # Test file templates
    │   └── workflows/             # ci.yml.template
    ├── scripts/                   # Test generation utilities
    └── logs/                      # Test execution logs
```

## 🔧 Installation

### Quick Start (Recommended: pipx)

```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install MultiAgent Core
pipx install multiagent-core

# Verify installation
multiagent --version
```

### Alternative: pip Installation

```bash
# Global installation (may require sudo)
pip install multiagent-core

# Or user installation
pip install --user multiagent-core
```

## 🚀 Quick Start Guide

### Full Workflow Example

```bash
# PHASE 1-2: SETUP (Spec Creation)
specify init --here --ai claude
/specify                              # Create spec
/plan                                 # Create plan
/tasks                                # Generate tasks

# PHASE 3: PROJECT SETUP
multiagent init                       # Deploy framework
/docs:init                            # Initialize docs
/deployment:deploy-prepare 001        # Generate deployment
/testing:test-generate 001            # Generate tests
/iterate:tasks 001                    # Layer tasks

# PHASE 4: DEVELOPMENT
# Agents work in parallel on assigned tasks
/testing:test --quick                 # Run tests during dev
/docs:update                          # Update docs as code changes
/supervisor:mid 001                   # Check progress

# PHASE 4.5: PR REVIEW
gh pr create                          # Create PR
/github:pr-review 123                 # Analyze feedback
/supervisor:end 001                   # Pre-merge validation

# PHASE 5: DEPLOYMENT
/testing:test-prod                    # Validate production tests
/deployment:prod-ready                # Comprehensive checks
/deployment:deploy-run up             # Test locally
/deployment:deploy preview            # Deploy to preview
/deployment:deploy production         # Deploy to prod

# PHASE 6: END (Cleanup)
git worktree remove ../project-*      # Clean up worktrees
```

## 🎓 Key Concepts

### 1. Slash Commands Spawn Subagents
Slash commands don't run scripts directly - they spawn specialized subagents:
```
/docs:init → docs-init subagent → reads templates → writes docs
```

### 2. Subagents Handle Complexity
Subagents have specialized knowledge and use subsystem resources:
- Read templates from `.multiagent/{subsystem}/templates/`
- May call utility scripts from `.multiagent/{subsystem}/scripts/`
- Write output to project locations (`docs/`, `tests/`, etc.)

### 3. Layered Task Organization
Tasks are organized by dependency layers, not sequence:
- **Foundation** - Database models, core infrastructure
- **Implementation** - Business logic, adapters
- **Testing** - Test suites, validation

### 4. Parallel Agent Workflows
Multiple agents work simultaneously in isolated worktrees:
- No merge conflicts
- Independent progress
- Coordinated integration via PRs

### 5. Phase-Based Development
Commands are organized by development phase:
- **Setup** - Infrastructure deployment
- **Development** - Feature implementation
- **PR Review** - Quality gates
- **Deployment** - Production launch
- **End** - Cleanup and maintenance

## 🔍 Common Workflows

### Workflow: Adding a New Feature

```bash
# 1. Create spec (Spec-Kit)
/specify
/plan
/tasks

# 2. Setup infrastructure (MultiAgent)
/iterate:tasks 001
/testing:test-generate 001
/deployment:deploy-prepare 001

# 3. Implement (Agents)
# Agents work in parallel on layered tasks

# 4. Review & merge (Judge)
/github:pr-review 123
gh pr merge 123

# 5. Deploy (Production)
/deployment:prod-ready
/deployment:deploy production
```

### Workflow: Updating Documentation

```bash
# Initial setup
/docs:init

# During development
/docs:update            # After code changes

# Before release
/docs:validate --strict # Ensure completeness
```

### Workflow: Testing Strategy

```bash
# Generate test structure
/testing:test-generate 001

# During development
/testing:test --quick         # Fast feedback
/testing:test --backend       # API tests
/testing:test --frontend      # UI tests

# Before production
/testing:test-prod --verbose  # Validate prod readiness
```

## 📖 Additional Resources

- **Agent Workflows**: `.multiagent/agents/docs/`
- **Subsystem Documentation**: Each subsystem has `README.md`
- **Archived Scripts**: `.archive/` (root level)

## 🐛 Troubleshooting

### Command Not Found

```bash
# For pipx installation
python3 -m pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# For pip installation
export PATH="$PATH:$HOME/.local/bin"
```

### Slash Command Errors

Check that spec exists:
```bash
ls -la specs/001-*/
```

Check that subsystem is deployed:
```bash
ls -la .multiagent/deployment/
ls -la .multiagent/testing/
```

### Subagent Not Activating

Verify agent configuration:
```bash
ls -la .claude/agents/
cat .claude/agents/backend-tester.md
```

## 📞 Getting Help

- **Documentation**: https://github.com/vanman2024/multiagent-core
- **Issues**: https://github.com/vanman2024/multiagent-core/issues

## 🤝 Contributing

See [DEVELOPMENT.md](../DEVELOPMENT.md) for contributor guide.

## 📄 License

MIT License - see [LICENSE](https://github.com/vanman2024/multiagent-core/blob/main/LICENSE).

---

🤖 **Powered by MultiAgent Framework**

Version: `multiagent --version`
