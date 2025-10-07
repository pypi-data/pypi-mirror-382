#!/bin/bash

# Security Audit Script
# Comprehensive security checks for deployment readiness

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="${1:-$(pwd)}"

echo -e "${BLUE}=== Security Audit ===${NC}"
echo "Project: $PROJECT_DIR"
echo ""

VULNERABILITIES=0
WARNINGS=0

# Check 1: Hardcoded secrets
echo -e "${YELLOW}Scanning for hardcoded secrets...${NC}"
PATTERNS=(
    "api[_-]?key.*=.*['\"]"
    "secret.*=.*['\"]"
    "password.*=.*['\"]"
    "token.*=.*['\"]"
    "AWS_[A-Z_]*=.*['\"]"
    "GITHUB_[A-Z_]*=.*['\"]"
)

for pattern in "${PATTERNS[@]}"; do
    if grep -r -i "$pattern" "$PROJECT_DIR" \
        --include="*.js" --include="*.ts" --include="*.py" \
        --exclude-dir=node_modules --exclude-dir=.git \
        --exclude-dir=venv --exclude-dir=.venv \
        --exclude="*.test.*" --exclude="*_test.*" \
        2>/dev/null | grep -v ".env" | grep -q .; then
        echo -e "  ${RED}✗${NC} Potential hardcoded secrets found (pattern: $pattern)"
        ((VULNERABILITIES++))
    fi
done

if [[ $VULNERABILITIES -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} No hardcoded secrets detected"
fi

# Check 2: SQL injection vulnerabilities
echo -e "${YELLOW}Checking for SQL injection risks...${NC}"
if grep -r "query.*+.*\$\|query.*+.*req\.\|execute.*+.*\$" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -q .; then
    echo -e "  ${RED}✗${NC} Potential SQL injection vulnerabilities found"
    ((VULNERABILITIES++))
else
    echo -e "  ${GREEN}✓${NC} No obvious SQL injection patterns"
fi

# Check 3: XSS vulnerabilities
echo -e "${YELLOW}Checking for XSS vulnerabilities...${NC}"
if grep -r "innerHTML\|dangerouslySetInnerHTML\|document.write" "$PROJECT_DIR" \
    --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -q .; then
    echo -e "  ${YELLOW}⚠${NC} Potential XSS vulnerabilities found - ensure proper sanitization"
    ((WARNINGS++))
fi

# Check 4: Authentication
echo -e "${YELLOW}Checking authentication setup...${NC}"
AUTH_PATTERNS=(
    "jwt\|jsonwebtoken"
    "passport\|auth0"
    "@auth\|authenticate"
    "session\|cookie"
)

AUTH_FOUND=false
for pattern in "${AUTH_PATTERNS[@]}"; do
    if grep -r -i "$pattern" "$PROJECT_DIR" \
        --include="*.js" --include="*.ts" --include="*.py" \
        --exclude-dir=node_modules --exclude-dir=.git \
        2>/dev/null | grep -q .; then
        AUTH_FOUND=true
        break
    fi
done

if $AUTH_FOUND; then
    echo -e "  ${GREEN}✓${NC} Authentication implementation found"
else
    echo -e "  ${YELLOW}⚠${NC} No authentication implementation detected"
    ((WARNINGS++))
fi

# Check 5: CORS configuration
echo -e "${YELLOW}Checking CORS configuration...${NC}"
if grep -r "cors\|Access-Control-Allow-Origin.*\*" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -q "\*"; then
    echo -e "  ${YELLOW}⚠${NC} Wildcard CORS detected - consider restricting origins"
    ((WARNINGS++))
else
    echo -e "  ${GREEN}✓${NC} No wildcard CORS detected"
fi

# Check 6: Rate limiting
echo -e "${YELLOW}Checking rate limiting...${NC}"
if grep -r "rate-limit\|ratelimit\|express-rate-limit\|throttle" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -q .; then
    echo -e "  ${GREEN}✓${NC} Rate limiting configured"
else
    echo -e "  ${YELLOW}⚠${NC} No rate limiting detected"
    ((WARNINGS++))
fi

# Check 7: HTTPS enforcement
echo -e "${YELLOW}Checking HTTPS enforcement...${NC}"
if grep -r "http://" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" --include="*.env.example" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -v "localhost\|127.0.0.1\|0.0.0.0" | grep -q .; then
    echo -e "  ${YELLOW}⚠${NC} Non-HTTPS URLs found in production code"
    ((WARNINGS++))
fi

# Check 8: Input validation
echo -e "${YELLOW}Checking input validation...${NC}"
if grep -r "joi\|yup\|express-validator\|pydantic\|marshmallow" "$PROJECT_DIR" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=node_modules --exclude-dir=.git \
    2>/dev/null | grep -q .; then
    echo -e "  ${GREEN}✓${NC} Input validation library detected"
else
    echo -e "  ${YELLOW}⚠${NC} No input validation library detected"
    ((WARNINGS++))
fi

# Check 9: Dependency vulnerabilities
echo -e "${YELLOW}Checking for dependency vulnerabilities...${NC}"
if [[ -f "$PROJECT_DIR/package-lock.json" ]]; then
    echo -e "  ${BLUE}ℹ${NC} Run 'npm audit' to check for vulnerabilities"
elif [[ -f "$PROJECT_DIR/yarn.lock" ]]; then
    echo -e "  ${BLUE}ℹ${NC} Run 'yarn audit' to check for vulnerabilities"
elif [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
    echo -e "  ${BLUE}ℹ${NC} Run 'safety check' to check for vulnerabilities"
fi

# Check 10: Security headers
echo -e "${YELLOW}Checking security headers...${NC}"
SECURITY_HEADERS=(
    "helmet"
    "X-Frame-Options"
    "X-Content-Type-Options"
    "Content-Security-Policy"
    "Strict-Transport-Security"
)

HEADERS_FOUND=false
for header in "${SECURITY_HEADERS[@]}"; do
    if grep -r "$header" "$PROJECT_DIR" \
        --include="*.js" --include="*.ts" --include="*.py" \
        --exclude-dir=node_modules --exclude-dir=.git \
        2>/dev/null | grep -q .; then
        HEADERS_FOUND=true
        break
    fi
done

if $HEADERS_FOUND; then
    echo -e "  ${GREEN}✓${NC} Security headers configured"
else
    echo -e "  ${YELLOW}⚠${NC} No security headers detected"
    ((WARNINGS++))
fi

echo ""
echo -e "${BLUE}=== Security Audit Summary ===${NC}"
echo -e "Vulnerabilities: ${RED}$VULNERABILITIES${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [[ $VULNERABILITIES -gt 0 ]]; then
    echo -e "${RED}CRITICAL:${NC} Fix vulnerabilities before deployment!"
    exit 1
elif [[ $WARNINGS -gt 5 ]]; then
    echo -e "${YELLOW}WARNING:${NC} Many security improvements needed"
    exit 0
else
    echo -e "${GREEN}PASSED:${NC} Basic security checks passed"
    exit 0
fi