#!/bin/bash
# Documentation System Initialization Hook
# Called during multiagent init to set up documentation management

set -e

echo "📚 Initializing Documentation Management System..."

# Check if we're in a project with .multiagent directory
if [ ! -d ".multiagent" ]; then
    echo "Error: .multiagent directory not found. Run this from project root."
    exit 1
fi

# Copy documentation system to project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create documentation structure
if [ -f "$SCRIPT_DIR/scripts/create-structure.sh" ]; then
    echo "Creating documentation structure..."
    bash "$SCRIPT_DIR/scripts/create-structure.sh"
fi

echo "✅ Documentation management system initialized!"
echo ""
echo "Available documentation commands:"
echo "  /docs init     - Initialize and fill documentation"
echo "  /docs update   - Update docs based on code changes"
echo "  /docs validate - Check documentation consistency"