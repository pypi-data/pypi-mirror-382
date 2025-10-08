#!/bin/bash

# work-checkpoint.sh - Runs when Claude Code session stops (Stop event)
# Provides work continuation safety and state preservation

set -euo pipefail

# Notify about uncommitted work (NO AUTO-STASHING to prevent file restoration)
notify_uncommitted_work() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        return 0
    fi
    
    # Count uncommitted changes
    changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    # Notify if significant uncommitted work exists (>15 files)
    if [ "$changes" -gt 15 ]; then
        echo ""
        echo "⚠️ Large amount of uncommitted work detected!"
        echo "   Uncommitted files: $changes"
        echo "   💡 Consider committing your work to prevent loss"
        echo "   💡 Use 'git add -A && git commit -m \"WIP: description\"' to save progress"
        echo ""
    fi
}

# Show current status for continuity
show_status() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
        
        if [ "$uncommitted" -gt 0 ] || [ "$(git stash list 2>/dev/null | wc -l)" -gt 0 ]; then
            echo ""
            echo "📋 Work Status Checkpoint"
            echo "   Branch: $current_branch"
            [ "$uncommitted" -gt 0 ] && echo "   Uncommitted: $uncommitted files"
            
            stash_count=$(git stash list 2>/dev/null | wc -l)
            [ "$stash_count" -gt 0 ] && echo "   Stashes: $stash_count available"
            echo ""
        fi
    fi
}

# Main execution
main() {
    # Notify about uncommitted work (NO auto-stashing)
    notify_uncommitted_work
    
    # Show status for next session
    show_status
    
    # Output empty JSON for Claude Code (hooks must output valid JSON)
    echo '{}'
}

# Run main function
main "$@"