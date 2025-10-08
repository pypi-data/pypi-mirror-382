---
allowed-tools: Task(docs-update), Read, Edit, Glob
description: Update existing documentation based on code changes and test structure
argument-hint: [--check-patterns]
---

User input:

$ARGUMENTS

# Update Documentation

**Purpose**: Update existing documentation to reflect code changes and document existing test structure.

**Instructions**:

Parse arguments and invoke the docs-update subagent:

```
Arguments: $ARGUMENTS

Invoke docs-update subagent with instructions:
   - Check if any update scripts need to run first
   - Scan existing documentation in /docs/
   - Read test structure from /tests/ directory
   - Check for pattern changes if --check-patterns provided
   - Document existing tests from testing command center
   - Parse test organization and extract commands
   - Detect code changes by comparing specs
   - Update documentation in-place (preserve all content)
   - Track all updates in memory/ state files

The docs-update subagent will:
1. Run any necessary update scripts (if they exist)
2. Read test files created by testing command center
3. Parse test organization and structure
4. Detect changes in specs and code patterns
5. Update outdated information while preserving content
6. Maintain cross-references
7. Log all changes in update-history.json

Return summary:
- Files updated: count
- Files unchanged: count
- Test docs updated: true/false
- Content preserved: all
```

The subagent handles running scripts, pattern recognition, and content updates.