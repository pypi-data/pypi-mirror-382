#!/bin/bash

# phase2-ecosystem-sync.sh - Sync entire spec ecosystem to match layered tasks
# Usage: phase2-ecosystem-sync.sh <spec-directory-name>
# Example: phase2-ecosystem-sync.sh 002-system-context-we

set -e

SPEC_NAME="$1"

if [[ -z "$SPEC_NAME" ]]; then
    echo "Usage: $0 <spec-directory-name>"
    echo "Example: $0 002-system-context-we"
    exit 1
fi

SPEC_DIR="specs/$SPEC_NAME"
LAYERED_TASKS="$SPEC_DIR/agent-tasks/layered-tasks.md"

# Validate inputs
if [[ ! -d "$SPEC_DIR" ]]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

if [[ ! -f "$LAYERED_TASKS" ]]; then
    echo "Error: Layered tasks not found: $LAYERED_TASKS"
    echo "Run Phase 1 first: /iterate tasks $SPEC_NAME"
    exit 1
fi

echo "=== Phase 2: Spec Ecosystem Sync ==="
echo "Spec Directory: $SPEC_DIR"
echo "Layered Tasks: $LAYERED_TASKS"
echo ""

# Create iteration tracking
ITERATION_LOG="$SPEC_DIR/agent-tasks/iteration-log.md"
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

# Check if this is first sync or subsequent
if [[ -f "$ITERATION_LOG" ]]; then
    ITERATION_NUM=$(grep -c "## Iteration" "$ITERATION_LOG" 2>/dev/null || echo "0")
    ITERATION_NUM=$((ITERATION_NUM + 1))
else
    ITERATION_NUM=1
    echo "# Iteration Log - $SPEC_NAME" > "$ITERATION_LOG"
    echo "" >> "$ITERATION_LOG"
fi

echo "## Iteration $ITERATION_NUM - $TIMESTAMP" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"

# Analyze layered tasks for ecosystem updates needed
echo "Analyzing layered tasks for ecosystem sync requirements..."

# Extract agent assignments and new requirements
AGENTS_FOUND=$(grep -E "^- \[.\] T[0-9]+ @" "$LAYERED_TASKS" | sed 's/.*@\([a-z]*\).*/\1/' | sort -u | tr '\n' ' ')
LAYER_COUNT=$(grep -c "^## Layer [0-9]:" "$LAYERED_TASKS" || echo "0")

echo "- Agents involved: $AGENTS_FOUND"
echo "- Layers found: $LAYER_COUNT"

# Log what we found
echo "**Changes Detected:**" >> "$ITERATION_LOG"
echo "- Agents involved: $AGENTS_FOUND" >> "$ITERATION_LOG"
echo "- Layers organized: $LAYER_COUNT" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"

# Update plan.md to reflect layered structure
echo "Updating plan.md to reflect layered task structure..."
if [[ -f "$SPEC_DIR/plan.md" ]]; then
    # Add iteration tracking to plan
    if ! grep -q "## Task Layering Status" "$SPEC_DIR/plan.md"; then
        echo "" >> "$SPEC_DIR/plan.md"
        echo "## Task Layering Status" >> "$SPEC_DIR/plan.md"
        echo "" >> "$SPEC_DIR/plan.md"
        echo "**Current Iteration**: $ITERATION_NUM (as of $TIMESTAMP)" >> "$SPEC_DIR/plan.md"
        echo "**Layered Structure**: $LAYER_COUNT layers with parallel coordination" >> "$SPEC_DIR/plan.md" 
        echo "**Agents Coordinating**: $AGENTS_FOUND" >> "$SPEC_DIR/plan.md"
        echo "" >> "$SPEC_DIR/plan.md"
        echo "*Agents should work from \`agent-tasks/layered-tasks.md\` for proper coordination*" >> "$SPEC_DIR/plan.md"
        
        echo "- Updated plan.md with layering status" >> "$ITERATION_LOG"
    fi
fi

# Check for feedback integration
FEEDBACK_DIR="$SPEC_DIR/feedback"
if [[ -d "$FEEDBACK_DIR" && -f "$FEEDBACK_DIR/tasks.md" ]]; then
    echo "Integrating feedback from PR reviews..."
    echo "- Found feedback tasks to integrate" >> "$ITERATION_LOG"
    
    # Note: Phase 3 will handle feedback integration
    echo "  (Feedback integration requires Phase 3: /iterate adjust)"
fi

# Update quickstart.md to reference layered tasks
if [[ -f "$SPEC_DIR/quickstart.md" ]]; then
    if ! grep -q "layered-tasks.md" "$SPEC_DIR/quickstart.md"; then
        echo "" >> "$SPEC_DIR/quickstart.md"
        echo "## Agent Coordination" >> "$SPEC_DIR/quickstart.md"
        echo "" >> "$SPEC_DIR/quickstart.md"
        echo "Agents work from the layered task structure:" >> "$SPEC_DIR/quickstart.md"
        echo "\`\`\`bash" >> "$SPEC_DIR/quickstart.md"
        echo "# Agents read from layered structure instead of tasks.md" >> "$SPEC_DIR/quickstart.md"
        echo "cat $SPEC_DIR/agent-tasks/layered-tasks.md" >> "$SPEC_DIR/quickstart.md"
        echo "\`\`\`" >> "$SPEC_DIR/quickstart.md"
        
        echo "- Updated quickstart.md with agent coordination info" >> "$ITERATION_LOG"
    fi
fi

# Create current-tasks.md symlink
CURRENT_TASKS="$SPEC_DIR/agent-tasks/current-tasks.md"
if [[ -L "$CURRENT_TASKS" ]]; then
    rm "$CURRENT_TASKS"
fi
ln -s layered-tasks.md "$CURRENT_TASKS"
echo "- Created current-tasks.md symlink" >> "$ITERATION_LOG"

echo "" >> "$ITERATION_LOG"
echo "**Status**: Spec ecosystem synchronized with layered tasks" >> "$ITERATION_LOG"
echo "" >> "$ITERATION_LOG"

echo ""
echo "✅ Phase 2 Complete: Spec Ecosystem Synchronized"
echo ""
echo "**Updated Files:**"
echo "- $SPEC_DIR/plan.md (layering status added)"
echo "- $SPEC_DIR/quickstart.md (agent coordination added)"  
echo "- $SPEC_DIR/agent-tasks/current-tasks.md (symlink created)"
echo "- $SPEC_DIR/agent-tasks/iteration-log.md (tracking added)"
echo ""
echo "**Next Steps:**"
echo "- Agents should now work from agent-tasks/layered-tasks.md"
echo "- Use '/iterate adjust' for live development changes"
echo "- Use '/judge' on PRs to generate feedback for next iteration"
echo ""
echo "**Iteration**: $ITERATION_NUM | **Agents**: $AGENTS_FOUND | **Layers**: $LAYER_COUNT"