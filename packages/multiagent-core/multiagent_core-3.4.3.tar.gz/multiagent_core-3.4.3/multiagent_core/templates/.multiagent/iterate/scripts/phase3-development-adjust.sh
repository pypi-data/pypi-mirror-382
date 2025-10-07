#!/bin/bash

# phase3-development-adjust.sh - Handle live development adjustments with ecosystem sync
# Usage: phase3-development-adjust.sh <spec-directory-name>
# Example: phase3-development-adjust.sh 002-system-context-we

set -e

SPEC_NAME="$1"

if [[ -z "$SPEC_NAME" ]]; then
    echo "Usage: $0 <spec-directory-name>"
    echo "Example: $0 002-system-context-we"
    exit 1
fi

SPEC_DIR="specs/$SPEC_NAME"
AGENT_TASKS_DIR="$SPEC_DIR/agent-tasks"
ORIGINAL_TASKS="$SPEC_DIR/tasks.md"
LAYERED_TASKS="$AGENT_TASKS_DIR/layered-tasks.md"
ITERATION_LOG="$AGENT_TASKS_DIR/iteration-log.md"

# Validate inputs
if [[ ! -d "$SPEC_DIR" ]]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

if [[ ! -f "$ORIGINAL_TASKS" ]]; then
    echo "Error: Original tasks.md not found: $ORIGINAL_TASKS"
    exit 1
fi

echo "=== Phase 3: Development Adjustments ==="
echo "Spec Directory: $SPEC_DIR"
echo "Processing changes and re-syncing ecosystem..."
echo ""

# Create iteration backup before changes
TIMESTAMP=$(date -u '+%Y-%m-%d_%H-%M-%S')
if [[ -f "$LAYERED_TASKS" ]]; then
    cp "$LAYERED_TASKS" "$AGENT_TASKS_DIR/iteration-backup-$TIMESTAMP.md"
    echo "📁 Backed up current layered tasks to iteration-backup-$TIMESTAMP.md"
fi

# Check for feedback integration needs
FEEDBACK_DIR="$SPEC_DIR/feedback"
FEEDBACK_TASKS="$FEEDBACK_DIR/tasks.md"
HAS_FEEDBACK=false

if [[ -d "$FEEDBACK_DIR" && -f "$FEEDBACK_TASKS" ]]; then
    echo "🔄 Found feedback tasks to integrate..."
    HAS_FEEDBACK=true
    
    # Append feedback tasks to original tasks for re-layering
    echo "" >> "$ORIGINAL_TASKS"
    echo "## Feedback Integration - $TIMESTAMP" >> "$ORIGINAL_TASKS"
    echo "" >> "$ORIGINAL_TASKS"
    cat "$FEEDBACK_TASKS" >> "$ORIGINAL_TASKS"
    
    echo "✅ Integrated feedback into tasks.md"
fi

# Re-run Phase 1: Re-layer the tasks with any changes/feedback
echo ""
echo "🔄 Re-running Phase 1: Task Layering with adjustments..."
if ! .multiagent/pr-review/scripts/planning/layer-tasks.sh "$SPEC_NAME"; then
    echo "❌ Error: Phase 1 re-layering failed"
    exit 1
fi

# Re-run Phase 2: Re-sync the ecosystem  
echo ""
echo "🔄 Re-running Phase 2: Ecosystem Sync..."
if ! .multiagent/iterate/scripts/phase2-ecosystem-sync.sh "$SPEC_NAME"; then
    echo "❌ Error: Phase 2 ecosystem sync failed"
    exit 1
fi

# Create new iteration file
ITERATION_NUM=$(grep -c "## Iteration" "$ITERATION_LOG" 2>/dev/null || echo "0")
NEW_ITERATION_FILE="$AGENT_TASKS_DIR/iteration-$ITERATION_NUM-tasks.md"
cp "$LAYERED_TASKS" "$NEW_ITERATION_FILE"

# Log the adjustment in iteration log
echo "" >> "$ITERATION_LOG"
echo "## Development Adjustment - $TIMESTAMP" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"
echo "**Type**: Live development adjustment" >> "$ITERATION_LOG"

if [[ "$HAS_FEEDBACK" == "true" ]]; then
    echo "**Changes**: Integrated PR feedback and re-layered tasks" >> "$ITERATION_LOG"
    echo "**Feedback Source**: $FEEDBACK_TASKS" >> "$ITERATION_LOG"
else
    echo "**Changes**: Manual task adjustments detected" >> "$ITERATION_LOG"
fi

echo "**New Iteration File**: iteration-$ITERATION_NUM-tasks.md" >> "$ITERATION_LOG"
echo "**Backup Created**: iteration-backup-$TIMESTAMP.md" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"

# Clean up feedback if integrated
if [[ "$HAS_FEEDBACK" == "true" ]]; then
    echo "🧹 Archiving integrated feedback..."
    mkdir -p "$FEEDBACK_DIR/processed"
    mv "$FEEDBACK_TASKS" "$FEEDBACK_DIR/processed/tasks-processed-$TIMESTAMP.md"
    echo "**Feedback Status**: Processed and archived" >> "$ITERATION_LOG"
fi

echo "" >> "$ITERATION_LOG"
echo "**Status**: Development adjustments complete, ecosystem re-synchronized" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"

echo ""
echo "✅ Phase 3 Complete: Development Adjustments Applied"
echo ""
echo "**Changes Made:**"
echo "- Re-layered tasks with adjustments: $LAYERED_TASKS"
echo "- Re-synchronized entire spec ecosystem"
echo "- Created iteration file: iteration-$ITERATION_NUM-tasks.md"
echo "- Backed up previous state: iteration-backup-$TIMESTAMP.md"

if [[ "$HAS_FEEDBACK" == "true" ]]; then
    echo "- Integrated and archived feedback: $FEEDBACK_DIR/processed/"
fi

echo ""
echo "**Next Steps:**"
echo "- Agents work from the updated layered-tasks.md"
echo "- Development continues with re-organized task structure"
echo "- Use '/judge' on future PRs for continued iteration"
echo ""
echo "**Iteration**: $ITERATION_NUM | **Timestamp**: $TIMESTAMP"