#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
PR_NUMBER=""

for arg in "$@"; do
    case "$arg" in
        --json) 
            JSON_MODE=true 
            ;;
        --help|-h) 
            echo "Usage: $0 [--json] PR_NUMBER"
            echo "  --json      Output results in JSON format"
            echo "  PR_NUMBER   GitHub PR number to process"
            echo "  --help      Show this help message"
            exit 0 
            ;;
        *) 
            if [[ "$arg" =~ ^[0-9]+$ ]]; then
                PR_NUMBER="$arg"
            fi
            ;;
    esac
done

if [ -z "$PR_NUMBER" ]; then
    echo "❌ Error: PR number required"
    echo "Usage: $0 [--json] PR_NUMBER"
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Create session ID with timestamp
SESSION_ID="pr-${PR_NUMBER}-$(date +%Y%m%d-%H%M%S)"
LOGS_DIR="$PROJECT_ROOT/.multiagent/feedback/logs/$SESSION_ID"


echo "🚀 Setting up PR feedback session for PR #$PR_NUMBER"
echo "📁 Session: $SESSION_ID"

# Create session directory structure
mkdir -p "$LOGS_DIR"

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is required but not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if we're authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "🔍 Fetching PR data from GitHub..."

# Get PR metadata
echo "  - PR metadata..."
gh pr view "$PR_NUMBER" --json title,body,author,headRefName,baseRefName,url,state,number,createdAt,updatedAt > "$LOGS_DIR/pr-data.json"

# Get PR comments and reviews
echo "  - PR comments and reviews..."
gh pr view "$PR_NUMBER" --json comments,reviews > "$LOGS_DIR/pr-comments.json"

# Get PR diff
echo "  - PR diff..."
gh pr diff "$PR_NUMBER" > "$LOGS_DIR/pr-diff.txt"

# Extract key data from PR for variables
PR_TITLE=$(jq -r '.title' "$LOGS_DIR/pr-data.json")
PR_AUTHOR=$(jq -r '.author.login' "$LOGS_DIR/pr-data.json")
HEAD_BRANCH=$(jq -r '.headRefName' "$LOGS_DIR/pr-data.json")
BASE_BRANCH=$(jq -r '.baseRefName' "$LOGS_DIR/pr-data.json")
PR_URL=$(jq -r '.url' "$LOGS_DIR/pr-data.json")

# Extract key data from PR
PR_TITLE=$(jq -r '.title' "$LOGS_DIR/pr-data.json")
PR_AUTHOR=$(jq -r '.author.login' "$LOGS_DIR/pr-data.json")
HEAD_BRANCH=$(jq -r '.headRefName' "$LOGS_DIR/pr-data.json")
BASE_BRANCH=$(jq -r '.baseRefName' "$LOGS_DIR/pr-data.json")
PR_URL=$(jq -r '.url' "$LOGS_DIR/pr-data.json")

echo "  - Title: $PR_TITLE"
echo "  - Author: $PR_AUTHOR"
echo "  - Branch: $HEAD_BRANCH → $BASE_BRANCH"

# Detect original agent from branch name
DETECTED_AGENT=""
if [[ "$HEAD_BRANCH" =~ ^agent-([a-z]+)- ]]; then
    DETECTED_AGENT="${BASH_REMATCH[1]}"
    echo "  - Detected agent: @$DETECTED_AGENT"
elif [[ "$HEAD_BRANCH" =~ ^project-([a-z]+) ]]; then
    DETECTED_AGENT="${BASH_REMATCH[1]}"
    echo "  - Detected agent: @$DETECTED_AGENT (project branch)"
fi

# Check for MCP availability (Slack notifications)
SLACK_ENABLED=false
MCP_CONFIG="$HOME/.config/claude-mcp/servers.json"
if [ -f "$MCP_CONFIG" ] && grep -q "slack" "$MCP_CONFIG" 2>/dev/null; then
    SLACK_ENABLED=true
    echo "  - Slack MCP: Available"
else
    echo "  - Slack MCP: Not configured"
fi

# Create session metadata BEFORE processing
SESSION_DATA=$(cat << EOF
{
  "session_id": "$SESSION_ID",
  "pr_number": "$PR_NUMBER",
  "pr_title": "$PR_TITLE",
  "pr_author": "$PR_AUTHOR",
  "head_branch": "$HEAD_BRANCH",
  "base_branch": "$BASE_BRANCH",
  "pr_url": "$PR_URL",
  "detected_agent": "$DETECTED_AGENT",
  "logs_dir": "$LOGS_DIR",
  "output_tasks": "$LOGS_DIR/generated-tasks.md",
  "slack_enabled": $SLACK_ENABLED,
  "created_at": "$(date -Iseconds)",
  "project_root": "$PROJECT_ROOT"
}
EOF
)

# Save session metadata BEFORE processing
echo "$SESSION_DATA" > "$LOGS_DIR/session.json"

echo "📡 Processing PR feedback and generating tasks..."

# Use SpecKit-style layered processing: bash script → template → output
PROCESSOR_SCRIPT="$SCRIPT_DIR/../process-pr-feedback.sh"

if [ -f "$PROCESSOR_SCRIPT" ]; then
    echo "  - Executing SpecKit-style layered task generation..."
    echo "    (bash script → template → structured output)"
    
    if bash "$PROCESSOR_SCRIPT" "$LOGS_DIR"; then
        echo "  ✅ Task generation completed successfully using SpecKit approach"
    else
        echo "  ⚠️  SpecKit processor failed - creating fallback template"
        # Create a basic template if processor fails
        cat > "$LOGS_DIR/generated-tasks.md" << EOF
# Feedback Tasks - Session $SESSION_ID

**Generated**: $(date '+%Y-%m-%d %H:%M:%S UTC')
**PR**: #$PR_NUMBER  
**Title**: $PR_TITLE
**Author**: $PR_AUTHOR
**Branch**: $HEAD_BRANCH → $BASE_BRANCH
**Session**: [$SESSION_ID](.multiagent/feedback/logs/$SESSION_ID/)

## Processing Failed

SpecKit-style processor failed - manual review required.

## Action Items

### Priority 1: Immediate Actions
- [ ] **T001** Review PR changes manually
- [ ] **T002** Address any technical concerns identified
- [ ] **T003** Test changes thoroughly

### Priority 2: Code Quality  
- [ ] **T004** Run linting and type checking
- [ ] **T005** Update documentation if needed
- [ ] **T006** Add tests for new functionality

### Priority 3: Integration
- [ ] **T007** Verify integration with existing systems
- [ ] **T008** Test deployment process
- [ ] **T009** Update CI/CD if necessary

---
*Generated by MultiAgent Core Feedback System*
EOF
    fi
else
    echo "⚠️  SpecKit processor not found - creating basic template"
    echo "   Expected processor at: $PROCESSOR_SCRIPT"
    
    # Create a basic template if processor is missing
    cat > "$LOGS_DIR/generated-tasks.md" << EOF
# Feedback Tasks - Session $SESSION_ID

**Generated**: $(date '+%Y-%m-%d %H:%M:%S UTC')
**PR**: #$PR_NUMBER  
**Title**: $PR_TITLE
**Author**: $PR_AUTHOR
**Branch**: $HEAD_BRANCH → $BASE_BRANCH
**Session**: [$SESSION_ID](.multiagent/feedback/logs/$SESSION_ID/)

## Processor Missing

SpecKit-style processor not available - manual review required.

## Action Items

### Priority 1: Immediate Actions
- [ ] **T001** Review PR changes manually
- [ ] **T002** Address any technical concerns identified
- [ ] **T003** Test changes thoroughly

### Priority 2: Code Quality  
- [ ] **T004** Run linting and type checking
- [ ] **T005** Update documentation if needed
- [ ] **T006** Add tests for new functionality

### Priority 3: Integration
- [ ] **T007** Verify integration with existing systems
- [ ] **T008** Test deployment process
- [ ] **T009** Update CI/CD if necessary

---
*Generated by MultiAgent Core Feedback System*
EOF
fi


echo "✅ Session setup complete!"
echo "📂 Logs: $LOGS_DIR"

# Output based on mode
if [ "$JSON_MODE" = true ]; then
    echo "$SESSION_DATA"
else
    echo ""
    echo "Session Data:"
    echo "$SESSION_DATA" | jq .
    echo ""
    echo "Next steps:"
    echo "1. Run: .multiagent-feedback/scripts/parse-review.sh '$LOGS_DIR/session.json'"
    echo "2. Run: .multiagent-feedback/scripts/judge-feedback.sh '$LOGS_DIR/session.json'"
    echo "3. Run: .multiagent-feedback/scripts/generate-tasks.sh '$LOGS_DIR/session.json'"
fi