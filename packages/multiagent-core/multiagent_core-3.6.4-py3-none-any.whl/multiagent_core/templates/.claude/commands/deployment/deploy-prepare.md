---
allowed-tools: Bash(*), Read(*), Task(*)
description: Orchestrate deployment preparation analyzing entire spec folder
argument-hint: [spec-directory]
---

User input (optional spec directory):

$ARGUMENTS

Given the spec directory (or find the most recent one), orchestrate deployment preparation:

1. Determine the target specification directory - use $ARGUMENTS if provided, otherwise find the most recent spec folder containing tasks.md.

2. Run `.multiagent/deployment/scripts/scan-mocks.sh` to check for test code in production paths. Warn about any mock code found but continue preparation.

3. Check git status for uncommitted changes and warn the user if any exist.

4. Analyze the ENTIRE spec directory by reading all files - spec.md, tasks.md, plan.md, data-model.md, everything in contracts/, agent-tasks/layered-tasks.md, and any other subdirectories. Build a comprehensive understanding of what's being built.

5. Create a context file at `/tmp/deployment-context.txt` summarizing what was found - project type, services needed, APIs defined, databases mentioned, agent structure, and deployment requirements.

6. Invoke the deployment-prep agent to analyze the context and generate deployment configurations to the `/deployment` directory based on the comprehensive spec analysis.

7. Validate that `/deployment` directory was created and contains expected files. Count generated artifacts and check for critical files like Dockerfile and docker-compose.yml.

8. Display a summary showing project type detected, number of files generated, any warnings about mock code, and next steps for the user.

Note: The deployment must be based on the COMPLETE spec folder contents, not just spec.md. Every file contributes to understanding what needs to be deployed.