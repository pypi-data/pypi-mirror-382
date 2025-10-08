#!/bin/bash
# Update templates in a deployed project from installed multiagent-core package
#
# Usage:
#   ./scripts/update-project-templates.sh /path/to/project
#   ./scripts/update-project-templates.sh  # Updates current directory

set -e

PROJECT_DIR="${1:-.}"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"

echo "🔄 Updating project templates from multiagent-core package..."
echo ""

# Find package location
PACKAGE_DIR=$(python -c "import multiagent_core; import os; print(os.path.dirname(multiagent_core.__file__))" 2>/dev/null)

if [ -z "$PACKAGE_DIR" ]; then
    echo "❌ multiagent-core not found. Install it with:"
    echo "   pip install multiagent-core"
    exit 1
fi

echo "📦 Package location: $PACKAGE_DIR"
echo "📁 Project location: $(cd "$PROJECT_DIR" && pwd)"
echo ""

# Check if project has .multiagent directory
if [ ! -d "$PROJECT_DIR/.multiagent" ]; then
    echo "❌ Not a multiagent project (no .multiagent directory found)"
    echo "   Run 'multiagent init' first to initialize the project"
    exit 1
fi

# Get package version
PACKAGE_VERSION=$(python -c "import multiagent_core; print(multiagent_core.__version__)" 2>/dev/null || echo "unknown")
echo "📌 Installed multiagent-core version: $PACKAGE_VERSION"
echo ""

# Confirm before proceeding
read -p "Continue with template update? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔧 Updating templates..."
echo ""

# Backup and update .multiagent
if [ -d "$PROJECT_DIR/.multiagent" ]; then
    echo "  📋 Backing up .multiagent/ → .multiagent${BACKUP_SUFFIX}/"
    cp -r "$PROJECT_DIR/.multiagent" "$PROJECT_DIR/.multiagent${BACKUP_SUFFIX}"

    echo "  🔄 Syncing .multiagent/ templates"
    rsync -av --delete \
        "$PACKAGE_DIR/templates/.multiagent/" \
        "$PROJECT_DIR/.multiagent/"
    echo "     ✓ Updated .multiagent/"
fi

# Update .claude if it exists
if [ -d "$PROJECT_DIR/.claude" ] && [ -d "$PACKAGE_DIR/templates/.claude" ]; then
    echo "  📋 Backing up .claude/ → .claude${BACKUP_SUFFIX}/"
    cp -r "$PROJECT_DIR/.claude" "$PROJECT_DIR/.claude${BACKUP_SUFFIX}"

    echo "  🔄 Syncing .claude/ templates (preserving local settings)"
    rsync -av --exclude="settings.json" --exclude="settings.local.json" \
        "$PACKAGE_DIR/templates/.claude/" \
        "$PROJECT_DIR/.claude/"
    echo "     ✓ Updated .claude/ (kept local settings)"
fi

# Update docs if it exists
if [ -d "$PROJECT_DIR/docs" ] && [ -d "$PACKAGE_DIR/templates/docs" ]; then
    echo "  🔄 Syncing docs/ templates (preserving project-specific docs)"
    # Only update framework docs, not project-specific ones
    if [ -d "$PACKAGE_DIR/templates/docs/framework-analysis" ]; then
        rsync -av \
            "$PACKAGE_DIR/templates/docs/framework-analysis/" \
            "$PROJECT_DIR/docs/framework-analysis/" 2>/dev/null || true
    fi
    if [ -d "$PACKAGE_DIR/templates/docs/architecture" ]; then
        rsync -av \
            "$PACKAGE_DIR/templates/docs/architecture/" \
            "$PROJECT_DIR/docs/architecture/" 2>/dev/null || true
    fi
    echo "     ✓ Updated docs/ (framework templates only)"
fi

# Update .vscode if it exists
if [ -d "$PROJECT_DIR/.vscode" ] && [ -d "$PACKAGE_DIR/templates/.vscode" ]; then
    echo "  🔄 Syncing .vscode/ settings (preserving user preferences)"
    rsync -av --ignore-existing \
        "$PACKAGE_DIR/templates/.vscode/" \
        "$PROJECT_DIR/.vscode/"
    echo "     ✓ Updated .vscode/ (kept existing files)"
fi

# Update scripts if they exist
if [ -d "$PROJECT_DIR/scripts" ] && [ -d "$PACKAGE_DIR/templates/scripts" ]; then
    echo "  🔄 Syncing scripts/"
    rsync -av \
        "$PACKAGE_DIR/templates/scripts/" \
        "$PROJECT_DIR/scripts/"
    chmod +x "$PROJECT_DIR/scripts"/**/*.sh 2>/dev/null || true
    echo "     ✓ Updated scripts/"
fi

echo ""
echo "✅ Template update complete!"
echo ""
echo "📌 Backups created with suffix: ${BACKUP_SUFFIX}"
echo "📝 Review changes with: git diff"
echo "🗑️  Remove backups with: rm -rf ./*${BACKUP_SUFFIX}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test your project"
echo "  3. Commit changes: git commit -am 'chore: Update templates from multiagent-core $PACKAGE_VERSION'"
echo ""
