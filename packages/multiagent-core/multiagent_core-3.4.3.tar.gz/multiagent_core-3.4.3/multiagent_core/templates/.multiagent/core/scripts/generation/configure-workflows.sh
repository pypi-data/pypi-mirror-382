#!/bin/bash

# Configure GitHub Workflows from templates based on project spec
# Usage: ./configure-workflows.sh <spec-dir>

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SPEC_DIR="${1:-specs/001-*}"
TEMPLATE_DIR=".multiagent/core/templates/github-workflows"
OUTPUT_DIR=".github/workflows"

# Find spec directory
if [[ "$SPEC_DIR" == *"*"* ]]; then
    SPEC_DIR=$(find . -type d -path "./specs/001-*" | head -1)
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

echo -e "${BLUE}=== Configuring GitHub Workflows ===${NC}"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Detect project configuration from spec
detect_project_config() {
    local config_file="/tmp/workflow-config.env"

    # Set defaults
    echo "NODE_VERSION=20" > "$config_file"
    echo "PYTHON_VERSION=3.11" >> "$config_file"
    echo "PROJECT_NAME=$(basename $(pwd))" >> "$config_file"
    echo "ENVIRONMENT=production" >> "$config_file"

    # Detect from spec
    if [ -f "$SPEC_DIR/spec.md" ]; then
        # Node.js detection
        if grep -qi "next\|react\|node\|npm" "$SPEC_DIR/spec.md"; then
            echo "PROJECT_TYPE=node" >> "$config_file"
            echo "LINT_COMMAND=npm run lint" >> "$config_file"
            echo "TEST_COMMAND=npm test" >> "$config_file"
            echo "BUILD_COMMAND=npm run build" >> "$config_file"
            echo "HAS_BUILD=true" >> "$config_file"
            echo "IF_NODE=true" >> "$config_file"
        fi

        # Python detection
        if grep -qi "python\|fastapi\|flask\|django" "$SPEC_DIR/spec.md"; then
            echo "PROJECT_TYPE=python" >> "$config_file"
            echo "LINT_COMMAND=flake8 ." >> "$config_file"
            echo "TEST_COMMAND=pytest" >> "$config_file"
            echo "BUILD_COMMAND=python -m build" >> "$config_file"
            echo "HAS_BUILD=false" >> "$config_file"
            echo "IF_PYTHON=true" >> "$config_file"
        fi

        # Deployment detection
        if grep -qi "vercel" "$SPEC_DIR/spec.md"; then
            echo "DEPLOYMENT_TARGET=vercel" >> "$config_file"
            echo "IF_VERCEL=true" >> "$config_file"
        elif grep -qi "aws\|lambda" "$SPEC_DIR/spec.md"; then
            echo "DEPLOYMENT_TARGET=aws" >> "$config_file"
            echo "IF_AWS=true" >> "$config_file"
            echo "AWS_REGION=us-east-1" >> "$config_file"
        else
            echo "DEPLOYMENT_TARGET=docker" >> "$config_file"
            echo "IF_DOCKER=true" >> "$config_file"
        fi
    fi

    source "$config_file"
}

# Process template file
process_template() {
    local template="$1"
    local output="$2"

    echo -e "${YELLOW}Processing: $(basename $template)${NC}"

    # Read the template
    local content=$(cat "$template")

    # Replace variables {{VAR|default}}
    content=$(echo "$content" | sed -E 's/\{\{([A-Z_]+)\|([^}]*)\}\}/\{\{\1:-\2\}\}/g')

    # Process conditionals {{#IF_VAR}}...{{/IF_VAR}}
    while [[ "$content" =~ \{\{#IF_([A-Z_]+)\}\}([^{]*)\{\{/IF_[A-Z_]+\}\} ]]; do
        local var="${BASH_REMATCH[1]}"
        local block="${BASH_REMATCH[2]}"
        local full_match="${BASH_REMATCH[0]}"

        # Check if variable is set
        if [ -n "${!var}" ]; then
            # Keep the block content
            content="${content//$full_match/$block}"
        else
            # Remove the block
            content="${content//$full_match/}"
        fi
    done

    # Expand remaining variables
    while [[ "$content" =~ \{\{([A-Z_]+)(:-([^}]*))?\}\} ]]; do
        local var="${BASH_REMATCH[1]}"
        local default="${BASH_REMATCH[3]}"
        local full_match="${BASH_REMATCH[0]}"
        local value="${!var:-$default}"

        content="${content//$full_match/$value}"
    done

    # Write output
    echo "$content" > "$output"
    echo -e "${GREEN}✓${NC} Created: $output"
}

# Main execution
main() {
    # Detect project configuration
    detect_project_config

    # Load configuration
    source /tmp/workflow-config.env

    echo -e "${BLUE}Detected configuration:${NC}"
    echo "  Project Type: ${PROJECT_TYPE:-unknown}"
    echo "  Deployment: ${DEPLOYMENT_TARGET:-none}"
    echo ""

    # Process templates
    for template in "$TEMPLATE_DIR"/*.yml.template; do
        if [ -f "$template" ]; then
            output_name=$(basename "$template" .template)
            process_template "$template" "$OUTPUT_DIR/$output_name"
        fi
    done

    # Copy existing specialized workflows that don't need templating
    echo ""
    echo -e "${BLUE}Preserving specialized workflows:${NC}"

    # These workflows are project-specific and don't need templating
    local specialized_workflows=(
        "claude-code-review.yml"
        "claude-feedback-router.yml"
        "pr-feedback-automation.yml"
    )

    for workflow in "${specialized_workflows[@]}"; do
        if [ -f ".github/workflows/$workflow" ]; then
            echo -e "${GREEN}✓${NC} Keeping: $workflow"
        fi
    done

    echo ""
    echo -e "${GREEN}=== Workflow Configuration Complete ===${NC}"
    echo -e "${GREEN}Configured workflows in $OUTPUT_DIR${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review generated workflows"
    echo "2. Add required secrets to GitHub repository"
    echo "3. Commit workflows to trigger CI/CD"
}

main