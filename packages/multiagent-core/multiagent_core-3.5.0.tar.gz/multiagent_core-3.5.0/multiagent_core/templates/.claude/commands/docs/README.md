# Documentation Commands - Documentation Management

## Overview

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/docs:init` | Initialize and fill documentation for ANY project | After project setup, before development |
| `/docs:update` | Update existing docs based on code changes | After code changes, before commits |
| `/docs:validate` | Validate documentation consistency | Before releases, during reviews |
| `/docs:docs` | Universal documentation management | Wrapper for init/update/validate |

## Command Details

### 1. `/docs:init [--project-type <type>]`

**Purpose**: Initialize documentation structure and fill templates for any project.

**What It Does**:
1. Read project specifications
2. Detect project type (auto or specified)
3. Create documentation structure
4. Fill templates with project-specific content
5. Generate comprehensive, ready-to-use documentation

**Project Types**:
- `multiagent` - Multiagent orchestration system
- `web-app` - Web application
- `api` - REST/GraphQL API
- `library` - Reusable library/package
- `cli` - Command-line tool
- Auto-detect if not specified

**Usage**:
```bash
/docs:init                        # Auto-detect project type
/docs:init --project-type web-app # Specify type
/docs:init --project-type api     # API project
```

**Output**:
- `README.md` - Project overview
- `docs/` - Comprehensive documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `API.md` - API documentation (if applicable)

**Invokes**: docs-init agent

---

### 2. `/docs:update [--check-patterns]`

**Purpose**: Update existing documentation based on code changes and test structure.

**What It Does**:
1. Read test files created by testing system
2. Detect code changes since last update
3. Update documentation in-place
4. Preserve all existing content
5. Add new sections for new features

**Flags**:
- `--check-patterns` - Validate documentation patterns

**Usage**:
```bash
/docs:update                   # Update docs based on changes
/docs:update --check-patterns  # Update and validate
```

**Invokes**: docs-update agent

---

### 3. `/docs:validate [--strict]`

**Purpose**: Validate documentation consistency and completeness.

**What It Does**:
1. Check for unfilled placeholders ({{VARIABLE}})
2. Ensure cross-document consistency
3. Enforce quality standards
4. Generate detailed validation reports
5. Identify missing or outdated content

**Flags**:
- `--strict` - Enforce strict validation rules

**Usage**:
```bash
/docs:validate          # Standard validation
/docs:validate --strict # Strict mode
```

**Validation Checks**:
- ✅ No unfilled placeholders
- ✅ Cross-document links valid
- ✅ Code examples up-to-date
- ✅ API documentation matches code
- ✅ All sections complete

**Invokes**: docs-validate agent

---

### 4. `/docs:docs [init\|update\|validate]`

**Purpose**: Universal documentation management wrapper.

**What It Does**:
- Routes to appropriate subcommand
- Provides unified interface
- Simplifies documentation workflow

**Usage**:
```bash
/docs:docs init      # Same as /docs:init
/docs:docs update    # Same as /docs:update
/docs:docs validate  # Same as /docs:validate
```

---

## Typical Documentation Workflow

### New Project
```bash
1. # Complete project setup
2. /docs:init --project-type web-app
3. # Review generated docs
4. # Customize as needed
```

### During Development
```bash
1. # Make code changes
2. # Update tests
3. /docs:update
4. git commit  # Commit code and updated docs
```

### Before Release
```bash
1. /docs:validate --strict
2. # Fix any validation errors
3. /docs:update
4. # Final review
5. # Release
```

## Documentation Structure Generated

### Multiagent Project
```
docs/
├── overview/
│   ├── introduction.md
│   ├── architecture.md
│   └── quick-start.md
├── subsystems/
│   ├── core.md
│   ├── deployment.md
│   └── testing.md
├── workflows/
│   ├── development.md
│   └── deployment.md
└── api/
    └── reference.md
```

### Web App Project
```
docs/
├── getting-started.md
├── architecture.md
├── api/
│   ├── endpoints.md
│   └── authentication.md
├── deployment/
│   └── production.md
└── contributing.md
```

## Subsystem Integration

- **Core System**: Calls `/docs:init` during `/core:project-setup`
- **Testing System**: Test structure informs documentation
- **Deployment System**: Deployment docs auto-generated
- **GitHub System**: Contributing guide for PR process

## Related Documentation

- Documentation subsystem: `.multiagent/documentation/README.md`
- Docs-init agent: `.claude/agents/docs-init.md`
- Docs-update agent: `.claude/agents/docs-update.md`
- Docs-validate agent: `.claude/agents/docs-validate.md`
