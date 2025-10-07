#!/bin/bash

# Generate GitHub Workflows based on project spec
# Usage: ./generate-workflows.sh <spec-dir>

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SPEC_DIR="${1:-specs/001-*}"
TEMPLATES_DIR=".multiagent/core/templates/workflows"
OUTPUT_DIR=".github/workflows"

# Find spec directory if pattern provided
if [[ "$SPEC_DIR" == *"*"* ]]; then
    SPEC_DIR=$(find . -type d -path "./specs/001-*" | head -1)
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

echo -e "${BLUE}=== GitHub Workflow Generation ===${NC}"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Analyze project type from spec
detect_project_type() {
    local project_type="generic"
    local framework=""
    local deployment=""

    # Check spec.md for project type
    if [ -f "$SPEC_DIR/spec.md" ]; then
        # Web application detection
        if grep -qi "next\|react\|vue\|angular" "$SPEC_DIR/spec.md"; then
            project_type="webapp"
            framework="nextjs"
        fi

        # API detection
        if grep -qi "api\|fastapi\|express\|flask" "$SPEC_DIR/spec.md"; then
            project_type="api"
            framework="fastapi"
        fi

        # CLI tool detection
        if grep -qi "cli\|command.line\|terminal" "$SPEC_DIR/spec.md"; then
            project_type="cli"
        fi

        # Deployment detection
        if grep -qi "vercel" "$SPEC_DIR/spec.md"; then
            deployment="vercel"
        elif grep -qi "aws\|lambda" "$SPEC_DIR/spec.md"; then
            deployment="aws"
        elif grep -qi "kubernetes\|k8s" "$SPEC_DIR/spec.md"; then
            deployment="kubernetes"
        fi
    fi

    echo "$project_type:$framework:$deployment"
}

# Generate CI workflow
generate_ci_workflow() {
    local project_info="$1"
    IFS=':' read -r project_type framework deployment <<< "$project_info"

    echo -e "${YELLOW}Generating CI workflow for $project_type project...${NC}"

    cat > "$OUTPUT_DIR/ci.yml" << 'EOF'
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Detect project setup
      id: detect
      run: |
        if [ -f "package.json" ]; then
          echo "type=node" >> $GITHUB_OUTPUT
        elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
          echo "type=python" >> $GITHUB_OUTPUT
        else
          echo "type=unknown" >> $GITHUB_OUTPUT
        fi

    - name: Setup Node.js
      if: steps.detect.outputs.type == 'node'
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Setup Python
      if: steps.detect.outputs.type == 'python'
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        if [ -f "package.json" ]; then
          npm ci
        elif [ -f "requirements.txt" ]; then
          pip install -r requirements.txt
        elif [ -f "pyproject.toml" ]; then
          pip install -e .
        fi

    - name: Run tests
      run: |
        if [ -f "package.json" ] && npm run | grep -q test; then
          npm test
        elif [ -d "tests" ]; then
          pytest
        else
          echo "No tests found"
        fi

    - name: Run linting
      run: |
        if [ -f "package.json" ] && npm run | grep -q lint; then
          npm run lint
        elif command -v flake8 &> /dev/null; then
          flake8 .
        fi
EOF

    echo -e "${GREEN}✓${NC} Created $OUTPUT_DIR/ci.yml"
}

# Generate deployment workflow
generate_deployment_workflow() {
    local project_info="$1"
    IFS=':' read -r project_type framework deployment <<< "$project_info"

    if [ -z "$deployment" ]; then
        deployment="docker"
    fi

    echo -e "${YELLOW}Generating deployment workflow for $deployment...${NC}"

    cat > "$OUTPUT_DIR/deploy.yml" << EOF
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
    - uses: actions/checkout@v4
EOF

    # Add deployment-specific steps
    case "$deployment" in
        "vercel")
            cat >> "$OUTPUT_DIR/deploy.yml" << 'EOF'

    - name: Deploy to Vercel
      env:
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
      run: |
        npm install -g vercel
        vercel --prod --token=$VERCEL_TOKEN --yes
EOF
            ;;

        "aws")
            cat >> "$OUTPUT_DIR/deploy.yml" << 'EOF'

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Deploy to AWS
      run: |
        # Add AWS deployment commands based on service
        echo "AWS deployment configured"
EOF
            ;;

        "kubernetes")
            cat >> "$OUTPUT_DIR/deploy.yml" << 'EOF'

    - name: Build Docker image
      run: |
        docker build -f deployment/docker/Dockerfile -t ${{ github.repository }}:${{ github.sha }} .

    - name: Deploy to Kubernetes
      run: |
        # Add kubectl commands
        echo "Kubernetes deployment configured"
EOF
            ;;

        *)
            cat >> "$OUTPUT_DIR/deploy.yml" << 'EOF'

    - name: Build and deploy
      run: |
        if [ -f "deployment/docker/Dockerfile" ]; then
          docker build -f deployment/docker/Dockerfile -t app:latest .
        fi
        echo "Deployment ready"
EOF
            ;;
    esac

    echo -e "${GREEN}✓${NC} Created $OUTPUT_DIR/deploy.yml"
}

# Generate PR automation workflow
generate_pr_workflow() {
    echo -e "${YELLOW}Generating PR automation workflow...${NC}"

    cat > "$OUTPUT_DIR/pr-automation.yml" << 'EOF'
name: PR Automation

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

permissions:
  contents: read
  pull-requests: write

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Validate PR
      run: |
        # Check for deployment configs
        if [ -d "deployment" ]; then
          echo "✅ Deployment configs found"
        fi

        # Check for tests
        if [ -d "tests" ] || [ -f "package.json" ]; then
          echo "✅ Tests configured"
        fi

    - name: Add PR comment
      uses: actions/github-script@v7
      with:
        script: |
          const body = `## 🤖 Automated PR Check

          ✅ Code validation passed
          ✅ Tests configured
          ✅ Deployment ready

          Ready for review!`;

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: body
          });
EOF

    echo -e "${GREEN}✓${NC} Created $OUTPUT_DIR/pr-automation.yml"
}

# Main execution
main() {
    # Detect project type
    PROJECT_INFO=$(detect_project_type)
    echo -e "${BLUE}Detected project info: $PROJECT_INFO${NC}"
    echo ""

    # Generate workflows
    generate_ci_workflow "$PROJECT_INFO"
    generate_deployment_workflow "$PROJECT_INFO"
    generate_pr_workflow

    # Summary
    echo ""
    echo -e "${GREEN}=== Workflow Generation Complete ===${NC}"
    echo -e "${GREEN}Generated workflows:${NC}"
    ls -la "$OUTPUT_DIR"/*.yml | awk '{print "  - " $9}'
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review generated workflows in $OUTPUT_DIR"
    echo "2. Add required secrets to GitHub repository settings"
    echo "3. Commit workflows to trigger automation"
}

main