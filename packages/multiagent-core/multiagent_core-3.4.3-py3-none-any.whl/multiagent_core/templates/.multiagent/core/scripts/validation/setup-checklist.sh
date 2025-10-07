#!/bin/bash

# Project Setup Checklist - Verify everything is configured correctly
# Usage: ./setup-checklist.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Checklist items
TOTAL_CHECKS=0
PASSED_CHECKS=0
WARNINGS=0

echo -e "${BLUE}=== Project Setup Checklist ===${NC}"
echo ""

# Function to check item
check_item() {
    local description="$1"
    local check_command="$2"
    local is_warning="${3:-false}"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        if [ "$is_warning" = "true" ]; then
            echo -e "${YELLOW}⚠️ ${NC} $description"
            WARNINGS=$((WARNINGS + 1))
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}❌${NC} $description"
        fi
        return 1
    fi
}

echo -e "${YELLOW}1. Core Structure${NC}"
check_item "multiagent init completed" "test -d .multiagent"
check_item "Spec directory exists" "test -d specs/001-*"
check_item "Deployment configs exist" "test -d deployment"
check_item "Testing structure exists" "test -d tests || test -f package.json"
echo ""

echo -e "${YELLOW}2. GitHub Workflows${NC}"
check_item "CI workflow exists" "test -f .github/workflows/ci.yml"
check_item "Deploy workflow exists" "test -f .github/workflows/deploy.yml"
check_item "PR automation exists" "test -f .github/workflows/pr-automation.yml"
check_item "Workflows are valid YAML" "command -v yq && yq eval . .github/workflows/*.yml" true
echo ""

echo -e "${YELLOW}3. Deployment Configuration${NC}"
check_item "Docker config exists" "test -f deployment/docker/Dockerfile"
check_item "Docker compose exists" "test -f deployment/docker/docker-compose.yml"
check_item "Environment template exists" "test -f deployment/configs/.env.example || test -f .env.example"
check_item "Kubernetes configs exist" "test -d deployment/k8s" true
echo ""

echo -e "${YELLOW}4. Git Configuration${NC}"
check_item "Git repository initialized" "test -d .git"
check_item "Pre-commit hook exists" "test -f .git/hooks/pre-commit" true
check_item "Pre-push hook exists" "test -f .git/hooks/pre-push" true
check_item ".gitignore configured" "test -f .gitignore"
check_item ".env excluded from git" "grep -q '^\.env$' .gitignore" true
echo ""

echo -e "${YELLOW}5. Project Dependencies${NC}"
if [ -f "package.json" ]; then
    check_item "Node modules installed" "test -d node_modules"
    check_item "Package lock exists" "test -f package-lock.json || test -f yarn.lock"
    check_item "Test script defined" "grep -q '\"test\"' package.json" true
    check_item "Lint script defined" "grep -q '\"lint\"' package.json" true
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    check_item "Python virtual env exists" "test -d venv || test -d .venv" true
    check_item "Requirements file exists" "test -f requirements.txt || test -f pyproject.toml"
fi
echo ""

echo -e "${YELLOW}6. Testing Framework${NC}"
check_item "Test directory exists" "test -d tests"
check_item "Test files exist" "find tests -name '*.test.*' -o -name 'test_*.py' | grep -q ." true
check_item "Mock detection script available" "test -f .multiagent/deployment/scripts/scan-mocks.sh"
echo ""

echo -e "${YELLOW}7. Environment Configuration${NC}"
check_item "Environment example exists" "test -f .env.example || test -f deployment/configs/.env.example"
check_item "Development env configured" "test -f .env.development || test -f deployment/configs/.env.development" true
check_item "Production env template" "test -f .env.production || test -f deployment/configs/.env.production" true
echo ""

echo -e "${YELLOW}8. Documentation${NC}"
check_item "README exists" "test -f README.md"
check_item "Spec documentation exists" "test -f specs/001-*/spec.md"
check_item "Plan documentation exists" "test -f specs/001-*/plan.md"
check_item "Setup complete marker" "test -f SETUP_COMPLETE.md" true
echo ""

# Generate summary
echo -e "${BLUE}=== Setup Summary ===${NC}"
echo -e "Total checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$((TOTAL_CHECKS - PASSED_CHECKS))${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

# Generate recommendations
if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}🎉 Perfect! Project is fully configured!${NC}"
elif [ $((TOTAL_CHECKS - PASSED_CHECKS)) -le 3 ]; then
    echo -e "${YELLOW}⚠️  Almost ready! Fix the remaining items above.${NC}"
else
    echo -e "${RED}❌ Project needs configuration. Run:${NC}"
    echo "  /project-setup specs/001-*"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Fix any ❌ items above"
echo "2. Review ⚠️  warnings"
echo "3. Add GitHub secrets for deployment"
echo "4. Run: npm test (or pytest) to verify tests"
echo "5. Run: docker-compose up in deployment/docker to test locally"

# Create setup report
cat > SETUP_CHECKLIST.md << EOF
# Project Setup Checklist Report

Generated: $(date)

## Results
- Total Checks: $TOTAL_CHECKS
- Passed: $PASSED_CHECKS
- Failed: $((TOTAL_CHECKS - PASSED_CHECKS))
- Warnings: $WARNINGS

## Status
$(if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo "✅ **Project fully configured**"
elif [ $((TOTAL_CHECKS - PASSED_CHECKS)) -le 3 ]; then
    echo "⚠️ **Almost ready - minor fixes needed**"
else
    echo "❌ **Configuration required**"
fi)

## Manual Actions Required

1. **GitHub Secrets**: Add to repository settings:
   - VERCEL_TOKEN (if using Vercel)
   - CLAUDE_API_KEY (if using Claude)
   - SLACK_BOT_TOKEN (if using Slack)

2. **Environment Variables**: Copy and configure:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your values
   \`\`\`

3. **Test the setup**:
   \`\`\`bash
   # Run tests
   npm test  # or pytest

   # Test deployment locally
   cd deployment/docker
   docker-compose up
   \`\`\`

## Commands Reference

- Start development: \`npm run dev\` or \`python app.py\`
- Run tests: \`npm test\` or \`pytest\`
- Deploy locally: \`cd deployment/docker && docker-compose up\`
- Deploy to production: \`git push main\` (triggers GitHub Actions)
EOF

echo ""
echo -e "${GREEN}Report saved to: SETUP_CHECKLIST.md${NC}"

# Exit with appropriate code
if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    exit 0
else
    exit 1
fi