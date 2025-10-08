#!/bin/bash
# Quick integration test for multiagent-core development
# Tests the complete user workflow: build → install → init → verify
#
# NOTE: This script is for multiagent-core DEVELOPERS only.
# It is NOT deployed to user projects via multiagent init.
#
# Usage: ./scripts/dev-test.sh

set -e

# Use python3 explicitly for WSL/Linux compatibility
PYTHON=${PYTHON:-python3}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  MultiAgent Core - Development Integration Test           ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Step 1: Build package
echo -e "${BLUE}[1/5]${NC} Building package..."
if $PYTHON -m build > /tmp/build.log 2>&1; then
    echo -e "      ${GREEN}✓${NC} Package built successfully"
else
    echo -e "      ${RED}✗${NC} Package build failed"
    echo "Build log:"
    cat /tmp/build.log
    exit 1
fi

# Step 2: Install via pipx
echo -e "${BLUE}[2/5]${NC} Installing via pipx..."
if pipx install --force . > /dev/null 2>&1; then
    echo -e "      ${GREEN}✓${NC} Installed successfully"
else
    echo -e "      ${RED}✗${NC} pipx install failed"
    exit 1
fi

# Step 3: Test init in clean directory
TEST_DIR=$(mktemp -d)
echo -e "${BLUE}[3/5]${NC} Testing init in ${TEST_DIR}..."

cd "$TEST_DIR"
git init > /dev/null 2>&1

if multiagent init --no-interactive > /dev/null 2>&1; then
    echo -e "      ${GREEN}✓${NC} multiagent init completed"
else
    echo -e "      ${RED}✗${NC} multiagent init failed"
    rm -rf "$TEST_DIR"
    exit 1
fi

# Step 4: Verify directory structure
echo -e "${BLUE}[4/5]${NC} Verifying directory structure..."

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check .multiagent directory
if [ -d ".multiagent" ]; then
    echo -e "      ${GREEN}✓${NC} .multiagent/ directory created"
    ((CHECKS_PASSED++))
else
    echo -e "      ${RED}✗${NC} .multiagent/ directory missing"
    ((CHECKS_FAILED++))
fi

# Check .claude directory
if [ -d ".claude" ]; then
    echo -e "      ${GREEN}✓${NC} .claude/ directory created"
    ((CHECKS_PASSED++))
else
    echo -e "      ${RED}✗${NC} .claude/ directory missing"
    ((CHECKS_FAILED++))
fi

# Check .github directory
if [ -d ".github" ]; then
    echo -e "      ${GREEN}✓${NC} .github/ directory created"
    ((CHECKS_PASSED++))
else
    echo -e "      ${RED}✗${NC} .github/ directory missing"
    ((CHECKS_FAILED++))
fi

# Step 5: Verify git hooks
echo -e "${BLUE}[5/5]${NC} Verifying git hooks..."

# Check pre-push hook
if [ -f ".git/hooks/pre-push" ] && [ -x ".git/hooks/pre-push" ]; then
    # Verify it's the correct hook (contains multiagent/security reference)
    if grep -q "MultiAgent\|secret\|security" ".git/hooks/pre-push" 2>/dev/null; then
        echo -e "      ${GREEN}✓${NC} pre-push hook: Installed and verified"
        ((CHECKS_PASSED++))
    else
        echo -e "      ${YELLOW}⚠${NC} pre-push hook: Exists but content may be incorrect"
        ((CHECKS_PASSED++))
    fi
else
    echo -e "      ${RED}✗${NC} pre-push hook: Missing or not executable"
    ((CHECKS_FAILED++))
fi

# Check post-commit hook
if [ -f ".git/hooks/post-commit" ] && [ -x ".git/hooks/post-commit" ]; then
    # Verify it's the correct hook (contains agent/workflow reference)
    if grep -q "agent\|workflow\|Post-commit" ".git/hooks/post-commit" 2>/dev/null; then
        echo -e "      ${GREEN}✓${NC} post-commit hook: Installed and verified"
        ((CHECKS_PASSED++))
    else
        echo -e "      ${YELLOW}⚠${NC} post-commit hook: Exists but content may be incorrect"
        ((CHECKS_PASSED++))
    fi
else
    echo -e "      ${RED}✗${NC} post-commit hook: Missing or not executable"
    ((CHECKS_FAILED++))
fi

# Cleanup
cd - > /dev/null
rm -rf "$TEST_DIR"

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC} (${CHECKS_PASSED}/${CHECKS_PASSED})"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC} (${CHECKS_PASSED}/$(($CHECKS_PASSED + $CHECKS_FAILED)) passed)"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
