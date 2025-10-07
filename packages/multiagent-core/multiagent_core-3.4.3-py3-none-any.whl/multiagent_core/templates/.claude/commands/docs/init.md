---
allowed-tools: Task(docs-init), Bash, Write, Edit
description: Initialize documentation structure and fill templates for any project
argument-hint: [--project-type <type>]
---

User input:

$ARGUMENTS

# Initialize Documentation System

**Purpose**: Create complete documentation structure and fill all templates intelligently in one operation.

**Instructions**:

Parse arguments and invoke the docs-init subagent:

```
Arguments: $ARGUMENTS

Invoke docs-init subagent with instructions:

1. Run the setup script:
   - Execute: bash .multiagent/documentation/scripts/create-structure.sh
   - Creates basic /docs/ directory structure
   - Creates minimal README.md template with standard placeholders

2. Detect project type:
   - Analyze /specs/ folder to understand project
   - Identify: Backend API, Frontend, Full Stack, CLI, Library, etc.
   - Determine which documentation is relevant

3. Create adaptive documentation:
   - Fill placeholders in existing templates
   - CREATE additional files based on project type:
     * Backend: API docs, database docs, deployment docs
     * Frontend: Component docs, styling, build docs
     * CLI: Command reference, configuration docs
     * Library: API reference, integration guides
   - Skip irrelevant documentation sections

4. Fill with rich content:
   - Use standard placeholders (see PLACEHOLDER_REFERENCE.md)
   - Generate comprehensive content from specs
   - Ensure no {{PLACEHOLDER}} remains unfilled

Return summary:
- Structure created: true/false
- Documents filled: count
- Templates used: list
- Completion: percentage
```

The subagent handles both running the script AND filling the templates intelligently.