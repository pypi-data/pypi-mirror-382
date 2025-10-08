# {FEATURE_NAME}

**Status**: Draft (from issue #{ISSUE_NUMBER})
**Priority**: {CRITICAL|HIGH|MEDIUM|LOW}
**Complexity**: {LOW|MEDIUM|HIGH}
**Size**: {XS|S|M|L|XL} ({ESTIMATE})
**Related Issues**: #{ISSUE_NUMBER}, {#OTHER_ISSUES}

---

## Overview

{1-2 paragraph overview of feature/fix from issue}

---

## User Story

**From issue #{ISSUE_NUMBER} by @{AUTHOR}:**

> {Quote relevant parts of the issue that describe the user need}

**User Need**:
{What problem does this solve for users?}

**User Benefit**:
{What value does this provide?}

---

## Requirements

### Functional Requirements

{Extract requirements from issue:}

1. **{Requirement 1}**
   - {Detail}
   - {Detail}

2. **{Requirement 2}**
   - {Detail}
   - {Detail}

3. **{Requirement 3}**
   - {Detail}
   - {Detail}

### Non-Functional Requirements

- **Performance**: {Any performance requirements}
- **Security**: {Any security considerations}
- **Compatibility**: {Platform/version requirements}
- **Usability**: {UX requirements}

### Out of Scope

{What this spec does NOT include - important for boundary setting}

- {Item not included}
- {Future enhancement}

---

## Technical Approach

**NOTE**: To be filled using `/planning:plan` command.

### Architecture

{High-level architecture}

### Components Affected

- {Component 1}
- {Component 2}
- {Component 3}

### Integration Points

{What systems/services does this integrate with?}

### Data Model Changes

{Any database schema changes needed?}

---

## Implementation Plan

**NOTE**: To be generated using `/planning:tasks` command.

### Task Breakdown

{Will be auto-generated into tasks.md}

### Dependencies

- [ ] {Dependency 1}
- [ ] {Dependency 2}

### Risks

1. **{Risk 1}**
   - **Impact**: {High|Medium|Low}
   - **Mitigation**: {How to address}

2. **{Risk 2}**
   - **Impact**: {High|Medium|Low}
   - **Mitigation**: {How to address}

---

## Testing Strategy

### Unit Tests

- {Test area 1}
- {Test area 2}

### Integration Tests

- {Integration test 1}
- {Integration test 2}

### Manual Testing

- [ ] {Manual test 1}
- [ ] {Manual test 2}

### Acceptance Criteria

From issue requirements:

- [ ] {Acceptance criterion 1}
- [ ] {Acceptance criterion 2}
- [ ] {Acceptance criterion 3}

---

## Documentation

### Documentation Updates Needed

- [ ] Update README.md with {what}
- [ ] Add guide to docs/ for {what}
- [ ] Update API documentation if applicable
- [ ] Add examples to templates/ if applicable

### User Communication

- [ ] Comment on issue #{ISSUE_NUMBER} with implementation plan
- [ ] Link related issues #{OTHER_ISSUES}
- [ ] Update CHANGELOG.md when complete
- [ ] Announce in release notes

---

## Rollout Plan

### Phase 1: Implementation
- {What gets built first}

### Phase 2: Testing
- {How it gets tested}

### Phase 3: Deployment
- {How it gets deployed}

### Phase 4: Monitoring
- {What to watch after deployment}

---

## Success Criteria

✅ **Definition of Done**:

- [ ] All requirements implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] PR approved and merged
- [ ] Deployed to production
- [ ] Issue #{ISSUE_NUMBER} closed
- [ ] Related issues #{OTHER_ISSUES} addressed

✅ **User Impact Metrics**:

- {How will we measure success?}
- {What metrics indicate this solved the problem?}

---

## Timeline

**Estimated Effort**: {DAYS/WEEKS}
**Target Completion**: {DATE or SPRINT}
**Assignee**: {AGENT or TBD}

---

## Related Issues & PRs

**Issues Addressed**:
- #{ISSUE_NUMBER} (primary)
- {#OTHER_ISSUES}

**Pull Requests**:
- {To be added when PRs created}

---

## Notes

{Any additional context, links to discussions, design documents, etc.}

---

**Spec Created**: {DATE}
**Created By**: @{CREATOR} (via `/github:issue-review`)
**Last Updated**: {DATE}
