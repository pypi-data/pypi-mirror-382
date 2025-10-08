# MultiAgent Systems Visual Map

## System Architecture Overview

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

## Pattern Evolution Visualization

### Script-Heavy (Old Pattern) ❌
```
Command → Many Scripts → Templates with instructions → Output
         ↑
    Scripts do the work
```
**Examples**: pr-review (7 scripts), iterate (5 scripts)

### Hybrid (Transitional) ⚠️
```
Command → Some Scripts → Subagent → Output
         ↑                    ↑
    Setup tasks         Main work
```
**Example**: deployment (10 scripts but has subagent)

### Subagent-Driven (Target Pattern) ✅
```
Command → Subagent (with tools) → Minimal Scripts → Output
              ↑                           ↑
        Does most work            Only bulk/system ops
```
**Examples**: security (3 scripts), testing (3 scripts)

## Output Patterns

### Single Output (Old) ❌
```
pr-review → specs/XXX/feedback/
iterate   → specs/XXX/agent-tasks/
```

### Dual Output (Correct) ✅
```
security → specs/XXX/security/ (reports)
        → project-root/ (infrastructure)

deployment → specs/XXX/deployment/ (analysis)
          → deployment/ (configs)

testing → specs/XXX/testing/ (coverage)
       → tests/ (actual tests)
```

## Subagent Mapping

```
System          → Subagent(s)
─────────────────────────────────────
core            → (orchestrates all)
deployment      → deployment-prep ✅
                → deployment-runner ✅
                → deployment-validator ✅
testing         → backend-tester ✅
                → test-generator ✅
                → frontend-playwright-tester ✅
pr-review       → review-pickup ⚠️ (partial)
iterate         → None ❌ (needs one)
supervisor      → None (monitoring pattern)
security        → security-auth-compliance ✅
```

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

### 🟢 Already Good
- Security: Perfect pattern
- Testing: Good balance
- Core: Minimal by design

## Success Indicators

✅ **Good System**:
- 2-3 scripts max
- Clear subagent
- Dual output
- Templates as context
- Memory/logs tracking

⚠️ **Needs Work**:
- 5+ scripts
- No/partial subagent
- Single output only
- Templates with variables
- Missing memory/logs

## The Gold Standard: Security System

```
security/
├── scripts/          → Only 3 essential
│   ├── scan-mocks.sh (bulk scan - keep)
│   └── install-hooks.sh (system op - keep)
├── templates/        → Pure context/examples
└── subagent:         → Does ALL intelligent work
```

**This is the pattern all systems should follow!**