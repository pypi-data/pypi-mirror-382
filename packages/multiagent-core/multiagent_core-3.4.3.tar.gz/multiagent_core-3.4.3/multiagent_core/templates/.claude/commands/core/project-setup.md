---
allowed-tools: Bash(*), Read(*), Write(*), Glob(*), TodoWrite(*)
description: Configure project after multiagent init and first spec and after specify has run its course and has its spec 001 ready. This sets up workflows, deployment, testing, hooks, envs, dependencies, services, and generates a setup report.
name: project-setup
argument-hint: [spec-directory]
---

User input (spec directory): @claude I think you can pass this in yourself now as you can run slash commands with arguments so you can pass in the spec directory if you want to override the default behavior of finding the first 001-* spec.

@claude are we not invoking a subagent to do this or are we doing it all here? I think we should do it all here as its a single command that does everything so we can control the flow better? What are the agents involves in this process and when?

$ARGUMENTS

# Project Setup Command

After `multiagent init` and `/specify`, configure the entire project based on the first spec.

Given the spec directory (or find 001-* if not provided), perform complete project setup:

## 1. Verify Prerequisites

1. Check that `multiagent init` has been run - verify `.multiagent/` directory exists.

2. Locate the spec directory - use $ARGUMENTS or find first spec matching `specs/001-*`.

3. Verify spec has been created with `/specify` - check for spec.md, plan.md, etc. ![alt text](image.png) all of these files should be in the spec directory.

## 2. Analyze Project Requirements

4. Read the ENTIRE spec directory to understand the project:
   - Read spec.md for project type and requirements
   - Read plan.md for technical architecture
   - Read data-model.md for database needs
   - Read contracts/ for API definitions
   - Read agent-tasks/layered-tasks.md if it exists this would come after this part so it would not be in there but possibly.

5. Create project analysis at `/tmp/project-setup-context.txt` with:
   - Project type (web app, API, CLI tool, etc.)
   - Framework detected (Next.js, FastAPI, Express, etc.)
   - Database requirements (PostgreSQL, MongoDB, none)
   - External services (GitHub, Slack, AWS, etc.)
   - Deployment target (Vercel, AWS, Kubernetes, etc.)

## 3. Generate GitHub Workflows 
@claude don't we already have workflows as templates to use for this? we should have it read the teamplates and create the workflows based on the spec? We Can try it liks this its fine but I don't want template overhead if its not used.

6. Based on project type, generate appropriate workflows:
   - Run `.multiagent/core/scripts/generate-workflows.sh` with spec directory
   - This creates project-specific workflows in `.github/workflows/`
   - Workflows are tailored to the tech stack from spec

## 4. Configure Deployment

7. Generate deployment configurations:
   - Execute the slash command: `/deploy-prepare` followed by the spec directory path
   - You should invoke this command yourself using the SlashCommand tool
   - This creates `/deployment` directory with Docker, K8s configs
   - Wait for completion before proceeding

## 5. Setup Testing Framework

8. Configure testing framework:
   - Execute the slash command: `/testing-workflow --generate`
   - You should invoke this command yourself using the SlashCommand tool
   - Creates test structure in `/tests`
   - Wait for completion before proceeding

9. Configure pytest in pyproject.toml (Python projects):
   - Check if project uses Python (has pyproject.toml or requirements.txt)
   - If Python project, check if `[tool.pytest.ini_options]` exists in pyproject.toml
   - If missing, add pytest configuration:
     ```toml
     [tool.pytest.ini_options]
     testpaths = ["tests"]
     python_files = ["test_*.py", "*_test.py", "*.test.py"]
     python_classes = ["Test*"]
     python_functions = ["test_*"]
     ```
   - This ensures pytest finds all test files regardless of naming convention
   - Prevents CI failures from "no tests found" (exit code 5)

## 6. Validate Deployment

9. Verify deployment setup:
   - Execute the slash command: `/deploy-validate`
   - You should invoke this command yourself using the SlashCommand tool
   - Ensures all deployment configs are valid

## 7. Configure Git Hooks 
@claude look how the projects initialize git hooks when we do multiagent init I am not sure if we should do it again here or not?

10. Setup git hooks for the project:
    - Create `.git/hooks/pre-commit` for linting
    - Create `.git/hooks/pre-push` for tests
    - Make hooks executable with chmod +x

## 8. Environment Configuration 
@claude there is wholp process that needs to be run through here I think due to how the ~/.global-config for envs should load I think there are some scripts we aer using this is where scripts can help to speeed tings up or just use agent tools to get what we need and set them up. 

11. Create environment files:
    - Generate `.env.example` with required variables from spec
    - Create `.env.development` with default dev values
    - Add `.env` to `.gitignore` if not already there

## 9. Install Dependencies

12. Based on project type, install required packages:
    - If Node.js: Run npm install for detected packages
    - If Python: Run pip install for requirements
    - Install dev dependencies for testing/linting

## 10. Initialize Services 
@claude not sure about this part either we can do it here or we can leave it to the user to do it manually I think it depends on how complex the setup is for each service if its just a matter of running a command we can do it here if its more complex we should leave it to the user.

13. Set up external service connections:
    - Configure GitHub webhook if needed
    - Set up Slack integration if mentioned
    - Initialize database if required

## 11. Run Setup Checklist

14. Execute `.multiagent/core/scripts/setup-checklist.sh` to verify:
    - All workflows are valid
    - Deployment configs are complete
    - Tests can run
    - Hooks are executable
    - Environment is configured

## 12. Generate Setup Report

15. Create `SETUP_COMPLETE.md` in project root with:
    - Checklist of completed items
    - Any manual steps required
    - Commands to run the project
    - Deployment instructions
    - Next steps for development

## 13. Display Summary

16. Show the user:
    - What was configured
    - Any warnings or issues
    - Manual steps required
    - Quick start commands
    - Link to SETUP_COMPLETE.md

Note: This command should be run once after initial project creation throuhg spec kit to fully configure everything based on the spec.