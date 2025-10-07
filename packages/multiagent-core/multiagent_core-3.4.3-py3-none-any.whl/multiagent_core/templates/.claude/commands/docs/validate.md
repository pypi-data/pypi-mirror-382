---
allowed-tools: Task(docs-validate), Read, Grep
description: Validate documentation consistency and completeness
argument-hint: [--strict]
---

User input:

$ARGUMENTS

# Validate Documentation

**Purpose**: Check documentation consistency, completeness, and quality across all files.

**Instructions**:

Parse arguments and invoke the docs-validate subagent:

```
Arguments: $ARGUMENTS

Invoke docs-validate subagent with instructions:
   - Run any validation scripts if needed
   - Check all documentation files in /docs/
   - Apply strict validation if --strict provided
   - Read state from memory/ directory
   - Scan for remaining {{PLACEHOLDERS}}
   - Verify consistency across all docs
   - Check minimum quality standards
   - Generate detailed validation report

The docs-validate subagent will:
1. Run validation scripts (if they exist)
2. Scan for any remaining placeholders
3. Verify all templates are properly filled
4. Cross-reference project information
5. Check version consistency
6. Validate minimum section lengths
7. Ensure required sections present
8. Generate comprehensive report with fix suggestions

Return summary:
- Valid files: count
- Issues: count
- Completeness: percentage
- Status: PASS/FAIL
- Priority fixes: list
```

The subagent handles running scripts, consistency checking, and report generation.