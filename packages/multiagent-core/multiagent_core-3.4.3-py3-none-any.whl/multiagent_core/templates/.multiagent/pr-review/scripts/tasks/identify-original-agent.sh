#!/bin/bash
# Agent attribution and commit analysis
# Usage: identify-original-agent.sh <session_id>

set -euo pipefail

SESSION_ID="${1:-}"

if [[ -z "$SESSION_ID" ]]; then
    echo "Usage: $0 <session_id>"
    echo "Example: $0 20250926_143022_pr123"
    exit 1
fi

SESSION_DIR=".multiagent/feedback/logs/${SESSION_ID}"

if [[ ! -d "$SESSION_DIR" ]]; then
    echo "❌ Session not found: ${SESSION_ID}"
    exit 1
fi

echo "🔍 Identifying original agent for session: ${SESSION_ID}"

# Extract PR number from session metadata
PR_NUMBER=$(jq -r '.pr_number' "${SESSION_DIR}/session-metadata.json")
REPOSITORY=$(jq -r '.repository' "${SESSION_DIR}/session-metadata.json")

if [[ "$PR_NUMBER" == "null" || "$REPOSITORY" == "null" ]]; then
    echo "❌ Invalid session metadata"
    exit 1
fi

echo "📋 Analyzing PR #${PR_NUMBER} in ${REPOSITORY}"

# Get commit messages from PR
echo "Fetching commit history..."
gh api "/repos/${REPOSITORY}/pulls/${PR_NUMBER}/commits" | \
    jq -r '.[].commit.message' > "${SESSION_DIR}/commit-messages.txt"

# Analyze commit messages for agent attribution
AGENTS_FOUND=$(grep -o "@[a-z][a-z]*" "${SESSION_DIR}/commit-messages.txt" | sort | uniq -c | sort -nr || echo "")

# Look for Co-Authored-By patterns
CO_AUTHORS=$(grep -o "Co-Authored-By: @[a-z][a-z]*" "${SESSION_DIR}/commit-messages.txt" | cut -d'@' -f2 | sort | uniq -c | sort -nr || echo "")

# Identify primary agent (most commits)
if [[ -n "$AGENTS_FOUND" ]]; then
    PRIMARY_AGENT=$(echo "$AGENTS_FOUND" | head -1 | awk '{print $2}' | sed 's/@//')
else
    PRIMARY_AGENT="unknown"
fi

# Get file changes to understand scope
echo "Analyzing changed files..."
gh pr diff "$PR_NUMBER" --repo "$REPOSITORY" --name-only > "${SESSION_DIR}/changed-files.txt"

# Categorize changes
FRONTEND_FILES=$(grep -E "\.(tsx?|jsx?|vue|svelte)$" "${SESSION_DIR}/changed-files.txt" | wc -l || echo 0)
BACKEND_FILES=$(grep -E "\.(py|java|go|rs|rb)$" "${SESSION_DIR}/changed-files.txt" | wc -l || echo 0)
CONFIG_FILES=$(grep -E "\.(json|yaml|yml|toml|ini)$" "${SESSION_DIR}/changed-files.txt" | wc -l || echo 0)
DOC_FILES=$(grep -E "\.(md|rst|txt)$" "${SESSION_DIR}/changed-files.txt" | wc -l || echo 0)

# Create agent analysis
cat > "${SESSION_DIR}/agent-analysis.json" << EOF
{
  "session_id": "${SESSION_ID}",
  "analysis_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pr_analysis": {
    "pr_number": ${PR_NUMBER},
    "repository": "${REPOSITORY}",
    "primary_agent": "${PRIMARY_AGENT}",
    "confidence": "$(if [[ -n "$AGENTS_FOUND" ]]; then echo "high"; else echo "low"; fi)"
  },
  "commit_analysis": {
    "total_commits": $(wc -l < "${SESSION_DIR}/commit-messages.txt"),
    "agents_detected": $(echo "$AGENTS_FOUND" | wc -l),
    "co_authors": $(echo "$CO_AUTHORS" | wc -l)
  },
  "change_scope": {
    "frontend_files": ${FRONTEND_FILES},
    "backend_files": ${BACKEND_FILES},
    "config_files": ${CONFIG_FILES},
    "documentation_files": ${DOC_FILES},
    "total_files": $(wc -l < "${SESSION_DIR}/changed-files.txt")
  },
  "agent_attribution": {
    "recommended_assignee": "${PRIMARY_AGENT}",
    "reasoning": "Most active agent in commit history with relevant expertise"
  }
}
EOF

echo "✅ Agent identification complete"
echo "🎯 Primary Agent: ${PRIMARY_AGENT}"
echo "📊 Change Scope: ${FRONTEND_FILES} frontend, ${BACKEND_FILES} backend, ${CONFIG_FILES} config"
echo "📂 Analysis stored in: ${SESSION_DIR}/agent-analysis.json"