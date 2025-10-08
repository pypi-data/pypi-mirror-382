#!/bin/bash

# save-work-state.sh - Runs when session ends (SessionEnd event)
# Provides safety net for uncommitted work

set -euo pipefail

# Warn about critical uncommitted work (NO EMERGENCY STASHING to prevent restoration)
warn_critical_work() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        exit 0
    fi
    
    # Only warn if there are many changes
    changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$changes" -gt 30 ]; then
        echo ""
        echo "🚨 CRITICAL: Large amount of uncommitted work detected!"
        echo "   Uncommitted files: $changes"
        echo "   💡 STRONGLY recommend committing before session ends"
        echo "   💡 Use: git add -A && git commit -m 'WIP: session end checkpoint'"
        echo "   ⚠️  Auto-stashing disabled to prevent file restoration issues"
        echo ""
    fi
}

# Main execution
main() {
    # Warn about critical work (NO emergency stashing)
    warn_critical_work
    
    # Output empty JSON for Claude Code (hooks must output valid JSON)
    echo '{}'
}

# Run main function
main "$@"