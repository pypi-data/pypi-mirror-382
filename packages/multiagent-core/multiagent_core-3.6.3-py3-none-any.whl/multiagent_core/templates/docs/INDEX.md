# Architecture Documentation Index

**Last Updated**: 2025-09-29
**Status**: Complete Documentation Set

## Core Architecture Documents

### 🎯 Primary Documents

1. **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)**
   - Master architecture document
   - Core principles and patterns
   - System component overview
   - Anti-patterns and best practices

2. **[SYSTEM_WORKFLOW_PATTERN.md](./SYSTEM_WORKFLOW_PATTERN.md)**
   - The table-setting pattern
   - Separating mechanical from intelligence
   - Mise en place philosophy
   - Command orchestration patterns

3. **[SYSTEM_VISUAL_MAP.md](./SYSTEM_VISUAL_MAP.md)**
   - Visual system overview
   - Script count heat map
   - Maturity levels
   - Refactoring priorities

## Specialized Architecture

### 🔄 Pattern Documentation

4. **[SPECKIT_VS_MULTIAGENT_PATTERNS.md](./SPECKIT_VS_MULTIAGENT_PATTERNS.md)**
   - Comparison of approaches
   - Template-driven vs subagent-driven
   - When to use each pattern

5. **[SCRIPT_EVOLUTION_PATTERN.md](./SCRIPT_EVOLUTION_PATTERN.md)**
   - Evolution from scripts to subagents
   - The 3-script rule
   - Consolidation strategies

### 🚀 Implementation Guides

6. **[WORKFLOW_GENERATION_ARCHITECTURE.md](./WORKFLOW_GENERATION_ARCHITECTURE.md)**
   - How workflows are generated (not copied)
   - Template-based generation
   - Project-specific workflow creation

7. **[GIT_HOOKS_SYSTEM.md](./GIT_HOOKS_SYSTEM.md)**
   - Pre-commit hooks architecture
   - Security scanning integration
   - Mock detection and prevention

## Key Concepts

### The Table-Setting Pattern
```
Scripts (Mechanical) → Templates (Context) → Agents (Intelligence)
```

### The Golden Rule
**When you run a slash command, YOU are the agent**
- Scripts set the table
- Templates provide context
- Agents make decisions

### Target Pattern
All systems should follow the **Security System Gold Standard**:
- 2-3 scripts maximum
- Clear subagent ownership
- Dual output pattern
- Templates as pure context

### Script Count Goals
```
🟩 IDEAL: 2-3 scripts (security, testing, core)
🟧 ACCEPTABLE: 3-4 scripts (supervisor)
🟥 NEEDS REFACTORING: 5+ scripts (deployment, pr-review, iterate)
```

## Architecture Principles

1. **Immutable Tooling** - `.multiagent/` is read-only after init
2. **Specification-Driven** - Everything generated from specs
3. **System Isolation** - Each system owns its domain
4. **Command Orchestration** - Commands can chain and invoke others
5. **Dual Output Pattern** - Spec docs + project infrastructure

## Current Status

### ✅ Completed
- Architecture documentation complete
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
3. Test complete workflow generation
4. Deploy to fresh project for validation

## Quick Reference

**Need to understand the system?**
→ Start with [SYSTEM_VISUAL_MAP.md](./SYSTEM_VISUAL_MAP.md)

**Working on patterns?**
→ Read [SYSTEM_WORKFLOW_PATTERN.md](./SYSTEM_WORKFLOW_PATTERN.md)

**Implementing workflows?**
→ See [WORKFLOW_GENERATION_ARCHITECTURE.md](./WORKFLOW_GENERATION_ARCHITECTURE.md)

**Comparing approaches?**
→ Check [SPECKIT_VS_MULTIAGENT_PATTERNS.md](./SPECKIT_VS_MULTIAGENT_PATTERNS.md)