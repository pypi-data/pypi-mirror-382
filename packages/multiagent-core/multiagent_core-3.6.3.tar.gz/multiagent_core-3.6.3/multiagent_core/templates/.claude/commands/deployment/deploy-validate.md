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

   **WAIT FOR TASK COMPLETION** - The subagent will return a validation report with detailed findings.

8. After receiving the subagent's validation report, aggregate all validation results from both helper scripts (steps 3-5) and the subagent. If security issues exist, mark as critical blocker. Determine overall status as READY or NEEDS_FIXES.

9. Generate final validation report showing:
   - Overall status (READY / NEEDS_FIXES / BLOCKED)
   - Checks performed (list all validation steps)
   - Issues by category (Docker, Kubernetes, Security, Environment)
   - Clear next steps based on whether deployment is ready

Note: Security issues must always block deployment. The validator subagent performs deep technical validation while you orchestrate and make the go/no-go decision.