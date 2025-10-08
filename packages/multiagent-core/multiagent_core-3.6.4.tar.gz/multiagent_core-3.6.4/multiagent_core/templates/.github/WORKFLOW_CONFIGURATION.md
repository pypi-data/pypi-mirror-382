# GitHub Workflows Configuration Guide

## Standardized Workflows Overview

MultiAgent-Core provides **portable standardized workflows** that are copied to every new project during `multiagent init`. These workflows provide comprehensive CI/CD coverage while being configurable for project-specific needs.

## Core Workflows

### 1. `ci-standard.yml` - Essential Quality Checks
**Purpose**: Fast feedback for every commit and PR
**Runs on**: All pushes and PRs
**Includes**:
- Automatic language detection (Node.js, Python)
- Dependency installation
- Linting and type checking
- Basic test execution
- Ops CLI integration when available

### 2. `security-scan.yml` - Security Validation  
**Purpose**: Vulnerability scanning and dependency checks
**Runs on**: Main/develop pushes, PRs to main, daily schedule
**Includes**:
- Trivy vulnerability scanner
- Node.js security audit
- Python safety/bandit checks  
- Security report uploads

### 3. `integration-tests.yml` - Cross-Environment Testing
**Purpose**: Matrix testing across Node/Python versions
**Runs on**: PRs and main pushes
**Includes**:
- Multi-version testing (Node 16/18/20, Python 3.9/3.10/3.11)
- Integration test execution
- Production build verification
- Test result artifacts

### 4. `deployment-validation.yml` - Production Readiness
**Purpose**: Validate deployability and production configuration
**Runs on**: Main pushes, tags, PRs to main
**Includes**:
- Production build creation
- Production environment testing
- Secret detection
- Performance checks
- Deployment readiness reporting

## Project-Specific Configuration

### Standard Configuration Pattern
Each workflow automatically detects project structure:

```yaml
# Auto-detects Node.js projects
- name: Setup Node.js
  if: hashFiles('package.json') != ''
  
# Auto-detects Python projects  
- name: Setup Python
  if: hashFiles('**/*.py') != '' || hashFiles('pyproject.toml') != ''
```

### Custom Commands Integration

#### Option 1: Ops CLI (Recommended)
If your project has `scripts/ops`, workflows use it automatically:
```bash
./scripts/ops qa          # Quality checks
./scripts/ops test        # Test execution  
./scripts/ops build       # Production build
./scripts/ops verify-prod # Production validation
```

#### Option 2: Package.json Scripts
For Node.js projects, workflows check for standard script names:
```json
{
  "scripts": {
    "lint": "eslint src/",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:integration": "jest --testPathPattern=integration",
    "build": "webpack --mode=production",
    "build:prod": "NODE_ENV=production webpack"
  }
}
```

#### Option 3: Python Standards
For Python projects, workflows use standard tools:
```bash
flake8 .           # Linting
black --check .    # Formatting check
mypy .            # Type checking
pytest            # Testing
python -m build   # Building
```

## Workflow Customization

### Environment Variables
Add to your repository settings > Secrets and variables:

```yaml
# Required for deployment workflows
PRODUCTION_URL: https://your-app.com
STAGING_URL: https://staging.your-app.com

# Optional customization
NODE_VERSION: "18"
PYTHON_VERSION: "3.11"
SKIP_SECURITY_SCAN: false
```

### Custom Workflow Steps
Extend workflows by creating additional files:

#### `.github/workflows/project-specific.yml`
```yaml
name: Project Specific Checks

on:
  push:
    branches: [ main ]

jobs:
  custom-checks:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    # Add your custom steps here
    - name: Database migration check
      run: ./scripts/check-migrations.sh
    
    - name: API documentation update
      run: ./scripts/update-api-docs.sh
```

### Workflow Overrides
To customize a standard workflow:

1. **Modify the copied workflow** in your project's `.github/workflows/`
2. **Add conditional steps** based on repository variables
3. **Extend with additional jobs** rather than modifying core jobs

## Multi-Language Project Support

### Node.js + Python Projects
Workflows automatically handle mixed-language projects:
```yaml
# Both setups run automatically
- name: Setup Node.js
  if: hashFiles('package.json') != ''
  
- name: Setup Python  
  if: hashFiles('**/*.py') != ''
```

### Monorepo Support
For projects with multiple languages in subdirectories:
```yaml
# Add to workflow customization
- name: Frontend tests
  run: cd frontend && npm test
  
- name: Backend tests
  run: cd backend && pytest
```

## Integration with Agent Workflows

### Agent Branch Protection
Standard workflows run on agent branches (`agent-*`):
```yaml
on:
  push:
    branches: [ main, develop, 'feature/*', 'agent-*' ]
```

### PR Review Integration  
Security and integration workflows provide data for:
- Automated code review processing
- Quality gate enforcement
- Deployment readiness assessment

## Troubleshooting

### Common Issues

#### Workflow doesn't detect my language
**Problem**: Python/Node.js setup steps are skipped
**Solution**: Ensure you have the correct files:
- Node.js: `package.json` in repository root
- Python: `.py` files or `pyproject.toml`/`requirements.txt`

#### Tests fail in CI but pass locally
**Problem**: Environment differences
**Solution**: 
1. Check matrix versions match your local setup
2. Verify all dependencies are in `package.json`/`requirements.txt`
3. Add environment variables to repository settings

#### Security scan reports false positives
**Problem**: Trivy/safety flags legitimate dependencies
**Solution**: Add suppression files:
- `.trivyignore` for Trivy
- `.safety-policy.yml` for Python safety

### Debug Information
All workflows include debug output:
```yaml
- name: Debug environment
  run: |
    echo "Node version: $(node --version 2>/dev/null || echo 'not installed')"
    echo "Python version: $(python --version 2>/dev/null || echo 'not installed')"
    echo "Working directory: $(pwd)"
    echo "Available files: $(ls -la)"
```

## Workflow Evolution

### Adding New Standard Workflows
1. Create workflow in multiagent-core `.github/workflows/`
2. Test with multiple project types
3. Update this configuration guide
4. Workflows are distributed on next `build` cycle

### Project-Specific Extensions
Encourage projects to:
1. **Extend rather than replace** standard workflows
2. **Contribute improvements** back to multiagent-core
3. **Follow naming conventions** for consistency

This standardized approach ensures all projects get comprehensive CI/CD while maintaining flexibility for specific needs.