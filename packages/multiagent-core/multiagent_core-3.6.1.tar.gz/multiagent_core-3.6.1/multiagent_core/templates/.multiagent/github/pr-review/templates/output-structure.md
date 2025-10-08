# Feedback System Output Structure

## Output Location Pattern

Simple consolidated approach - everything goes into one feedback tasks file:

```
specs/
├── feedback-tasks.md          # All feedback tasks from all PRs
└── .feedback/
    └── sessions/
        ├── pr-123-codex/
        │   ├── session.json
        │   ├── analysis.json
        │   ├── judgment.json
        │   └── artifacts/
        └── pr-456-qwen/
            ├── session.json
            ├── analysis.json  
            ├── judgment.json
            └── artifacts/
```

## Consolidated Tasks Approach

- **Main Output**: `specs/feedback-tasks.md` - Single file with all feedback tasks
- **Session Data**: Hidden in `specs/.feedback/sessions/` for reference but not cluttering main specs
- **Task Format**: Each PR's feedback gets appended to the main tasks file with clear sections

## File Contents

### feedback-analysis.md
Main human-readable analysis using judge-output-review.md template with:
- Executive summary
- Detailed feedback breakdown
- Priority action items
- Quality assessment

### tasks.md
Generated actionable tasks in SpecKit format:
- Task numbering (T001, T002, etc.)
- Agent assignments (@claude, @codex, etc.)
- Priority grouping (Critical, Important, Enhancement)
- Clear acceptance criteria

### judgment-review.md
Judge's decision document with:
- Recommendation (approve/revise/rework)
- Significance scoring
- Risk assessment
- Approval requirements

### implementation-plan.md
Execution roadmap with:
- Phase breakdown
- Dependencies
- Resource requirements
- Timeline estimates

### artifacts/
Raw data directory containing all JSON files and original GitHub data for traceability and debugging.

## Integration with SpecKit

The feedback system output follows SpecKit conventions:

1. **Consistent Structure**: Same directory patterns as `specs/001-build-a-complete/`
2. **Task Format**: Uses same T001-style numbering as SpecKit tasks.md
3. **Agent Assignment**: Uses @agent notation for task routing
4. **Documentation Standards**: Follows same markdown formatting patterns

## Usage in Scripts

Scripts should create output in this structure:

```bash
# Setup creates the directory
FEEDBACK_DIR="specs/feedback-${PR_NUMBER}-${DETECTED_AGENT}"
mkdir -p "$FEEDBACK_DIR/artifacts"

# Each script contributes to the structure
# setup-pr-session.sh → artifacts/*.json
# parse-review.sh → analysis.json, feedback-analysis.md  
# judge-feedback.sh → judgment.json, judgment-review.md
# generate-tasks.sh → tasks.json, tasks.md, implementation-plan.md
```

This creates a complete, organized output that integrates seamlessly with the existing SpecKit workflow and provides both human-readable documents and machine-readable data for automation.