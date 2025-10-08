# Deployment Preparation System

## Purpose

Generates platform-specific deployment configurations (Docker, Vercel, K8s, Railway, etc.) based on your spec requirements. Handles both config generation and actual deployment to cloud platforms.

## What It Does

1. **Analyzes spec** - Reads tasks.md to determine deployment target
2. **Generates configs** - Creates Dockerfile, docker-compose.yml, vercel.json, etc.
3. **Validates setup** - Ensures all required environment variables and configs exist
4. **Deploys to cloud** - Executes deployment to Vercel, Railway, AWS, etc.

## Agents Used

- **@claude/deployment-prep** - Analyzes spec and generates platform configs
- **@claude/deployment-validator** - Validates deployment readiness
- **@claude/deployment-runner** - Executes local deployments (Docker)

## Commands

- **`/deployment:deploy-prepare <spec-dir>`** - Generate deployment configs (Docker, K8s, etc.)
- **`/deployment:deploy-validate`** - Validate deployment configuration readiness
- **`/deployment:deploy-run [up|down|restart|logs]`** - Execute local deployment with Docker
- **`/deployment:deploy [production|preview]`** - Deploy to cloud platform (Vercel, Railway, AWS)
- **`/deployment:prod-ready [--fix] [--verbose]`** - Comprehensive production readiness scan

## Architecture

```
.claude/
├── agents/deployment/        # Deployment subagents
│   ├── deployment-prep.md   # Main prep agent
│   └── deployment-analyzer.md # Stack analyzer
└── commands/deployment/     # Commands
    └── deploy-prepare.md    # Main command

.multiagent/deployment/
├── scripts/                 # Generation scripts
│   └── generate-deployment.sh
├── templates/              # Deployment templates
│   ├── docker/            # Dockerfile templates
│   ├── compose/           # docker-compose templates
│   ├── k8s/              # Kubernetes manifests
│   ├── env/              # Environment configs
│   ├── nginx/            # Nginx configs
│   └── scripts/          # Deployment scripts
├── memory/                # Session memory
└── logs/                  # Generation logs
```

## How It Works

1. **Command Invocation**: User runs deployment preparation command
2. **Subagent Analysis**: deployment-prep agent analyzes tasks and project
3. **Stack Detection**: Automatically detects tech stack (Python, Node, etc.)
4. **Template Selection**: Chooses appropriate templates based on analysis
5. **Generation**: Creates deployment artifacts in `/deployment` directory

## Generated Output Structure

```
deployment/
├── docker/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── configs/
│   ├── .env.example
│   ├── .env.development
│   └── nginx.conf
└── scripts/
    ├── deploy.sh
    └── health-check.sh
```

## Intelligent Detection

The system automatically detects:
- **Language**: Python, JavaScript, Java, Go, etc.
- **Framework**: FastAPI, Express, React, Django, etc.
- **Services**: PostgreSQL, Redis, MongoDB, etc.
- **Architecture**: Monolith, microservices, serverless

## Usage

```bash
# Generate deployment configurations
multiagent deploy-prepare

# Generate for specific spec
multiagent deploy-prepare specs/001-build-a-complete
```

## Templates

Templates use placeholders that get replaced based on project analysis:
- `{{APP_NAME}}` - Application name from project
- `{{PORT}}` - Detected or default port
- `{{STACK}}` - Technology stack
- `{{SERVICES}}` - Required services

## Complements GitHub Actions

This system prepares artifacts that GitHub Actions uses but doesn't duplicate CI/CD logic:
- **We Generate**: Dockerfiles, configs, manifests
- **GitHub Does**: Build, test, deploy, validate

## Post-Generation Steps

After generation, you need to:

### 1. Update `.env` files with real values:
```bash
# Edit deployment/configs/.env.development
DATABASE_URL=      # Add your actual database URL
JWT_SECRET=        # Generate a secure secret
API_KEYS=          # Add actual API keys
WEBHOOK_SECRETS=   # Add webhook secrets from integrations
```

### 2. Adjust ports if needed:
- Check `docker-compose.yml` for port conflicts
- Update exposed ports based on your setup

### 3. Add secrets for production:
```bash
# Never commit these!
cp deployment/configs/.env.production .env.production.local
# Edit .env.production.local with real production values
```

### 4. Customize for your infrastructure:
- Update K8s namespace
- Adjust resource limits
- Configure ingress rules

## Session Memory

Each generation session is logged with:
- Timestamp
- Spec analyzed
- Stack detected
- Files generated
- Decisions made

This allows for consistent regeneration and debugging.

## Troubleshooting

Having deployment issues? Check our comprehensive guides:

- 📚 [Troubleshooting Index](docs/TROUBLESHOOTING_INDEX.md) - Start here!
- 🌊 [DigitalOcean Issues](docs/troubleshooting/digitalocean-droplet.md)
- ☁️ [AWS Issues](docs/troubleshooting/aws-common-issues.md)
- 🐳 [Docker Issues](docs/troubleshooting/docker-common-issues.md)
- ☸️ [Kubernetes Issues](docs/troubleshooting/kubernetes-common-issues.md)

Most common issues:
1. **Firewall blocking ports** - Check UFW and cloud firewall
2. **Binding to localhost** - Use 0.0.0.0 instead
3. **Missing env variables** - Check .env file loaded
4. **Health check failing** - Verify /health endpoint