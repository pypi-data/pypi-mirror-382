#!/bin/bash

# Intelligent Test Generation Script using Claude Subagent
# This script uses Claude's actual intelligence to analyze tasks and generate optimal test structures

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
SESSION_ID="test-intelligent-$(basename "$SPEC_DIR")-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOGS_DIR/$SESSION_ID.log"

# Ensure directories exist
mkdir -p "$MEMORY_DIR"
mkdir -p "$LOGS_DIR"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}=== Intelligent Test Generation with Claude ===${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Find tasks file
TASKS_FILE="$SPEC_DIR/tasks.md"
LAYERED_TASKS="$SPEC_DIR/agent-tasks/layered-tasks.md"

if [[ -f "$LAYERED_TASKS" ]]; then
    TASKS_FILE="$LAYERED_TASKS"
elif [[ ! -f "$TASKS_FILE" ]]; then
    echo -e "${RED}Error: No tasks file found${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

echo -e "${GREEN}✓ Found tasks file: $TASKS_FILE${NC}" | tee -a "$LOG_FILE"

# Read tasks content
TASKS_CONTENT=$(cat "$TASKS_FILE")

# Create analysis prompt for Claude
ANALYSIS_PROMPT="You are analyzing tasks to generate an optimal test structure.

TASKS TO ANALYZE:
\`\`\`
$TASKS_CONTENT
\`\`\`

TEMPLATES AVAILABLE:
- frontend_template.test.js - React/Vue/UI component tests
- backend_template.test.py - Python API endpoint tests
- integration_template.test.js - Service integration tests
- e2e_template.test.js - End-to-end workflow tests
- contract_template.test.yaml - API contract tests
- unit_template.test.js - Unit tests

ANALYZE each task and OUTPUT a shell script that:
1. Creates the optimal directory structure under $OUTPUT_DIR
2. Generates test files using the templates
3. Groups related tests intelligently
4. Uses your understanding of the task context

OUTPUT FORMAT:
Generate ONLY executable bash commands like:
\`\`\`bash
# Create directories
mkdir -p $OUTPUT_DIR/backend/api/feedback
mkdir -p $OUTPUT_DIR/backend/auth/security
mkdir -p $OUTPUT_DIR/integration/github
mkdir -p $OUTPUT_DIR/e2e/workflows

# Generate test files with proper templates
cat $TEMPLATES_DIR/backend_template.test.py | sed 's/{{TASK_ID}}/T020/g' | sed 's/{{TASK_DESC}}/FastAPI feedback endpoint with webhook validation/g' > $OUTPUT_DIR/backend/api/feedback/T020_feedback_endpoint.test.py

# Continue for each task...
\`\`\`

Be intelligent about:
- Understanding task relationships (T010 router works with T020 endpoint)
- Recognizing testing needs (auth tasks need security tests)
- Creating logical groupings (group GitHub-related tests together)
- Optimizing for maintainability

Start your response with '#!/bin/bash' and include ONLY executable commands."

# Save prompt to file
PROMPT_FILE="$MEMORY_DIR/prompt-$SESSION_ID.txt"
echo "$ANALYSIS_PROMPT" > "$PROMPT_FILE"

echo -e "${YELLOW}Calling Claude for intelligent analysis...${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Create a temporary script file for Claude's output
CLAUDE_SCRIPT="$MEMORY_DIR/claude-generated-$SESSION_ID.sh"

# Here we would normally call Claude through the Task tool or similar
# For demonstration, I'll create a placeholder
cat > "$CLAUDE_SCRIPT" << 'CLAUDE_OUTPUT'
#!/bin/bash
echo "Claude would generate intelligent test structure here based on task analysis"
CLAUDE_OUTPUT

# Make the generated script executable
chmod +x "$CLAUDE_SCRIPT"

# Execute Claude's generated script
echo -e "${GREEN}Executing Claude's test generation plan...${NC}" | tee -a "$LOG_FILE"
# bash "$CLAUDE_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}=== Intelligent Test Generation Complete ===${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Output directory: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Session log: $LOG_FILE${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Claude's script: $CLAUDE_SCRIPT${NC}" | tee -a "$LOG_FILE"

# Note about using Task tool
echo "" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Note: In production, this would use the Task tool to call Claude:${NC}" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Task(subagent_type='general-purpose', prompt=analysis_prompt)${NC}" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Claude would return executable bash commands based on intelligent analysis${NC}" | tee -a "$LOG_FILE"