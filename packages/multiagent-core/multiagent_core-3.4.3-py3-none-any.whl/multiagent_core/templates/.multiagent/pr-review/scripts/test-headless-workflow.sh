#!/usr/bin/env bash

set -e

PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
    echo "❌ Usage: $0 PR_NUMBER"
    echo "Example: $0 123"
    exit 1
fi

echo "🧪 Testing headless workflow for PR #$PR_NUMBER"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📂 Project root: $PROJECT_ROOT"
echo "📂 Script dir: $SCRIPT_DIR"

cd "$PROJECT_ROOT"

# Step 1: Fetch GitHub data (bash script responsibility)
echo "🔍 Step 1: Fetching GitHub data..."

SESSION_ID="test-pr-${PR_NUMBER}-$(date +%Y%m%d-%H%M%S)"
LOGS_DIR="$PROJECT_ROOT/.multiagent-feedback/logs/$SESSION_ID"
mkdir -p "$LOGS_DIR"

echo "  📁 Session: $SESSION_ID"
echo "  📁 Logs dir: $LOGS_DIR"

# Check GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) required but not installed"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Fetch PR data
echo "  - Fetching PR metadata..."
gh pr view "$PR_NUMBER" --json title,body,author,headRefName,baseRefName,url,state,number,createdAt,updatedAt > "$LOGS_DIR/pr-data.json"

echo "  - Fetching PR comments and reviews..."
gh pr view "$PR_NUMBER" --json comments,reviews > "$LOGS_DIR/pr-comments.json" 

echo "  - Fetching PR diff..."
gh pr diff "$PR_NUMBER" > "$LOGS_DIR/pr-diff.txt"

# Create session metadata
cat > "$LOGS_DIR/session.json" << EOF
{
  "session_id": "$SESSION_ID",
  "pr_number": "$PR_NUMBER", 
  "logs_dir": "$LOGS_DIR",
  "created_at": "$(date -Iseconds)",
  "project_root": "$PROJECT_ROOT"
}
EOF

echo "✅ GitHub data fetched successfully"

# Step 2: Call Claude Code SDK in headless mode (if available)
echo "🤖 Step 2: Calling Claude Code SDK in headless mode..."

if command -v claude &> /dev/null; then
    echo "  - Claude Code CLI found"
    echo "  - Executing: claude -p \"/process-pr-feedback $PR_NUMBER\""
    
    # Call Claude Code in headless mode using the documented pattern
    claude -p "/process-pr-feedback $PR_NUMBER" \
        --output-format json \
        --allowedTools "Bash,Read,Write,Glob,TodoWrite" \
        --append-system-prompt "Process PR feedback using organized script workflow"
    
    echo "✅ Claude Code processing complete"
else
    echo "⚠️  Claude Code CLI not found"
    echo "   - Install Claude Code CLI"
    echo "   - Or run manually: claude -p \"/process-pr-feedback $PR_NUMBER\""
    echo "   - Data is ready at: $LOGS_DIR"
fi

echo ""
echo "🎯 Workflow Summary:"
echo "  - Session ID: $SESSION_ID"
echo "  - PR Number: $PR_NUMBER" 
echo "  - Data Location: $LOGS_DIR"
echo "  - Next Steps: Check specs/feedback-tasks.md for generated tasks"