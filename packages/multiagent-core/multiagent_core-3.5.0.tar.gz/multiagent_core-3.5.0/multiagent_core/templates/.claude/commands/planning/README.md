# Planning Commands - Specification & Task Generation

## Overview

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/planning:plan-generate` | Generate detailed technical docs from PROJECT_PLAN.md | After vision document created |
| `/planning:plan` | Add technical implementation details to specs | When specs need technical depth |
| `/planning:tasks` | Generate implementation tasks from plan | After plan.md completed |

## Command Details

### 1. `/planning:plan-generate [--from-vision\|--fresh-analysis] [domain]`

**Purpose**: Generate detailed technical documentation from PROJECT_PLAN.md vision.

**What It Does**:
- Reads PROJECT_PLAN.md vision document
- Generates comprehensive technical specifications
- Creates data models, API contracts, architecture diagrams
- Produces implementation roadmaps

**Flags**:
- `--from-vision` - Generate from existing PROJECT_PLAN.md
- `--fresh-analysis` - Re-analyze and regenerate
- `[domain]` - Optional domain focus (e.g., "authentication", "payments")

**Usage**:
```bash
/planning:plan-generate --from-vision
/planning:plan-generate --fresh-analysis authentication
```

---

### 2. `/planning:plan [tech stack and implementation requirements]`

**Purpose**: Wrapper for spec-kit's /plan command - adds technical implementation details.

**What It Does**:
- Enhances existing specs with technical details
- Defines tech stack choices
- Specifies implementation patterns
- Documents architectural decisions

**Usage**:
```bash
/planning:plan "React, TypeScript, FastAPI, PostgreSQL"
/planning:plan "Next.js 14, Supabase, Vercel deployment"
```

---

### 3. `/planning:tasks [optional: specific feature or "all"]`

**Purpose**: Wrapper for spec-kit's /tasks command - generates implementation tasks.

**What It Does**:
- Reads plan.md specifications
- Generates actionable tasks
- Creates tasks.md in spec directory
- Organizes by implementation phases

**Usage**:
```bash
/planning:tasks                # Generate all tasks
/planning:tasks authentication # Tasks for specific feature
/planning:tasks all            # Explicit all tasks
```

---

## Typical Planning Workflow

### From Vision to Implementation
```bash
1. # Create PROJECT_PLAN.md with vision
2. /planning:plan-generate --from-vision
3. # Review generated technical specs
4. /planning:plan "Tech stack choices"
5. /planning:tasks all
6. /iterate:tasks [spec-directory]
```

### Enhancing Existing Specs
```bash
1. # Review existing spec.md
2. /planning:plan "Additional technical details"
3. /planning:tasks authentication
4. # Review and adjust tasks.md
```

## Subsystem Integration

- **Core System**: Planning runs before `/core:project-setup`
- **Iterate System**: Tasks from planning feed into `/iterate:tasks`
- **Documentation System**: Specs become basis for docs
- **Deployment System**: Technical details guide deployment configs

## Related Documentation

- SpecKit documentation: External SpecKit tool
- Iterate subsystem: `.multiagent/iterate/README.md`
- Documentation subsystem: `.multiagent/documentation/README.md`
