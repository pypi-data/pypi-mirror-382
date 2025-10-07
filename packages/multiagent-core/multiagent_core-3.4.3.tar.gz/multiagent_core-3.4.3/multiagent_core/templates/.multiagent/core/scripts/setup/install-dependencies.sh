#!/bin/bash

# Install Dependencies Script
# Purpose: Install project dependencies based on detected framework
# Invoked at: /project-setup Step 9
# Usage: ./install-dependencies.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Installing Project Dependencies ===${NC}"
echo ""

# Detect and install Node.js dependencies
install_node_deps() {
    if [ -f "package.json" ]; then
        echo -e "${YELLOW}Installing Node.js dependencies...${NC}"

        # Check if npm is available
        if command -v npm &> /dev/null; then
            # Install production dependencies
            npm install

            # Install common dev dependencies
            npm install --save-dev \
                eslint \
                jest \
                @types/node \
                prettier \
                husky \
                lint-staged || true

            echo -e "${GREEN}✓${NC} Node.js dependencies installed"
            echo -e "${GREEN}✓${NC} Created node_modules/"
            echo -e "${GREEN}✓${NC} Created package-lock.json"
        else
            echo -e "${RED}✗${NC} npm not found. Please install Node.js"
            return 1
        fi
    fi
}

# Detect and install Python dependencies
install_python_deps() {
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"

        # Check if pip is available
        if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
            PIP_CMD=$(command -v pip3 || command -v pip)

            # Create virtual environment if it doesn't exist
            if [ ! -d "venv" ]; then
                echo -e "${YELLOW}Creating Python virtual environment...${NC}"
                python3 -m venv venv
                echo -e "${GREEN}✓${NC} Created venv/"
            fi

            # Activate virtual environment and install
            source venv/bin/activate 2>/dev/null || . venv/bin/activate

            # Upgrade pip
            $PIP_CMD install --upgrade pip

            # Install dependencies
            $PIP_CMD install -r requirements.txt

            # Install common dev dependencies
            $PIP_CMD install \
                pytest \
                pytest-cov \
                black \
                flake8 \
                mypy \
                pre-commit || true

            echo -e "${GREEN}✓${NC} Python dependencies installed"

            deactivate 2>/dev/null || true
        else
            echo -e "${RED}✗${NC} pip not found. Please install Python 3"
            return 1
        fi
    fi
}

# Install Docker dependencies if needed
check_docker_deps() {
    if [ -f "docker-compose.yml" ] || [ -f "deployment/docker/docker-compose.yml" ]; then
        echo -e "${YELLOW}Checking Docker setup...${NC}"

        if command -v docker &> /dev/null; then
            echo -e "${GREEN}✓${NC} Docker is installed"

            if command -v docker-compose &> /dev/null; then
                echo -e "${GREEN}✓${NC} Docker Compose is installed"
            else
                echo -e "${YELLOW}!${NC} Docker Compose not found (optional)"
            fi
        else
            echo -e "${YELLOW}!${NC} Docker not installed (optional for local development)"
        fi
    fi
}

# Install project-specific tools
install_project_tools() {
    echo -e "${YELLOW}Checking for project-specific tools...${NC}"

    # Check for GitHub CLI
    if grep -r "gh pr\|gh issue" .claude/commands/ 2>/dev/null; then
        if command -v gh &> /dev/null; then
            echo -e "${GREEN}✓${NC} GitHub CLI installed"
        else
            echo -e "${YELLOW}!${NC} GitHub CLI not found (recommended: gh auth login)"
        fi
    fi

    # Check for AWS CLI
    if grep -qi "aws\|lambda" specs/*/spec.md 2>/dev/null; then
        if command -v aws &> /dev/null; then
            echo -e "${GREEN}✓${NC} AWS CLI installed"
        else
            echo -e "${YELLOW}!${NC} AWS CLI not found (needed for AWS deployments)"
        fi
    fi

    # Check for Vercel CLI
    if grep -qi "vercel" specs/*/spec.md 2>/dev/null; then
        if command -v vercel &> /dev/null; then
            echo -e "${GREEN}✓${NC} Vercel CLI installed"
        else
            echo -e "${YELLOW}!${NC} Vercel CLI not found (install with: npm i -g vercel)"
        fi
    fi
}

# Main execution
main() {
    local has_node=false
    local has_python=false

    # Check what needs to be installed
    [ -f "package.json" ] && has_node=true
    [ -f "requirements.txt" ] && has_python=true

    if [ "$has_node" = false ] && [ "$has_python" = false ]; then
        echo -e "${YELLOW}No package files found (package.json or requirements.txt)${NC}"
        echo "Skipping dependency installation"
        return 0
    fi

    # Install dependencies
    if [ "$has_node" = true ]; then
        install_node_deps || echo -e "${YELLOW}Node.js installation incomplete${NC}"
    fi

    if [ "$has_python" = true ]; then
        install_python_deps || echo -e "${YELLOW}Python installation incomplete${NC}"
    fi

    # Check additional tools
    check_docker_deps
    install_project_tools

    echo ""
    echo -e "${GREEN}=== Dependency Installation Complete ===${NC}"

    # Show summary
    echo -e "${BLUE}Installed:${NC}"
    [ "$has_node" = true ] && [ -d "node_modules" ] && echo "  ✓ Node.js packages in node_modules/"
    [ "$has_python" = true ] && [ -d "venv" ] && echo "  ✓ Python packages in venv/"

    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Configure environment variables in .env"
    echo "2. Run tests to verify installation"
    [ "$has_python" = true ] && echo "3. Activate Python venv: source venv/bin/activate"
}

main