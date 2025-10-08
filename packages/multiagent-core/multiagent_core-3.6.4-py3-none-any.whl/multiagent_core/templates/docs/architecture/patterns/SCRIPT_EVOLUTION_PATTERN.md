# Script Evolution: From Spec-Kit to MultiAgent

## The Key Insight

**Subagents can replace many scripts** because they have powerful tools (Read, Write, Edit, Bash) that can do what scripts do. The evolution shows a shift from script-heavy to agent-intelligent systems.

## Script Usage Patterns

### Spec-Kit: Scripts Do Essential Setup

```bash
# create-new-feature.sh does things Claude CAN'T easily do:
- Find repository root (complex logic)
- Generate sequential branch names (001, 002, 003)
- Create git branches
- Initialize directory structure
- Return JSON for parsing
```

**Why Scripts in Spec-Kit?**
1. **No subagents** - Claude must rely on scripts
2. **Complex git operations** - Finding repo root, branch management
3. **State management** - Tracking feature numbers
4. **Structured output** - JSON for reliable parsing

### MultiAgent: Subagents Replace Most Scripts

**What Subagents CAN Do (No Script Needed):**
```bash
# Subagent with tools can:
- Read files (Read tool)
- Write files (Write tool)
- Create directories (Bash: mkdir)
- Check file existence (Bash: test -f)
- Parse content (native intelligence)
- Generate configs (intelligent creation)
```

**What Still Needs Scripts:**
```bash
# Scripts still valuable for:
- Bulk operations (scan 100+ files)
- Complex git operations
- System-level tasks
- Performance-critical operations
- Reusable workflows
```

## Evolution Examples

### Example 1: Creating Project Structure

#### Spec-Kit Approach
```bash
# Script: create-new-feature.sh
- Finds repo root (complex logic)
- Creates specs/001-feature/
- Initializes spec.md
- Returns JSON with paths
```

#### MultiAgent Approach (No Script Needed)
```python
# Subagent uses tools:
Bash("mkdir -p specs/001-feature")
Write("specs/001-feature/spec.md", content)
# No script required!
```

### Example 2: Security Setup

#### If Using Scripts (Traditional)
```bash
# setup-security.sh
- Copy .gitignore template
- Create .env.example
- Install git hooks
- Generate workflows
```

#### Using Subagent (MultiAgent)
```python
# security-auth-compliance agent:
Read(".multiagent/security/templates/.gitignore")
Write(".gitignore", security_patterns)
Write(".env.example", safe_template)
Bash("chmod +x .git/hooks/pre-push")
# Agent does it all!
```

## When Scripts Are Still Valuable

### 1. Bulk Operations
```bash
# scan-mocks.sh - Scanning hundreds of files
find . -type f -name "*.py" | xargs grep -l "mock\|Mock\|stub"
# Much faster than agent doing Read() 100 times
```

### 2. Complex Git Operations
```bash
# find-pr-spec-directory.sh
gh pr view $PR --json files | jq -r '.files[].path' | \
  grep "^specs/" | head -1 | cut -d'/' -f1-2
# Complex piping and git/GitHub integration
```

### 3. System Operations
```bash
# Scripts can do things agents can't:
- Change file permissions recursively
- Set up system services
- Configure environment variables globally
```

## The Pattern Evolution

### Phase 1: Spec-Kit (Script-Heavy)
```
Command → Script (setup) → Template (instructions) → Output
         ↑
    Scripts do the work
```

### Phase 2: Hybrid (Some Scripts)
```
Command → Some Scripts → Subagent → Output
         ↑                    ↑
    Setup only          Does main work
```

### Phase 3: MultiAgent (Script-Light)
```
Command → Subagent (with tools) → Output
              ↑
    Agent does almost everything
    Scripts only for bulk/special ops
```

## Decision Framework

### Use Scripts When:
1. **Performance matters** - Scanning many files
2. **System integration** - Git, GitHub API, OS operations
3. **Reusable workflows** - Common operations across systems
4. **Bulk operations** - Batch processing
5. **Complex piping** - Unix philosophy chains

### Use Subagents When:
1. **Intelligence needed** - Analysis, decisions
2. **File operations** - Read, write, edit individual files
3. **Adaptability required** - Different per project
4. **Context matters** - Reading templates, understanding structure
5. **Generation tasks** - Creating new content

## Real-World Examples

### Deployment System
```bash
# Still uses generate-deployment.sh for:
- Bulk template processing
- Complex stack detection

# But subagent does:
- Reading all spec files
- Making architectural decisions
- Adapting templates intelligently
```

### Security System
```bash
# Minimal scripts (just scan-mocks.sh)
# Subagent handles everything else:
- Template deployment
- File creation
- Hook installation
- Workflow generation
```

## The Trend

**Moving from scripts to subagents** because:
1. Subagents are more flexible
2. Less code to maintain
3. More intelligent adaptation
4. Better error handling
5. Unified tool usage

**But keeping scripts for**:
1. Performance-critical operations
2. System-level integrations
3. Reusable bulk operations

## Summary

The evolution from spec-kit to MultiAgent shows:
- **Spec-Kit**: Scripts do setup work, templates have instructions
- **MultiAgent**: Subagents replace most scripts, templates provide context

Scripts aren't eliminated - they're **optimized** for what they do best:
- **Bulk operations** (faster than agents)
- **System integration** (git, OS, APIs)
- **Reusable workflows** (common patterns)

Subagents take over what they do best:
- **Intelligent generation**
- **Adaptive decisions**
- **File manipulation**
- **Context understanding**

This is the natural evolution: from script-heavy procedural systems to agent-intelligent adaptive systems.