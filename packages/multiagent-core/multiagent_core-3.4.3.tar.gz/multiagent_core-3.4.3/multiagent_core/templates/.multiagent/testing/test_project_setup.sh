#!/bin/bash

# Project Multi-Agent Setup Verification
# This script verifies that the multi-agent framework is properly set up in your project
# Run this AFTER `multiagent init` to verify everything is working

set -e

echo "🔍 Multi-Agent Project Verification"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# This script runs IN the project directory
PROJECT_DIR="${PWD}"
ERRORS=0

echo -e "${YELLOW}Checking project: $PROJECT_DIR${NC}"

# Step 1: Verify directory structure
echo -e "\n${GREEN}Step 1: Verifying directory structure...${NC}"

REQUIRED_DIRS=(
    ".multiagent"
    ".multiagent/core"
    ".multiagent/templates"
    ".multiagent/docs"
    ".claude"
    ".github/workflows"
    ".vscode"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir"
    else
        echo -e "  ${RED}✗${NC} $dir missing"
        ((ERRORS++))
    fi
done

# Step 2: Verify essential files
echo -e "\n${GREEN}Step 2: Verifying essential files...${NC}"

REQUIRED_FILES=(
    ".multiagent/README.md"
    ".multiagent/components.json"
    ".claude/settings.local.json"
    ".github/workflows/multi-environment-test.yml"
    ".vscode/settings.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file missing"
        ((ERRORS++))
    fi
done

# Step 3: Check for AI CLI availability
echo -e "\n${GREEN}Step 3: Checking AI CLI availability...${NC}"

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $2 available"
        return 0
    else
        echo -e "  ${YELLOW}○${NC} $2 not installed"
        return 1
    fi
}

check_command "specify" "spec-kit"
check_command "gemini" "Gemini CLI"
check_command "qwen" "Qwen CLI"
check_command "codex" "Codex CLI"
check_command "claude" "Claude CLI"
check_command "openai" "OpenAI CLI"

# Step 4: Display components status
echo -e "\n${GREEN}Step 4: Component status...${NC}"

if [ -f ".multiagent/components.json" ]; then
    echo "Current components configuration:"
    cat .multiagent/components.json | head -20
fi

# Step 5: Summary
echo -e "\n${GREEN}================================${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Multi-agent setup verified successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  • Install optional components with pipx:"
    echo "    - pipx install multiagent-testing"
    echo "    - pipx install multiagent-devops"
    echo "    - pipx install multiagent-agentswarm"
    echo "  • Start developing with your AI assistants"
else
    echo -e "${RED}❌ Found $ERRORS issues with multi-agent setup${NC}"
    echo ""
    echo "To fix:"
    echo "  • Run: multiagent init --no-interactive"
    echo "  • Check the .multiagent/README.md for setup instructions"
fi