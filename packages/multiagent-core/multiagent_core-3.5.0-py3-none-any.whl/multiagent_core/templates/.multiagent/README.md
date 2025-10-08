# MultiAgent Framework

Welcome to MultiAgent - the intelligent development framework that orchestrates multiple AI assistants to work together on your projects through specialized subsystems.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Subsystem Overview](#subsystem-overview)
- [Complete Directory Structure](#complete-directory-structure)
- [Installation](#installation)
- [Complete Workflow](#complete-workflow)
- [Command Reference](#command-reference)
- [Template Organization](#template-organization)
- [Advanced Usage](#advanced-usage)

## Prerequisites

### Install Spec-Kit First (REQUIRED)

MultiAgent works with spec-kit to provide specification-driven development. Install spec-kit first:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install spec-kit persistently (recommended)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Verify installation
specify check
```

Requirements:
- Linux/macOS (or WSL2 on Windows)
- Python 3.11+
- Git

## Subsystem Overview

MultiAgent has 8 specialized subsystems that work together. Each subsystem owns its complete setup including templates, scripts, workflows, and documentation.

### Subsystem Architecture

| Subsystem | Purpose | Owns | Outputs To |
|-----------|---------|------|------------|
| **Core** | Master orchestrator | Setup scripts, hooks | `.git/hooks/`, project config |
| **Security** | Security enforcement | Hooks, secret scanning, SECURITY.md | `.git/hooks/`, `docs/`, `.github/workflows/` |
| **Deployment** | Platform configs | Docker, K8s, deploy.yml | `deployment/`, `.github/workflows/` |
| **Testing** | Test generation | Test templates, ci.yml | `tests/`, `.github/workflows/` |
| **Documentation** | Doc generation | Doc templates, ARCHITECTURE.md | `docs/` |
| **Iterate** | Task organization | Task layering logic | `specs/*/agent-tasks/` |
| **PR Review** | PR analysis | Judge templates, feedback | `specs/*/feedback/` |
| **Supervisor** | Agent monitoring | Compliance rules | Validation reports |

### Subsystem Slash Commands

| Command | Subsystem | Phase | Description |
|---------|-----------|-------|-------------|
| `/core:project-setup [spec]` | Core | 3 | Orchestrates complete project setup |
| `/security:setup` | Security | 3 | Security infrastructure (auto via core) |
| `/deployment:deploy-prepare [spec]` | Deployment | 3 | Generate deployment configs |
| `/deployment:deploy-validate` | Deployment | 3,5 | Validate deployment readiness |
| `/deployment:deploy-run [up\|down\|logs]` | Deployment | 3,5 | Local Docker deployment |
| `/deployment:deploy [env] [--platform]` | Deployment | 5 | Cloud deployment |
| `/deployment:prod-ready [--fix]` | Deployment | 5 | Production readiness scan |
| `/testing:test [--quick\|--create]` | Testing | 3-5 | Run or create tests |
| `/testing:test-generate [spec]` | Testing | 3 | Generate test structure |
| `/testing:test-prod [--fix]` | Testing | 5 | Production test validation |
| `/docs:init [--project-type]` | Documentation | 3 | Initialize documentation |
| `/docs:update [--check-patterns]` | Documentation | 4-5 | Update existing docs |
| `/docs:validate [--strict]` | Documentation | 5 | Validate doc consistency |
| `/iterate:tasks [spec]` | Iterate | 3 | Layer tasks for parallel work |
| `/iterate:sync [spec]` | Iterate | 4 | Sync spec ecosystem |
| `/iterate:adjust [spec]` | Iterate | 4 | Live development adjustments |
| `/github:pr-review [PR#]` | PR Review | 4.5 | Analyze PR review feedback |
| `/github:create-issue [--type]` | PR Review | 4.5 | Create GitHub issues |
| `/github:discussions [topic]` | PR Review | 4.5 | Manage GitHub Discussions |
| `/supervisor:start [spec]` | Supervisor | 3.5 | Pre-work setup verification |
| `/supervisor:mid [spec]` | Supervisor | 4 | Mid-work progress check |
| `/supervisor:end [spec]` | Supervisor | 4.5 | Pre-PR completion check |

## Complete Directory Structure

**Note**: Archived scripts are located in the root-level `.archive/` directory, organized as:
- `.archive/multiagent-core/` - Core infrastructure scripts
- `.archive/multiagent-deployment/` - Deployment & security scripts
- `.archive/multiagent-iterate/` - Task layering scripts
- `.archive/multiagent-pr-review/` - PR feedback scripts
- `.archive/multiagent-testing/` - Test generation scripts

See `.archive/README.md` and `.archive/multiagent-scripts-README.md` for details.

```
.multiagent/
│
├── agents/                         # Agent Coordination & Workflows
│   ├── docs/                       # Agent workflow documentation
│   │   ├── GIT_WORKTREE_GUIDE.md
│   │   ├── AGENT_BRANCH_PROTOCOL.md
│   │   ├── AGENT_COORDINATION_GUIDE.md
│   │   ├── COMMIT_PR_WORKFLOW.md
│   │   ├── GIT_HOOKS_SYSTEM.md
│   │   └── WORKTREE_BRANCHING_ARCHITECTURE.md
│   ├── templates/                  # Agent behavior templates
│   │   ├── CLAUDE.md               # Claude agent instructions
│   │   ├── GEMINI.md               # Gemini agent instructions
│   │   ├── QWEN.md                 # Qwen agent instructions
│   │   ├── AGENTS.md               # General agent workflow
│   │   └── agent-responsibilities.yaml
│   ├── prompts/                    # User prompt templates
│   │   └── README.md
│   └── hooks/                      # Agent workflow hooks
│       └── post-commit             # Agent @tag guidance
│
├── core/                           # Phase 3: Project Setup Orchestrator
│   ├── docs/
│   │   ├── TASK_LAYERING_PRINCIPLES.md
│   │   └── README.md
│   ├── logs/                       # Execution logs
│   ├── scripts/
│   │   ├── generation/             # Workflow generation scripts
│   │   ├── setup/                  # Project setup automation
│   │   └── validation/             # Configuration validation
│   └── README.md                   # Core subsystem documentation
│
├── deployment/                     # Phase 3, 5: Deployment Configuration
│   ├── docs/
│   │   ├── troubleshooting/       # Deployment troubleshooting
│   │   └── workflows/             # Deployment workflow docs
│   ├── logs/                      # Deployment execution logs
│   ├── memory/                    # Session state tracking (JSON)
│   ├── scripts/
│   │   ├── generate-deployment.sh
│   │   ├── validate-deployment.sh
│   │   └── scan-mocks.sh
│   ├── templates/
│   │   ├── docker/                # Dockerfile templates
│   │   ├── compose/               # docker-compose templates
│   │   ├── k8s/                   # Kubernetes manifests
│   │   ├── nginx/                 # Nginx configurations
│   │   ├── env/                   # Environment file templates
│   │   └── workflows/             # ✨ deploy.yml.template
│   └── README.md
│
├── documentation/                  # Phase 3-5: Documentation Generation
│   ├── docs/                      # Subsystem documentation
│   ├── logs/                      # Doc generation logs
│   ├── memory/                    # State tracking (JSON)
│   │   ├── template-status.json
│   │   ├── doc-registry.json
│   │   ├── consistency-check.json
│   │   └── update-history.json
│   ├── scripts/
│   │   ├── create-structure.sh    # Initialize doc structure
│   │   ├── update-docs.sh
│   │   └── validate-docs.sh
│   ├── templates/                 # ✨ Documentation Templates
│   │   ├── ARCHITECTURE.md        # Architecture documentation
│   │   ├── DESIGN_SYSTEM.md       # Design system (frontend)
│   │   ├── README.template.md     # Project README
│   │   ├── CHANGELOG.md           # Version history
│   │   ├── CONTRIBUTING.md        # Contribution guide
│   │   └── TROUBLESHOOTING.md     # Troubleshooting guide
│   └── README.md
│
├── iterate/                        # Phase 3-4: Task Organization
│   ├── logs/                      # Task layering logs
│   ├── memory/                    # Task state (JSON)
│   ├── scripts/
│   │   ├── layer-tasks.sh         # Transform sequential → layered
│   │   ├── sync-ecosystem.sh      # Sync spec updates
│   │   ├── adjust-live.sh         # Live development adjustments
│   │   └── setup-spec-worktrees.sh # Automated worktree setup
│   ├── templates/
│   │   ├── layered-tasks.md.template
│   │   └── task-assignment.md.template
│   └── README.md
│
├── pr-review/                      # Phase 4.5: PR Analysis & Feedback
│   ├── logs/                      # PR review execution logs
│   │   └── pr-[number]-[timestamp]/
│   ├── memory/                    # Review state tracking
│   ├── scripts/
│   │   ├── approval/              # Human approval workflows
│   │   ├── github/                # GitHub API integration
│   │   └── tasks/                 # Task generation from reviews
│   ├── sessions/                  # ⚠️ DEPRECATED (outputs to specs/)
│   ├── templates/
│   │   ├── judge-output-review.md # Judge execution flow
│   │   ├── review-tasks.md.template
│   │   ├── judge-summary.md.template
│   │   └── future-enhancements.md.template
│   └── README.md
│
├── security/                       # Phase 3, 4.5, 5: Security Enforcement
│   ├── docs/                      # Security documentation
│   ├── hooks/                      # Security git hooks
│   │   └── pre-push                # Secret scanning before push
│   ├── scripts/
│   │   ├── generate-github-workflows.sh
│   │   ├── scan-secrets.sh        # Secret detection
│   │   └── validate-compliance.sh # Security compliance
│   ├── templates/
│   │   ├── configs/               # Security configurations
│   │   ├── docs/                  # ✨ Security Documentation
│   │   │   ├── SECURITY.md.template          # Security policy
│   │   │   ├── SECURITY_CHECKLIST.md.template
│   │   │   ├── INCIDENT_RESPONSE.md.template
│   │   │   └── SECRET_MANAGEMENT.md.template
│   │   ├── github-workflows/      # ✨ Security Workflows
│   │   │   ├── security-scan.yml.template
│   │   │   └── security-scanning.yml.template
│   │   └── reports/               # Security report templates
│   └── README.md
│
├── supervisor/                     # Phase 3.5-4.5: Agent Compliance
│   ├── logs/                      # Supervision logs
│   ├── memory/                    # Compliance rules (Markdown)
│   │   └── compliance-rules.md
│   ├── scripts/
│   │   ├── check-compliance.sh
│   │   ├── verify-setup.sh
│   │   └── validate-completion.sh
│   ├── templates/
│   │   ├── compliance-report.md.template
│   │   └── progress-report.md.template
│   └── README.md
│
└── testing/                        # Phase 3-5: Test Generation & Execution
    ├── docs/                      # Testing documentation
    ├── logs/                      # Test execution logs
    ├── memory/                    # Test state (JSON)
    ├── scripts/
    │   ├── generate-tests.sh      # Test file generation
    │   └── run-tests.sh
    ├── templates/
    │   ├── workflows/             # ✨ Testing Workflows
    │   │   └── ci.yml.template    # CI/test workflow
    │   ├── backend_template.test.py
    │   ├── frontend_template.test.js
    │   ├── e2e_template.test.js
    │   ├── integration_template.test.js
    │   ├── unit_template.test.js
    │   └── contract_template.test.yaml
    └── README.md
```

## Template Organization

### Subsystem Template Ownership

Each subsystem owns its complete template set and knows where outputs go:

#### 🔐 Security Subsystem Templates
**Owns:** Security-related documentation and workflows
**Template Location:** `.multiagent/security/templates/`
**Outputs To:** `docs/SECURITY.md`, `.github/workflows/security-*.yml`

```
security/templates/
├── docs/
│   ├── SECURITY.md.template              # Created by docs-init agent
│   ├── SECURITY_CHECKLIST.md.template    # Internal checklist
│   ├── INCIDENT_RESPONSE.md.template
│   └── SECRET_MANAGEMENT.md.template
└── github-workflows/
    ├── security-scan.yml.template
    └── security-scanning.yml.template
```

#### 🚀 Deployment Subsystem Templates
**Owns:** Deployment configs and workflows
**Template Location:** `.multiagent/deployment/templates/`
**Outputs To:** `deployment/`, `.github/workflows/deploy.yml`

```
deployment/templates/
├── workflows/
│   └── deploy.yml.template               # Created by deployment-prep agent
├── docker/
├── compose/
├── k8s/
├── nginx/
└── env/
```

#### 🧪 Testing Subsystem Templates
**Owns:** Test templates and CI workflows
**Template Location:** `.multiagent/testing/templates/`
**Outputs To:** `tests/`, `.github/workflows/ci.yml`

```
testing/templates/
├── workflows/
│   └── ci.yml.template                   # Created by test-generator agent
├── backend_template.test.py
├── frontend_template.test.js
├── e2e_template.test.js
├── integration_template.test.js
├── unit_template.test.js
└── contract_template.test.yaml
```

#### 📚 Documentation Subsystem Templates
**Owns:** General documentation templates
**Template Location:** `.multiagent/documentation/templates/`
**Outputs To:** `docs/`

```
documentation/templates/
├── ARCHITECTURE.md                       # Created by docs-init agent
├── DESIGN_SYSTEM.md                      # Created by docs-init (frontend)
├── README.template.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── TROUBLESHOOTING.md
```

### Agent-Template Relationships

| Agent | Reads Templates From | Writes Output To | Purpose |
|-------|---------------------|------------------|---------|
| **docs-init** | `.multiagent/documentation/templates/` AND `.multiagent/security/templates/docs/` | `docs/` | Creates all project documentation |
| **deployment-prep** | `.multiagent/deployment/templates/` | `deployment/`, `.github/workflows/` | Generates deployment configs and workflows |
| **test-generator** | `.multiagent/testing/templates/` | `tests/`, `.github/workflows/` | Creates tests and CI workflows |
| **judge-architect** | `.multiagent/pr-review/templates/` | `specs/*/feedback/` | PR review analysis |

### Cross-Subsystem Template Usage

**Documentation agent reads security templates:**
```
docs-init agent:
  1. Read .multiagent/documentation/templates/ARCHITECTURE.md
  2. Read .multiagent/security/templates/docs/SECURITY.md.template
  3. Fill both with project-specific content
  4. Write docs/ARCHITECTURE.md and docs/SECURITY.md
```

This follows the pattern: **Security owns the template content, Documentation owns the file placement.**

## Installation

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

## Complete Workflow

### Phase 1-2: Specify (Spec-Kit) - Create Specifications

```bash
# 1. Initialize project with SpecKit
specify init --here --ai claude

# 2. Create feature specification
/specify                # Creates specs/001-feature-name/spec.md

# 3. Create technical plan
/plan                   # Creates plan.md, data-model.md

# 4. Generate sequential tasks
/tasks                  # Creates tasks.md

# ✓ Spec directory ready: specs/001-feature-name/
```

### Phase 2.5: MultiAgent Init - Deploy Infrastructure

```bash
# 5. Deploy MultiAgent framework
multiagent init

# ✓ Framework deployed:
#   - .multiagent/ (8 subsystems)
#   - .claude/ (agent configs)
#   - .github/ (workflows, templates)
#   - .vscode/ (editor settings)
```

### Phase 3: Project Setup - Configure for Development

**Run these commands in order:**

```bash
# 6. Initialize documentation
/docs:init
# → Creates docs/ structure
# → Fills templates from specs
# → Reads security/SECURITY.md.template

# 7. Generate deployment configs
/deployment:deploy-prepare 001
# → Analyzes spec for deployment target
# → Generates Docker, K8s configs
# → Creates .github/workflows/deploy.yml from template

# 8. Generate test structure
/testing:test-generate 001
# → Creates tests/ directory
# → Generates test files from tasks
# → Creates .github/workflows/ci.yml from template

# 9. Layer tasks for parallel work
/iterate:tasks 001
# → Transforms sequential tasks.md
# → Creates agent-tasks/layered-tasks.md
# → Organizes by: Models → Infrastructure → Adapters → Wrappers → Integration
# → Assigns tasks to agents

# ✓ Project fully configured
```

### Phase 3.5: Worktree Setup - Automated Agent Environments

```bash
# 10. Set up agent worktrees automatically
.multiagent/iterate/scripts/setup-spec-worktrees.sh 001-feature-name

# ✓ Creates worktrees ONLY for agents with assigned tasks:
#   ../project-claude (agent-claude-001)
#   ../project-codex (agent-codex-001)
#   ../project-qwen (agent-qwen-001)
#   etc.
```

### Phase 4: Development - Agents Work in Parallel

Agents work in isolated worktrees on their assigned tasks:

```bash
# Each agent:
git worktree list                              # Find their worktree
cd ../project-[agent]                          # Navigate to worktree
grep "@[agent]" specs/.../layered-tasks.md    # View tasks
# Implement, commit, push
gh pr create                                   # Create PR when done

# Optional during development:
/docs:update              # Update docs as code changes
/testing:test --quick     # Run tests
/supervisor:mid 001       # Check progress
```

### Phase 4.5: PR Review & Judge Evaluation

```bash
# 11. Agent creates PR from worktree
gh pr create

# 12. Run judge evaluation
/github:pr-review [PR-number]
# → Invokes judge-architect subagent
# → Analyzes PR against specs
# → Creates feedback in specs/*/feedback/
# → Outputs:
#   - judge-summary.md (APPROVE/DEFER/REJECT)
#   - tasks.md (actionable items)
#   - future-enhancements.md
#   - plan.md

# 13. Human decision:
# If APPROVED → gh pr merge [PR-number]
# If CHANGES NEEDED → implement tasks.md, push updates
```

### Phase 5: Pre-Deployment - Production Readiness

```bash
# 14. Validate production readiness
/testing:test-prod --fix
# → Checks for mocks in production code
# → Validates production config

# 15. Comprehensive production scan
/deployment:prod-ready --verbose
# → Security checks
# → Environment validation
# → Dependency audits

# 16. Deploy to preview
/deployment:deploy preview

# 17. Deploy to production
/deployment:deploy production

# ✓ Live in production
```

## Command Reference

See [Subsystem Slash Commands](#subsystem-slash-commands) table above for complete command reference.

### Key Principles

1. **Subsystem Ownership**: Each subsystem owns its complete setup (templates, workflows, scripts, docs)
2. **Template Organization**: Templates live in subsystems, outputs go to standard locations
3. **Cross-Subsystem Reading**: Agents can read templates from other subsystems (e.g., docs-init reads security templates)
4. **Idempotent Commands**: Commands check what exists before creating
5. **Spec-Driven**: All commands read from SpecKit specs

## Advanced Usage

### Custom Templates

Add project-specific templates:

```bash
# Add custom deployment template
mkdir -p .multiagent/deployment/templates/custom
cp my-template.yml .multiagent/deployment/templates/custom/

# Reference in deployment configs
```

### Workflow Automation

Each subsystem has automation scripts in `scripts/` directory.

### Agent Configuration

Configure agents in `.claude/agents/`:
- Agent behavior and specializations
- Tool permissions
- Subagent relationships

## Troubleshooting

### Command Not Found

```bash
# For pipx installation
python3 -m pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# For pip installation
export PATH="$PATH:$HOME/.local/bin"
```

### Missing Templates

If templates are missing, check subsystem README for template locations:

```bash
# Check what each subsystem has
cat .multiagent/security/README.md
cat .multiagent/deployment/README.md
cat .multiagent/testing/README.md
cat .multiagent/documentation/README.md
```

## Getting Help

- **Documentation**: https://github.com/vanman2024/multiagent-core
- **Issues**: https://github.com/vanman2024/multiagent-core/issues
- **Discord**: [Join our community](https://discord.gg/multiagent)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/vanman2024/multiagent-core/blob/main/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](https://github.com/vanman2024/multiagent-core/blob/main/LICENSE).

---

🤖 **Powered by MultiAgent Framework**
Version: `multiagent --version`
