---
allowed-tools: Task(production-specialist)
description: Run comprehensive production readiness scan and tests
argument-hint: [--fix] [--verbose] [--test-only]
---

User input:

$ARGUMENTS

# Invoke Production Specialist Subagent

**Purpose**: Use the production-specialist subagent for comprehensive production readiness analysis, mock detection, and SpecKit compliance validation.

**Subagent Responsibilities**:
- Run comprehensive production readiness scans
- Detect mock implementations in production code
- Validate multiagent devops deployment configurations
- Provide auto-fix capabilities for critical issues
- Generate detailed production readiness reports

**Instructions**:

Invoke the production-specialist subagent with the arguments:

```
Arguments: $ARGUMENTS

Run comprehensive production readiness analysis:

1. Parse arguments for execution mode:
   - --fix: Auto-fix critical mock implementations
   - --verbose: Include detailed analysis output
   - --test-only: Skip mock detection, only run tests
2. Execute integrated production tests:
   - Run `./scripts/ops qa --production --verbose`
   - Tests located in `testing/backend-tests/production/`
3. If not --test-only, run mock detection:
   - Primary: `multiagent devops --mock-detection --spec-path /specs/`
   - Fallback: `python .claude/scripts/mock_detector.py --verbose --format markdown`
4. Analyze combined results:
   - Critical production readiness issues
   - Mock implementations needing replacement
   - Environment configuration problems
   - Security vulnerabilities
5. If --fix provided:
   - Identify auto-fixable issues
   - Implement real replacements for mocks
   - Validate fixes with additional scans
   - Re-run production tests to confirm
6. Generate comprehensive report:
   - Production readiness status (READY/BLOCKED/WARNING)
   - Critical issues with remediation steps
   - Environment validation results
   - CI/CD automation recommendations
7. Provide specific guidance:
   - Payment systems: Replace with production integrations
   - Authentication: Proper JWT/OAuth implementation
   - Database: Real connection strings with SSL
   - External APIs: Production endpoints with error handling

The subagent will:
- Execute ops qa production tests
- Run multiagent devops mock detection
- Analyze results for critical blockers
- If --fix provided, implement real replacements
- Validate all fixes work correctly
- Generate comprehensive readiness assessment

Return production readiness status, issue count by severity, and deployment recommendations.
```

This command delegates all production readiness validation to the specialized production-specialist subagent.