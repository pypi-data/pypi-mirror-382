#!/bin/bash
# GitHub API interaction and review parsing
# Usage: process-pr-review.sh <pr_number> <repository> [session_id]

set -euo pipefail

PR_NUMBER="${1:-}"
REPOSITORY="${2:-}"
SESSION_ID="${3:-$(date +%Y%m%d_%H%M%S)_pr${PR_NUMBER}}"

if [[ -z "$PR_NUMBER" || -z "$REPOSITORY" ]]; then
    echo "Usage: $0 <pr_number> <repository> [session_id]"
    echo "Example: $0 123 owner/repo"
    exit 1
fi

# Create session directory
SESSION_DIR=".multiagent/feedback/logs/${SESSION_ID}"
mkdir -p "$SESSION_DIR"

echo "🔍 Processing PR #${PR_NUMBER} in ${REPOSITORY}"
echo "📁 Session: ${SESSION_ID}"

# Extract PR details using GitHub CLI
echo "Fetching PR details..."
gh pr view "$PR_NUMBER" --repo "$REPOSITORY" --json number,title,body,author,state,reviews > "${SESSION_DIR}/pr-details.json"

# Extract review content (filter for Claude Code reviews)
echo "Extracting Claude Code reviews..."
gh api "/repos/${REPOSITORY}/pulls/${PR_NUMBER}/reviews" | \
    jq '.[] | select(.user.login == "claude-code[bot]") | {id: .id, body: .body, state: .state, submitted_at: .submitted_at}' > "${SESSION_DIR}/claude-reviews.json"

# Extract diff for context
echo "Fetching PR diff..."
gh pr diff "$PR_NUMBER" --repo "$REPOSITORY" > "${SESSION_DIR}/pr-diff.patch"

# Create session metadata
cat > "${SESSION_DIR}/session-metadata.json" << EOF
{
  "session_id": "${SESSION_ID}",
  "pr_number": ${PR_NUMBER},
  "repository": "${REPOSITORY}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "phase": "review-extraction",
  "status": "active"
}
EOF

echo "✅ PR review extraction complete"
echo "📂 Session data stored in: ${SESSION_DIR}/"
echo "🎯 Next: Run judge-feedback.sh ${SESSION_ID}"