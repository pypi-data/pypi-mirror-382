# Security Model for MultiAgent Framework

## Security Boundaries

### 1. File System Boundaries

#### Read Permissions
- **Scripts CAN read**:
  - Anywhere in project directory
  - Spec files for analysis
  - Existing code for understanding
  - Configuration files

#### Write Permissions
- **Scripts CAN write**:
  - `deployment/` - Deployment configs only
  - `tests/` - Test files only
  - `.github/workflows/` - Generated workflows
  - `src/`, `backend/`, `frontend/` - Project code
  - Root config files (`.env.example`, etc.)

- **Scripts CANNOT write**:
  - `.multiagent/` - Framework directory (read-only)
  - `.git/` - Git internals (except hooks)
  - System files outside project

### 2. Command Execution Boundaries

#### Allowed Operations
- Package installation (`npm install`, `pip install`)
- Build commands (`npm run build`, `pytest`)
- Git operations (status, diff, commit)
- Docker operations (build, compose)

#### Restricted Operations
- System modifications (`sudo` commands)
- Global package installations without approval
- Network operations to unknown hosts
- File operations outside project root

### 3. Secret Management

#### Never Written to Files
- API keys
- Passwords
- Private keys
- Tokens
- Webhook secrets

#### Placeholder Strategy
```bash
# Generated .env.example
DATABASE_URL=postgresql://user:password@localhost/db  # Placeholder
API_KEY=your_api_key_here                            # Placeholder
JWT_SECRET=generate_a_secure_secret_here             # Placeholder
```

#### Secret Storage
- Use GitHub Secrets for CI/CD
- Use environment variables for local dev
- Never commit actual secrets
- Always use `.env.example` templates

## Agent Security Boundaries

### Agent Isolation
Each agent works in isolated worktrees:
- Cannot affect other agents' work
- Cannot merge to main without PR
- Cannot bypass CI/CD checks
- Must follow commit signing rules

### Agent Permissions

#### @claude (Architecture)
- **CAN**: Design systems, review security
- **CANNOT**: Deploy to production, modify CI/CD

#### @copilot (Implementation)
- **CAN**: Write code, create tests
- **CANNOT**: Modify architecture, change security

#### @qwen (Optimization)
- **CAN**: Improve performance, refactor
- **CANNOT**: Add features, change APIs

#### @gemini (Research)
- **CAN**: Analyze, document, research
- **CANNOT**: Implement code, modify systems

## GitHub Integration Security

### Workflow Permissions
```yaml
# Minimal permissions in workflows
permissions:
  contents: read        # Read-only by default
  pull-requests: write  # Only when needed
  issues: write        # Only when needed
```

### Secret Usage
```yaml
# Secrets never exposed in logs
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    # Secret available but not logged
    deploy-script
```

### PR Security
- All changes via Pull Requests
- Required status checks
- No direct push to main
- Automated security scanning

## Template Security

### Variable Sanitization
Templates use safe placeholders:
```yaml
# Template
{{DATABASE_URL|postgresql://localhost/db}}

# Never includes actual credentials
```

### Conditional Logic
Safe conditional rendering:
```yaml
{{#IF_NODE}}
  # Node.js specific config
{{/IF_NODE}}
```

### No Code Execution
Templates are data-only:
- No executable code in templates
- No eval() or dynamic execution
- Only variable substitution

## Script Security

### Input Validation
All scripts validate inputs:
```bash
# Validate spec directory exists
if [ ! -d "$SPEC_DIR" ]; then
    echo "Error: Invalid spec directory"
    exit 1
fi
```

### Path Sanitization
Prevent directory traversal:
```bash
# Ensure paths stay within project
SAFE_PATH=$(realpath "$USER_INPUT")
if [[ ! "$SAFE_PATH" == "$(pwd)"* ]]; then
    echo "Error: Path outside project"
    exit 1
fi
```

### Command Injection Prevention
No direct shell expansion:
```bash
# BAD - vulnerable to injection
eval "docker run $USER_INPUT"

# GOOD - safe execution
docker run "$CONTAINER_NAME"
```

## Deployment Security

### Environment Isolation
- Development != Staging != Production
- Separate credentials per environment
- No production access from dev

### Container Security
```dockerfile
# Run as non-root user
USER node

# Read-only filesystem where possible
RUN chmod -R 555 /app/static

# Health checks required
HEALTHCHECK --interval=30s CMD curl -f http://localhost/health
```

### Network Security
- Internal services not exposed
- Use reverse proxy for public access
- SSL/TLS required for production
- Rate limiting on all endpoints

## Testing Security

### Test Data Isolation
- Never use production data in tests
- Mock external services
- Sanitize test fixtures
- Clear test data after runs

### Coverage Requirements
Ensure security paths tested:
```javascript
describe('Authentication', () => {
  it('should reject invalid tokens', () => {
    // Security test case
  });

  it('should prevent SQL injection', () => {
    // Security test case
  });
});
```

## Monitoring & Auditing

### Activity Logging
All operations logged:
```
.multiagent/core/logs/
├── initialization.log
├── deployment-generation.log
├── test-generation.log
└── security-scan.log
```

### Audit Trail
Track who did what:
```bash
# Git commits include co-authors
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Human Developer <dev@company.com>
```

### Security Scanning
Automated scanning in CI:
- Dependency vulnerabilities (npm audit, safety)
- Code vulnerabilities (CodeQL, Semgrep)
- Secret scanning (GitGuardian, TruffleHog)
- Container scanning (Trivy, Snyk)

## Incident Response

### If Secrets Exposed
1. Immediately rotate affected credentials
2. Check git history for exposure duration
3. Audit access logs for unauthorized use
4. Update secret management process

### If Framework Compromised
1. Stop using affected version
2. Audit all generated code
3. Re-init from clean version
4. Report issue to maintainers

### If Agent Misbehaves
1. Revoke agent permissions
2. Review agent's commits
3. Reset to known good state
4. Update agent constraints

## Best Practices

### For Framework Users
- Never modify `.multiagent/` directory
- Always use `.env.example` as template
- Review generated code before deploying
- Keep framework version documented

### For Framework Developers
- Minimize required permissions
- Validate all inputs
- Use safe defaults
- Document security implications

### For Both
- Follow principle of least privilege
- Defense in depth strategy
- Regular security updates
- Security-first mindset

## Compliance Considerations

### Data Protection
- No PII in logs or templates
- Encryption at rest for secrets
- Encryption in transit for APIs
- Right to deletion support

### Access Control
- Role-based permissions
- Audit logging enabled
- Regular permission reviews
- Principle of least privilege

### Security Standards
- OWASP Top 10 compliance
- CIS benchmarks for containers
- NIST framework alignment
- SOC 2 considerations