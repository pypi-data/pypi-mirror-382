---
allowed-tools: Task(production-specialist)
description: Run production readiness tests to validate mock replacements
argument-hint: [--verbose] [--fix]
---

User input:

$ARGUMENTS

# Invoke Production Specialist Subagent

**Purpose**: Use the production-specialist subagent to validate production deployment readiness, SpecKit compliance, and identify mock implementations that need replacement.

**Subagent Responsibilities**:
- Run mock detection across production code paths
- Validate production configurations are correct
- Identify critical blockers (payment, auth, database mocks)
- Provide specific implementation guidance for replacements
- Generate prioritized remediation plans

**Instructions**:

Invoke the production-specialist subagent with the arguments:

```
Arguments: $ARGUMENTS

Validate production readiness and identify mock implementations:

1. Run multiagent devops CLI for comprehensive deployment readiness:
   - `multiagent devops --deploy-check --environment production`
   - `multiagent devops --mock-detection --spec-path /specs/`
   - `multiagent devops --security-scan --production-ready`
2. If multiagent CLI unavailable, fallback to mock detector:
   - `python .claude/scripts/mock_detector.py --verbose --format markdown`
3. Categorize issues by priority:
   - Critical Blockers: Payment, auth, database mocks
   - High Priority: External API, configuration issues
   - Medium Priority: Logging, monitoring, performance
4. For each critical issue provide:
   - Specific code examples for replacement
   - Configuration requirements
   - Testing validation steps
   - Estimated effort to complete
5. If --fix argument provided, implement real replacements for critical mocks
6. Validate fixes with additional scans:
   - `grep -r "mock\|fake\|dummy" src/ --exclude-dir=node_modules`
   - Test API endpoints return real data
7. Run production readiness tests:
   - `./scripts/ops qa --production --verbose`
   - Tests located in `testing/backend-tests/production/`
8. Generate prioritized checklist with:
   - Dependencies between fixes
   - Staging environment validation steps
   - Production deployment readiness criteria

The subagent will:
- Execute multiagent devops CLI or fallback to mock detector
- Analyze production code for test/mock implementations
- Categorize issues by severity and impact
- Provide implementation guidance for each issue
- If --fix provided, implement real replacements
- Validate all fixes work correctly
- Generate comprehensive readiness report

Return production readiness status, critical issues found, and remediation plan.
```

This command delegates all production validation and mock detection to the specialized production-specialist subagent.