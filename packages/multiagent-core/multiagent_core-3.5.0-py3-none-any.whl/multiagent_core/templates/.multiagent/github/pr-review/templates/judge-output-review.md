# Judge Output Review Template

## Execution Flow (judge-architect)
```
1. Parse PR context from session directory
   → Read pr-context.json for PR_NUMBER, BRANCH, SPEC_DIR
2. Extract spec number from branch name
   → Pattern: agent-{agent}-{spec} → extract {spec}
3. Load original SpecKit spec
   → Read specs/{spec}/spec.md to understand requirements
4. Fetch Claude Code review
   → Run: gh pr view {{pr_number}} --json reviews,comments
5. Parse review feedback
   → Identify priority markers (🚨 critical, ⚠️ high, 📋 medium)
6. For each feedback item:
   → Estimate effort (<1h, 1-4h, 4-8h, >1day)
   → Assess value (low/medium/high)
   → Cross-reference against spec requirements
7. Calculate decision matrix scores
   → Quality, cost, value, risk scores
8. Fill template sections with analysis
9. Generate recommendation (APPROVE/DEFER/REJECT)
10. Create review-tasks.md with agent assignments
11. Return: SUCCESS (judge analysis complete)
```

## Session Information
- **Session ID**: {{session_id}}
- **PR Number**: #{{pr_number}}
- **PR Title**: {{pr_title}}
- **Detected Agent**: @{{detected_agent}}
- **Analysis Date**: {{judged_at}}

## Executive Summary

### Overall Assessment
- **Recommendation**: {{recommendation}}
- **Action Required**: {{requires_action}}
- **Priority Level**: {{action_urgency}}
- **Estimated Effort**: {{estimated_effort}}
- **Significance Score**: {{significance_score}}/100

### Key Findings
{{reasoning}}

## Detailed Analysis

### Feedback Metrics
- **Total Feedback Items**: {{total_feedback}}
- **Priority Breakdown**:
  - High Priority: {{high_priority}} items
  - Medium Priority: {{medium_priority}} items  
  - Low Priority: {{low_priority}} items

### Category Analysis
- **Security Issues**: {{security_count}} items
- **Architecture Concerns**: {{architecture_count}} items
- **Testing Requirements**: {{testing_count}} items
- **Task Completion**: {{task_count}} items

## Action Plan

### Priority Actions
{{#priority_actions}}
- {{.}}
{{/priority_actions}}

### Recommended Next Steps
1. Generate actionable tasks from priority feedback
2. Route to appropriate agent for implementation
3. Schedule follow-up review after changes

## Quality Assessment

### Review Quality Indicators
- **Actionable Feedback**: {{has_actionable_feedback}}
- **Specific Suggestions**: {{specific_suggestions_count}}
- **Code References**: {{code_references_count}}
- **Implementation Guidance**: {{has_implementation_guidance}}

### Cost-Benefit Analysis
- **Implementation Hours**: {{estimated_implementation_hours}}
- **Value Impact**: {{potential_value_impact}}
- **Technical Complexity**: {{technical_complexity}}
- **Goal Alignment**: {{alignment_with_goals}}

## Decision Matrix

| Factor | Score | Weight | Impact |
|--------|-------|--------|--------|
| Feedback Quality | {{quality_score}} | 30% | {{quality_impact}} |
| Implementation Cost | {{cost_score}} | 25% | {{cost_impact}} |
| Value Potential | {{value_score}} | 25% | {{value_impact}} |
| Technical Risk | {{risk_score}} | 20% | {{risk_impact}} |
| **Total** | **{{total_score}}** | **100%** | **{{final_decision}}** |

## Approval Requirements

### Human Approval Gate
- **Requires Human Review**: {{requires_human_approval}}
- **Auto-Approve Threshold**: {{auto_approve_threshold}}
- **Current Score**: {{quality_score}}
- **Auto-Approve Eligible**: {{auto_approve_eligible}}

### Approval Criteria Met
- [ ] Technical merit verified
- [ ] Implementation cost reasonable
- [ ] No security concerns
- [ ] Aligns with project goals
- [ ] Resource availability confirmed

## Implementation Roadmap

### Phase 1: Critical Issues ({{high_priority}} items)
{{#high_priority_items}}
- **{{type}}**: {{content}}
  - File: {{file}}
  - Line: {{line}}
  - Impact: Critical
{{/high_priority_items}}

### Phase 2: Quality Improvements ({{medium_priority}} items)
{{#medium_priority_items}}
- **{{type}}**: {{content}}
  - File: {{file}}
  - Line: {{line}}
  - Impact: Medium
{{/medium_priority_items}}

### Phase 3: Enhancements ({{low_priority}} items)
{{#low_priority_items}}
- **{{type}}**: {{content}}
  - File: {{file}}
  - Line: {{line}}
  - Impact: Low
{{/low_priority_items}}

## Risk Assessment

### Technical Risks
- **Implementation Complexity**: {{technical_complexity}}
- **Breaking Change Potential**: {{breaking_change_risk}}
- **Dependency Impact**: {{dependency_risk}}
- **Testing Requirements**: {{testing_complexity}}

### Mitigation Strategies
1. **Incremental Implementation**: Break changes into smaller, testable chunks
2. **Comprehensive Testing**: Ensure full test coverage before deployment
3. **Rollback Plan**: Maintain ability to revert changes if issues arise
4. **Stakeholder Communication**: Keep all stakeholders informed of progress

## Conclusion

### Summary
Based on the analysis of {{total_feedback}} feedback items with a significance score of {{significance_score}}/100, the recommendation is to **{{recommendation}}** with {{action_urgency}} priority.

### Key Success Factors
1. Address all high-priority security and architecture concerns first
2. Maintain clear communication throughout implementation
3. Ensure thorough testing before deployment
4. Schedule follow-up review to validate improvements

### Final Decision
- **Proceed**: {{should_proceed}}
- **Conditional Approval**: {{conditional_approval}}
- **Human Review Required**: {{requires_human_approval}}
- **Next Phase**: {{next_phase}}

---
*Generated by MultiAgent Core Feedback System*  
*Session: {{session_id}} | {{judged_at}}*