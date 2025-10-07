#!/bin/bash

# Find which spec directory an agent was working in when they created a PR
# Usage: find-pr-spec-directory.sh <PR_NUMBER>

set -euo pipefail

PR_NUMBER="$1"

if [[ -z "$PR_NUMBER" ]]; then
    echo "Usage: $0 <PR_NUMBER>" >&2
    exit 1
fi

# Get repository owner dynamically
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null || echo "")

# Get PR branch name
PR_BRANCH=$(gh pr view "$PR_NUMBER" --json headRefName --jq '.headRefName' 2>/dev/null || echo "")

if [[ -z "$PR_BRANCH" ]]; then
    echo "ERROR: Could not find PR #$PR_NUMBER" >&2
    exit 1
fi

echo "PR #$PR_NUMBER branch: $PR_BRANCH" >&2

# Function to check if a branch contains work from a spec directory
find_spec_for_branch() {
    local branch="$1"
    
    # Look for commits that mention the spec directory
    for spec_dir in specs/*/; do
        if [[ ! -d "$spec_dir" ]]; then
            continue
        fi
        
        spec_name=$(basename "$spec_dir")
        
        # Check if branch has commits that modified files in this spec directory
        if git log --oneline "origin/main..$branch" --name-only 2>/dev/null | grep -q "^$spec_dir" 2>/dev/null; then
            echo "$spec_dir"
            return 0
        fi
        
        # Check if any tasks.md mentions this PR or branch
        if [[ -f "$spec_dir/tasks.md" ]]; then
            if grep -q "#$PR_NUMBER\|$branch" "$spec_dir/tasks.md" 2>/dev/null; then
                echo "$spec_dir"
                return 0
            fi
        fi
    done
    
    return 1
}

# Try to find spec directory from branch
SPEC_DIR=""

# First, try to find based on git history
if SPEC_DIR=$(find_spec_for_branch "$PR_BRANCH"); then
    echo "Found spec directory from git history: $SPEC_DIR" >&2
else
    # Fallback: look at recent specs with agent assignments
    echo "No spec found from git history, checking recent specs..." >&2
    
    # Find the most recent spec directory that has tasks
    LATEST_SPEC=$(find specs/ -name "tasks.md" -exec stat -c '%Y %n' {} \; 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2- | xargs dirname 2>/dev/null || echo "")
    
    if [[ -n "$LATEST_SPEC" && -d "$LATEST_SPEC" ]]; then
        SPEC_DIR="$LATEST_SPEC"
        echo "Using most recent spec with tasks: $SPEC_DIR" >&2
    else
        echo "ERROR: Could not determine spec directory for PR #$PR_NUMBER" >&2
        echo "Available spec directories:" >&2
        ls -1d specs/*/ 2>/dev/null | head -5 >&2
        exit 1
    fi
fi

# Output the spec directory (this is what gets used by the judge command)
echo "$SPEC_DIR"