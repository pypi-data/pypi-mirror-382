#!/bin/bash

# Project Initialization Script
# Purpose: Initialize project structure after spec creation
# Invoked at: /project-setup Step 2
# Usage: ./project-init.sh <spec-dir>

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

echo -e "${BLUE}=== Initializing Project Structure ===${NC}"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}"
echo ""

# Detect project type from spec
detect_project_type() {
    local project_type="unknown"

    if [ -f "$SPEC_DIR/spec.md" ]; then
        if grep -qi "next\|react" "$SPEC_DIR/spec.md"; then
            project_type="node-frontend"
        elif grep -qi "fastapi\|flask\|django" "$SPEC_DIR/spec.md"; then
            project_type="python-backend"
        elif grep -qi "express\|node" "$SPEC_DIR/spec.md"; then
            project_type="node-backend"
        elif grep -qi "full.stack" "$SPEC_DIR/spec.md"; then
            project_type="fullstack"
        fi
    fi

    echo "$project_type"
}

# Initialize Node.js project
init_node_project() {
    echo -e "${YELLOW}Initializing Node.js project structure...${NC}"

    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        cat > package.json << 'EOF'
{
  "name": "multiagent-project",
  "version": "1.0.0",
  "description": "Project generated from multiagent spec",
  "main": "index.js",
  "scripts": {
    "dev": "node src/index.js",
    "test": "jest",
    "lint": "eslint .",
    "build": "echo 'Build script needed'"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
EOF
        echo -e "${GREEN}✓${NC} Created package.json"
    fi

    # Create source structure
    mkdir -p src
    mkdir -p src/utils
    mkdir -p src/services
    mkdir -p src/api

    # Create basic test structure
    mkdir -p tests/unit
    mkdir -p tests/integration

    echo -e "${GREEN}✓${NC} Node.js structure initialized"
}

# Initialize Python project
init_python_project() {
    echo -e "${YELLOW}Initializing Python project structure...${NC}"

    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << 'EOF'
# Core dependencies
python-dotenv==1.0.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1

# Linting
flake8==6.0.0
black==23.3.0
mypy==1.4.1
EOF
        echo -e "${GREEN}✓${NC} Created requirements.txt"
    fi

    # Create source structure
    mkdir -p src
    mkdir -p src/utils
    mkdir -p src/services
    mkdir -p src/api

    # Create __init__.py files
    touch src/__init__.py
    touch src/utils/__init__.py
    touch src/services/__init__.py
    touch src/api/__init__.py

    # Create basic test structure
    mkdir -p tests/unit
    mkdir -p tests/integration
    touch tests/__init__.py

    echo -e "${GREEN}✓${NC} Python structure initialized"
}

# Create environment template
create_env_template() {
    echo -e "${YELLOW}Creating environment template...${NC}"

    # Read spec to determine required env vars
    local env_vars=""

    if [ -f "$SPEC_DIR/spec.md" ]; then
        # Check for common services
        if grep -qi "github" "$SPEC_DIR/spec.md"; then
            env_vars="${env_vars}# GitHub Integration\n"
            env_vars="${env_vars}GITHUB_TOKEN=your_github_token_here\n"
            env_vars="${env_vars}GITHUB_WEBHOOK_SECRET=your_webhook_secret_here\n\n"
        fi

        if grep -qi "database\|postgres\|mysql" "$SPEC_DIR/spec.md"; then
            env_vars="${env_vars}# Database Configuration\n"
            env_vars="${env_vars}DATABASE_URL=postgresql://user:password@localhost:5432/dbname\n\n"
        fi

        if grep -qi "redis" "$SPEC_DIR/spec.md"; then
            env_vars="${env_vars}# Redis Configuration\n"
            env_vars="${env_vars}REDIS_URL=redis://localhost:6379\n\n"
        fi

        if grep -qi "api.key\|secret" "$SPEC_DIR/spec.md"; then
            env_vars="${env_vars}# API Configuration\n"
            env_vars="${env_vars}API_KEY=your_api_key_here\n"
            env_vars="${env_vars}API_SECRET=your_api_secret_here\n\n"
        fi
    fi

    # Create .env.example
    cat > .env.example << EOF
# Environment Configuration
NODE_ENV=development
PORT=3000

${env_vars}
# Logging
LOG_LEVEL=debug

# Feature Flags
ENABLE_DEBUG=true
EOF

    echo -e "${GREEN}✓${NC} Created .env.example"

    # Update .gitignore
    if ! grep -q "^.env$" .gitignore 2>/dev/null; then
        echo ".env" >> .gitignore
        echo -e "${GREEN}✓${NC} Added .env to .gitignore"
    fi
}

# Main execution
main() {
    local project_type=$(detect_project_type)

    echo -e "${BLUE}Detected project type: $project_type${NC}"
    echo ""

    # Initialize based on project type
    case "$project_type" in
        node-frontend|node-backend)
            init_node_project
            ;;
        python-backend)
            init_python_project
            ;;
        fullstack)
            init_node_project
            init_python_project
            ;;
        *)
            echo -e "${YELLOW}Unknown project type, creating basic structure${NC}"
            mkdir -p src tests
            ;;
    esac

    # Create environment template
    create_env_template

    echo ""
    echo -e "${GREEN}=== Project Initialization Complete ===${NC}"
    echo -e "${GREEN}Structure created based on $SPEC_DIR${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review generated structure"
    echo "2. Configure environment variables in .env"
    echo "3. Install dependencies"
}

main