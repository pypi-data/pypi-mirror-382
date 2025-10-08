# Slash Command Design Pattern

**Author**: @claude
**Date**: 2025-09-30
**Status**: Active Pattern

## Philosophy

**Simple Command → Powerful Agent**

The best slash commands are entry points, not complex workflows. All intelligence lives in the subagent.

## The Pattern

```
┌─────────────────┐
│ Slash Command   │  ← Simple entry point (1 file, ~50 lines)
│ /github:pr-review│
└────────┬────────┘
         │ invokes
         ↓
┌─────────────────┐
│ Subagent        │  ← All the intelligence
│ judge-architect │  • Reads from GitHub
│                 │  • Analyzes against specs
│                 │  • Follows templates
│                 │  • Runs scripts
│                 │  • Outputs to correct location
└─────────────────┘
```

## Case Study: PR Review Simplification

### ❌ Before (Complex Multi-Step)
```
/pr-review:pr 9        → pr-session-setup subagent
                         ↓ creates session files
/pr-review:judge 9     → judge-architect subagent
                         ↓ analyzes and decides
/pr-review:tasks 9     → task-assignment-router
                         ↓ routes to agents
```
**Result**: 3 commands, 3 subagents, complex state management

### ✅ After (Streamlined)
```
/github:pr-review 9    → judge-architect subagent
                         ↓ does everything
```
**Result**: 1 command, 1 subagent, clean output

## What Changed

**Removed:**
- `pr-session-setup.md` - Session management overhead
- `review-pickup.md` - Unnecessary abstraction
- `pr-plan-generator.md` - Judge does this
- `task-assignment-router.md` - Judge does this
- `/pr-review:pr` command - Not needed
- `/pr-review:tasks` command - Not needed
- `/pr-review:plan` command - Not needed

**Kept:**
- `judge-architect.md` - One agent with all logic
- `/github:pr-review` - One entry point

## Design Principles

### 1. **One Command = One Outcome**

Commands fall into two categories:

**A. Output-Generating Commands**
```markdown
✅ /github:pr-review <PR#>
   → Analyze PR, generate feedback in spec directory

✅ /docs:init
   → Generate documentation structure

✅ /deployment:deploy-prepare [spec-dir]
   → Create deployment configurations
```

**B. Analysis/Review Commands** (Non-Output)
```markdown
✅ /specify:clarify [topic]
   → Chat-based clarification (no files generated)

✅ /specify:analyze [spec-dir]
   → Review existing spec (report to chat)

✅ /review:code [path]
   → Code review feedback (conversational)
```

**Anti-Pattern:**
```markdown
❌ /pr-review:setup → /pr-review:analyze → /pr-review:route
   → Too many steps, too much complexity
```

### 2. **Subagents Are Smart, Commands Are Simple**

**Command File (~50 lines)**:
```markdown
---
allowed-tools: Task(judge-architect)
description: Analyze Claude Code PR review and generate actionable feedback
---

Invoke judge-architect with PR number.
```

**Subagent File (comprehensive)**:
- All the logic
- Template structure
- Script execution
- Error handling
- Output management

### 3. **Scripts Are Helpers, Not Required**

Subagents can:
- Run scripts for bulk operations
- Use templates for consistency
- Process multiple files at once
- Create structured output

But they don't NEED scripts. Scripts are just helpers for:
- Batch processing
- Complex analysis across many files
- Structured directory creation

### 4. **Output Goes Where It Belongs**

```
✅ specs/005/pr-feedback/session-{timestamp}/
   → Feedback lives with the spec

❌ .multiagent/github/pr-review/sessions/
   → Global state, hard to find
```

## Implementation Checklist

When creating a new slash command:

- [ ] **Is this really needed?** Could it be a subagent improvement instead?
- [ ] **One clear outcome?** Command does ONE thing well
- [ ] **Subagent handles logic?** All intelligence in the subagent
- [ ] **Simple invocation?** Command just passes arguments to subagent
- [ ] **Correct output location?** Files go where they belong (spec dirs, not global)
- [ ] **Scripts are optional?** Subagent can work without them

## Real-World Examples

### Example 1: Documentation Management ✅

**Command**: `/docs init`

**What it does**:
1. Invokes `docs-init` subagent
2. Subagent reads spec
3. Runs `create-structure.sh` script (helper)
4. Fills templates with content
5. Outputs to project root

**Why it works**: One command, one clear outcome, subagent handles all logic

### Example 2: PR Review ✅

**Command**: `/github:pr-review <PR#>`

**What it does**:
1. Invokes `judge-architect` subagent
2. Subagent reads from GitHub directly
3. Analyzes against spec
4. Creates feedback files in spec directory

**Why it works**: Simplified from 3 commands to 1, all logic in subagent

### Example 3: Project Setup ✅

**Command**: `/core:project-setup [spec-dir]`

**What it does**:
1. Analyzes first spec (001-*)
2. Invokes other slash commands as needed
3. Configures entire project
4. Generates setup report

**Why it works**: Orchestrates other commands, but each does one thing

### Example 4: Specify Integration (Analysis Commands) ✅

**Command**: `/specify:clarify [topic]`

**What it does**:
1. Invokes conversational analysis
2. Asks clarifying questions
3. Outputs insights to chat (no files)
4. Helps refine understanding

**Why it works**: Not everything needs file output - some commands facilitate thinking

**Command**: `/specify:analyze [spec-dir]`

**What it does**:
1. Reads existing spec files
2. Analyzes completeness and coherence
3. Reports findings to chat
4. Suggests improvements

**Why it works**: Review commands enhance existing work without generating artifacts

## Anti-Patterns to Avoid

### ❌ Command with Complex Logic
```markdown
# DON'T DO THIS
Run script X, then parse output, then if Y do Z, else...
```

### ❌ Multi-Step Workflows
```markdown
# DON'T DO THIS
Step 1: /command:setup
Step 2: /command:process
Step 3: /command:finalize
```

### ❌ Global State Management
```markdown
# DON'T DO THIS
Create session in .multiagent/sessions/
Store state for later commands
```

### ✅ Simple Delegation
```markdown
# DO THIS
Invoke subagent-name with these arguments.
Subagent handles everything.
```

## Migration Guide

If you have a complex command workflow:

1. **Identify the core outcome** - What's the ONE thing this achieves?
2. **Consolidate subagents** - Can one smart agent do it all?
3. **Move logic to subagent** - Commands should just invoke
4. **Fix output location** - Spec dirs, not global state
5. **Archive legacy** - Move old complexity to .archive/

## Benefits

✅ **Easier to understand** - One command = one outcome
✅ **Easier to maintain** - Logic in one place
✅ **Easier to debug** - No complex state
✅ **Easier to extend** - Improve the subagent
✅ **Better UX** - Users run one command, not three

## Command Categories Reference

### Output-Generating Commands
These commands create files, configurations, or structured artifacts:
- `/docs:init` - Creates documentation structure
- `/deployment:deploy-prepare` - Generates deployment configs
- `/testing:test-generate` - Creates test files
- `/github:pr-review` - Generates feedback files
- `/core:project-setup` - Outputs setup report

### Analysis/Review Commands
These commands provide insights, reviews, and conversational guidance:
- `/specify:clarify` - Conversational clarification
- `/specify:analyze` - Reviews existing specs
- `/review:code` - Code quality feedback
- `/supervisor:mid` - Progress check (chat report)
- `/docs:validate` - Validation feedback

### Orchestration Commands
These commands coordinate multiple systems:
- `/core:project-setup` - Invokes multiple commands
- `/iterate:sync` - Syncs spec ecosystem
- `/deployment:deploy` - Full deployment workflow

## Integration with Spec-Kit (Specify)

MultiAgent commands enhance Specify workflows:

```
Specify Creates          →  MultiAgent Enhances
───────────────────────     ───────────────────────
/specify → spec.md       →  /specify:clarify (review)
/plan → plan.md          →  /specify:analyze (validate)
/tasks → tasks.md        →  /iterate:tasks (layer tasks)
                         →  /core:project-setup (implement)
```

**Key Principle**: MultiAgent reads Specify outputs, never recreates them.

## Worktree Integration

Commands work seamlessly with agent worktrees:

```bash
# Agent in worktree: ../project-claude (agent-claude-architecture)
cd ../project-claude

# Run commands in isolated environment
/docs:init                    # Works in worktree
/deployment:deploy-prepare    # Reads spec, outputs to worktree
/specify:analyze specs/001    # Reviews work in worktree

# Changes stay isolated until PR merge
git push origin agent-claude-architecture
gh pr create
```

**Symlink Strategy**: Worktrees use symlinks to see main's layered-tasks.md
```bash
# In worktree specs directory
./setup-worktree-symlinks.sh
# Creates: layered-tasks-main.md -> main repo's layered-tasks.md
```

## Conclusion

**The best slash command is barely there.**

It just invokes a smart subagent that does all the work.

### Command Design Checklist
- [ ] **Clear purpose** - Output generation OR analysis/review
- [ ] **Simple invocation** - One command, clear arguments
- [ ] **Smart subagent** - All logic in agent, not command
- [ ] **Correct output** - Files in spec dirs, or chat for reviews
- [ ] **Worktree compatible** - Works in isolated environments
- [ ] **Specify integration** - Reads outputs, doesn't recreate

---

*This pattern emerged from simplifying the PR review workflow from 3 commands to 1.*
*See: `.archive/claude/agents/pr-review-legacy/` for the old complexity we removed.*
