---
allowed-tools: Bash(*), Read(*), mcp__github(*), Task(*)
description: Deploy to cloud platform (Vercel, AWS, Railway, Render, etc.)
argument-hint: [production|preview|staging] [--platform=vercel|aws|railway|render]
---

# Deploy Command - Cloud Deployment

## Context
- Current branch: !`git branch --show-current`
- Project type: @package.json
- Deployment config: @deployment/
- Git status: !`git status --short`

## Your Task

When user runs `/deploy $ARGUMENTS`, deploy the application to the configured cloud platform:

### Step 1: Parse Arguments
Extract from $ARGUMENTS:
- Environment: preview (default), staging, or production
- Platform: --platform=vercel|aws|railway|render|fly|digital-ocean (or auto-detect)
- Options: --skip-tests flag

### Step 2: Pre-deployment Checks
1. Check for uncommitted changes:
   ```bash
   git status --porcelain
   ```
   If changes exist, warn user and ask to commit or stash.

2. Verify on correct branch:
   - preview/staging: any branch allowed
   - production: must be on main branch

### Step 3: Run Tests (unless --skip-tests)
```bash
# Check if tests exist and run them
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  npm test
elif [ -f "requirements.txt" ] && [ -d "tests" ]; then
  pytest
fi
```

### Step 4: Detect Deployment Platform
Check deployment configuration to determine platform:
1. Read `deployment/config.json` or `deployment/platform.txt`
2. Check for platform-specific files:
   - `vercel.json` → Vercel
   - `railway.json` or `railway.toml` → Railway
   - `render.yaml` → Render
   - `fly.toml` → Fly.io
   - `Dockerrun.aws.json` → AWS Elastic Beanstalk
   - `.platform/` directory → AWS
3. Check environment variables: `DEPLOYMENT_PLATFORM`
4. If none found, ask user or default to Docker deployment

### Step 5: Deploy to Selected Platform

Based on detected or specified platform, execute appropriate deployment:

#### Vercel
```bash
# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
  npm install -g vercel
fi

# Deploy
if [[ "$ENVIRONMENT" == "production" ]]; then
  DEPLOYMENT_URL=$(vercel --prod --token=$VERCEL_TOKEN)
else
  DEPLOYMENT_URL=$(vercel --token=$VERCEL_TOKEN)
fi
```

#### Railway
```bash
# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
  npm install -g @railway/cli
fi

# Deploy
railway up --environment $ENVIRONMENT
DEPLOYMENT_URL=$(railway domain)
```

#### Render
```bash
# Check if render CLI is installed
if ! command -v render &> /dev/null; then
  curl -fsSL https://render.com/install | sh
fi

# Deploy
render deploy --environment $ENVIRONMENT
DEPLOYMENT_URL=$(render info --format json | jq -r '.url')
```

#### Fly.io
```bash
# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
  curl -L https://fly.io/install.sh | sh
fi

# Deploy
flyctl deploy --app $APP_NAME --env $ENVIRONMENT
DEPLOYMENT_URL=$(flyctl info --json | jq -r '.Hostname')
```

#### AWS (Elastic Beanstalk)
```bash
# Check if AWS CLI and EB CLI are installed
if ! command -v eb &> /dev/null; then
  pip install awsebcli
fi

# Deploy
eb deploy $ENVIRONMENT
DEPLOYMENT_URL=$(eb status | grep CNAME | awk '{print $2}')
```

#### Digital Ocean App Platform
```bash
# Use doctl CLI
if ! command -v doctl &> /dev/null; then
  snap install doctl
fi

# Deploy
doctl apps create-deployment $APP_ID
DEPLOYMENT_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)
```

#### Docker Deployment (Fallback)
```bash
# If no platform detected, use Docker deployment
echo "No cloud platform detected, using Docker deployment"
# Invoke deploy-run command for local/Docker deployment
/deployment:deploy-run up
```

### Step 6: Platform-Agnostic Post-Deployment
Regardless of platform:

1. **Verify deployment health:**
```bash
# Wait for deployment to be ready
sleep 10

# Check health endpoint
curl -f "${DEPLOYMENT_URL}/api/health" || curl -f "${DEPLOYMENT_URL}/health" || echo "⚠️ No health endpoint found"
```

2. **Configure environment variables (platform-specific):**
```bash
# Each platform has its own method - use appropriate CLI or dashboard
echo "Configure environment variables in platform dashboard:"
echo "Platform: $PLATFORM"
echo "Environment: $ENVIRONMENT"
```

### Step 7: Update GitHub Deployment Status
```bash
# Create deployment record
gh api repos/:owner/:repo/deployments \
  -f ref="$(git rev-parse HEAD)" \
  -f environment="${ENVIRONMENT}" \
  -f description="Deployed to Vercel" \
  -f production_environment=$([[ "$ENVIRONMENT" == "production" ]] && echo "true" || echo "false")
```

### Step 8: Comment on PR (if applicable)
```bash
# If on a PR branch
if [ -n "$PR_NUMBER" ]; then
  gh pr comment $PR_NUMBER --body "🚀 Deployed to ${ENVIRONMENT} on ${PLATFORM}: ${DEPLOYMENT_URL}"
fi
```

### Step 9: Provide Platform-Agnostic Summary

Output deployment summary:
```
✅ Deployment Complete!

Platform: ${PLATFORM}
Environment: ${ENVIRONMENT}
URL: ${DEPLOYMENT_URL}
Branch: $(git branch --show-current)
Commit: $(git rev-parse --short HEAD)

Features deployed:
- Application: ${DEPLOYMENT_URL}
- Health check: ${DEPLOYMENT_URL}/health or ${DEPLOYMENT_URL}/api/health

Next steps:
1. Test the deployment: ${DEPLOYMENT_URL}
2. Check health endpoint: ${DEPLOYMENT_URL}/api/health
3. Monitor logs in platform dashboard
4. Configure custom domain (if needed)
```

## Error Handling

If deployment fails:
1. Check platform-specific logs for errors
2. Verify environment variables are set correctly
3. Ensure build command succeeds locally
4. Check for TypeScript, linting, or syntax errors
5. Verify platform CLI is authenticated
6. Check deployment config files are valid

## Rollback Instructions

Platform-specific rollback procedures:

### Vercel
```bash
vercel ls && vercel rollback
```

### Railway
```bash
railway rollback
```

### Render
```bash
render rollback --service $SERVICE_ID
```

### Fly.io
```bash
flyctl releases && flyctl releases rollback
```

### AWS EB
```bash
eb deploy --version <previous-version>
```

## Supported Platforms

| Platform | CLI Tool | Config File | Best For |
|----------|----------|-------------|----------|
| Vercel | `vercel` | `vercel.json` | Next.js, frontend apps |
| Railway | `railway` | `railway.json` | Full-stack, databases |
| Render | `render` | `render.yaml` | Web services, APIs |
| Fly.io | `flyctl` | `fly.toml` | Global apps, edge |
| AWS EB | `eb` | `Dockerrun.aws.json` | Enterprise apps |
| Digital Ocean | `doctl` | `.do/` | Simple apps |
| Docker | `docker` | `docker-compose.yml` | Local/self-hosted |

## Examples

```bash
# Auto-detect platform and deploy to preview
/deployment:deploy

# Deploy to specific platform and environment
/deployment:deploy production --platform=railway

# Deploy to staging without tests
/deployment:deploy staging --skip-tests

# Deploy to AWS production
/deployment:deploy production --platform=aws
```

## Configuration

Create `deployment/platform.txt` to set default platform:
```
railway
```

Or use `deployment/config.json`:
```json
{
  "platform": "railway",
  "environments": {
    "preview": "preview-env",
    "staging": "staging-env",
    "production": "prod-env"
  }
}
```

## Important Notes

- Platform auto-detection based on config files
- Fallback to Docker if no platform detected
- All platforms provide HTTPS automatically
- Environment variables managed per-platform
- Rollback support varies by platform
- Monitor deployments in platform dashboards