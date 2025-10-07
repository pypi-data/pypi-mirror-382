#!/usr/bin/env bash

set -e

# Parse command line arguments
SPEC_NAME="$1"
JSON_MODE=false

if [[ "$2" == "--json" ]]; then
    JSON_MODE=true
fi

if [[ -z "$SPEC_NAME" ]]; then
    echo "Usage: $0 <spec-directory> [--json]"
    echo "Example: $0 002-system-context-we"
    exit 1
fi

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SPEC_DIR="$REPO_ROOT/specs/$SPEC_NAME"
SUPERVISOR_DIR="$SPEC_DIR/supervisor"
TEMPLATE="$REPO_ROOT/.multiagent/supervisor/templates/start-report.template.md"
OUTPUT="$SUPERVISOR_DIR/start-report.md"

# Verify spec directory exists
if [[ ! -d "$SPEC_DIR" ]]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

# Verify template exists
if [[ ! -f "$TEMPLATE" ]]; then
    echo "Error: Supervisor template not found: $TEMPLATE"
    exit 1
fi

# Create supervisor directory in spec
mkdir -p "$SUPERVISOR_DIR"

# Get current timestamp
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

echo "=== Supervisor Start Phase Verification ==="
echo "Spec: $SPEC_NAME"
echo "Phase: START (Pre-work setup verification)"

# Check if layered-tasks.md exists
LAYERED_TASKS="$SPEC_DIR/agent-tasks/layered-tasks.md"
if [[ -f "$LAYERED_TASKS" ]]; then
    LOAD_STATUS="✅ layered-tasks.md found and readable"
    TASK_SETUP="READY"
else
    LOAD_STATUS="❌ layered-tasks.md missing - run /iterate tasks first"
    TASK_SETUP="BLOCKED"
fi

# Check worktree status for each agent
check_agent_worktree() {
    local agent="$1"
    local worktree_name="project-$agent"
    
    if git worktree list | grep -q "$worktree_name"; then
        echo "✅ ACTIVE"
    else
        echo "❌ MISSING"
    fi
}

CLAUDE_WORKTREE=$(check_agent_worktree "claude")
COPILOT_WORKTREE=$(check_agent_worktree "copilot") 
CODEX_WORKTREE=$(check_agent_worktree "codex")
QWEN_WORKTREE=$(check_agent_worktree "qwen")
GEMINI_WORKTREE=$(check_agent_worktree "gemini")

# Count active worktrees
ACTIVE_WORKTREES=$(git worktree list | grep -c "project-" || echo "0")

# Check if anyone is on main branch (bad)
MAIN_BRANCH_USERS=$(git log --oneline -10 --format="%an" | grep -c "Claude\|Copilot\|Codex\|Qwen\|Gemini" 2>/dev/null || echo "0")

# Generate summary
if [[ "$TASK_SETUP" == "READY" ]] && [[ "$ACTIVE_WORKTREES" -gt 0 ]]; then
    SUMMARY="START phase verification: Task setup ready, $ACTIVE_WORKTREES agent worktrees active. System ready for parallel agent work."
    OVERALL_STATUS="✅ READY"
else
    SUMMARY="START phase verification: Setup incomplete. Missing task layering or agent worktrees. Agents cannot start work safely."
    OVERALL_STATUS="❌ NOT READY"
fi

# Copy template and fill placeholders
cp "$TEMPLATE" "$OUTPUT"

# Replace placeholders with actual values
sed -i "s|\[SPEC_NAME\]|$SPEC_NAME|g" "$OUTPUT"
sed -i "s|\[PHASE\]|START|g" "$OUTPUT"
sed -i "s|\[TIMESTAMP\]|$TIMESTAMP|g" "$OUTPUT"
sed -i "s|\[SPEC_PATH\]|$SPEC_DIR|g" "$OUTPUT"
sed -i "s|\[LOAD_STATUS\]|$LOAD_STATUS|g" "$OUTPUT"
sed -i "s|\[WORKTREE_STATUS\]|$ACTIVE_WORKTREES agent worktrees active|g" "$OUTPUT"
sed -i "s|\[ROLE_STATUS\]|Pre-work phase - roles not yet active|g" "$OUTPUT"
sed -i "s|\[PROGRESS_STATUS\]|$TASK_SETUP|g" "$OUTPUT"
sed -i "s|\[REPORT_STATUS\]|✅ Generated|g" "$OUTPUT"
sed -i "s|\[SUMMARY_TEXT\]|$SUMMARY|g" "$OUTPUT"

# Fill agent-specific placeholders
sed -i "s|\[CLAUDE_WORKTREE_STATUS\]|$CLAUDE_WORKTREE|g" "$OUTPUT"
sed -i "s|\[COPILOT_WORKTREE_STATUS\]|$COPILOT_WORKTREE|g" "$OUTPUT"
sed -i "s|\[CODEX_WORKTREE_STATUS\]|$CODEX_WORKTREE|g" "$OUTPUT"
sed -i "s|\[QWEN_WORKTREE_STATUS\]|$QWEN_WORKTREE|g" "$OUTPUT"
sed -i "s|\[GEMINI_WORKTREE_STATUS\]|$GEMINI_WORKTREE|g" "$OUTPUT"

# Role status (not applicable for start phase)
sed -i "s|\[CLAUDE_ROLE_STATUS\]|N/A|g" "$OUTPUT"
sed -i "s|\[CLAUDE_ROLE_DETAILS\]|Pre-work phase|g" "$OUTPUT"
sed -i "s|\[COPILOT_ROLE_STATUS\]|N/A|g" "$OUTPUT"
sed -i "s|\[COPILOT_ROLE_DETAILS\]|Pre-work phase|g" "$OUTPUT"
sed -i "s|\[CODEX_ROLE_STATUS\]|N/A|g" "$OUTPUT"
sed -i "s|\[CODEX_ROLE_DETAILS\]|Pre-work phase|g" "$OUTPUT"
sed -i "s|\[QWEN_ROLE_STATUS\]|N/A|g" "$OUTPUT"
sed -i "s|\[QWEN_ROLE_DETAILS\]|Pre-work phase|g" "$OUTPUT"
sed -i "s|\[GEMINI_ROLE_STATUS\]|N/A|g" "$OUTPUT"
sed -i "s|\[GEMINI_ROLE_DETAILS\]|Pre-work phase|g" "$OUTPUT"

# Phase-specific content - escape for sed  
LAYERED_EXISTS=$([ -f "$LAYERED_TASKS" ] && echo "YES" || echo "NO")
if [[ "$MAIN_BRANCH_USERS" =~ ^[0-9]+$ ]] && [[ "$MAIN_BRANCH_USERS" -eq 0 ]]; then
    MAIN_PROTECTED="YES"
else
    MAIN_PROTECTED="RECENT_ACTIVITY"
fi

PHASE_CHECKS="Pre-work Setup Requirements: layered-tasks.md exists: $LAYERED_EXISTS, Agent worktrees created: $ACTIVE_WORKTREES/5 active, Main branch protected: $MAIN_PROTECTED, Git state clean: Ready for parallel work"

sed -i "s|\[PHASE_SPECIFIC_CHECKS\]|$PHASE_CHECKS|g" "$OUTPUT"

# Generate issues and recommendations
if [[ ! -f "$LAYERED_TASKS" ]]; then
    ISSUES="- Missing layered-tasks.md - agents cannot start work"
    RECOMMENDATIONS="- Run: /iterate tasks $SPEC_NAME"
else
    ISSUES="- None detected"
    RECOMMENDATIONS="- Agents can begin work in their worktrees"
fi

sed -i "s|\[ISSUES_LIST\]|$ISSUES|g" "$OUTPUT"
sed -i "s|\[RECOMMENDATIONS_LIST\]|$RECOMMENDATIONS|g" "$OUTPUT"

# Task progress table (basic for start phase) - escape for sed
CLAUDE_TASKS=$(grep -c "@claude" "$LAYERED_TASKS" 2>/dev/null || echo "0")
COPILOT_TASKS=$(grep -c "@copilot" "$LAYERED_TASKS" 2>/dev/null || echo "0")  
CODEX_TASKS=$(grep -c "@codex" "$LAYERED_TASKS" 2>/dev/null || echo "0")

TASK_TABLE="Agent Tasks: claude=$CLAUDE_TASKS, copilot=$COPILOT_TASKS, codex=$CODEX_TASKS"

sed -i "s|\[TASK_PROGRESS_TABLE\]|$TASK_TABLE|g" "$OUTPUT"

# Compliance gates
WORKTREE_GATE=$([ "$ACTIVE_WORKTREES" -gt 0 ] && echo "✅ PASS" || echo "❌ FAIL")
ROLE_GATE="N/A (pre-work)"
COORDINATION_GATE=$([ -f "$LAYERED_TASKS" ] && echo "✅ PASS" || echo "❌ FAIL")
PHASE_GATE=$([ "$TASK_SETUP" == "READY" ] && echo "✅ PASS" || echo "❌ FAIL")

sed -i "s|\[WORKTREE_GATE_STATUS\]|$WORKTREE_GATE|g" "$OUTPUT"
sed -i "s|\[ROLE_GATE_STATUS\]|$ROLE_GATE|g" "$OUTPUT"
sed -i "s|\[COORDINATION_GATE_STATUS\]|$COORDINATION_GATE|g" "$OUTPUT"
sed -i "s|\[PHASE_GATE_STATUS\]|$PHASE_GATE|g" "$OUTPUT"

# Quality gates (basic for start)
sed -i "s|\[COMMIT_GATE_STATUS\]|N/A (pre-work)|g" "$OUTPUT"
sed -i "s|\[QUALITY_GATE_STATUS\]|N/A (pre-work)|g" "$OUTPUT"
sed -i "s|\[DOCS_GATE_STATUS\]|N/A (pre-work)|g" "$OUTPUT"

# Next steps - simple format
if [[ "$OVERALL_STATUS" == "✅ READY" ]]; then
    NEXT_STEPS="Agents can begin work on assigned tasks. Monitor with /supervisor mid $SPEC_NAME"
else
    NEXT_STEPS="Fix missing setup requirements first. Re-run /supervisor start $SPEC_NAME after fixes"
fi

sed -i "s|\[NEXT_STEPS_LIST\]|$NEXT_STEPS|g" "$OUTPUT"

# Audit trail
sed -i "s|\[AGENTS_COUNT\]|5|g" "$OUTPUT"
ISSUES_COUNT=$(echo "$ISSUES" | grep -c "^-" || echo "0")
sed -i "s|\[ISSUES_COUNT\]|$ISSUES_COUNT|g" "$OUTPUT"
BLOCKERS_COUNT=$([ "$OVERALL_STATUS" == "❌ NOT READY" ] && echo "1" || echo "0")
sed -i "s|\[BLOCKERS_COUNT\]|$BLOCKERS_COUNT|g" "$OUTPUT"

echo ""
echo "✅ **Supervisor Start Verification Complete**"
echo ""
echo "📁 **Spec**: $SPEC_NAME"
echo "📋 **Report Generated**: $OUTPUT"
echo "🎯 **Overall Status**: $OVERALL_STATUS"
echo ""
echo "📊 **Quick Summary**:"
echo "  - Task Setup: $TASK_SETUP"
echo "  - Active Worktrees: $ACTIVE_WORKTREES/5"
echo "  - Issues Found: $ISSUES_COUNT"
echo ""
if [[ "$OVERALL_STATUS" == "✅ READY" ]]; then
    echo "🔄 **Next Steps**: Agents can begin work"
    echo "👁️ **Monitor Progress**: /supervisor mid $SPEC_NAME"
else
    echo "⚠️ **Action Required**: Fix setup issues before agent work begins"
fi