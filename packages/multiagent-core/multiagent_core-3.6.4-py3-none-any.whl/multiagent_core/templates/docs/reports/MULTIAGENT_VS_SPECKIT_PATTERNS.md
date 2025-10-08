# MultiAgent Core vs SpecKit - Architecture Comparison

**Date**: 2025-10-06

## Key Insight

SpecKit and MultiAgent Core serve **different purposes** and have **different capabilities**:

### SpecKit = Setup & Planning Framework
- **Purpose**: Create specs, plans, tasks
- **Agent Model**: Single main agent (no subagents)
- **Pattern**: Script → JSON → Agent (necessary because agent needs handoff)
- **Stops at**: Planning phase

### MultiAgent Core = Execution & Automation Framework
- **Purpose**: Take plans and EXECUTE them
- **Agent Model**: Sophisticated subagent system with full tool access
- **Pattern**: Slash command → Subagent (no handoff needed)
- **Goes from**: Planning → Implementation → Deployment → Testing

---

## Why SpecKit Uses JSON Handoff Pattern

**SpecKit doesn't have subagents**, so:
1. Script does mechanical work (create dirs, copy templates)
2. Script outputs JSON to stdout
3. Main agent captures JSON from stdout
4. Main agent uses paths from JSON to do intelligence work

**Example from issue #11:**
```bash
# Script creates structure, outputs JSON
create-new-feature.sh --json "description"
# Output: {"BRANCH_NAME":"001-feature","SPEC_FILE":"/path/spec.md"}

# Main agent captures JSON, reads template, fills it in
```

---

## Why MultiAgent Core Doesn't Need This

**We have sophisticated subagents with full tool access:**

### Subagent Capabilities
- ✅ **Read tool** - Read any file directly
- ✅ **Write tool** - Create/write files
- ✅ **Edit tool** - Modify existing files
- ✅ **Bash tool** - Execute commands, create dirs, run scripts
- ✅ **Grep/Glob tools** - Search files
- ✅ **Task tool** - Spawn other subagents

### Our Pattern (Simpler & More Powerful)
```bash
# Slash command directly invokes subagent
/deployment:deploy-prepare 005-feature

# Subagent does EVERYTHING:
1. Read spec files (Read tool)
2. Run validation scripts (Bash tool)
3. Create directories (Bash mkdir)
4. Analyze architecture (intelligence)
5. Generate configs (Write tool)
6. Validate output (Bash/Read tools)
```

**No JSON handoff needed** - subagent has all the tools it needs!

---

## What Scripts We Actually Need

### ✅ KEEP - Bulk/Mechanical Operations

**1. Bulk File Scanning**
- `scan-mocks.sh` - Scan many files for patterns (faster than subagent looping)
- `scan-secrets.sh` - Secret detection across codebase

**2. Git Operations**
- `setup-spec-worktrees.sh` - Create multiple git worktrees
- `setup-worktree-symlinks.sh` - Symlink setup

**3. Docker Commands**
- `run-local-deployment.sh` - Execute docker-compose up/down

**4. System Validation**
- `check-project-config.sh` - Validate prerequisites
- `install-dependencies.sh` - Run npm/pip install

**5. Monitoring Scripts**
- `start-verification.sh` - Gather git stats
- `mid-monitoring.sh` - Progress monitoring
- `end-verification.sh` - Completion validation

**Total: ~10-15 scripts** (all mechanical/bulk operations)

### ❌ REMOVE - Intelligence Work

**These duplicate what subagents already do better:**
- ❌ `generate-deployment.sh` - Subagent analyzes and generates
- ❌ `generate-tests.sh` - Subagent creates tests
- ❌ `process-pr-feedback.sh` - Subagent analyzes PRs
- ❌ `layer-tasks.sh` - Subagent organizes tasks
- ❌ `parse-review.sh` - Subagent parses comments
- ❌ All analysis/generation scripts

**Total: ~32 scripts to archive**

---

## Slash Command Best Practices

### ✅ Good Pattern (Current)
```markdown
---
description: Generate deployment configs
---

1. Determine spec directory
2. Run scan-mocks.sh for validation
3. Check git status
4. Invoke deployment-prep subagent:
   - Subagent reads all spec files
   - Subagent analyzes architecture
   - Subagent generates configs
   - Subagent validates output
5. Report results
```

### ❌ Bad Pattern (Unnecessary)
```markdown
---
description: Generate deployment configs
---

1. Run setup-deployment.sh --json
2. Parse JSON output
3. Pass JSON to subagent
4. Subagent uses JSON paths...
```

**Why bad?** Subagent can find files itself using Bash/Read tools!

---

## The Division of Labor

### SpecKit's Strength
- ✅ Creating well-structured specs and plans
- ✅ Standardized documentation
- ✅ Planning workflow

### MultiAgent Core's Strength
- ✅ **EXECUTING** those plans with subagents
- ✅ Parallel agent coordination via worktrees
- ✅ Automated testing, deployment, security
- ✅ GitHub PR automation
- ✅ Production readiness validation

---

## Conclusion

**SpecKit uses JSON handoff because it must** - it doesn't have subagents with tool access.

**MultiAgent Core doesn't need it** - our subagents are sophisticated enough to:
1. Find files themselves
2. Read and analyze content
3. Execute scripts when needed
4. Generate outputs
5. Validate results

**Keep scripts only for truly mechanical/bulk operations.** Everything else, let subagents handle - they're better at it!

---

## Action Items

1. ✅ Archive 32 intelligence scripts
2. ✅ Keep 10-15 mechanical/bulk operation scripts
3. ✅ Slash commands continue invoking subagents directly (already correct)
4. ❌ Don't add JSON handoff pattern (adds no value for us)

**Result**: Simpler, more maintainable, leverages subagent capabilities fully.
