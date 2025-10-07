#!/bin/bash

# Improved Test Generation Script - Better Structure
# Usage: ./generate-tests-improved.sh <spec-dir> [output-dir]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SPEC_DIR="${1:-specs/001-build-a-complete}"
OUTPUT_DIR="${2:-tests}"
TEMPLATES_DIR=".multiagent/testing/templates"
MEMORY_DIR=".multiagent/testing/memory"
LOGS_DIR=".multiagent/testing/logs"

# Create session ID
SESSION_ID="test-$(basename "$SPEC_DIR")-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOGS_DIR/$SESSION_ID.log"

# Ensure directories exist - ONLY backend and frontend at root
mkdir -p "$OUTPUT_DIR"/{backend,frontend}
mkdir -p "$MEMORY_DIR"
mkdir -p "$LOGS_DIR"

# Create subdirectories
mkdir -p "$OUTPUT_DIR"/backend/{api,auth,services,models,middleware,utils,workers}
mkdir -p "$OUTPUT_DIR"/frontend/{components,pages,hooks,utils,services}

echo -e "${BLUE}=== Improved Test Generation ===${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Find tasks file
LAYERED_TASKS="$SPEC_DIR/agent-tasks/layered-tasks.md"
if [[ ! -f "$LAYERED_TASKS" ]]; then
    LAYERED_TASKS="$SPEC_DIR/tasks.md"
    if [[ ! -f "$LAYERED_TASKS" ]]; then
        echo -e "${RED}Error: No tasks file found${NC}" | tee -a "$LOG_FILE"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Found tasks file: $LAYERED_TASKS${NC}" | tee -a "$LOG_FILE"

# Function to determine if task is backend or frontend
determine_category() {
    local task="$1"
    local task_lower=$(echo "$task" | tr '[:upper:]' '[:lower:]')

    # Python files are ALWAYS backend
    if echo "$task_lower" | grep -q "\.py"; then
        echo "backend"
    # JavaScript/TypeScript files are frontend
    elif echo "$task_lower" | grep -q "\.jsx\|\.tsx\|\.js\|\.ts"; then
        echo "frontend"
    # Backend keywords
    elif echo "$task_lower" | grep -qE "fastapi|api|endpoint|webhook|hmac|auth|security|token|rate.limit|background|queue|handler|server|backend|database|model|schema|middleware|worker|celery|redis|postgres|mysql|mongodb"; then
        echo "backend"
    # Frontend keywords
    elif echo "$task_lower" | grep -qE "component|ui|frontend|react|vue|angular|dashboard|form|button|page|view|style|css|html|dom|browser|client"; then
        echo "frontend"
    # GitHub Actions/Workflows - treat as frontend (config files)
    elif echo "$task_lower" | grep -qE "github.action|workflow|\.yml|\.yaml|ci/cd"; then
        echo "frontend"
    # Default to backend for technical tasks
    else
        echo "backend"
    fi
}

# Function to determine subdirectory within backend/frontend
determine_subdirectory() {
    local task="$1"
    local category="$2"
    local task_lower=$(echo "$task" | tr '[:upper:]' '[:lower:]')

    if [[ "$category" == "backend" ]]; then
        # Backend subdirectories
        if echo "$task_lower" | grep -qE "auth|security|token|login|permission|user.management"; then
            echo "auth"
        elif echo "$task_lower" | grep -qE "api|endpoint|route|fastapi|feedback.endpoint"; then
            echo "api"
        elif echo "$task_lower" | grep -qE "agentswarm|integration|bridge|service.communication"; then
            echo "services"
        elif echo "$task_lower" | grep -qE "model|schema|database|orm"; then
            echo "models"
        elif echo "$task_lower" | grep -qE "middleware|interceptor"; then
            echo "middleware"
        elif echo "$task_lower" | grep -qE "background|queue|worker|celery|task.processing"; then
            echo "workers"
        else
            echo "utils"
        fi
    else
        # Frontend subdirectories
        if echo "$task_lower" | grep -qE "component|button|form|modal|widget"; then
            echo "components"
        elif echo "$task_lower" | grep -qE "page|route|view|screen"; then
            echo "pages"
        elif echo "$task_lower" | grep -qE "hook|use[A-Z]"; then
            echo "hooks"
        elif echo "$task_lower" | grep -qE "service|api.client|fetch"; then
            echo "services"
        else
            echo "utils"
        fi
    fi
}

# Function to generate test file
generate_test_file() {
    local task_id="$1"
    local task_desc="$2"
    local layer="$3"

    # Clean task description for filename
    local clean_desc=$(echo "$task_desc" | sed 's/\x1b\[[0-9;]*m//g' | sed 's/@[a-z]*//g' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//' | cut -c1-50)

    # Determine category (backend or frontend)
    local category=$(determine_category "$task_desc")

    # Determine subdirectory
    local subdir=$(determine_subdirectory "$task_desc" "$category")

    # Determine file extension
    local ext="test.js"
    [[ "$category" == "backend" ]] && ext="test.py"

    # Create test file path - ALWAYS in a subdirectory
    local test_dir="$OUTPUT_DIR/$category/$subdir"
    mkdir -p "$test_dir"

    local test_file="$test_dir/${task_id}_${clean_desc}.$ext"
    local template_file="$TEMPLATES_DIR/${category}_template.$ext"

    # Use template if exists, otherwise use basic template
    if [[ -f "$template_file" ]]; then
        cat "$template_file" | \
        sed "s|{{TASK_ID}}|$task_id|g" | \
        sed "s|{{TASK_DESC}}|$task_desc|g" | \
        sed "s|{{LAYER}}|$layer|g" | \
        sed "s|{{CATEGORY}}|$category/$subdir|g" > "$test_file"
    else
        # Create basic test structure
        if [[ "$ext" == "test.py" ]]; then
            cat > "$test_file" << EOF
"""
Test for $task_id: $task_desc
Layer: $layer
Category: $category/$subdir
Generated: $(date -Iseconds)
"""

import pytest
from unittest.mock import Mock, patch

class Test${task_id}:
    """Test suite for $task_id"""

    def test_implementation_exists(self):
        """Test that implementation exists"""
        # TODO: Implement test for $task_desc
        pass
EOF
        else
            cat > "$test_file" << EOF
/**
 * Test for $task_id: $task_desc
 * Layer: $layer
 * Category: $category/$subdir
 * Generated: $(date -Iseconds)
 */

describe('$task_id', () => {
  it('should implement: $task_desc', () => {
    // TODO: Implement test
    expect(true).toBe(true);
  });
});
EOF
        fi
    fi

    echo -e "  ${GREEN}✓${NC} Created: $test_file" | tee -a "$LOG_FILE"
}

# Process all tasks
echo -e "${BLUE}Processing tasks...${NC}" | tee -a "$LOG_FILE"

while IFS= read -r line; do
    # Skip empty lines and headers
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]] || [[ "$line" =~ ^-- ]] || [[ "$line" =~ ^## ]]; then
        continue
    fi

    # Extract task ID if present
    if echo "$line" | grep -qE "T[0-9]{3}"; then
        task_id=$(echo "$line" | grep -oE "T[0-9]{3}" | head -1)
        # Remove ANSI codes and clean up description
        task_desc=$(echo "$line" | sed 's/\x1b\[[0-9;]*m//g' | sed 's/^- \[.\] //' | sed "s/T[0-9]\{3\} //" | sed 's/✅.*//' | sed 's/^[ \t@]*//' | sed 's/[ \t]*$//')

        # Determine which layer this task belongs to
        layer="unknown"
        if echo "$line" | grep -q "Layer 1"; then
            layer="1"
        elif echo "$line" | grep -q "Layer 2"; then
            layer="2"
        elif echo "$line" | grep -q "Layer 3"; then
            layer="3"
        fi

        echo -e "Processing: ${YELLOW}$task_id${NC} - $task_desc" | tee -a "$LOG_FILE"

        # Generate test file
        generate_test_file "$task_id" "$task_desc" "$layer"
    fi
done < "$LAYERED_TASKS"

# Generate README files
echo "" | tee -a "$LOG_FILE"
echo -e "${BLUE}Generating README files...${NC}" | tee -a "$LOG_FILE"

# Backend README
cat > "$OUTPUT_DIR/backend/README.md" << EOF
# Backend Tests

## Structure
- **api/** - API endpoints and routes
- **auth/** - Authentication and security
- **services/** - External service integrations
- **models/** - Database models and schemas
- **middleware/** - Request/response middleware
- **workers/** - Background tasks and queues
- **utils/** - Utility functions and helpers

## Running Tests
\`\`\`bash
pytest tests/backend/
\`\`\`
EOF

# Frontend README
cat > "$OUTPUT_DIR/frontend/README.md" << EOF
# Frontend Tests

## Structure
- **components/** - React/Vue components
- **pages/** - Page components and views
- **hooks/** - Custom hooks
- **services/** - API clients and services
- **utils/** - Utility functions

## Running Tests
\`\`\`bash
npm test tests/frontend/
\`\`\`
EOF

echo -e "${GREEN}✓${NC} Created README files" | tee -a "$LOG_FILE"

# Summary
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}=== Test Generation Complete ===${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Backend tests: $(find $OUTPUT_DIR/backend -name "*.py" | wc -l)${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Frontend tests: $(find $OUTPUT_DIR/frontend -name "*.js" | wc -l)${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Total tests: $(find $OUTPUT_DIR -name "*.py" -o -name "*.js" | wc -l)${NC}" | tee -a "$LOG_FILE"