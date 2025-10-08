# MultiAgent System Architecture

## System Overview

The MultiAgent framework is a **meta-framework** that generates project-specific infrastructure based on specifications. It follows a clear separation between tooling (deployed) and output (generated).

## Core Philosophy: Building on Spec-Kit Foundation

### The Foundational Principle
**MultiAgent is designed to build off Spec-Kit** - we don't duplicate, we extend:
- **Spec-Kit** provides specification, planning, and task generation
- **MultiAgent** adds infrastructure generation and agent orchestration
- **Together** they form a complete development ecosystem

### Separating Mechanical from Intelligence

The system follows a **table-setting pattern** where:
- **Scripts** do mechanical work (create directories, copy files, validate)
- **Templates** provide context and structure
- **Agents** apply intelligence (make decisions, customize, adapt)

## Architectural Principles

### 1. Building on Spec-Kit Foundation
- **Spec-Kit creates**: Specifications, plans, tasks, documentation
- **MultiAgent reads**: Spec-Kit outputs to generate infrastructure
- **Never duplicate**: If Spec-Kit does it, we use their output
- **Always extend**: Add infrastructure generation on top of specs

### 2. Immutable Tooling
- `.multiagent/` directory is read-only after deployment
- Scripts and templates never self-modify
- Version-locked at initialization time

### 3. Specification-Driven
- Everything generated from specs (created by Spec-Kit)
- No hardcoded project assumptions
- Adaptive to project needs
- Workflows generated AFTER understanding project (not during init)

### 4. System Isolation
- Each system owns its domain
- No cross-system file writing
- Clear interface boundaries

### 5. Command Orchestration
- Slash commands as primary interface
- Commands can invoke other commands (NEW: command chaining)
- When you run a slash command, YOU are the agent
- Scripts are tools that set the table for agent work

### 6. Dual Output Pattern
- **Spec Output**: Documentation in `specs/XXX/[system]/`
- **Project Output**: Infrastructure in project root or specific dirs
- Clear separation between documentation and implementation

## System Components Visual Map

```
.multiagent/
├── 🎯 core/           [Orchestrator] ✅
│   ├── docs/          → Architecture patterns
│   ├── scripts/       → 2 scripts (minimal)
│   └── templates/     → None (orchestrator)
│
├── 🚀 deployment/     [Hybrid] ⚠️ Script-heavy
│   ├── scripts/       → 10 scripts! (TOO MANY)
│   ├── templates/     → Docker, K8s patterns
│   └── subagent:      → deployment-prep ✅
│
├── 🧪 testing/        [Subagent-driven] ✅
│   ├── scripts/       → 3 scripts (good)
│   ├── templates/     → Test patterns
│   └── subagents:     → backend-tester, test-generator ✅
│
├── 🔄 pr-review/      [Script-heavy] ⚠️
│   ├── scripts/       → 7 scripts (too many)
│   ├── templates/     → Feedback templates
│   └── subagent:      → review-pickup (partial)
│
├── 🔁 iterate/        [Script-heavy] ⚠️
│   ├── scripts/       → 5 scripts
│   ├── templates/     → Task layering
│   └── subagent:      → None ❌
│
├── 👁️ supervisor/     [Monitor] 🚧
│   ├── scripts/       → 3 scripts
│   ├── templates/     → Report templates
│   └── subagent:      → None (monitoring pattern)
│
└── 🔒 security/       [Subagent-driven] ✅ GOLD STANDARD
    ├── scripts/       → 3 scripts (minimal)
    ├── templates/     → Security patterns
    └── subagent:      → security-auth-compliance ✅
```

### System Maturity Levels

#### 🟩 Gold Standard (Security, Testing)
- 2-3 scripts maximum
- Clear subagent ownership
- Dual output pattern
- Templates as pure context
- Example: Security system with security-auth-compliance agent

#### 🟧 Transitional (Deployment)
- Too many scripts but has subagent
- Needs script consolidation
- Moving toward target pattern
- Action needed: Reduce from 10 to 3 scripts

#### 🟥 Needs Refactoring (PR-Review, Iterate)
- 5+ scripts doing work
- Missing or partial subagents
- Scripts contain business logic
- Action needed: Move logic to subagents

## Data Flow Architecture: Spec-Kit → MultiAgent

```mermaid
graph TD
    subgraph "Phase 1: Spec-Kit Foundation"
        A[/specify] --> B[specs/001-*/spec.md]
        B --> C[/plan]
        C --> D[plan.md]
        D --> E[/tasks]
        E --> F[tasks.md]
    end

    subgraph "Phase 2: MultiAgent Initialization"
        G[multiagent init] --> H[Deploy .multiagent/]
        H --> I[Deploy .claude/]
        H --> J[Deploy .github/ templates]
    end

    subgraph "Phase 3: MultiAgent Generation"
        F --> K[/project-setup]
        K --> L[Read Spec-Kit outputs]
        L --> M[Generate infrastructure]
        M --> N[workflows/, configs, tests]
    end

    subgraph "Generation"
        H --> I[/project-setup]
        I --> J[/deploy-prepare]
        I --> K[/testing-workflow]
        J --> L[deployment/]
        K --> M[tests/]
        I --> N[.github/workflows/]
    end

    subgraph "Development"
        O[/iterate] --> P[Update Specs]
        Q[/supervisor] --> R[Monitor Agents]
        S[/pr-review] --> T[Process Feedback]
    end
```

## Command Architecture

### Command Hierarchy
```
/project-setup              # Master orchestrator
├── /deploy-prepare        # Deployment generation
├── /testing-workflow      # Test generation
├── /deploy-validate      # Validation
└── Generates:
    ├── .github/workflows/ # Based on project needs
    ├── pyproject.toml    # If Python project
    ├── package.json      # If Node project
    └── .env.example      # Environment template
```

### Command Communication
- Commands invoke via SlashCommand tool (NEW capability)
- Command chaining supported (e.g., specify→plan→tasks)
- Async execution supported
- State passed through filesystem
- Commands can now pass arguments directly

## File System Architecture

### Directory Ownership Model
```
PROJECT_ROOT/
├── .multiagent/          # Framework (read-only)
│   ├── core/            # Core system
│   ├── deployment/      # Deployment system
│   ├── testing/         # Testing system
│   ├── pr-review/       # PR review system
│   ├── iterate/         # Iterate system
│   └── supervisor/      # Supervisor system
│
├── deployment/          # Generated (mutable)
├── tests/              # Generated (mutable)
├── specs/              # Generated (mutable)
└── src/                # Generated (mutable)
```

### Template Processing Pipeline
```
Template (.template) → Variable Resolution → Output File
                     ↑
                     │
                Spec Analysis
```

## Security Architecture

### Boundary Enforcement
- Read anywhere in project
- Write only to designated directories
- No system-level modifications
- No network operations without approval

### Secret Management
```
GitHub Secrets → Environment Variables → Application
                                      ↑
                                      │
                                Never in Files
```

## Agent Architecture

### Agent Isolation Model
```
main branch
├── agent-claude-architecture    # @claude worktree
├── agent-copilot-impl          # @copilot worktree
├── agent-qwen-optimize         # @qwen worktree
└── agent-gemini-docs           # @gemini worktree
```

### Agent Communication
- Through git commits and PRs
- Task assignments in specs
- Shared context in documentation
- No direct agent-to-agent communication

## Scalability Architecture

### Horizontal Scaling
- Multiple agents work in parallel
- Task layering for dependency management
- Independent worktrees prevent conflicts

### Vertical Scaling
- Complex tasks delegated to specialized agents
- Subagent system for deep specialization
- Hierarchical task decomposition

## Extension Points

### Adding New Systems
1. Create directory in `.multiagent/`
2. Add scripts and templates
3. Create slash command in `.claude/commands/`
4. Document in system README

### Adding New Commands
1. Create command file in `.claude/commands/`
2. Define allowed-tools
3. Implement command logic
4. Update command registry

### Adding New Templates
1. Add to appropriate `templates/` directory
2. Use `{{VARIABLE|default}}` syntax
3. Document variables
4. Update generation script

## Performance Considerations

### Optimization Strategies
- Parallel command execution where possible
- Lazy loading of templates
- Incremental generation
- Caching of spec analysis

### Resource Management
- Cleanup old worktrees
- Prune generation logs
- Limit session history
- Archive completed specs

## Error Handling

### Failure Modes
1. **Spec not found**: Graceful fallback to defaults
2. **Template missing**: Skip generation with warning
3. **Script failure**: Log and report, don't corrupt
4. **Permission denied**: Clear error message

### Recovery Strategies
- Idempotent operations
- Transaction-like generation
- Rollback capabilities
- Manual override options

## Integration Architecture

### GitHub Integration
```
GitHub Webhooks → Actions → Commands → Scripts → Output
```

### CI/CD Integration
```
Code Push → Workflow Trigger → Tests → Build → Deploy
```

### External Services
```
Project → API Gateway → Service
        ↑
        │
    Secret Management
```

## Monitoring Architecture

### Observability
- Generation logs in `.multiagent/*/logs/`
- Session tracking in memory directories
- Git history for audit trail
- GitHub Actions for CI/CD visibility

### Metrics
- Task completion rates
- Generation success/failure
- Agent compliance scores
- System performance metrics

## Future Architecture Considerations

### Potential Enhancements
1. **Plugin System**: Dynamic system loading
2. **Remote Templates**: Fetch from registry
3. **Multi-Project**: Manage multiple projects
4. **Cloud Sync**: Backup and sync specs

### Compatibility
- Backward compatibility maintained
- Version detection in scripts
- Migration paths documented
- Deprecation warnings

## Pattern Evolution

### Script-Heavy Pattern (Old) ❌
```
Command → Many Scripts → Templates with instructions → Output
         ↑
    Scripts do the work
```
**Examples**: pr-review (7 scripts), iterate (5 scripts)
**Problem**: Scripts contain business logic, hard to maintain

### Hybrid Pattern (Transitional) ⚠️
```
Command → Some Scripts → Subagent → Output
         ↑                    ↑
    Setup tasks         Main work
```
**Example**: deployment (10 scripts but has subagent)
**Status**: Moving toward target, but still script-heavy

### Subagent-Driven Pattern (Target) ✅
```
Command → Subagent (with tools) → Minimal Scripts → Output
              ↑                           ↑
        Does most work            Only bulk/system ops
```
**Examples**: security (3 scripts), testing (3 scripts)
**Goal**: Scripts only for mechanical tasks, agents for intelligence

## Script Count Heat Map

```
🟥 HIGH (10): deployment
🟧 MEDIUM (5-7): pr-review (7), iterate (5)
🟩 LOW (2-3): security (3), testing (3), supervisor (3), core (2)
```

**Target**: All systems 🟩 (2-3 scripts max)

## Refactoring Priority

### 🔴 Priority 1: Deployment
- Reduce from 10 to 3 scripts
- Move logic to deployment-prep subagent
- Scripts to remove:
  - validate-compose.sh → subagent
  - check-stack.sh → subagent
  - generate-configs.sh → subagent

### 🟠 Priority 2: PR-Review
- Reduce from 7 to 3 scripts
- Create proper pr-review-analyst subagent
- Move analysis to subagent

### 🟡 Priority 3: Iterate
- Reduce from 5 to 2 scripts
- Create iterate-coordinator subagent
- Move layering logic to subagent

## Anti-Patterns to Avoid

### ❌ Self-Modifying Scripts
Never have scripts modify `.multiagent/`

### ❌ Cross-System Writing
Systems shouldn't write to each other's domains

### ❌ Hardcoded Paths
Always use relative or configurable paths

### ❌ Synchronous Blocking
Use async operations where possible

### ❌ Tight Coupling
Maintain loose coupling between systems

### ❌ Business Logic in Scripts
Scripts should only do mechanical work

### ❌ Too Many Scripts (>3)
Indicates logic that should be in subagents

## Best Practices

### ✅ Idempotent Operations
Running twice produces same result

### ✅ Defensive Programming
Validate inputs, handle errors gracefully

### ✅ Clear Boundaries
Each system owns specific directories

### ✅ Documentation First
Document before implementing

### ✅ Test Coverage
Every generator needs tests