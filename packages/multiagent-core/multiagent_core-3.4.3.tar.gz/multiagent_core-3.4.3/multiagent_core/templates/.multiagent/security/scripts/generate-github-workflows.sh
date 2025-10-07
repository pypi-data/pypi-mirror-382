#!/usr/bin/env bash
# Security Tool: GitHub Workflow Generator
# Called by: security-auth-compliance agent during setup
# Purpose: Copy and customize workflow templates for project

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SECURITY_DIR="$PROJECT_ROOT/.multiagent/security"
WORKFLOWS_DIR="$PROJECT_ROOT/.github/workflows"

# Detect project name
PROJECT_NAME=$(basename "$PROJECT_ROOT")

# Detect tech stack
TECH_STACK="unknown"
if [[ -f "$PROJECT_ROOT/package.json" ]]; then
    TECH_STACK="node"
elif [[ -f "$PROJECT_ROOT/requirements.txt" ]] || [[ -f "$PROJECT_ROOT/setup.py" ]]; then
    TECH_STACK="python"
elif [[ -f "$PROJECT_ROOT/go.mod" ]]; then
    TECH_STACK="go"
fi

echo "[GENERATE] Creating GitHub security workflows for: $PROJECT_NAME ($TECH_STACK)"
echo ""

# Ensure workflows directory exists
mkdir -p "$WORKFLOWS_DIR"

# Copy and customize security-scan.yml
if [[ -f "$SECURITY_DIR/templates/github-workflows/security-scan.yml.template" ]]; then
    echo "[COPY] security-scan.yml.template → .github/workflows/security-scan.yml"

    sed -e "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" \
        -e "s/{{TECH_STACK}}/$TECH_STACK/g" \
        "$SECURITY_DIR/templates/github-workflows/security-scan.yml.template" \
        > "$WORKFLOWS_DIR/security-scan.yml"

    echo "✅ Created security-scan.yml"
else
    echo "❌ Template not found: security-scan.yml.template"
    exit 1
fi
echo ""

# Copy and customize security-scanning.yml
if [[ -f "$SECURITY_DIR/templates/github-workflows/security-scanning.yml.template" ]]; then
    echo "[COPY] security-scanning.yml.template → .github/workflows/security-scanning.yml"

    sed -e "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" \
        -e "s/{{TECH_STACK}}/$TECH_STACK/g" \
        "$SECURITY_DIR/templates/github-workflows/security-scanning.yml.template" \
        > "$WORKFLOWS_DIR/security-scanning.yml"

    echo "✅ Created security-scanning.yml"
else
    echo "❌ Template not found: security-scanning.yml.template"
    exit 1
fi
echo ""

echo "[SUCCESS] GitHub security workflows generated successfully!"
echo ""
echo "Next steps:"
echo "  1. Review workflows in .github/workflows/"
echo "  2. Commit workflows to git"
echo "  3. Push to GitHub to activate security scanning"