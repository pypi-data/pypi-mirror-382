# MultiAgent Scripts Audit - Mechanical vs Intelligence

**Date**: 2025-10-06
**Current Total**: 47 scripts (5 archived)
**Target**: 10-15 scripts (mechanics only)

## Executive Summary

Based on SpecKit's pattern (issue #11), scripts should ONLY do mechanical setup and output JSON for subagents to consume. Currently, **most scripts are doing intelligence work** that subagents should handle.

### SpecKit Reference Pattern (5 scripts):
1. ✅ **common.sh** - Path resolution, git operations, JSON helpers
2. ✅ **check-prerequisites.sh** - File validation, output JSON
3. ✅ **setup-plan.sh** - Copy template, output paths as JSON
4. ✅ **create-new-feature.sh** - Create dirs, git branch, output JSON
5. ✅ **update-agent-context.sh** - Parse plan.md, update AGENT.md (parse only)

**Pattern**: Script outputs JSON → Subagent reads JSON → Subagent does intelligence work

---

## Audit Results by Category

### ✅ KEEP - Mechanical Work (15 scripts)

**These scripts do ONLY mechanical setup:**

#### Core (3 scripts)
- `check-project-config.sh` - Validate files exist, output JSON
- `project-init.sh` - Create dirs, copy templates
- `wsl-setup.template.sh` - WSL path configuration

#### Security (3 scripts) ✅ **Already correct!**
- `generate-github-workflows.sh` - Copy workflow templates to .github/
- `scan-secrets.sh` - Run secret scanner tools (bulk file operation)
- `validate-compliance.sh` - Check file existence, output JSON

#### Supervisor (3 scripts) ✅ **Already correct!**
- `start-verification.sh` - Check prerequisites, output JSON
- `mid-monitoring.sh` - Gather git/file stats, output JSON
- `end-verification.sh` - Validate completion, output JSON

#### Documentation (1 script) ✅ **Already correct!**
- `create-structure.sh` - Create doc directories

#### Iterate (2 scripts)
- `setup-spec-worktrees.sh` - Git worktree creation
- `setup-worktree-symlinks.sh` - Symlink setup

#### Deployment (2 scripts)
- `run-local-deployment.sh` - Docker commands (docker-compose up/down)
- `scan-mocks.sh` - Bulk file scanning for mock patterns

#### Core (1 script)
- `install-dependencies.sh` - Run npm/pip install commands

---

### ❌ REMOVE - Intelligence Work (32 scripts)

**These scripts do analysis/generation that subagents should handle:**

#### Deployment (8 scripts) → **Use deployment-prep subagent instead**
- ❌ `check-apis.sh` - Analyzes API endpoints (intelligence)
- ❌ `check-deployment-readiness.sh` - Analyzes project structure (intelligence)
- ❌ `check-production-readiness.sh` - Evaluates production requirements (intelligence)
- ❌ `extract-values.sh` - Parses and extracts config (intelligence)
- ❌ `generate-deployment.sh` - **MAJOR CULPRIT** - Analyzes specs, generates configs (intelligence)
- ❌ `security-audit.sh` - Security analysis (intelligence)
- ❌ `security-scan.sh` - Duplicate of scan-secrets.sh
- ❌ `validate-deployment.sh` - Validates generated configs (intelligence)

**Replacement**: deployment-prep subagent reads JSON from script, analyzes specs, generates all deployment artifacts

#### Testing (3 scripts) → **Use backend-tester/test-generator subagents instead**
- ❌ `generate-mocks.sh` - Generates mock data (intelligence)
- ❌ `generate-tests.sh` - Generates test code (intelligence)
- ❌ `test-coverage.sh` - Analyzes coverage (intelligence)

**Already archived** (4 scripts):
- `generate-tests-ai.sh`
- `generate-tests-improved.sh`
- `generate-tests-intelligent.sh`
- `run-test-generator.sh`

**Replacement**: test-generator subagent reads JSON from script, analyzes code, generates tests

#### PR Review (9 scripts) → **Use judge-architect subagent instead**
- ❌ `find-pr-spec-directory.sh` - File searching (mechanical, but redundant)
- ❌ `generate-tasks.sh` - Task generation (intelligence)
- ❌ `human-approval-gate.sh` - Decision logic (intelligence)
- ❌ `identify-original-agent.sh` - Pattern matching (intelligence)
- ❌ `judge-feedback.sh` - Analyzes PR feedback (intelligence)
- ❌ `parse-review.sh` - Parses review comments (intelligence)
- ❌ `process-pr-feedback.sh` - **MAJOR CULPRIT** - Processes and categorizes feedback (intelligence)
- ❌ `setup-pr-session.sh` - Creates context (intelligence)
- ❌ `test-headless-workflow.sh` - Test orchestration (intelligence)

**Replacement**: judge-architect subagent reads JSON with PR data, analyzes feedback, generates recommendations

#### Iterate (3 scripts) → **Use task-layering subagent instead**
- ❌ `layer-tasks.sh` - Task analysis and layering (intelligence)
- ❌ `phase2-ecosystem-sync.sh` - Sync analysis (intelligence)
- ❌ `phase3-development-adjust.sh` - Adjustment logic (intelligence)

**Replacement**: task-layering subagent reads JSON with task paths, analyzes dependencies, generates layered-tasks.md

#### Core (6 scripts) → **Let subagents handle**
- ❌ `configure-workflows.sh` - Workflow generation (intelligence)
- ❌ `dev-init.sh` - Development setup (intelligence)
- ❌ `generate-deployment.sh` - Duplicate
- ❌ `generate-workflows.sh` - Workflow generation (intelligence)
- ❌ `setup-checklist.sh` - Checklist generation (intelligence)

---

## Recommended Script Structure

### Each subsystem should have 1-3 scripts MAX:

#### Example: Deployment Subsystem
**Current**: 10 scripts (8 intelligence, 2 mechanical)
**Target**: 2 scripts

1. ✅ `setup-deployment.sh` - Mechanical
   ```bash
   # Create dirs, output JSON
   mkdir -p deployment/{docker,k8s,configs}
   echo '{"SPEC_DIR":"...","OUTPUT_DIR":"..."}'
   ```

2. ✅ `run-local-deployment.sh` - Mechanical
   ```bash
   # Execute docker commands
   docker-compose up -d
   ```

**Subagent does**: Read JSON, analyze specs, generate all configs (Docker, K8s, etc.)

#### Example: Testing Subsystem
**Current**: 7 scripts (3 active + 4 archived)
**Target**: 1 script

1. ✅ `setup-tests.sh` - Mechanical
   ```bash
   # Create test dirs, output JSON
   mkdir -p tests/{unit,integration,e2e}
   echo '{"SPEC_DIR":"...","TEST_DIR":"...","TASKS_FILE":"..."}'
   ```

**Subagent does**: Read JSON, analyze tasks, generate test structure

---

## Implementation Plan

### Phase 1: Archive Intelligence Scripts (Immediate)
Move all ❌ scripts to `subsystem/scripts/archive/` with README explaining they're replaced by subagents.

### Phase 2: Create Setup Scripts (1-2 days)
For each subsystem, create one `setup-<subsystem>.sh` that:
1. Creates necessary directories
2. Validates prerequisites
3. Outputs JSON with all paths
4. Lets subagent do the rest

### Phase 3: Update Slash Commands (1 day)
Modify slash commands to:
1. Run setup script, capture JSON
2. Pass JSON to subagent
3. Subagent does all intelligence work

### Phase 4: Test & Validate (1 day)
- Verify all workflows still work
- Confirm JSON handoff pattern
- Validate subagent integration

---

## Success Metrics

### Target State (10-15 scripts total):
- **Core**: 3 scripts (setup, validate, install)
- **Deployment**: 2 scripts (setup, run-local)
- **Testing**: 1 script (setup)
- **Security**: 3 scripts ✅ (already correct)
- **Supervisor**: 3 scripts ✅ (already correct)
- **Documentation**: 1 script ✅ (already correct)
- **Iterate**: 2 scripts (setup-worktrees, setup-symlinks)
- **PR Review**: 1 script (setup)

**Total**: 16 scripts → All mechanical, subagents do intelligence

---

## Key Insight from Issue #11

> **"The script is just the mechanics - it sets up the files and folders. The AI (Claude) does the actual content generation."**

We violated this principle by having scripts analyze files, generate content, and make decisions. **Scripts should only prepare the workspace and output JSON. Subagents do the thinking.**

---

## Next Steps

1. ✅ Create this audit report
2. ⏳ Get approval for reduction plan
3. ⏳ Archive 32 intelligence scripts
4. ⏳ Create 10-15 mechanical setup scripts
5. ⏳ Update slash commands to use new pattern
6. ⏳ Test complete workflow end-to-end
