# MultiAgent Core: Local Storage & CLI Architecture

> **Understanding how multiagent-core stores data, manages projects, and provides global CLI access**

## Table of Contents
- [System-Wide Directories](#system-wide-directories)
- [Registered Projects](#registered-projects)
- [How Local Storage Works](#how-local-storage-works)
- [Per-Project Structure](#per-project-structure)
- [CLI Architecture](#cli-architecture)
- [Auto-Update System](#auto-update-system)
- [Future CLI Expansion](#future-cli-expansion)

---

## System-Wide Directories

### pipx Installation Structure

```
~/.local/
├── bin/
│   └── multiagent -> symlink to venv executable
└── share/pipx/venvs/multiagent-core/
    ├── bin/multiagent              # Entry point script
    └── lib/python3.12/site-packages/
        ├── __editable__.multiagent_core-3.2.0.pth  # Editable install pointer
        ├── __editable___multiagent_core_3_2_0_finder.py
        ├── multiagent_core/        # Package (or editable link)
        │   ├── cli.py             # Main CLI entry point
        │   ├── detector.py        # Project detection
        │   ├── analyzer.py        # Tech stack analysis
        │   ├── auto_updater.py    # Auto-update system
        │   └── templates/         # Packaged templates
        │       ├── .multiagent/
        │       ├── .claude/
        │       ├── .github/
        │       └── .vscode/
        └── multiagent_core-3.2.0.dist-info/
```

**Key Points:**
- `multiagent` command globally available in `~/.local/bin/`
- Editable install uses `.pth` file pointing to development source
- Changes to source code are **instant** (no rebuild needed)
- Templates stored in `multiagent_core/templates/`

### Project Tracking Database

```
~/.multiagent-core-deployments.json
```

**Structure:**
```json
{
  "projects": {
    "/home/user/Projects/my-backend-api": {
      "registered": "2025-10-02T14:27:58.431607",
      "last_updated": "2025-10-02T18:45:12.123456"
    },
    "/home/user/Projects/agentswarm": {
      "registered": "2025-09-23T10:07:38.899054",
      "last_updated": "2025-10-02T14:27:58.431607"
    }
  },
  "last_updated": "2025-10-02T14:27:58.431607"
}
```

**Purpose:**
- Tracks all initialized projects
- Auto-excludes `/tmp/` test projects (v3.2.0+)
- Enables automatic template updates across all projects
- Maintains update history per project

---

## Registered Projects

### Production Projects vs Test Projects

**Auto-Registration Rules (v3.2.0+):**
```python
# multiagent_core/auto_updater.py
def register_deployment(project_path):
    # Skip /tmp projects - they're temporary test projects
    if str(project_path).startswith('/tmp/'):
        print(f"[SKIP] Not registering temporary project")
        return

    # Register production projects
    data["projects"][project_str] = {
        "registered": datetime.now().isoformat(),
        "last_updated": None
    }
```

**Typical Registered Projects:**
1. Component projects (`agentswarm`, `devops`, `multiagent-testing`)
2. Client/production projects
3. Development instances
4. Local backend APIs

**NOT Registered:**
- `/tmp/test-*` projects (temporary testing)
- One-off experiments
- CI/CD test runs

---

## How Local Storage Works

### Initialization Flow

```
┌─────────────────────────────────────────────────────────┐
│ $ multiagent init /path/to/project                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 1. pipx finds: ~/.local/bin/multiagent                  │
│ 2. Runs: Python in isolated venv                        │
│ 3. Editable .pth points to: multiagent-core/src         │
│ 4. Loads templates from: multiagent_core/templates/     │
│ 5. Copies to: /path/to/project/.multiagent/             │
│ 6. Registers: ~/.multiagent-core-deployments.json       │
└─────────────────────────────────────────────────────────┘
```

### Editable Install Behavior

**Development Mode:**
```bash
cd /home/user/Projects/multiagent-core
pipx install -e . --force
```

**What Happens:**
1. Creates `.pth` file in pipx venv
2. Points to source directory (not dist packages)
3. Python imports directly from source
4. Template changes are **instant**
5. No rebuild needed for testing

**Template Sync:**
```python
# multiagent_core/_template_build.py
def _sync_for_build():
    """Copy template sources into package before build"""
    package_templates = _package_template_root()
    sync_templates(quiet=True, repo_root=_repo_root())

    # Syncs: .multiagent/, .claude/, .github/, .vscode/
    # From: repo root
    # To: multiagent_core/templates/
```

---

## Per-Project Structure

### Full Mode (`multiagent init`)

```
your-project/
├── .multiagent/          # Core framework infrastructure
│   ├── README.md        # Framework documentation
│   ├── components.json  # Linked components registry
│   ├── core/            # Core scripts and templates
│   │   ├── scripts/     # Setup, generation, validation
│   │   ├── templates/   # Agent, workflow templates
│   │   └── docs/        # Agent workflow guides
│   ├── deployment/      # Docker, K8s, deployment automation
│   │   ├── scripts/     # Deployment scripts
│   │   ├── templates/   # Dockerfile, compose templates
│   │   ├── logs/        # Deployment logs
│   │   └── memory/      # Deployment state
│   ├── documentation/   # Documentation automation
│   │   ├── scripts/     # Doc generation
│   │   ├── templates/   # Doc templates
│   │   └── memory/      # Doc state tracking
│   ├── testing/         # Test generation and automation
│   │   ├── scripts/     # Test generators
│   │   ├── templates/   # Test templates
│   │   ├── logs/        # Test run logs
│   │   └── memory/      # Test state
│   ├── security/        # Security scanning and compliance
│   │   ├── scripts/     # Security scanners
│   │   └── templates/   # Security configs
│   ├── pr-review/       # PR review automation
│   │   ├── scripts/     # Review orchestration
│   │   ├── templates/   # Review templates
│   │   ├── logs/        # Review sessions
│   │   └── sessions/    # Active review data
│   ├── iterate/         # Task layering and spec iteration
│   │   ├── scripts/     # Layering automation
│   │   └── templates/   # Task templates
│   └── supervisor/      # Agent coordination
│       ├── scripts/     # Supervisor checks
│       └── templates/   # Report templates
├── .claude/             # Claude Code configuration
│   ├── agents/          # Agent definitions (17 specialized agents)
│   ├── commands/        # Slash commands (20+ commands)
│   ├── hooks/           # Event hooks (git, tool, session)
│   ├── sdk-config/      # MCP server configs
│   └── settings.json    # Claude IDE settings
├── .github/             # GitHub automation
│   ├── workflows/       # CI/CD workflows (15+ workflows)
│   ├── prompts/         # GitHub agent prompts
│   └── copilot-instructions.md
├── .vscode/             # VSCode configuration
│   ├── settings.json    # IDE settings
│   ├── keybindings.json # Custom keybindings
│   └── mcp.json         # MCP server config
└── docs/                # Documentation scaffold
    └── README.md        # Project docs entry point
```

### Backend-Heavy Mode (`multiagent init --backend-heavy`)

**Skips:**
- `.vscode/` (frontend IDE configs)
- `docs/` initially (created minimal scaffold)

**Includes:**
- All `.multiagent/` infrastructure (full backend automation)
- `.claude/` agents and commands
- `.github/` workflows

**Use Case:**
- API-only projects
- Microservices
- CLI tools
- Backend-heavy architectures

---

## CLI Architecture

### Current Commands

```bash
multiagent --version              # Show version
multiagent --help                 # Show help

multiagent init [PATH]            # Initialize project
  --dry-run                       # Preview changes
  --create-repo                   # Create GitHub repo
  --no-interactive                # Skip prompts
  --backend-heavy                 # Backend-optimized init

multiagent status                 # Show components and CLIs
multiagent upgrade                # Upgrade packages
multiagent detect                 # Detect project stack
multiagent env-init               # Generate .env file
```

### Command Flow

```
┌──────────────────────────────────────────────────────┐
│ ~/.local/bin/multiagent                              │
│ (symlink to pipx venv)                               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ multiagent_core/cli.py:main()                        │
│ @click.group()                                       │
└────────────────┬─────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ init()       │  │ status()     │
│ detect()     │  │ upgrade()    │
│ env-init()   │  │ ...          │
└──────────────┘  └──────────────┘
```

### Entry Point Registration

```toml
# pyproject.toml
[project.scripts]
multiagent = "multiagent_core.cli:main"
```

**How pipx Makes It Global:**
1. Installs package in isolated venv
2. Creates symlink: `~/.local/bin/multiagent`
3. Points to: `venv/bin/multiagent`
4. Which runs: `python -m multiagent_core.cli`

---

## Auto-Update System

### Build-Time Auto-Update

```python
# multiagent_core/_template_build.py
def _sync_for_build():
    """Runs during: python -m build"""

    # 1. Sync templates from repo root
    sync_templates(quiet=True, repo_root=_repo_root())

    # 2. Trigger auto-updater
    update_script = repo_root / "build-system/track_and_update.py"
    subprocess.run([sys.executable, str(update_script), "update"])

    # 3. Updates ALL registered projects
    # (Reads ~/.multiagent-core-deployments.json)
```

### Manual Sync

```bash
# Sync templates without full build
python -m multiagent_core.auto_updater

# Full rebuild + sync all projects
cd /path/to/multiagent-core
python -m build
```

### Update Flow

```
┌─────────────────────────────────────────┐
│ python -m build                         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ _template_build.py:_sync_for_build()    │
│ 1. Sync .multiagent/ → templates/       │
│ 2. Sync .claude/ → templates/           │
│ 3. Sync .github/ → templates/           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ auto_updater.update_all_deployments()   │
│ - Read ~/.multiagent-core-deployments   │
│ - For each registered project:          │
│   - sync_directory_recursively()        │
│   - Remove obsolete files/dirs          │
│   - Update timestamps                   │
└─────────────────────────────────────────┘
```

---

## Future CLI Expansion

### Proposed Commands

```bash
# Project Management
multiagent projects                    # List registered projects
multiagent projects clean              # Remove stale /tmp projects
multiagent projects sync [PATH]        # Sync specific project
multiagent projects unregister [PATH]  # Remove from tracking

# Template Management
multiagent templates list              # Show available templates
multiagent templates edit [NAME]       # Edit template in $EDITOR
multiagent templates sync              # Sync without full build
multiagent templates diff [PATH]       # Compare local vs package

# Backend Shortcuts
multiagent backend init [PATH]         # Alias for --backend-heavy
multiagent backend deploy              # Backend-focused deployment

# Component Management
multiagent component link [NAME] [PATH] # Link local component dev
multiagent component list              # Show linked components
multiagent component unlink [NAME]     # Remove component link

# Development Helpers
multiagent dev-init [PATH]             # Fast dev mode init
multiagent dev-sync                    # Quick template sync
multiagent dev-clean                   # Clean test projects
```

### Implementation Approach

```python
# multiagent_core/cli.py

@main.command()
def projects():
    """Manage registered projects"""
    pass

@projects.command()
def list():
    """List all registered projects"""
    # Read ~/.multiagent-core-deployments.json
    # Display table with project paths, registered date, last updated

@projects.command()
@click.argument('path', type=click.Path())
def sync(path):
    """Sync specific project with latest templates"""
    # Load templates from multiagent_core/templates/
    # Call auto_updater.sync_directory_recursively()
    # Update timestamps in registry
```

---

## Directory Permission Model

### System Directories (Read-Only for Users)

```
~/.local/share/pipx/venvs/multiagent-core/
```
- Managed by pipx
- Don't edit directly
- Rebuilt on `pipx install`

### Template Source (Editable in Dev Mode)

```
/home/user/Projects/multiagent-core/
├── .multiagent/          # Edit these (source of truth)
├── .claude/              # Edit these
├── multiagent_core/
│   └── templates/        # READ-ONLY (build output)
```

**Development Workflow:**
1. Edit source templates in repo root
2. Changes instant via editable install
3. Build syncs to `multiagent_core/templates/`
4. Build auto-updates all projects

### Per-Project Directories (Fully Editable)

```
/path/to/your-project/
├── .multiagent/          # Local overrides allowed
├── .claude/              # Customize per project
├── .github/              # Modify workflows
```

**Override System:**
- Templates copied on init
- Local changes preserved on update
- Merge strategy for conflicts
- `.multiagent/local-overrides/` (future feature)

---

## Architecture Benefits

### ✅ Fully Local
- No cloud dependencies
- No external databases
- Fast initialization
- Offline capable

### ✅ Isolated Environments
- pipx manages Python environments
- No global package pollution
- Multiple Python versions supported

### ✅ Auto-Sync
- Build once, update everywhere
- Consistent across projects
- Tracked update history

### ✅ Developer Friendly
- Editable installs for development
- Instant template changes
- Backend-heavy mode for APIs
- Comprehensive CLI

### ✅ Scalable
- Unlimited projects
- Efficient storage (symlinks)
- Selective sync capability
- Cleanup automation

---

## Related Documentation

- [System Architecture](./SYSTEM_ARCHITECTURE.md) - Overall system design
- [Workflow Generation](./WORKFLOW_GENERATION_ARCHITECTURE.md) - GitHub workflow automation
- [Git Hooks System](./GIT_HOOKS_SYSTEM.md) - Hook architecture
- [Slash Command Design](./SLASH_COMMAND_DESIGN_PATTERN.md) - Command patterns
- [Build System](../../build-system/README.md) - Template sync and build process

---

**Last Updated:** 2025-10-03
**Version:** 3.2.0+
**Status:** Production
