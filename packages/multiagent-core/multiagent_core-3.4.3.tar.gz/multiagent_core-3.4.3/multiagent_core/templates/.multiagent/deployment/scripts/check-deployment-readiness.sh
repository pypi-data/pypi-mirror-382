#!/bin/bash

# Comprehensive Deployment Readiness Check
# Combines production readiness, security audit, and mock verification

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="${1:-$(pwd)}"
ENVIRONMENT="${2:-production}"

echo -e "${BLUE}=== Deployment Readiness Check ===${NC}"
echo "Project: $PROJECT_DIR"
echo "Environment: $ENVIRONMENT"
echo ""

TOTAL_ISSUES=0
CRITICAL_ISSUES=0
WARNINGS=0

# Function to run a check
run_check() {
    local check_name="$1"
    local check_script="$2"

    echo -e "${YELLOW}Running $check_name...${NC}"

    if bash "$check_script" "$PROJECT_DIR" 2>&1 | tee /tmp/check_output.txt; then
        echo -e "  ${GREEN}✓${NC} $check_name passed"
    else
        local exit_code=$?
        if [[ $exit_code -eq 1 ]]; then
            echo -e "  ${RED}✗${NC} $check_name failed with critical issues"
            ((CRITICAL_ISSUES++))
        else
            echo -e "  ${YELLOW}⚠${NC} $check_name has warnings"
            ((WARNINGS++))
        fi
        ((TOTAL_ISSUES++))
    fi
    echo ""
}

# Check 1: Production Readiness
if [[ -f ".multiagent/deployment/scripts/check-production-readiness.sh" ]]; then
    run_check "Production Readiness" ".multiagent/deployment/scripts/check-production-readiness.sh"
fi

# Check 2: Security Audit
if [[ -f ".multiagent/deployment/scripts/security-audit.sh" ]]; then
    run_check "Security Audit" ".multiagent/deployment/scripts/security-audit.sh"
fi

# Check 3: Mock Detection (ensure no mocks in production)
echo -e "${YELLOW}Checking for mocks in production code...${NC}"
MOCK_FILES=$(find "$PROJECT_DIR" -name "*.mock.*" -o -name "*_mock.*" -o -name "mock_*.*" 2>/dev/null | grep -v node_modules | grep -v ".git" | grep -v "tests/" || true)

if [[ -n "$MOCK_FILES" ]]; then
    echo -e "  ${RED}✗${NC} Mock files found outside test directory:"
    echo "$MOCK_FILES" | head -5
    ((CRITICAL_ISSUES++))
else
    echo -e "  ${GREEN}✓${NC} No mock files in production code"
fi

# Check 4: Stub Detection
echo -e "${YELLOW}Checking for stubs in production code...${NC}"
if grep -r "stub\|fake\|dummy" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=tests \
    2>/dev/null | grep -v "// *comment\|# *comment" | grep -q .; then
    echo -e "  ${YELLOW}⚠${NC} Potential stub code found in production"
    ((WARNINGS++))
else
    echo -e "  ${GREEN}✓${NC} No obvious stub code in production"
fi

# Check 5: Test Dependencies in Production
echo -e "${YELLOW}Checking for test dependencies in production...${NC}"
if [[ -f "package.json" ]]; then
    TEST_DEPS=$(grep -E "jest|mocha|chai|sinon|enzyme|testing-library" package.json | grep -v devDependencies || true)
    if [[ -n "$TEST_DEPS" ]]; then
        echo -e "  ${RED}✗${NC} Test dependencies found in production dependencies"
        ((CRITICAL_ISSUES++))
    else
        echo -e "  ${GREEN}✓${NC} Test dependencies properly isolated"
    fi
fi

# Check 6: Environment Configuration
echo -e "${YELLOW}Checking environment configuration...${NC}"
ENV_ISSUES=0

if [[ ! -f ".env.example" ]]; then
    echo -e "  ${RED}✗${NC} Missing .env.example"
    ((ENV_ISSUES++))
fi

if [[ -f ".env" ]] && grep -q "localhost\|127.0.0.1" .env; then
    echo -e "  ${YELLOW}⚠${NC} Local URLs found in .env file"
    ((ENV_ISSUES++))
fi

if [[ $ENV_ISSUES -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} Environment configuration looks good"
else
    ((WARNINGS++))
fi

# Check 7: Build Artifacts
echo -e "${YELLOW}Checking build configuration...${NC}"
BUILD_READY=false

if [[ -f "package.json" ]] && grep -q '"build"' package.json; then
    BUILD_READY=true
    echo -e "  ${GREEN}✓${NC} Build script configured"

    # Try to run build in dry-run mode
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo -e "  ${BLUE}ℹ${NC} Run 'npm run build' to verify build process"
    fi
elif [[ -f "Dockerfile" ]]; then
    BUILD_READY=true
    echo -e "  ${GREEN}✓${NC} Docker build configured"
elif [[ -f "Makefile" ]]; then
    BUILD_READY=true
    echo -e "  ${GREEN}✓${NC} Makefile build configured"
fi

if [[ "$BUILD_READY" == false ]]; then
    echo -e "  ${RED}✗${NC} No build configuration found"
    ((CRITICAL_ISSUES++))
fi

# Check 8: Database Migrations
echo -e "${YELLOW}Checking database configuration...${NC}"
if [[ -d "migrations" ]] || [[ -d "alembic" ]] || [[ -d "prisma/migrations" ]]; then
    echo -e "  ${GREEN}✓${NC} Database migrations configured"

    # Check for pending migrations
    if [[ -f "package.json" ]] && grep -q "prisma" package.json; then
        echo -e "  ${BLUE}ℹ${NC} Run 'npx prisma migrate deploy' before deployment"
    elif [[ -d "alembic" ]]; then
        echo -e "  ${BLUE}ℹ${NC} Run 'alembic upgrade head' before deployment"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} No database migrations found"
fi

# Check 9: Testing Coverage
echo -e "${YELLOW}Checking test coverage...${NC}"
if [[ -d "tests" ]] || [[ -d "test" ]] || [[ -d "__tests__" ]]; then
    TEST_COUNT=$(find . -name "*.test.*" -o -name "*_test.*" -o -name "test_*.*" 2>/dev/null | wc -l)
    if [[ $TEST_COUNT -gt 10 ]]; then
        echo -e "  ${GREEN}✓${NC} Good test coverage ($TEST_COUNT test files)"
    elif [[ $TEST_COUNT -gt 0 ]]; then
        echo -e "  ${YELLOW}⚠${NC} Limited test coverage ($TEST_COUNT test files)"
        ((WARNINGS++))
    else
        echo -e "  ${RED}✗${NC} No tests found"
        ((CRITICAL_ISSUES++))
    fi
else
    echo -e "  ${RED}✗${NC} No test directory found"
    ((CRITICAL_ISSUES++))
fi

# Check 10: Deployment Configuration
echo -e "${YELLOW}Checking deployment configuration...${NC}"
DEPLOY_READY=false

if [[ -f "docker-compose.yml" ]] || [[ -f "docker-compose.yaml" ]]; then
    DEPLOY_READY=true
    echo -e "  ${GREEN}✓${NC} Docker Compose configured"
fi

if [[ -d ".github/workflows" ]]; then
    DEPLOY_READY=true
    echo -e "  ${GREEN}✓${NC} GitHub Actions configured"
fi

if [[ -f "vercel.json" ]] || [[ -f "netlify.toml" ]]; then
    DEPLOY_READY=true
    echo -e "  ${GREEN}✓${NC} Platform deployment configured"
fi

if [[ "$DEPLOY_READY" == false ]]; then
    echo -e "  ${YELLOW}⚠${NC} No deployment configuration found"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}=== Deployment Readiness Summary ===${NC}"
echo -e "Critical Issues: ${RED}$CRITICAL_ISSUES${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Total Issues: $TOTAL_ISSUES"
echo ""

if [[ $CRITICAL_ISSUES -gt 0 ]]; then
    echo -e "${RED}❌ NOT READY FOR DEPLOYMENT${NC}"
    echo "Fix critical issues before deploying to $ENVIRONMENT"
    exit 1
elif [[ $WARNINGS -gt 5 ]]; then
    echo -e "${YELLOW}⚠️  DEPLOYMENT RISKY${NC}"
    echo "Many warnings detected. Review before deploying to $ENVIRONMENT"
    exit 0
else
    echo -e "${GREEN}✅ READY FOR DEPLOYMENT${NC}"
    echo "Project appears ready for $ENVIRONMENT deployment"
    exit 0
fi