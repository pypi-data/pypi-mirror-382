# Implementation Documentation

Detailed implementation guides for MultiAgent Core build system and infrastructure generation.

## Documents

### 1. [WORKFLOW_GENERATION_ARCHITECTURE.md](./WORKFLOW_GENERATION_ARCHITECTURE.md)
**GitHub Workflow Generation**

- How workflows are generated (not copied)
- Template-based generation approach
- Project-specific workflow creation
- Reading from Spec-Kit outputs
- Dynamic workflow composition
- CI/CD automation patterns

## Agent Operational Guides

For agent workflow documentation (worktrees, git hooks, branch protocols), see:
- **[Agent Workflows](../../.multiagent/core/docs/agent-workflows/)** - Deployed operational guides
  - Git Worktree Management
  - Git Hooks System
  - Agent Branch Protocol
  - Task Coordination

These docs are in `.multiagent/` because they deploy with `multiagent init` and agents need to reference them.

## Implementation Categories

### Automation Systems
- Workflow generation
- CI/CD integration
- Deployment automation

### Integration Points
- GitHub Actions integration
- Security tool integration
- Testing framework integration

### Generation Strategies
- Template-based generation
- Dynamic configuration
- Project-specific customization
- Spec-driven automation

## Navigation

- [← Back to Architecture](../)
- [Core →](../core/)
- [Patterns →](../patterns/)
