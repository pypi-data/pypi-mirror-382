#!/bin/bash
# SLA enforcement and Slack MCP notifications
# Usage: human-approval-gate.sh <session_id> [decision]

set -euo pipefail

SESSION_ID="${1:-}"
DECISION="${2:-}"

if [[ -z "$SESSION_ID" ]]; then
    echo "Usage: $0 <session_id> [approve|reject|timeout]"
    echo "Example: $0 20250926_143022_pr123 approve"
    exit 1
fi

SESSION_DIR=".multiagent/feedback/logs/${SESSION_ID}"

if [[ ! -d "$SESSION_DIR" ]]; then
    echo "❌ Session not found: ${SESSION_ID}"
    exit 1
fi

echo "🚪 Human approval gate for session: ${SESSION_ID}"

# Check if judge analysis exists
if [[ ! -f "${SESSION_DIR}/judge-analysis.json" ]]; then
    echo "❌ Judge analysis not found. Run judge-feedback.sh first."
    exit 1
fi

# Calculate deadline (24 hours from session creation)
CREATED_AT=$(jq -r '.created_at' "${SESSION_DIR}/session-metadata.json")
DEADLINE=$(date -d "${CREATED_AT} + 24 hours" -u +%Y-%m-%dT%H:%M:%SZ)
CURRENT_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Check if decision provided
if [[ -n "$DECISION" ]]; then
    case "$DECISION" in
        approve|approved)
            DECISION="approved"
            echo "✅ Human approval: APPROVED"
            ;;
        reject|rejected)
            DECISION="rejected"
            echo "❌ Human approval: REJECTED"
            ;;
        timeout)
            DECISION="timeout"
            echo "⏰ Human approval: TIMEOUT"
            ;;
        *)
            echo "❌ Invalid decision: $DECISION (use approve/reject/timeout)"
            exit 1
            ;;
    esac
else
    # Check for timeout
    if [[ "$CURRENT_TIME" > "$DEADLINE" ]]; then
        DECISION="timeout"
        echo "⏰ SLA EXCEEDED: 24-hour approval deadline passed"
    else
        echo "⏳ Awaiting human decision (deadline: $DEADLINE)"
        echo "💡 To provide decision: $0 $SESSION_ID [approve|reject]"
        exit 0
    fi
fi

# Create human decision record
cat > "${SESSION_DIR}/human-decision.json" << EOF
{
  "session_id": "${SESSION_ID}",
  "decision": "${DECISION}",
  "decision_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deadline": "${DEADLINE}",
  "sla_exceeded": $(if [[ "$CURRENT_TIME" > "$DEADLINE" ]]; then echo "true"; else echo "false"; fi),
  "decision_method": "$(if [[ "$DECISION" == "timeout" ]]; then echo "automatic-timeout"; else echo "manual"; fi)"
}
EOF

# Update session metadata
case "$DECISION" in
    approved)
        jq '.phase = "task-generation" | .status = "approved"' "${SESSION_DIR}/session-metadata.json" > "${SESSION_DIR}/session-metadata.tmp"
        echo "🎯 Next: Run generate-feedback-tasks.sh ${SESSION_ID}"
        ;;
    rejected)
        jq '.phase = "completed" | .status = "rejected"' "${SESSION_DIR}/session-metadata.json" > "${SESSION_DIR}/session-metadata.tmp"
        echo "🛑 Feedback processing rejected. Session closed."
        ;;
    timeout)
        jq '.phase = "escalated" | .status = "sla-exceeded"' "${SESSION_DIR}/session-metadata.json" > "${SESSION_DIR}/session-metadata.tmp"
        echo "🚨 SLA exceeded. Escalating to manual review."
        
        # TODO: Send Slack MCP notification
        echo "📢 Slack notification: SLA exceeded for session ${SESSION_ID}"
        ;;
esac

mv "${SESSION_DIR}/session-metadata.tmp" "${SESSION_DIR}/session-metadata.json"

echo "✅ Human approval gate processed"
echo "📝 Decision: ${DECISION}"
echo "📂 Decision stored in: ${SESSION_DIR}/human-decision.json"