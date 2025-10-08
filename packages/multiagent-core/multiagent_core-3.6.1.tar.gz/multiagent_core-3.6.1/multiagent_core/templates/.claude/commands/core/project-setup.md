---
allowed-tools: Bash(*), Read(*), Write(*), Glob(*), SlashCommand(*), TodoWrite(*)
description: Configure project after multiagent init and first spec. Orchestrates deployment, testing, and documentation setup by coordinating subsystem slash commands and generating final setup report.
name: project-setup
argument-hint: [spec-directory]
---

User input (spec directory):

$ARGUMENTS

The text the user typed after `/core:project-setup` is the spec directory (or empty to auto-detect).

After `multiagent init` and `/specify`, perform complete project setup:

## Phase 1: Analysis & Prerequisites

1. **Locate spec directory**:
   - If $ARGUMENTS provided, use it as spec directory path
   - If empty, find first directory matching `specs/001-*`
   - Verify directory exists and contains spec.md

2. **Verify prerequisites**:
   - Check `.multiagent/` directory exists (multiagent init completed)
   - Check spec files exist (spec.md at minimum)
   - Check git repository initialized

3. **Analyze project structure**:
   - Read spec.md to determine project type (web app, API, CLI, library)
   - Check for pyproject.toml, package.json, Cargo.toml to detect languages
   - Check existing files in .github/workflows/, deployment/, tests/
   - Document findings in project root (will be included in SETUP_COMPLETE.md)

## Phase 2: Subsystem Coordination

4. **Invoke deployment setup**:
   - Run `/deployment:deploy-prepare {spec-dir}` using SlashCommand tool
   - This creates deployment/ directory with Docker configs
   - Wait for completion before proceeding

5. **Invoke testing setup**:
   - Run `/testing:test-generate {spec-dir}` using SlashCommand tool
   - This creates tests/ directory with test structure
   - Wait for completion before proceeding

6. **Invoke documentation setup**:
   - Run `/docs:init` using SlashCommand tool
   - This initializes project documentation structure
   - Wait for completion before proceeding

7. **Validate deployment**:
   - Run `/deployment:deploy-validate` using SlashCommand tool
   - Ensures all deployment configs are valid

## Phase 3: Project Configuration

8. **Configure pytest** (if Python project):
   - Check if pyproject.toml exists
   - Verify `[tool.pytest.ini_options]` section exists
   - If missing, add pytest configuration for test discovery

9. **Generate GitHub workflows**:
   - Check what workflows already exist in .github/workflows/
   - Based on project type, generate missing workflows from templates:
     - ci.yml (if not exists) - from .multiagent/core/templates/github-workflows/ci.yml.template
     - security.yml (if not exists) - from security.yml.template
   - Fill in template variables based on detected framework/language

10. **Verify git hooks**:
    - Check if .git/hooks/pre-push exists (created by multiagent init)
    - Verify hooks are executable: `ls -la .git/hooks/`
    - Do NOT recreate - just verify they exist

11. **Create environment files**:
    - Check if .env.example already exists (from multiagent init)
    - If missing, parse spec to identify required env vars
    - Create .env.example with placeholders (NO real secrets)
    - Create .env.development with development defaults
    - Verify .env is in .gitignore

## Phase 4: Final Setup

12. **Install dependencies**:
    - If Node.js (package.json exists): Run `npm install`
    - If Python (pyproject.toml or requirements.txt): Run `pip install -e .` or `pip install -r requirements.txt`
    - Log any installation errors but continue

13. **Generate setup report**:
    - Create SETUP_COMPLETE.md in project root
    - Include:
      - ✅ Completed items checklist
      - ⚠️ Manual steps required (external services like GitHub webhooks, database setup)
      - 🚀 Quick start commands
      - 📦 Deployment instructions
      - 🔧 Troubleshooting tips
      - ➡️ Next development steps

14. **Display summary**:
    - Show what was configured
    - List any warnings or issues encountered
    - Highlight manual steps user must complete
    - Provide quick start commands
    - Link to SETUP_COMPLETE.md

## Important Notes

- **Security**: Never create .env with real secrets - only templates
- **Git hooks**: Already created by multiagent init - just verify
- **External services**: Document setup steps, don't automate (too risky)
- **Idempotent**: Check what exists before creating to avoid overwrites
- **Subsystems**: Use SlashCommand tool to invoke specialized setup commands