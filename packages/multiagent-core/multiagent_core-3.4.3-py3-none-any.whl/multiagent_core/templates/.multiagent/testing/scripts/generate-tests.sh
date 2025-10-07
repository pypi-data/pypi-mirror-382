#!/bin/bash

# Test Generation Script - Creates test structure based on layered tasks
# Usage: ./generate-tests.sh <spec-dir> [output-dir]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SPEC_DIR="${1:-specs/002-system-context-we}"
OUTPUT_DIR="${2:-tests}"  # Output to root tests directory by default
TEMPLATES_DIR=".multiagent/testing/templates"
MEMORY_DIR=".multiagent/testing/memory"
LOGS_DIR=".multiagent/testing/logs"

# Create session ID
SESSION_ID="test-$(basename "$SPEC_DIR")-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOGS_DIR/$SESSION_ID.log"

# Ensure directories exist
mkdir -p "$OUTPUT_DIR"/{unit,integration,e2e,contract}
mkdir -p "$MEMORY_DIR"
mkdir -p "$LOGS_DIR"

echo -e "${BLUE}=== Test Generation Session: $SESSION_ID ===${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Check for layered tasks file
LAYERED_TASKS="$SPEC_DIR/agent-tasks/layered-tasks.md"
if [[ ! -f "$LAYERED_TASKS" ]]; then
    echo -e "${YELLOW}Warning: No layered-tasks.md found. Checking for regular tasks.md...${NC}" | tee -a "$LOG_FILE"
    LAYERED_TASKS="$SPEC_DIR/tasks.md"
    if [[ ! -f "$LAYERED_TASKS" ]]; then
        echo -e "${RED}Error: No tasks file found in $SPEC_DIR${NC}" | tee -a "$LOG_FILE"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Found tasks file: $LAYERED_TASKS${NC}" | tee -a "$LOG_FILE"

# Function to extract tasks from a layer
extract_layer_tasks() {
    local layer="$1"
    local layer_name="$2"

    echo -e "${BLUE}Processing Layer $layer: $layer_name${NC}" | tee -a "$LOG_FILE"

    # Extract tasks between layer markers
    awk "/^## Layer $layer:/{flag=1; next} /^## Layer [^$layer]:|^## Summary/{flag=0} flag" "$LAYERED_TASKS" | \
    grep -E "^- \[.\] T[0-9]+" || true
}

# Function to categorize task by content
categorize_task() {
    local task="$1"
    local task_lower=$(echo "$task" | tr '[:upper:]' '[:lower:]')

    # Check for explicit Python files first - these are ALWAYS backend
    if echo "$task_lower" | grep -q "\.py"; then
        echo "backend"
    # Backend patterns - CHECK THESE FIRST before integration
    elif echo "$task_lower" | grep -qE "fastapi|api|endpoint|webhook|hmac|auth|security|token|rate.limit|background.task|queue.handler|server|backend|feedback.endpoint|pr.feedback.router|database|model|schema|middleware"; then
        echo "backend"
    # Frontend patterns
    elif echo "$task_lower" | grep -qE "component|ui|frontend|react|vue|angular|dashboard|form|button|page|view|style|css|github.actions|workflow.yml"; then
        echo "frontend"
    # Integration patterns - ONLY for AgentSwarm or true integration
    elif echo "$task_lower" | grep -qE "agentswarm.integration|integration.bridge|integration.testing"; then
        echo "integration"
    # E2E patterns
    elif echo "$task_lower" | grep -qE "e2e|end.to.end|workflow|scenario|user journey|acceptance"; then
        echo "e2e"
    # Contract patterns
    elif echo "$task_lower" | grep -qE "contract|interface|api spec|protocol|standard|specification"; then
        echo "contract"
    else
        echo "unit"
    fi
}

# Function to generate test file from template
generate_test_file() {
    local task_id="$1"
    local task_desc="$2"
    local category="$3"
    local layer="$4"

    # Clean task description for filename - remove ANSI codes first
    local clean_desc=$(echo "$task_desc" | sed 's/\x1b\[[0-9;]*m//g' | sed 's/@[a-z]*//g' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//' | cut -c1-50)

    # Determine file extension based on category
    local ext="test.js"
    [[ "$category" == "backend" ]] && ext="test.py"
    [[ "$category" == "contract" ]] && ext="test.yaml"

    # Create more specific test directory structure based on task content
    local test_dir="$OUTPUT_DIR/$category"

    # Add subdirectories based on task type
    if echo "$task_desc" | grep -qi "api\|endpoint\|route"; then
        test_dir="$test_dir/api"
    elif echo "$task_desc" | grep -qi "auth\|login\|user\|permission"; then
        test_dir="$test_dir/auth"
    elif echo "$task_desc" | grep -qi "database\|model\|schema"; then
        test_dir="$test_dir/models"
    elif echo "$task_desc" | grep -qi "middleware"; then
        test_dir="$test_dir/middleware"
    elif echo "$task_desc" | grep -qi "component\|ui\|view"; then
        test_dir="$test_dir/components"
    elif echo "$task_desc" | grep -qi "service\|integration"; then
        test_dir="$test_dir/services"
    elif echo "$task_desc" | grep -qi "workflow\|scenario"; then
        test_dir="$test_dir/workflows"
    fi

    mkdir -p "$test_dir"

    # Generate test file
    local test_file="$test_dir/${task_id}_${clean_desc}.$ext"
    local template_file="$TEMPLATES_DIR/${category}_template.$ext"

    if [[ -f "$template_file" ]]; then
        # Use template if it exists
        cat "$template_file" | \
        sed "s|{{TASK_ID}}|$task_id|g" | \
        sed "s|{{TASK_DESC}}|$task_desc|g" | \
        sed "s|{{LAYER}}|$layer|g" | \
        sed "s|{{CATEGORY}}|$category|g" > "$test_file"
    else
        # Generate basic structure if no template
        echo "// Test for $task_id: $task_desc" > "$test_file"
        echo "// Layer: $layer" >> "$test_file"
        echo "// Category: $category" >> "$test_file"
        echo "" >> "$test_file"
        echo "describe('$task_id', () => {" >> "$test_file"
        echo "  it('should $task_desc', () => {" >> "$test_file"
        echo "    // TODO: Implement test" >> "$test_file"
        echo "  });" >> "$test_file"
        echo "});" >> "$test_file"
    fi

    echo -e "  ${GREEN}✓${NC} Created: $test_file" | tee -a "$LOG_FILE"
}

# Process each layer
for layer in 1 2 3; do
    echo "" | tee -a "$LOG_FILE"

    case $layer in
        1) layer_name="Contract & Interface Definition" ;;
        2) layer_name="Parallel Implementation" ;;
        3) layer_name="Integration & Validation" ;;
    esac

    # Extract and process tasks for this layer
    while IFS= read -r task_line; do
        if [[ -n "$task_line" ]]; then
            # Extract task ID and description - handle ANSI codes
            task_id=$(echo "$task_line" | grep -oE "T[0-9]{3}" | head -1 || echo "T000")
            # Remove ANSI color codes, task checkbox, and clean up
            task_desc=$(echo "$task_line" | sed 's/\x1b\[[0-9;]*m//g' | sed 's/^- \[.\] //' | sed "s/T[0-9]\{3\} //" | sed 's/✅.*//' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')

            # Categorize the task
            category=$(categorize_task "$task_desc")

            echo -e "  Processing: ${YELLOW}$task_id${NC} - $task_desc (${BLUE}$category${NC})" | tee -a "$LOG_FILE"

            # Generate test file
            generate_test_file "$task_id" "$task_desc" "$category" "$layer"
        fi
    done < <(extract_layer_tasks "$layer" "$layer_name")
done

# Generate README files for each test category
echo "" | tee -a "$LOG_FILE"
echo -e "${BLUE}Generating README files...${NC}" | tee -a "$LOG_FILE"

for category in unit integration e2e contract frontend backend; do
    if [[ -d "$OUTPUT_DIR/$category" ]] && [[ -n "$(ls -A "$OUTPUT_DIR/$category" 2>/dev/null)" ]]; then
        readme_template="$TEMPLATES_DIR/${category}_readme_template.md"
        readme_file="$OUTPUT_DIR/$category/README.md"

        if [[ -f "$readme_template" ]]; then
            cp "$readme_template" "$readme_file"
        else
            cat > "$readme_file" << EOF
# ${category^} Tests

## Overview
This directory contains ${category} tests generated from the layered task structure.

## Structure
- **Layer 1**: Contract & Interface Definition tests
- **Layer 2**: Parallel Implementation tests
- **Layer 3**: Integration & Validation tests

## Running Tests
\`\`\`bash
# Run all ${category} tests
npm test -- ${category}/

# Run specific layer tests
npm test -- ${category}/layer1/
\`\`\`

## Test Standards
- All tests should follow the project testing conventions
- Use appropriate mocking strategies for external dependencies
- Ensure tests are isolated and repeatable
- Follow the AAA pattern: Arrange, Act, Assert

Generated: $(date)
EOF
        fi
        echo -e "  ${GREEN}✓${NC} Created README: $readme_file" | tee -a "$LOG_FILE"
    fi
done

# Save session memory
MEMORY_FILE="$MEMORY_DIR/$SESSION_ID.json"
cat > "$MEMORY_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "timestamp": "$(date -Iseconds)",
  "spec_dir": "$SPEC_DIR",
  "output_dir": "$OUTPUT_DIR",
  "tasks_file": "$LAYERED_TASKS",
  "layers_processed": 3,
  "test_files_created": $(find "$OUTPUT_DIR" -name "*.test.*" 2>/dev/null | wc -l || echo 0)
}
EOF

echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}=== Test Generation Complete ===${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Output directory: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Session log: $LOG_FILE${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Session memory: $MEMORY_FILE${NC}" | tee -a "$LOG_FILE"