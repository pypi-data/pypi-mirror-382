# MultiAgent Framework

Welcome to MultiAgent - the intelligent development framework that orchestrates multiple AI assistants to work together on your projects.

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

Alternative one-time usage:
```bash
# Run without installing
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
```

Requirements:
- Linux/macOS (or WSL2 on Windows)
- Python 3.11+
- Git

## How This Directory Got Here

This `.multiagent/` directory was copied when you ran `multiagent init`.

### Source & Updates

- **Copied from**: Installed `multiagent-core` package (location independent)
- **Auto-updates**: Registered in `~/.multiagent-core-deployments.json`
- **When updated**: Automatically when multiagent-core is rebuilt
- **Package-based**: Uses `importlib` - no path dependencies

**Location Independence**: The init process works from **any directory** because it uses Python's `importlib_resources` to find the installed package, not relative paths. This means `multiagent init` works identically whether you run it from `/tmp/my-app`, `~/projects/my-app`, or anywhere else.

### Post-Install Configuration

After templates are copied, `/project-setup` runs automatically:
- Detects your tech stack (Node.js, Python, React, Next.js, FastAPI, Django, etc.)
- Configures GitHub workflows appropriately
- Sets up deployment based on your specs
- **Runs from package**, not from these copied files

This ensures you always get the latest configuration logic without needing sync scripts in your project.

### What You Can Customize

Feel free to customize in your project:
- `.multiagent/config/` - Project-specific settings
- `.multiagent/deployment/` - Custom deployment configs
- `.multiagent/testing/` - Project test configurations
- `.claude/agents/` - Agent behavior customizations

### What Gets Auto-Updated

These sync from package on updates:
- `.multiagent/docs/` - Framework documentation
- `.multiagent/core/templates/` - Core utilities
- `.multiagent/user-prompts/` - Agent contexts
- `.claude/commands/` - Slash command definitions

**User customizations** (config/, deployment/, testing/) are preserved during updates.

### Build System

For contributors editing templates in `multiagent-core` repository:
- **Source location**: Root `.multiagent/` in repo
- **Build process**: `python -m build` copies root → `multiagent_core/templates/`
- **Auto-sync**: Build automatically updates ALL registered projects
- **Documentation**: See `template-management/README.md` for details

## Clean Organization (After Reorganization)

### Directory Structure

**For Template Repository Only:**
- `template-management/` - Build system (NOT deployed)
  - Handles template packaging, project sync, auto-updates
  - Build automation and deployment tracking
  - Tech stack detection and configuration
- `.multiagent/tools/` - Development and deployment tools

**For Deployed Projects (Minimal):**
- `.multiagent/deployment/` - Deployment generation system
- `.multiagent/testing/` - Test generation system
- `.claude/` - Agent configurations

**Deployment Footprint:** ~200KB (vs 2MB+ before cleanup!)

## Installation

### Quick Start (Recommended: pipx)

The recommended way to install MultiAgent is using `pipx`, which creates an isolated environment for the CLI:

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

If you prefer using pip directly:

```bash
# Global installation (may require sudo)
pip install multiagent-core

# Or user installation
pip install --user multiagent-core
```

### Ubuntu 24.04+ Users

If you encounter the "externally managed environment" error:

```bash
# Option 1: Use pipx (recommended)
sudo apt update && sudo apt install pipx
pipx install multiagent-core

# Option 2: Use pip with break-system-packages flag
pip install --user --break-system-packages multiagent-core

# Option 3: Use a virtual environment
python3 -m venv ~/.multiagent-venv
~/.multiagent-venv/bin/pip install multiagent-core
echo 'alias multiagent="~/.multiagent-venv/bin/multiagent"' >> ~/.bashrc
source ~/.bashrc
```

## Getting Started

### Initialize Your Project

The setup is a two-step process: first create the spec-kit foundation, then enhance with MultiAgent:

#### Step 1: Create Spec-Kit Project Structure

```bash
# Basic project initialization (creates new directory)
specify init my-project

# Initialize with specific AI assistant
specify init my-project --ai claude
specify init my-project --ai copilot
specify init my-project --ai gemini
specify init my-project --ai codex
specify init my-project --ai qwen

# Initialize with Cursor IDE support
specify init my-project --ai cursor

# Initialize with Windsurf IDE support
specify init my-project --ai windsurf

# Initialize in current directory (COMMONLY USED)
specify init --here --ai claude
specify init --here --ai copilot

# Force merge into non-empty directory without confirmation
specify init --here --force --ai claude

# Initialize with PowerShell scripts (Windows/cross-platform)
specify init my-project --ai copilot --script ps

# Skip git initialization
specify init my-project --ai gemini --no-git

# Enable debug output for troubleshooting
specify init my-project --ai claude --debug

# Use GitHub token for API requests (corporate environments)
specify init my-project --ai claude --github-token ghp_your_token_here

# Check system requirements before initialization
specify check
```

**Most Common Usage:**
```bash
# For existing projects - initialize in current directory
specify init --here --ai claude

# For new projects - create project directory
specify init my-new-project --ai claude
```

This creates the initial spec-kit structure:
```
my-awesome-app/
├── memory/
│   └── constitution.md        # Project principles & guidelines
├── scripts/                   # Utility scripts
├── specs/                     # Feature specifications
└── templates/                 # Project templates
```

#### Step 2: Enhance with MultiAgent Framework

```bash
# Navigate to your project
cd my-awesome-app

# Add MultiAgent framework
multiagent init

# Or with framework detection
multiagent init --framework nextjs
multiagent init --framework django
```

### Complete Project Structure (After Both Steps)

After running both `specify init` and `multiagent init`, you get:

```
my-awesome-app/
├── memory/                     # Spec-kit memory & constitution
│   ├── constitution.md        # Project principles (from spec-kit)
│   └── context/               # Saved agent contexts
├── specs/                     # Feature specifications (spec-kit)
│   └── 001-user-auth/        # Example feature spec
│       ├── spec.md          # What to build
│       ├── plan.md          # How to build it
│       └── tasks.md         # Task breakdown for agents
├── scripts/                   # Utility scripts (spec-kit)
├── templates/                 # Project templates (spec-kit)
├── .claude/                   # Claude AI integration (multiagent)
│   ├── hooks/                # Development workflow hooks
│   ├── settings.json         # Claude configuration
│   └── prompts/              # Agent context & instructions
├── .github/                   # GitHub Actions (multiagent)
│   ├── workflows/            # CI/CD pipelines
│   └── ISSUE_TEMPLATE/       # Issue templates
├── .vscode/                   # VS Code config (multiagent)
│   ├── settings.json         # Editor settings
│   ├── keybindings.json     # Custom keybindings
│   └── mcp.json             # MCP server configuration
├── .multiagent/              # MultiAgent framework (multiagent)
│   ├── core/                # Framework utilities
│   ├── config/              # Configuration helpers
│   ├── docs/                # Framework documentation
│   ├── components.json      # Installed components
│   ├── state.json           # Project state
│   └── README.md            # This documentation
├── CLAUDE.md                 # Project context for AI agents
├── .gitmessage              # Git commit template
├── .env                     # Environment configuration
└── pyproject.toml           # Python project configuration
```

### Check Status

```bash
# View your project configuration
specify status

# Or use multiagent for framework status
multiagent status
```

### Update MultiAgent

```bash
# Check for updates
multiagent upgrade

# Or manually with pipx
pipx upgrade multiagent-core
```

## Optional Components

Enhance your development workflow with specialized packages:

### DevOps Tools
```bash
pipx install multiagent-devops
```
Provides CI/CD pipelines, Docker configurations, and deployment automation.

### Testing Framework
```bash
pipx install multiagent-testing
```
Adds comprehensive test generation, coverage analysis, and QA automation.

### Agent Swarm
```bash
pipx install multiagent-agentswarm
```
Enables parallel agent orchestration and distributed task execution.

## Directory Structure

After initialization, your `.multiagent/` directory contains:

- `core/` - Core framework modules and utilities
- `config/` - Framework configuration files
- `templates/` - Project templates and starter files
- `docs/` - Framework documentation
- `.gitmessage` - Professional git commit template
- `components.json` - Installed components tracking
- `state.json` - Project state and configuration

## Spec-Kit Workflow Integration

MultiAgent integrates with the spec-kit development methodology for structured, specification-driven development:

### Creating Feature Specs

```bash
# Create a new feature specification
specify create-spec user-authentication

# Or using the spec-kit workflow commands
specify /spec user-authentication

# This creates:
# specs/001-user-authentication/
#   ├── spec.md     # What to build
#   ├── plan.md     # How to build it  
#   └── tasks.md    # Task breakdown for agents
```

### Spec-Driven Development Flow

1. **Define Requirements** (`spec.md`)
   - User stories and requirements
   - Acceptance criteria
   - Technical constraints

2. **Create Technical Plan** (`plan.md`)
   - Architecture decisions
   - Technology choices
   - Implementation strategy

3. **Generate Tasks** (`tasks.md`)
   - Breakdown into actionable items
   - Agent assignments (@claude, @codex, etc.)
   - Dependencies and priorities

4. **Execute with Agents**
   ```bash
   # Deploy agents to work on tasks
   agentswarm deploy --spec specs/001-user-authentication
   
   # Or work on individual tasks
   multiagent task start T001
   ```

### Working with Specs

```bash
# List all feature specs
multiagent spec list

# Validate a spec structure
multiagent spec validate 001-user-authentication

# Generate tasks from spec
multiagent spec generate-tasks 001-user-authentication
```

## Framework Features

### Multi-Agent Coordination
Intelligent orchestration of AI assistants working together on your codebase. Each agent specializes in different aspects:
- **Claude**: Architecture, analysis, and complex problem-solving
- **Codex**: Implementation, refactoring, and code optimization
- **Copilot**: Quick fixes, completions, and pair programming
- **Qwen**: Documentation, testing, and code review
- **Gemini**: Creative solutions and alternative approaches

### Project Templates
Pre-configured templates for popular frameworks:
- React, Vue, Angular, Svelte
- Next.js, Nuxt, SvelteKit
- Express, FastAPI, Django, Rails
- And many more...

### Environment Detection
Automatic detection of your tech stack:
- Programming languages and versions
- Frameworks and libraries
- Package managers (npm, pip, cargo, etc.)
- Database systems
- Cloud services

### Git Integration
Professional development workflows:
- Semantic commit messages
- Conventional commits support
- Branch management
- PR/MR templates

### Cross-Platform Support
Full compatibility across:
- Windows (PowerShell/CMD)
- macOS (zsh/bash)
- Linux (all major distributions)
- WSL/WSL2
- Docker containers

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# AI Assistant Preferences
DEFAULT_AI_ASSISTANT=claude
AI_TEMPERATURE=0.7

# Project Settings
PROJECT_NAME=my-awesome-app
ENVIRONMENT=development

# Feature Flags
ENABLE_AUTO_COMMIT=false
ENABLE_TEST_GENERATION=true
```

### Component Configuration

The framework automatically generates appropriate configuration based on detected stack:
- ESLint/Prettier for JavaScript/TypeScript
- Black/Ruff for Python
- RuboCop for Ruby
- And more...

## Troubleshooting

### Command Not Found

If `multiagent` command is not found after installation:

```bash
# For pipx installation
python3 -m pipx ensurepath
# Then restart your terminal or run:
source ~/.bashrc  # or ~/.zshrc for zsh

# For pip installation
export PATH="$PATH:$HOME/.local/bin"
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Permission Errors

```bash
# Use user installation
pip install --user multiagent-core

# Or with pipx (recommended)
pipx install multiagent-core
```

### Python Version Issues

MultiAgent requires Python 3.9 or higher:

```bash
# Check your Python version
python3 --version

# Install Python 3.9+ if needed
# Ubuntu/Debian
sudo apt update && sudo apt install python3.9

# macOS
brew install python@3.9

# Windows
# Download from python.org
```

## Advanced Usage

### Custom Templates

Add your own templates to `.multiagent/templates/`:

```bash
# Create custom template
mkdir -p .multiagent/templates/my-template
echo "# My Template" > .multiagent/templates/my-template/README.md

# Use in initialization
multiagent init --template my-template
```

### Workflow Automation

Create `.multiagent/workflows/` for custom automation:

```yaml
# .multiagent/workflows/daily.yml
name: Daily Development Flow
steps:
  - name: Update dependencies
    run: multiagent deps update
  - name: Run tests
    run: multiagent test
  - name: Generate reports
    run: multiagent report
```

### Agent Configuration

Customize agent behavior in `.multiagent/agents.json`:

```json
{
  "claude": {
    "specialties": ["architecture", "security", "optimization"],
    "temperature": 0.7
  },
  "codex": {
    "specialties": ["implementation", "refactoring"],
    "temperature": 0.5
  }
}
```

## Getting Help

- **Documentation**: https://github.com/vanman2024/multiagent-core
- **Issues**: https://github.com/vanman2024/multiagent-core/issues
- **Discord**: [Join our community](https://discord.gg/multiagent)
- **Email**: support@multiagent.dev

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/vanman2024/multiagent-core/blob/main/CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](https://github.com/vanman2024/multiagent-core/blob/main/LICENSE) for details.

---

🤖 Powered by MultiAgent Framework
Version detection via `multiagent --version`