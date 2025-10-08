---
allowed-tools: Bash(*), Read(*), Task(*)
description: Execute local deployment
argument-hint: [up|down|restart|logs|status]
---

User action requested:

$ARGUMENTS

Given the deployment action (default: up), manage the local deployment:

1. Parse action from $ARGUMENTS - valid actions are up, down, restart, logs, status. Default to "up" if not specified.

2. Verify `/deployment` directory exists. If missing, exit with error telling user to run `/deploy-prepare` first.

3. Check Docker availability except for status action. Exit with error if Docker not available when needed.

4. Detect available deployment methods by checking for docker-compose.yml, Kubernetes manifests, or deployment scripts.

5. For simple management actions (down, restart, logs, status), handle directly:
   - down: Execute docker-compose down in deployment/docker
   - restart: Execute docker-compose restart in deployment/docker
   - logs: Execute docker-compose logs --tail=50 -f in deployment/docker
   - status: Display running containers using docker ps
   Exit after completing these actions.

6. For "up" action, check port availability for common ports (3000, 8000, 5432, 6379) and warn about conflicts.

7. Verify or create environment files from .env.example if .env is missing.

8. Create `/tmp/deployment-run-context.txt` with deployment method availability and project type.

9. Invoke the deployment-runner agent to orchestrate service startup with health checks for "up" action only.

10. After "up" completes, verify deployment by counting running containers, detecting service ports, and testing health endpoints if available.

11. Generate deployment status report showing services running, detected URLs for frontend/backend/API docs, quick commands reference, and troubleshooting guidance.

Note: Only invoke subagent for complex "up" deployment. Handle other actions directly as they are simple operations.