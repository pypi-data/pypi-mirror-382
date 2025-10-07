---
allowed-tools: Bash(*), Read(*), Task(*)
description: Validate deployment configuration readiness
---

Given the deployment configurations in `/deployment`, validate readiness:

1. Verify `/deployment` directory exists. If missing, exit with error telling user to run `/deploy-prepare` first.

2. Count deployment artifacts by type - Docker files, compose files, Kubernetes manifests, environment configs. Report the inventory found.

3. Run `.multiagent/deployment/scripts/check-apis.sh` to validate API endpoint definitions are complete.

4. Run `.multiagent/deployment/scripts/security-scan.sh` to check for exposed secrets or security issues.

5. Run `.multiagent/deployment/scripts/check-production-readiness.sh` to verify production requirements are met.

6. Create `/tmp/validation-context.txt` with counts of all issues found from helper scripts, Docker/kubectl availability, and list of files to validate.

7. Invoke deployment-validator subagent using Task tool with subagent_type: "deployment-validator". Pass validation context and request comprehensive validation of all deployment artifacts including Dockerfile syntax, compose structure, environment variables, and Kubernetes manifests.

8. Aggregate all validation results. If security issues exist, mark as critical blocker. Determine overall status as READY or NEEDS_FIXES.

9. Generate validation report showing status, checks performed, issues by category, and clear next steps based on whether deployment is ready.

Note: Security issues must always block deployment. The validator subagent performs deep technical validation while you orchestrate and make the go/no-go decision.