#!/usr/bin/env bash

# Process PR Feedback - SpecKit Style Layered Approach
# Usage: ./process-pr-feedback.sh <session_directory>

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <session_directory>"
    echo "Example: $0 /path/to/.multiagent/feedback/logs/pr-8-20250926-190113"
    exit 1
fi

SESSION_DIR="$1"

if [ ! -d "$SESSION_DIR" ]; then
    echo "❌ Session directory does not exist: $SESSION_DIR"
    exit 1
fi

echo "🎯 Processing PR feedback using SpecKit layered approach..."
echo "📁 Session: $(basename "$SESSION_DIR")"

# Read session metadata
SESSION_FILE="$SESSION_DIR/session.json"
if [ ! -f "$SESSION_FILE" ]; then
    echo "❌ Session file not found: $SESSION_FILE"
    exit 1
fi

# Extract key information using jq
PR_NUMBER=$(jq -r '.pr_number' "$SESSION_FILE")
PR_TITLE=$(jq -r '.pr_title' "$SESSION_FILE")
PR_AUTHOR=$(jq -r '.pr_author' "$SESSION_FILE")
HEAD_BRANCH=$(jq -r '.head_branch' "$SESSION_FILE")
BASE_BRANCH=$(jq -r '.base_branch' "$SESSION_FILE")
SESSION_ID=$(jq -r '.session_id' "$SESSION_FILE")

echo "📊 PR Details:"
echo "  - PR #$PR_NUMBER: $PR_TITLE"
echo "  - Author: $PR_AUTHOR"
echo "  - Branch: $HEAD_BRANCH → $BASE_BRANCH"

# Analyze the PR diff to extract key information
echo "🔍 Analyzing PR changes..."

# Count files changed, lines added/removed
DIFF_FILE="$SESSION_DIR/pr-diff.txt"
if [ -f "$DIFF_FILE" ]; then
    FILES_CHANGED=$(grep -c "^diff --git" "$DIFF_FILE" || echo "0")
    LINES_ADDED=$(grep -c "^+" "$DIFF_FILE" | grep -v "^+++" || echo "0")
    LINES_REMOVED=$(grep -c "^-" "$DIFF_FILE" | grep -v "^---" || echo "0")
    
    # Extract file extensions
    FILE_TYPES=$(grep "^diff --git" "$DIFF_FILE" | sed 's/.*b\///' | grep -o '\.[^/]*$' | sort | uniq | tr '\n' ',' | sed 's/,$//')
    
    echo "  - Files changed: $FILES_CHANGED"
    echo "  - Lines: +$LINES_ADDED -$LINES_REMOVED"
    echo "  - File types: $FILE_TYPES"
else
    echo "  ⚠️  No diff file found"
    FILES_CHANGED=0
    LINES_ADDED=0
    LINES_REMOVED=0
    FILE_TYPES=""
fi

# Determine PR type based on title and files
PR_TYPE="General"
if [[ "$PR_TITLE" =~ feat|feature ]]; then
    PR_TYPE="Feature"
elif [[ "$PR_TITLE" =~ fix|bug ]]; then
    PR_TYPE="Bug Fix"
elif [[ "$PR_TITLE" =~ doc|docs ]] || [[ "$FILE_TYPES" =~ md|txt|rst ]]; then
    PR_TYPE="Documentation"
elif [[ "$PR_TITLE" =~ refactor ]]; then
    PR_TYPE="Refactoring"
fi

# Determine complexity
COMPLEXITY="Low"
if [ "$FILES_CHANGED" -gt 10 ] || [ "$LINES_ADDED" -gt 200 ]; then
    COMPLEXITY="High"
elif [ "$FILES_CHANGED" -gt 3 ] || [ "$LINES_ADDED" -gt 50 ]; then
    COMPLEXITY="Medium"
fi

echo "  - Type: $PR_TYPE"
echo "  - Complexity: $COMPLEXITY"

# Now use AI analysis via Python orchestrator
echo "🤖 Using AI analysis for intelligent task generation..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATOR_SCRIPT="$SCRIPT_DIR/pr-feedback-orchestrator.py"

if [ -f "$ORCHESTRATOR_SCRIPT" ]; then
    echo "  - Running Python orchestrator with Claude SDK..."
    
    # Call the Python orchestrator with the session directory
    if python3 "$ORCHESTRATOR_SCRIPT" "$SESSION_DIR"; then
        echo "  ✅ AI-powered task generation completed successfully"
        echo "📁 Output: $SESSION_DIR/generated-tasks.md"
        
        # Show summary of generated content
        if [ -f "$SESSION_DIR/generated-tasks.md" ]; then
            TASK_COUNT=$(grep -c "^- \[ \]" "$SESSION_DIR/generated-tasks.md" || echo "0")
            LINE_COUNT=$(wc -l < "$SESSION_DIR/generated-tasks.md")
            echo "📏 Generated $LINE_COUNT lines with $TASK_COUNT actionable tasks"
        fi
        
        exit 0
    else
        echo "  ⚠️  AI orchestrator failed - falling back to template approach"
    fi
else
    echo "  ⚠️  AI orchestrator not found at: $ORCHESTRATOR_SCRIPT"
    echo "  📝 Falling back to template-based generation..."
fi

# Fallback: Template-based generation if AI fails
echo "📝 Generating tasks from template..."

TEMPLATE_FILE="$SCRIPT_DIR/../templates/pr-feedback-tasks.template.md"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    echo "Creating basic template..."
    
    # Create template directory if it doesn't exist
    mkdir -p "$(dirname "$TEMPLATE_FILE")"
    
    # Create basic template
    cat > "$TEMPLATE_FILE" << 'EOF'
# Feedback Tasks - Session {{SESSION_ID}}

**Generated**: {{TIMESTAMP}}
**PR**: #{{PR_NUMBER}}
**Title**: {{PR_TITLE}}
**Author**: {{PR_AUTHOR}}
**Branch**: {{HEAD_BRANCH}} → {{BASE_BRANCH}}
**Session**: [{{SESSION_ID}}](.multiagent/feedback/logs/{{SESSION_ID}}/)

## Claude Code Review Summary

This {{PR_TYPE}} PR modifies {{FILES_CHANGED}} files with {{LINES_ADDED}} additions and {{LINES_REMOVED}} deletions.
The changes have {{COMPLEXITY}} complexity and involve {{FILE_TYPES}} file types.

## Action Items

### Priority 1: Immediate Actions
- [ ] **T001** @claude **PRIORITY**: Review {{PR_TYPE}} implementation for architecture compliance
  - Verify technical approach aligns with project standards
  - **Location**: {{FILE_TYPES}} files in PR diff

- [ ] **T002** @copilot **MEDIUM**: Implement any missing error handling
  - Add proper error boundaries and validation
  - **Location**: Core implementation files

- [ ] **T003** @qwen **MEDIUM**: Optimize performance if applicable
  - Profile and optimize any performance-critical paths
  - **Location**: Main logic files

### Priority 2: Code Quality
- [ ] **T004** @gemini **LOW**: Update documentation for changes
  - Ensure README and docs reflect new functionality
  - **Location**: docs/ directory and README files

- [ ] **T005** @copilot **MEDIUM**: Add comprehensive tests
  - Create unit and integration tests for new functionality
  - **Location**: tests/ directory structure

- [ ] **T006** @claude **LOW**: Code review for standards compliance
  - Verify coding standards, naming, and patterns
  - **Location**: All modified files

### Priority 3: Integration
- [ ] **T007** @claude **LOW**: Verify deployment compatibility
  - Ensure changes work with existing deployment process
  - **Location**: CI/CD and deployment configs

- [ ] **T008** @qwen **LOW**: Performance impact assessment
  - Measure any performance impact of changes
  - **Location**: Performance-critical paths

- [ ] **T009** @gemini **LOW**: Update team knowledge base
  - Document any new patterns or architectural decisions
  - **Location**: Team documentation

## Change Impact Analysis

### Technical Scope
- **Complexity**: {{COMPLEXITY}}
- **Risk Level**: {{RISK_LEVEL}}
- **Testing Coverage**: Needs verification

### Recommendations
- Review changes for architectural impact
- Ensure proper testing coverage
- Update documentation as needed

## Session Details
- **Session ID**: {{SESSION_ID}}
- **Generated**: {{TIMESTAMP}}
- **Files Changed**: {{FILES_CHANGED}}
- **Lines Added**: {{LINES_ADDED}}
- **Lines Removed**: {{LINES_REMOVED}}
- **Change Type**: {{PR_TYPE}}

---
*Generated by MultiAgent Core Feedback System with SpecKit-Style Processing*
EOF
    
    echo "✅ Created template: $TEMPLATE_FILE"
fi

# Process the template by replacing variables
echo "🔄 Processing template with PR data..."

# Read template and replace variables
TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

# Replace all variables
PROCESSED_CONTENT="$TEMPLATE_CONTENT"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{SESSION_ID\}\}/$SESSION_ID}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{TIMESTAMP\}\}/$(date '+%Y-%m-%d %H:%M:%S UTC')}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{PR_NUMBER\}\}/$PR_NUMBER}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{PR_TITLE\}\}/$PR_TITLE}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{PR_AUTHOR\}\}/$PR_AUTHOR}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{HEAD_BRANCH\}\}/$HEAD_BRANCH}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{BASE_BRANCH\}\}/$BASE_BRANCH}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{PR_TYPE\}\}/$PR_TYPE}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{FILES_CHANGED\}\}/$FILES_CHANGED}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{LINES_ADDED\}\}/$LINES_ADDED}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{LINES_REMOVED\}\}/$LINES_REMOVED}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{FILE_TYPES\}\}/$FILE_TYPES}"
PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{COMPLEXITY\}\}/$COMPLEXITY}"

# Determine risk level based on complexity and type
RISK_LEVEL="Low"
if [ "$COMPLEXITY" = "High" ] || [ "$PR_TYPE" = "Feature" ]; then
    RISK_LEVEL="Medium"
fi
if [ "$FILES_CHANGED" -gt 20 ]; then
    RISK_LEVEL="High"
fi

PROCESSED_CONTENT="${PROCESSED_CONTENT//\{\{RISK_LEVEL\}\}/$RISK_LEVEL}"

# Write the processed content
OUTPUT_FILE="$SESSION_DIR/generated-tasks.md"
echo "$PROCESSED_CONTENT" > "$OUTPUT_FILE"

echo "✅ Task generation completed!"
echo "📁 Output: $OUTPUT_FILE"
echo "📏 Generated $(echo "$PROCESSED_CONTENT" | wc -l) lines of tasks"

# Show summary
echo ""
echo "📋 Task Summary:"
echo "  - Priority 1: 3 immediate action tasks"
echo "  - Priority 2: 3 code quality tasks"  
echo "  - Priority 3: 3 integration tasks"
echo "  - Total: 9 actionable tasks with agent assignments"

echo ""
echo "🎉 PR feedback processing completed using SpecKit-style layered approach!"