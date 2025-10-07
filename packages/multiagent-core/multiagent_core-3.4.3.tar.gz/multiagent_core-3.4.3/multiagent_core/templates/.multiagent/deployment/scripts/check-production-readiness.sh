#!/bin/bash

# Production Readiness Check Script
# This belongs in deployment, not core!

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="${1:-$(pwd)}"
SPEC_DIR="$PROJECT_DIR/specs"

echo -e "${BLUE}=== Production Readiness Check ===${NC}"
echo "Project: $PROJECT_DIR"
echo ""

ISSUES=0

# Check 1: Environment variables
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [[ -f "$PROJECT_DIR/.env.example" ]]; then
    echo -e "  ${GREEN}✓${NC} .env.example exists"
else
    echo -e "  ${RED}✗${NC} Missing .env.example"
    ((ISSUES++))
fi

if [[ -f "$PROJECT_DIR/.env" ]]; then
    echo -e "  ${YELLOW}⚠${NC} .env exists (ensure secrets are not committed)"
fi

# Check 2: Security audit
echo -e "${YELLOW}Checking security...${NC}"
if grep -r "password\|secret\|key" "$PROJECT_DIR" --include="*.js" --include="*.py" --include="*.ts" 2>/dev/null | grep -v ".env" | grep -q "="; then
    echo -e "  ${RED}✗${NC} Potential hardcoded secrets found"
    ((ISSUES++))
else
    echo -e "  ${GREEN}✓${NC} No obvious hardcoded secrets"
fi

# Check 3: Error handling
echo -e "${YELLOW}Checking error handling...${NC}"
if grep -r "catch.*{.*}" "$PROJECT_DIR" --include="*.js" --include="*.ts" 2>/dev/null | grep -q "// *empty\|//empty\|{ *}"; then
    echo -e "  ${YELLOW}⚠${NC} Empty catch blocks found"
    ((ISSUES++))
fi

# Check 4: Logging
echo -e "${YELLOW}Checking logging setup...${NC}"
if grep -r "console.log\|print(" "$PROJECT_DIR" --include="*.js" --include="*.py" --include="*.ts" 2>/dev/null | wc -l | grep -q "^0$"; then
    echo -e "  ${YELLOW}⚠${NC} No logging found - consider adding structured logging"
else
    echo -e "  ${GREEN}✓${NC} Logging statements found"
fi

# Check 5: Database migrations
echo -e "${YELLOW}Checking database setup...${NC}"
if [[ -d "$PROJECT_DIR/migrations" ]] || [[ -d "$PROJECT_DIR/alembic" ]] || [[ -d "$PROJECT_DIR/prisma" ]]; then
    echo -e "  ${GREEN}✓${NC} Database migration structure found"
else
    echo -e "  ${YELLOW}⚠${NC} No database migration structure detected"
fi

# Check 6: Testing
echo -e "${YELLOW}Checking test coverage...${NC}"
TEST_COUNT=$(find "$PROJECT_DIR/tests" -name "*.test.*" -o -name "*_test.*" 2>/dev/null | wc -l)
if [[ $TEST_COUNT -gt 0 ]]; then
    echo -e "  ${GREEN}✓${NC} Found $TEST_COUNT test files"
else
    echo -e "  ${RED}✗${NC} No test files found"
    ((ISSUES++))
fi

# Check 7: Documentation
echo -e "${YELLOW}Checking documentation...${NC}"
if [[ -f "$PROJECT_DIR/README.md" ]]; then
    echo -e "  ${GREEN}✓${NC} README.md exists"
else
    echo -e "  ${RED}✗${NC} Missing README.md"
    ((ISSUES++))
fi

# Check 8: Performance
echo -e "${YELLOW}Checking for common performance issues...${NC}"
if grep -r "SELECT.*FROM.*WHERE" "$PROJECT_DIR" --include="*.js" --include="*.py" --include="*.ts" 2>/dev/null | grep -q "for\|while\|map\|forEach"; then
    echo -e "  ${YELLOW}⚠${NC} Potential N+1 query patterns detected"
fi

# Check 9: Build artifacts
echo -e "${YELLOW}Checking build configuration...${NC}"
if [[ -f "$PROJECT_DIR/package.json" ]] && grep -q '"build"' "$PROJECT_DIR/package.json"; then
    echo -e "  ${GREEN}✓${NC} Build script configured"
elif [[ -f "$PROJECT_DIR/Makefile" ]]; then
    echo -e "  ${GREEN}✓${NC} Makefile found"
elif [[ -f "$PROJECT_DIR/setup.py" ]] || [[ -f "$PROJECT_DIR/pyproject.toml" ]]; then
    echo -e "  ${GREEN}✓${NC} Python build configuration found"
else
    echo -e "  ${YELLOW}⚠${NC} No build configuration detected"
fi

# Check 10: Monitoring
echo -e "${YELLOW}Checking monitoring setup...${NC}"
if grep -r "prometheus\|datadog\|newrelic\|sentry" "$PROJECT_DIR" --include="*.js" --include="*.py" --include="*.ts" --include="*.yml" 2>/dev/null | grep -q .; then
    echo -e "  ${GREEN}✓${NC} Monitoring/APM configuration found"
else
    echo -e "  ${YELLOW}⚠${NC} No monitoring setup detected"
fi

echo ""
echo -e "${BLUE}=== Summary ===${NC}"
if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}Production ready!${NC} All critical checks passed."
else
    echo -e "${RED}$ISSUES critical issues${NC} need to be addressed before production."
fi
echo ""

exit $ISSUES