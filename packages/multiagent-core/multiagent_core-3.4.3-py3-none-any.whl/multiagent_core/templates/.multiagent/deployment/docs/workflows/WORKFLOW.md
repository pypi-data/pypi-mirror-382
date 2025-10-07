# Deployment Workflow Guide

## Overview

The deployment system follows a sequential workflow that mirrors real development practices. You must follow these steps in order.

## Command Sequence

### Step 1: Prepare Deployment Configurations
```bash
/deploy-prepare [spec-directory]
```
- **Purpose**: Analyze specs and generate deployment configurations
- **Creates**: `/deployment` directory with Docker, K8s, and config files
- **Required**: Must run FIRST before any other deployment commands
- **Output**:
  - `deployment/docker/` - Dockerfile, docker-compose.yml
  - `deployment/k8s/` - Kubernetes manifests
  - `deployment/configs/` - Environment templates
  - `deployment/scripts/` - Deployment scripts

### Step 2: Validate Deployment Readiness
```bash
/deploy-validate
```
- **Purpose**: Check if deployment configs are valid and complete
- **Requires**: `/deployment` directory from Step 1
- **Validates**:
  - Docker configuration syntax
  - Required environment variables
  - No mock code in production
  - API endpoint definitions
- **Output**: Validation report with pass/fail status

### Step 3: Run Local Deployment
```bash
/deploy-run up      # Start services
/deploy-run status  # Check status
/deploy-run logs    # View logs
/deploy-run down    # Stop services
```
- **Purpose**: Test deployment locally before cloud deployment
- **Requires**: Valid deployment configs from Step 1
- **Actions**:
  - `up` - Start all services locally with Docker
  - `status` - Show running containers
  - `logs` - Stream service logs
  - `down` - Stop all services
  - `restart` - Restart services

### Step 4: Deploy to Cloud (Optional)
```bash
/deploy preview     # Deploy to preview environment
/deploy staging     # Deploy to staging
/deploy production  # Deploy to production
```
- **Purpose**: Deploy to Vercel/AWS/cloud provider
- **Requires**: Successful local testing from Step 3
- **Targets**:
  - `preview` - Feature branch deployment
  - `staging` - Pre-production testing
  - `production` - Live deployment

## Complete Example

```bash
# 1. Generate deployment configs for your spec
/deploy-prepare specs/002-system-context-we

# 2. Validate the generated configs
/deploy-validate

# 3. Set up environment variables
cp deployment/configs/.env.example deployment/configs/.env
# Edit .env with your actual values

# 4. Start services locally
/deploy-run up

# 5. Check everything is running
/deploy-run status

# 6. View logs to verify health
/deploy-run logs

# 7. Test your services
curl http://localhost:8080/health

# 8. When ready, deploy to preview
/deploy preview

# 9. After testing, deploy to production
/deploy production
```

## Important Notes

### Command Dependencies
- ❌ Cannot run `/deploy-validate` without `/deploy-prepare` first
- ❌ Cannot run `/deploy-run` without `/deployment` directory
- ❌ Cannot deploy to cloud without local validation

### When to Re-run Commands
Re-run `/deploy-prepare` when:
- Spec files change significantly
- New services are added
- Architecture changes

Re-run `/deploy-validate` when:
- Environment variables change
- Docker configs are manually edited
- Before any cloud deployment

### Common Issues

**"No /deployment directory found"**
- Solution: Run `/deploy-prepare` first

**"Docker not running"**
- Solution: Start Docker Desktop/daemon
- Alternative: Deploy directly to cloud with `/deploy preview`

**"Port already in use"**
- Solution: Check for conflicts with `/deploy-run status`
- Stop services with `/deploy-run down`

**"Environment variables missing"**
- Solution: Copy and edit `.env.example`
- Check required vars with `/deploy-validate`

## Directory Structure After Preparation

```
deployment/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── configs/
│   ├── .env.example
│   ├── .env.development
│   └── .env.production
└── scripts/
    ├── deploy.sh
    └── health-check.sh
```

## Best Practices

1. **Always validate before deploying**: Run `/deploy-validate` before cloud deployment
2. **Test locally first**: Use `/deploy-run up` before `/deploy production`
3. **Check logs**: Use `/deploy-run logs` to debug issues
4. **Clean up**: Use `/deploy-run down` when done testing
5. **Version control**: Commit `/deployment` configs after generation

## Workflow for Different Scenarios

### New Feature Development
1. `/deploy-prepare specs/new-feature`
2. `/deploy-validate`
3. `/deploy-run up`
4. Test locally
5. `/deploy preview`

### Hotfix to Production
1. `/deploy-prepare specs/hotfix`
2. `/deploy-validate`
3. `/deploy-run up` (quick local test)
4. `/deploy production --skip-tests`

### Debugging Deployment Issues
1. `/deploy-run logs`
2. `/deploy-run status`
3. Check `/deployment/docker/docker-compose.yml`
4. `/deploy-validate` to recheck

This workflow ensures a safe, tested deployment process from local development to production.