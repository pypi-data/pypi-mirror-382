# Deployment Commands

## Overview

The deployment subsystem provides 5 distinct commands for different deployment lifecycle stages:

| Command | Purpose | When to Use | Invokes |
|---------|---------|-------------|---------|
| `/deployment:deploy-prepare` | Generate deployment configs | After spec creation, before deployment | deployment-prep agent |
| `/deployment:deploy-validate` | Validate deployment readiness | Between prepare and run, before production | deployment-validator agent |
| `/deployment:deploy-run` | Execute local deployment | For local testing and development | deployment-runner agent (up only) |
| `/deployment:deploy` | Quick Vercel cloud deploy | For Vercel projects, cloud deployment | N/A (direct Vercel CLI) |
| `/deployment:prod-ready` | Production readiness scan | Before production deployment | production-specialist agent |

## Command Details

### 1. `/deployment:deploy-prepare [spec-directory]`

**Purpose**: Analyze specification and generate deployment configurations.

**What It Does**:
- Analyzes entire spec directory (spec.md, tasks.md, plan.md, data-model.md, contracts/)
- Detects project type and required services
- Generates `/deployment` directory with:
  - Dockerfile
  - docker-compose.yml
  - Kubernetes manifests (if applicable)
  - Environment templates

**Usage**:
```bash
/deployment:deploy-prepare specs/001-authentication-system
```

**When**: First step after spec creation, before any deployment.

---

### 2. `/deployment:deploy-validate`

**Purpose**: Validate deployment configurations are complete and ready.

**What It Does**:
- Verifies `/deployment` directory exists
- Checks Dockerfile syntax
- Validates docker-compose.yml structure
- Scans for security issues (exposed secrets)
- Validates environment variables
- Checks API endpoint definitions
- Runs production readiness checks

**Usage**:
```bash
/deployment:deploy-validate
```

**When**: After deploy-prepare, before deploy-run or production deployment.

---

### 3. `/deployment:deploy-run [action]`

**Purpose**: Execute and manage local deployment.

**Actions**:
- `up` (default) - Start all services with health checks
- `down` - Stop all services
- `restart` - Restart all services
- `logs` - View service logs
- `status` - Show running containers

**What It Does**:
- Verifies Docker availability
- Checks port conflicts
- Creates environment files from templates
- Starts/manages Docker containers
- Monitors service health
- Provides service URLs

**Usage**:
```bash
/deployment:deploy-run up        # Start services
/deployment:deploy-run logs      # View logs
/deployment:deploy-run down      # Stop services
```

**When**: After deploy-prepare and deploy-validate, for local testing.

---

### 4. `/deployment:deploy [production|preview|staging] [--platform=...]`

**Purpose**: Deploy to cloud platform (platform-agnostic).

**Supported Platforms**:
- Vercel (Next.js, frontend apps)
- Railway (full-stack, databases)
- Render (web services, APIs)
- Fly.io (global apps, edge)
- AWS Elastic Beanstalk (enterprise)
- Digital Ocean (simple apps)
- Docker (local/self-hosted fallback)

**What It Does**:
- Auto-detects deployment platform from config files
- Verifies git status and branch
- Runs tests before deployment
- Deploys using platform-specific CLI
- Manages environment variables per platform
- Performs post-deployment health checks
- Updates GitHub deployment status

**Platform Detection**:
1. Reads `deployment/config.json` or `deployment/platform.txt`
2. Checks for platform config files (vercel.json, railway.toml, render.yaml, etc.)
3. Falls back to Docker if no platform detected

**Usage**:
```bash
/deployment:deploy                          # Auto-detect platform, deploy to preview
/deployment:deploy production               # Deploy to production (auto-detect)
/deployment:deploy staging --platform=railway  # Deploy to Railway staging
/deployment:deploy production --platform=aws   # Deploy to AWS production
```

**When**: For cloud deployments to any supported platform.

**Note**: This is for **cloud deployments**. Use deploy-run for **local Docker** deployments.

---

### 5. `/deployment:prod-ready [--fix] [--verbose] [--test-only]`

**Purpose**: Comprehensive production readiness validation.

**Options**:
- `--fix` - Auto-fix critical mock implementations
- `--verbose` - Detailed analysis output
- `--test-only` - Skip mock detection, only run tests

**What It Does**:
- Runs production tests (./scripts/ops qa --production)
- Detects mock implementations in production code
- Validates environment configuration
- Checks security vulnerabilities
- Analyzes database connections
- Verifies external API integrations
- Generates production readiness report

**Usage**:
```bash
/deployment:prod-ready              # Standard scan
/deployment:prod-ready --fix        # Scan and auto-fix issues
/deployment:prod-ready --verbose    # Detailed output
```

**When**: Before deploying to production, to ensure no mock code or test data exists.

---

## Typical Deployment Workflow

### Local Development Flow
```bash
1. /deployment:deploy-prepare specs/001-*   # Generate configs
2. /deployment:deploy-validate              # Validate configs
3. /deployment:deploy-run up                # Start local services
4. /deployment:deploy-run logs              # Monitor services
5. /deployment:deploy-run down              # Stop when done
```

### Production Deployment Flow (Docker)
```bash
1. /deployment:deploy-prepare specs/001-*   # Generate configs
2. /deployment:prod-ready --verbose         # Check readiness
3. /deployment:deploy-validate              # Final validation
4. # Manual: Deploy to cloud provider
```

### Production Deployment Flow (Cloud Platform)
```bash
1. /deployment:deploy-prepare specs/001-*        # Generate configs
2. /deployment:prod-ready --fix                  # Check and fix issues
3. /deployment:deploy production                 # Auto-detect platform and deploy
# OR specify platform:
3. /deployment:deploy production --platform=railway
```

## Subsystem Integration

- **Core System**: Invokes `/deployment:deploy-prepare` during `/core:project-setup`
- **Testing System**: Tests run before `/deployment:deploy` and during `/deployment:prod-ready`
- **Security System**: Security scans run in `/deployment:deploy-validate` and `/deployment:prod-ready`
- **GitHub Workflows**: CI/CD pipelines use deploy commands for automated deployments

## Troubleshooting

### "deployment directory not found"
Run `/deployment:deploy-prepare specs/001-*` first.

### "Docker not available"
Install Docker Desktop or Docker Engine before using `/deployment:deploy-run`.

### "Port conflicts detected"
Stop conflicting services or modify ports in `deployment/docker/docker-compose.yml`.

### "Mock implementations found"
Run `/deployment:prod-ready --fix` to automatically replace mocks with production code.

## Related Documentation

- Deployment subsystem: `.multiagent/deployment/README.md`
- Production specialist agent: `.claude/agents/production-specialist.md`
- Deployment prep agent: `.claude/agents/deployment-prep.md`
- Deployment validator agent: `.claude/agents/deployment-validator.md`
