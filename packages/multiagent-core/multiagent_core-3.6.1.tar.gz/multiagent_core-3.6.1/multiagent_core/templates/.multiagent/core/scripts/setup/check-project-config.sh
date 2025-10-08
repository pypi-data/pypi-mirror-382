#!/bin/bash

# Project Configuration Validation Script
# Purpose: Check for required config files and create them if missing
# Based on: .specify/scripts/bash/check-prerequisites.sh pattern
# Usage: ./check-project-config.sh <spec-dir>

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SPEC_DIR="${1:-specs/001-*}"
PROJECT_ROOT="$(pwd)"

# Find spec directory
if [[ "$SPEC_DIR" == *"*"* ]]; then
    SPEC_DIR=$(find . -type d -path "./specs/001-*" | head -1)
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo -e "${RED}Error: Spec directory not found: $SPEC_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}=== Checking Project Configuration Files ===${NC}"
echo ""

# Detect project type from spec (reusing specify pattern)
detect_project_type() {
    local project_type="unknown"
    local tech_stack=""

    # Check plan.md first (more detailed)
    if [ -f "$SPEC_DIR/plan.md" ]; then
        if grep -qi "python.*3\.\|fastapi\|django\|flask" "$SPEC_DIR/plan.md"; then
            tech_stack="python"
        elif grep -qi "node\|npm\|react\|next\|express" "$SPEC_DIR/plan.md"; then
            tech_stack="node"
        elif grep -qi "rust\|cargo" "$SPEC_DIR/plan.md"; then
            tech_stack="rust"
        elif grep -qi "go.*mod" "$SPEC_DIR/plan.md"; then
            tech_stack="go"
        fi
    fi

    # Check spec.md as fallback
    if [ "$tech_stack" == "" ] && [ -f "$SPEC_DIR/spec.md" ]; then
        if grep -qi "python\|fastapi\|django\|flask" "$SPEC_DIR/spec.md"; then
            tech_stack="python"
        elif grep -qi "javascript\|typescript\|node\|react" "$SPEC_DIR/spec.md"; then
            tech_stack="node"
        fi
    fi

    echo "$tech_stack"
}

# Check for Python config files
check_python_config() {
    local needs_creation=false

    echo -e "${YELLOW}Checking Python configuration...${NC}"

    # Check pyproject.toml
    if [ ! -f "pyproject.toml" ]; then
        echo -e "  ${RED}✗${NC} pyproject.toml not found"
        needs_creation=true
    else
        echo -e "  ${GREEN}✓${NC} pyproject.toml exists"
    fi

    # Check requirements.txt or requirements.in
    if [ ! -f "requirements.txt" ] && [ ! -f "requirements.in" ]; then
        echo -e "  ${RED}✗${NC} requirements.txt not found"
        needs_creation=true
    else
        echo -e "  ${GREEN}✓${NC} requirements file exists"
    fi

    # Check setup.py (optional but good to have)
    if [ ! -f "setup.py" ] && [ ! -f "setup.cfg" ]; then
        echo -e "  ${YELLOW}⚠${NC} setup.py/setup.cfg not found (optional)"
    else
        echo -e "  ${GREEN}✓${NC} setup configuration exists"
    fi

    # Check .python-version
    if [ ! -f ".python-version" ]; then
        echo -e "  ${YELLOW}⚠${NC} .python-version not found (recommended)"
    else
        echo -e "  ${GREEN}✓${NC} .python-version exists"
    fi

    return $([ "$needs_creation" = true ] && echo 1 || echo 0)
}

# Check for Node.js config files
check_node_config() {
    local needs_creation=false

    echo -e "${YELLOW}Checking Node.js configuration...${NC}"

    # Check package.json
    if [ ! -f "package.json" ]; then
        echo -e "  ${RED}✗${NC} package.json not found"
        needs_creation=true
    else
        echo -e "  ${GREEN}✓${NC} package.json exists"
    fi

    # Check tsconfig.json for TypeScript projects
    if grep -qi "typescript" "$SPEC_DIR/plan.md" 2>/dev/null || grep -qi "typescript" "$SPEC_DIR/spec.md" 2>/dev/null; then
        if [ ! -f "tsconfig.json" ]; then
            echo -e "  ${RED}✗${NC} tsconfig.json not found (TypeScript project)"
            needs_creation=true
        else
            echo -e "  ${GREEN}✓${NC} tsconfig.json exists"
        fi
    fi

    # Check .nvmrc
    if [ ! -f ".nvmrc" ]; then
        echo -e "  ${YELLOW}⚠${NC} .nvmrc not found (recommended)"
    else
        echo -e "  ${GREEN}✓${NC} .nvmrc exists"
    fi

    # Check for lock file
    if [ ! -f "package-lock.json" ] && [ ! -f "yarn.lock" ] && [ ! -f "pnpm-lock.yaml" ]; then
        echo -e "  ${YELLOW}⚠${NC} No lock file found (will be created on install)"
    else
        echo -e "  ${GREEN}✓${NC} Lock file exists"
    fi

    return $([ "$needs_creation" = true ] && echo 1 || echo 0)
}

# Check for common config files
check_common_config() {
    echo -e "${YELLOW}Checking common configuration...${NC}"

    # Check .gitignore
    if [ ! -f ".gitignore" ]; then
        echo -e "  ${RED}✗${NC} .gitignore not found"
    else
        echo -e "  ${GREEN}✓${NC} .gitignore exists"
    fi

    # Check README
    if [ ! -f "README.md" ] && [ ! -f "README.rst" ] && [ ! -f "README.txt" ]; then
        echo -e "  ${YELLOW}⚠${NC} README not found"
    else
        echo -e "  ${GREEN}✓${NC} README exists"
    fi

    # Check .env.example
    if [ ! -f ".env.example" ] && [ ! -f ".env.template" ]; then
        echo -e "  ${YELLOW}⚠${NC} .env.example not found"
    else
        echo -e "  ${GREEN}✓${NC} Environment template exists"
    fi

    # Check for CI/CD config
    if [ ! -d ".github/workflows" ]; then
        echo -e "  ${YELLOW}⚠${NC} .github/workflows not found (will be generated)"
    else
        echo -e "  ${GREEN}✓${NC} GitHub workflows directory exists"
    fi
}

# Main execution
echo -e "${BLUE}Analyzing spec to detect project type...${NC}"
PROJECT_TYPE=$(detect_project_type)
echo -e "Detected project type: ${GREEN}$PROJECT_TYPE${NC}"
echo ""

# Run checks based on project type
case "$PROJECT_TYPE" in
    python)
        check_python_config
        PYTHON_MISSING=$?
        ;;
    node)
        check_node_config
        NODE_MISSING=$?
        ;;
    *)
        echo -e "${YELLOW}Unknown project type, checking for common files...${NC}"
        ;;
esac

echo ""
check_common_config

echo ""
echo -e "${BLUE}=== Summary ===${NC}"

# Determine if agent intervention needed
NEEDS_AGENT_HELP=false

if [[ "$PROJECT_TYPE" == "python" && "$PYTHON_MISSING" -eq 1 ]]; then
    echo -e "${YELLOW}Python configuration files need to be created${NC}"
    NEEDS_AGENT_HELP=true
elif [[ "$PROJECT_TYPE" == "node" && "$NODE_MISSING" -eq 1 ]]; then
    echo -e "${YELLOW}Node.js configuration files need to be created${NC}"
    NEEDS_AGENT_HELP=true
fi

if [ "$NEEDS_AGENT_HELP" = true ]; then
    echo -e "${YELLOW}→ Agent should create missing configuration files based on spec${NC}"
    echo -e "${YELLOW}→ Reading from: $SPEC_DIR${NC}"
    exit 1  # Non-zero exit indicates agent help needed
else
    echo -e "${GREEN}✓ All required configuration files present${NC}"
    echo -e "${GREEN}✓ Project ready for dependency installation${NC}"
    exit 0  # Zero exit indicates all good
fi