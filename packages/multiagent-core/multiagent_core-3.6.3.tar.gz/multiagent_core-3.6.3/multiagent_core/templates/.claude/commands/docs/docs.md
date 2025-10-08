---
allowed-tools: Bash
description: Universal documentation management system for any project
argument-hint: init | update | validate
---

User input:

$ARGUMENTS

# Documentation Management System

**Purpose**: Manage documentation for ANY project type with intelligent template filling and updates.

## Available Subcommands

- `/docs init` - Initialize and fill documentation
- `/docs update` - Update docs based on changes
- `/docs validate` - Check consistency and completeness

## Command Router

Parse the subcommand and route to appropriate handler:

```bash
# Extract subcommand from arguments
SUBCOMMAND=$(echo "$ARGUMENTS" | awk '{print $1}')
ARGS=$(echo "$ARGUMENTS" | cut -d' ' -f2-)

case "$SUBCOMMAND" in
  init)
    echo "Initializing documentation structure..."
    # Route to /docs init
    ;;
  update)
    echo "Updating existing documentation..."
    # Route to /docs update
    ;;
  validate)
    echo "Validating documentation consistency..."
    # Route to /docs validate
    ;;
  *)
    echo "Usage: /docs [init|update|validate] [options]"
    echo ""
    echo "Commands:"
    echo "  init     - Create and fill documentation structure"
    echo "  update   - Update docs based on code changes"
    echo "  validate - Check consistency and completeness"
    echo ""
    echo "Run '/docs <command> --help' for command-specific options"
    exit 1
    ;;
esac
```

## Documentation System Overview

The `/docs` command provides:

1. **Universal Templates** - Work for ANY project type
2. **Intelligent Filling** - Reads specs to fill placeholders
3. **Test Documentation** - Documents existing tests (doesn't create)
4. **Consistency Checking** - Validates across all docs
5. **Content Preservation** - Never deletes existing content

## Typical Workflow

```bash
# After creating project specs
/docs init

# After tests are built
/docs update

# Before deployment
/docs validate
```