# Issue Analysis Report

**Issue Number**: #{ISSUE_NUMBER}
**Title**: {ISSUE_TITLE}
**Author**: @{AUTHOR}
**Created**: {CREATED_DATE}
**Labels**: {LABELS}

---

## Quick Assessment

**Category**: {BUG|ENHANCEMENT|FEATURE|QUESTION|DOCS}
**Priority**: {CRITICAL|HIGH|MEDIUM|LOW}
**Clarity**: {✅ Clear | ⚠️ Unclear | ❌ Vague}
**Completeness**: {✅ Complete | ⚠️ Missing Info | ❌ Incomplete}

---

## Summary

{1-2 paragraph summary of what the user is requesting/reporting}

---

## Analysis

**User Need**:
{What problem is the user trying to solve?}

**Impact**:
{Who does this affect? How many users?}

**Scope**:
{Is this a small fix or large feature?}

**Complexity**:
{Low/Medium/High - implementation difficulty}

**Related Issues**:
{List similar or related issues: #XX, #YY}

---

## Recommendation

### ✅ Recommended Action

**{CREATE_SPEC | ADD_TO_SPEC | REQUEST_INFO | ANSWER_CLOSE | DEFER}**

**Rationale**:
{Why this action? 2-3 sentences}

---

## Next Steps

### If Creating Spec:

1. Create `specs/{NEXT_NUMBER}-{FEATURE_NAME}/`
2. Generate `spec.md` from issue content
3. Run `/planning:plan` to add technical details
4. Run `/planning:tasks` to generate task breakdown
5. Comment on issue with plan
6. Add `planned` label
7. Link related issues

### If Adding to Spec:

1. Add task to `specs/{EXISTING_SPEC}/tasks.md`
2. Update `specs/{EXISTING_SPEC}/spec.md` with notes
3. Comment on issue: "Added to specs/{EXISTING_SPEC}/"
4. Add `planned` label

### If Requesting Info:

**Missing Information**:
- {What's missing?}
- {What else needed?}

**Suggested Comment**:
```
Thanks for reporting! To help us {fix/implement} this, could you provide:

1. {Missing item 1}
2. {Missing item 2}
3. {Missing item 3}

This will help us address the issue faster!
```

**Action**: Add `needs-info` label

### If Answering & Closing:

**Suggested Comment**:
```
{Your answer or explanation}

{Link to docs if applicable}

Feel free to reopen if you have more questions!
```

**Action**: Close issue

### If Deferring:

**Suggested Comment**:
```
Thanks for the suggestion! This is {why it's low priority}.
We'll revisit this in the future when {condition}.
```

**Action**: Add `deferred` label, keep open

---

## Missing Information

{List any missing information that would help triage this issue}

- [ ] {Missing item 1}
- [ ] {Missing item 2}
- [ ] {Missing item 3}

---

## Linked Issues

**Similar issues**: {#XX, #YY}
**Blocked by**: {#ZZ}
**Related to**: {#AA}

---

## Implementation Estimate

**If approved for development:**

- **Effort**: {1-2 days | 3-5 days | 1-2 weeks | 2+ weeks}
- **Complexity**: {Low | Medium | High}
- **Dependencies**: {List any blockers or prerequisites}

---

## Roadmap Impact

**Current phase**: {Setup | Development | Deployment | Maintenance}
**Fits in**: {Phase X}
**Priority in roadmap**: {Next sprint | Backlog | Future}

---

**Reviewed by**: @{REVIEWER}
**Date**: {REVIEW_DATE}
