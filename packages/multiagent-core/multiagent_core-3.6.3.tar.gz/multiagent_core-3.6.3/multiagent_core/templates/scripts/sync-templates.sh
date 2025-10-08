#!/bin/bash
# Sync source directories to multiagent_core/templates/ for packaging
# This ensures the package always contains current templates

set -e

echo "[TEMPLATE-SYNC] Syncing templates to multiagent_core/templates/..."

# Sync directory structures
rsync -av --delete .multiagent/ multiagent_core/templates/.multiagent/
echo "  ✓ Synced .multiagent/"

rsync -av --delete .claude/ multiagent_core/templates/.claude/
echo "  ✓ Synced .claude/"

rsync -av --delete --exclude='workflows/claude.yml' --exclude='workflows/claude-code-review.yml' --exclude='workflows/claude-review-automation.yml' .github/ multiagent_core/templates/.github/
echo "  ✓ Synced .github/ (excluding Claude-specific workflows)"

rsync -av --delete .vscode/ multiagent_core/templates/.vscode/
echo "  ✓ Synced .vscode/"

# Sync .gitignore
cp .gitignore multiagent_core/templates/.gitignore
echo "  ✓ Synced .gitignore"

# Sync scripts/ directory (contains git hooks)
if [ -d "scripts" ]; then
    if [ ! -d "multiagent_core/templates/scripts" ]; then
        mkdir -p multiagent_core/templates/scripts
    fi
    rsync -av --delete scripts/ multiagent_core/templates/scripts/
    echo "  ✓ Synced scripts/"
else
    echo "  ⚠ scripts/ not found in source, skipping"
fi

# Create docs/ template if it doesn't exist
if [ ! -d "multiagent_core/templates/docs" ]; then
    mkdir -p multiagent_core/templates/docs
fi

# Sync docs/ if it exists
if [ -d "docs" ]; then
    rsync -av --delete docs/ multiagent_core/templates/docs/
    echo "  ✓ Synced docs/"
else
    echo "  ⚠ docs/ not found in source, skipping"
fi

echo "[TEMPLATE-SYNC] ✅ All templates synced successfully"
