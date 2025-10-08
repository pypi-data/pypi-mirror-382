# Auto-Update Status and Troubleshooting

## Current Status: ⚠️ Auto-Updates Not Implemented

### What Was Discovered

The auto-update feature for deployed projects **was never fully implemented**. Here's what we found:

1. **Missing Module**: `webhook_notifier.py` was archived but `sync_project.py` still tried to import it
2. **Silent Failure**: During `multiagent init`, the registration function would fail silently
3. **No Registry**: Because registration failed, no `deployed-projects-registry.json` file was ever created
4. **No Updates**: Without a registry, the auto-update workflow had no projects to update

### Why Orbit Has Old README

When you installed `multiagent-core` from PyPI and ran `multiagent init` in the Orbit project:

- Templates were copied from the package (one-time copy during init)
- Auto-update registration silently failed
- When newer versions of `multiagent-core` were released, Orbit didn't get updated
- The package templates HAVE the new content, but Orbit still has old content from its initial setup

## How to Update Orbit Project Now

### Option 1: Manual Template Update (Quick)

```bash
cd /home/vanman2025/Projects/Orbit

# Backup current README
cp .multiagent/README.md .multiagent/README.md.backup

# Install latest multiagent-core
pip install -U multiagent-core

# Re-run init (will update templates)
multiagent init --update
```

**Note**: The `--update` flag doesn't exist yet, so you may need to manually copy files.

### Option 2: Manual File Copy (Safest)

```bash
# Find where multiagent-core is installed
PACKAGE_DIR=$(python -c "import multiagent_core; import os; print(os.path.dirname(multiagent_core.__file__))")

# Copy the new README
cp "$PACKAGE_DIR/templates/.multiagent/README.md" /home/vanman2025/Projects/Orbit/.multiagent/README.md

# Or copy entire .multiagent structure
rsync -av "$PACKAGE_DIR/templates/.multiagent/" /home/vanman2025/Projects/Orbit/.multiagent/
```

### Option 3: Wait for Full Implementation

We can implement proper auto-updates in a future release. This would require:

1. Creating a proper project registry system
2. Implementing GitHub Actions workflow to sync templates
3. Adding version checking and selective updates

## What Was Fixed in This Release

**Version 3.6.4** (upcoming release) includes:

✅ **Removed broken auto-update registration**
- Commented out missing `WebhookUpdateNotifier` import
- Replaced `registerForTemplateUpdates()` with informative message
- No more silent failures during `multiagent init`

✅ **Updated package templates**
- Latest README with 3-layer architecture
- New VERSION_MANAGEMENT.md documentation
- All recent improvements synced

## How Updates Work Now

**Current Workflow** (Manual):

1. New version of `multiagent-core` is released on PyPI
2. Package includes latest templates in `multiagent_core/templates/`
3. Users upgrade: `pip install -U multiagent-core`
4. Users manually copy updated templates to their projects

**Future Workflow** (When Implemented):

1. New version released on PyPI
2. GitHub Actions workflow triggers
3. Registered projects get automatic PR with template updates
4. User reviews and merges PR

## Checking Package Version and Templates

```bash
# Check installed version
pip show multiagent-core

# Find package location
python -c "import multiagent_core; import os; print(os.path.dirname(multiagent_core.__file__))"

# Check what templates are in the package
ls -la $(python -c "import multiagent_core; import os; print(os.path.dirname(multiagent_core.__file__))")/templates/
```

## Why This Wasn't Noticed Earlier

1. **Silent Failures**: The import error didn't crash `multiagent init`, it just skipped registration
2. **One-Time Copy**: Templates were copied during initial setup, so the project worked fine
3. **Package Updates Work**: New installs got new templates, just not existing projects

## Next Steps

If you want to update Orbit project:
1. Use Option 2 (Manual File Copy) - safest and most reliable
2. Review the changes before committing
3. Commit with: `git commit -m "chore: Update .multiagent templates from multiagent-core 3.6.4"`

If you want auto-updates implemented:
- We can create a proper implementation in a future sprint
- Would involve webhook system, registry, and GitHub Actions coordination

---

**Last Updated**: 2025-10-07
**Issue**: Orbit project has old README despite package having new content
**Status**: Explained and documented - manual update available
**Fix Released**: Version 3.6.4 removes broken auto-update code
