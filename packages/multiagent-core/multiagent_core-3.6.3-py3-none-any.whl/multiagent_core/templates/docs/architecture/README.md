# Architecture Documentation - THE BIBLE

**Last Updated**: 2025-09-29
**Status**: Complete Documentation Set
**Foundation**: MULTIAGENT BUILDS ON SPEC-KIT

## 📕 THE FUNDAMENTAL PRINCIPLE

**MultiAgent is designed to build off Spec-Kit, never duplicate it.**

```
Spec-Kit Creates           →  MultiAgent Adds
───────────────────────       ───────────────────────
• Specifications          →  • Infrastructure
• Planning                →  • Deployment configs
• Task generation         →  • Testing suites
• Documentation           →  • Security setup
• Vision/requirements     →  • CI/CD workflows
```

## Documentation Structure

### 📁 [Core Architecture](./core/)
**Fundamental architecture documents**

1. **[SYSTEM_ARCHITECTURE.md](./core/SYSTEM_ARCHITECTURE.md)**
   - Master architecture document
   - Core principles (Building on Spec-Kit #1)
   - System component overview
   - Anti-patterns and best practices

2. **[SYSTEM_WORKFLOW_PATTERN.md](./core/SYSTEM_WORKFLOW_PATTERN.md)**
   - THE BIBLE for workflow patterns
   - Building on Spec-Kit foundation
   - The table-setting pattern
   - Scripts → Templates → Agents flow

3. **[LOCAL_STORAGE_AND_CLI.md](./core/LOCAL_STORAGE_AND_CLI.md)** ⭐ NEW
   - Local storage architecture
   - CLI command structure
   - Project registration & auto-update
   - Backend-heavy mode

4. **[SYSTEM_VISUAL_MAP.md](./core/SYSTEM_VISUAL_MAP.md)**
   - Visual system overview
   - Component heat map
   - Maturity levels

### 🔄 [Patterns](./patterns/)
**Design patterns and evolution strategies**

1. **[SPECKIT_VS_MULTIAGENT_PATTERNS.md](./patterns/SPECKIT_VS_MULTIAGENT_PATTERNS.md)**
   - Framework integration patterns
   - Template-driven vs subagent-driven
   - How MultiAgent extends Spec-Kit

2. **[SCRIPT_EVOLUTION_PATTERN.md](./patterns/SCRIPT_EVOLUTION_PATTERN.md)**
   - Evolution from scripts to subagents
   - The 3-script rule
   - Consolidation strategies

3. **[SLASH_COMMAND_DESIGN_PATTERN.md](./patterns/SLASH_COMMAND_DESIGN_PATTERN.md)**
   - Command architecture
   - Subagent invocation
   - Context passing

### 🚀 [Implementation](./implementation/)
**Build system and infrastructure generation guides**

1. **[WORKFLOW_GENERATION_ARCHITECTURE.md](./implementation/WORKFLOW_GENERATION_ARCHITECTURE.md)**
   - GitHub workflow generation
   - Template-based approach
   - Spec-driven automation

**Note**: Agent operational guides (worktrees, git hooks, branch protocols) are in `.multiagent/core/docs/agent-workflows/` because they deploy with `multiagent init`

## The Sacred Order of Operations

```
PHASE 1: Spec-Kit Foundation (MUST RUN FIRST)
────────────────────────────────────────────
/specify → Creates spec.md
/plan    → Creates plan.md, data-model.md
/tasks   → Creates tasks.md

PHASE 2: MultiAgent Infrastructure (BUILDS ON SPEC-KIT)
────────────────────────────────────────────────────────
/project-setup  → Reads ALL Spec-Kit outputs → Creates infrastructure
/deployment     → Reads specs + plan → Creates deployment/
/testing        → Reads specs + code → Creates tests/
/security       → Reads specs + requirements → Creates security setup
```

## Key Concepts

### The Golden Rules

1. **Never recreate what Spec-Kit already does**
   - Read their outputs, don't regenerate
   - Use their specs as your input
   - Build infrastructure from their documentation
   - Generate code from their tasks

2. **When you run a slash command, YOU are the agent**
   - Scripts set the table
   - Templates provide context
   - Agents make decisions

### The Table-Setting Pattern
```
Scripts (Mechanical) → Templates (Context) → Agents (Intelligence)
```

### Target Pattern
All systems should follow the **Security System Gold Standard**:
- 2-3 scripts maximum
- Clear subagent ownership
- Dual output pattern
- Templates as pure context
- Reads Spec-Kit outputs

### Script Count Goals
```
🟩 IDEAL: 2-3 scripts (security, testing, core)
🟧 ACCEPTABLE: 3-4 scripts (supervisor)
🟥 NEEDS REFACTORING: 5+ scripts (deployment, pr-review, iterate)
```

## Architecture Principles

1. **Building on Spec-Kit Foundation** - MultiAgent extends, never duplicates
2. **Immutable Tooling** - `.multiagent/` is read-only after init
3. **Specification-Driven** - Everything generated from Spec-Kit specs
4. **System Isolation** - Each system owns its domain
5. **Command Orchestration** - Commands can chain and invoke others
6. **Dual Output Pattern** - Spec docs + project infrastructure

## Current Status

### ✅ Completed
- Architecture documentation complete
- Spec-Kit foundation principle documented
- Visual mapping created
- Pattern documentation established
- Workflow generation strategy defined

### 🚧 In Progress
- Deployment system refactoring (10→3 scripts)
- PR-review consolidation (7→3 scripts)
- Iterate system subagent creation (5→2 scripts)

### 📅 Next Steps
1. Implement script consolidation per SYSTEM_VISUAL_MAP
2. Create missing subagents (iterate-coordinator)
3. Test complete workflow generation with Spec-Kit
4. Deploy to fresh project for validation

## Quick Reference

**Need to understand the foundation?**
→ Start with [core/SYSTEM_WORKFLOW_PATTERN.md](./core/SYSTEM_WORKFLOW_PATTERN.md) - THE BIBLE

**How does local storage work?** ⭐ NEW
→ Read [core/LOCAL_STORAGE_AND_CLI.md](./core/LOCAL_STORAGE_AND_CLI.md)

**Need to see the system visually?**
→ Check [core/SYSTEM_VISUAL_MAP.md](./core/SYSTEM_VISUAL_MAP.md)

**Working on patterns?**
→ Browse [patterns/](./patterns/)

**Implementing workflows?**
→ See [implementation/WORKFLOW_GENERATION_ARCHITECTURE.md](./implementation/WORKFLOW_GENERATION_ARCHITECTURE.md)

## The MultiAgent Mantra

```
Spec-Kit creates the vision
MultiAgent builds the reality

Spec-Kit writes the specification
MultiAgent generates the infrastructure

Together, they are complete
Separate, they are incomplete
```

This is THE BIBLE - all development follows these principles.