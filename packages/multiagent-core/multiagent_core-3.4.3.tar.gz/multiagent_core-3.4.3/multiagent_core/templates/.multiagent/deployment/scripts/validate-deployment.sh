#!/bin/bash

# Deployment Validation Script - Checks deployment readiness
# Usage: ./validate-deployment.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Deployment Validation ===${NC}"
echo ""

# Track validation status
READY=true
WARNINGS=""
ERRORS=""

# Check deployment directory exists
echo -e "${YELLOW}Checking deployment structure...${NC}"
if [[ -d "deployment" ]]; then
    echo -e "  ${GREEN}✓${NC} Deployment directory exists"

    # Check subdirectories
    for dir in docker k8s configs scripts; do
        if [[ -d "deployment/$dir" ]]; then
            echo -e "  ${GREEN}✓${NC} deployment/$dir exists"
        else
            echo -e "  ${YELLOW}⚠${NC} deployment/$dir missing"
            WARNINGS="$WARNINGS\n- Missing $dir directory"
        fi
    done
else
    echo -e "  ${RED}✗${NC} Deployment directory not found"
    ERRORS="$ERRORS\n- No deployment directory"
    READY=false
fi
echo ""

# Check Docker files
echo -e "${YELLOW}Checking Docker configuration...${NC}"
if [[ -f "deployment/docker/Dockerfile" ]]; then
    echo -e "  ${GREEN}✓${NC} Dockerfile exists"

    # Validate Dockerfile content
    if grep -q "FROM" deployment/docker/Dockerfile; then
        echo -e "  ${GREEN}✓${NC} Dockerfile has FROM instruction"
    else
        echo -e "  ${RED}✗${NC} Invalid Dockerfile"
        ERRORS="$ERRORS\n- Dockerfile missing FROM"
        READY=false
    fi

    if grep -q "HEALTHCHECK" deployment/docker/Dockerfile; then
        echo -e "  ${GREEN}✓${NC} Health check configured"
    else
        echo -e "  ${YELLOW}⚠${NC} No health check"
        WARNINGS="$WARNINGS\n- Consider adding HEALTHCHECK"
    fi
else
    echo -e "  ${RED}✗${NC} Dockerfile not found"
    ERRORS="$ERRORS\n- Missing Dockerfile"
    READY=false
fi

if [[ -f "deployment/docker/docker-compose.yml" ]]; then
    echo -e "  ${GREEN}✓${NC} docker-compose.yml exists"

    # Validate compose file
    if command -v docker-compose &> /dev/null; then
        if docker-compose -f deployment/docker/docker-compose.yml config &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} docker-compose.yml is valid"
        else
            echo -e "  ${RED}✗${NC} docker-compose.yml has errors"
            ERRORS="$ERRORS\n- Invalid docker-compose.yml"
            READY=false
        fi
    fi
else
    echo -e "  ${RED}✗${NC} docker-compose.yml not found"
    ERRORS="$ERRORS\n- Missing docker-compose.yml"
    READY=false
fi
echo ""

# Check environment configuration
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [[ -f "deployment/configs/.env.development" ]]; then
    echo -e "  ${GREEN}✓${NC} .env.development exists"

    # Check for required variables
    REQUIRED_VARS=("DATABASE_URL" "API_PORT" "REDIS_URL")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" deployment/configs/.env.development; then
            # Check if value is empty
            if grep -q "^$var=$" deployment/configs/.env.development; then
                echo -e "  ${YELLOW}⚠${NC} $var is empty"
                WARNINGS="$WARNINGS\n- $var needs value"
            else
                echo -e "  ${GREEN}✓${NC} $var is set"
            fi
        else
            echo -e "  ${RED}✗${NC} $var not found"
            ERRORS="$ERRORS\n- Missing $var"
            READY=false
        fi
    done

    # Check for placeholder values
    if grep -q "change-this\|your-.*-here\|TODO" deployment/configs/.env.development; then
        echo -e "  ${YELLOW}⚠${NC} Placeholder values found"
        WARNINGS="$WARNINGS\n- Replace placeholder values"
    fi

    # Check for exposed secrets
    if grep -q "secret\|password\|key" deployment/docker/docker-compose.yml 2>/dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Possible hardcoded secrets"
        WARNINGS="$WARNINGS\n- Check for hardcoded secrets"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} .env.development not found"
    WARNINGS="$WARNINGS\n- Create .env.development"
fi
echo ""

# Check if Docker is available
echo -e "${YELLOW}Checking Docker availability...${NC}"
if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Docker is installed"

    if docker info &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Docker daemon is running"
    else
        echo -e "  ${RED}✗${NC} Docker daemon not running"
        ERRORS="$ERRORS\n- Start Docker daemon"
        READY=false
    fi
else
    echo -e "  ${RED}✗${NC} Docker not installed"
    ERRORS="$ERRORS\n- Install Docker"
    READY=false
fi
echo ""

# Check port availability
echo -e "${YELLOW}Checking port availability...${NC}"
PORTS=(8000 3000 5432 6379)
for port in "${PORTS[@]}"; do
    if lsof -i :$port &> /dev/null; then
        echo -e "  ${YELLOW}⚠${NC} Port $port is in use"
        WARNINGS="$WARNINGS\n- Port $port in use"
    else
        echo -e "  ${GREEN}✓${NC} Port $port is available"
    fi
done
echo ""

# Generate validation report
echo -e "${BLUE}=== Validation Report ===${NC}"
echo ""

if [[ "$READY" == "true" ]]; then
    echo -e "${GREEN}✅ Deployment is ready!${NC}"
else
    echo -e "${RED}❌ Deployment has blocking issues${NC}"
fi

if [[ -n "$ERRORS" ]]; then
    echo -e "\n${RED}Errors (must fix):${NC}"
    echo -e "$ERRORS"
fi

if [[ -n "$WARNINGS" ]]; then
    echo -e "\n${YELLOW}Warnings (should fix):${NC}"
    echo -e "$WARNINGS"
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
if [[ "$READY" == "true" ]]; then
    echo "1. Review warnings if any"
    echo "2. Run: cd deployment/docker && docker-compose up"
    echo "3. Access app at http://localhost:3000"
else
    echo "1. Fix errors listed above"
    echo "2. Run validation again: ./validate-deployment.sh"
fi

# Exit with error if not ready
[[ "$READY" == "true" ]] || exit 1