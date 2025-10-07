# Known Issues - Deployment System

## Critical Bug: Incomplete Spec Reading

### Issue Description
The deployment generation system only reads `spec.md` instead of analyzing the ENTIRE spec folder, missing critical information.

### Files Being Ignored
- `agent-tasks/layered-tasks.md` - The actual project structure and components
- `plan.md` - Technical implementation details
- `data-model.md` - Database schemas
- `contracts/` - API endpoint definitions
- `feedback/` - Any adjustments from PR reviews

### Impact
Generated deployment configurations are incomplete because they don't include:
- Services mentioned in layered-tasks.md
- Database tables from data-model.md
- API endpoints from contracts/
- Architecture decisions from plan.md

### Current Behavior
```bash
# Script only does this:
grep -i "service\|api\|database" "$SPEC_DIR/spec.md"
```

### Required Fix
Update `.multiagent/deployment/scripts/generate-deployment.sh` to:

```bash
# Should analyze entire spec directory:
find "$SPEC_DIR" -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" \) | while read file; do
    echo "Analyzing: $file" >> "$LOG_FILE"
    # Extract services, APIs, databases, etc. from each file
done
```

### Workaround
Until fixed, manually review generated deployment configs and add missing services based on:
1. Components listed in `layered-tasks.md`
2. APIs defined in `contracts/`
3. Database schema in `data-model.md`

### Test Case
```bash
# Clean test to verify the issue
rm -rf deployment/
/deploy-prepare specs/002-system-context-we
cat /tmp/deployment-context.txt  # Should show ALL spec files analyzed

# Expected: References to content from all spec files
# Actual: Only references content from spec.md
```

### Related Files
- `.multiagent/deployment/scripts/generate-deployment.sh` - Needs update
- `.multiagent/deployment/README.md` - Document the fix when complete

## Other Known Issues

### Template Selection
- May default to generic templates when spec analysis is incomplete
- Fix depends on resolving the spec reading bug above

### Context Generation
- `/tmp/deployment-context.txt` only contains partial project information
- Should include comprehensive analysis from all spec files

## Resolution Status
- **Identified**: Yes
- **Root Cause Known**: Yes
- **Fix Planned**: Update script to read entire spec directory
- **Priority**: HIGH - Affects all deployment generation