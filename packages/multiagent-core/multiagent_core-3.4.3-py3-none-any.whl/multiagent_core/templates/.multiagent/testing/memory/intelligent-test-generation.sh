#!/bin/bash

# Claude's Intelligent Test Generation based on Task Analysis
# Generated after analyzing specs/001-build-a-complete/tasks.md

OUTPUT_DIR="tests"
TEMPLATES_DIR=".multiagent/testing/templates"

echo "Creating intelligent test structure based on task analysis..."

# ============================================
# BACKEND TESTING STRUCTURE
# ============================================

# API Endpoints - Core functionality tests
mkdir -p "$OUTPUT_DIR/backend/api/endpoints"
mkdir -p "$OUTPUT_DIR/backend/api/webhooks"
mkdir -p "$OUTPUT_DIR/backend/api/deployment"

# Authentication & Security - Critical path tests
mkdir -p "$OUTPUT_DIR/backend/security/auth"
mkdir -p "$OUTPUT_DIR/backend/security/validation"
mkdir -p "$OUTPUT_DIR/backend/security/rate-limiting"

# Background Processing - Async operation tests
mkdir -p "$OUTPUT_DIR/backend/workers/queue"
mkdir -p "$OUTPUT_DIR/backend/workers/tasks"

# ============================================
# INTEGRATION TESTING STRUCTURE
# ============================================

# GitHub Integration - Webhook and API tests
mkdir -p "$OUTPUT_DIR/integration/github/webhooks"
mkdir -p "$OUTPUT_DIR/integration/github/actions"
mkdir -p "$OUTPUT_DIR/integration/github/pr-automation"

# AgentSwarm Integration - Core integration point
mkdir -p "$OUTPUT_DIR/integration/agentswarm/routing"
mkdir -p "$OUTPUT_DIR/integration/agentswarm/deployment"
mkdir -p "$OUTPUT_DIR/integration/agentswarm/feedback"

# Service Communication - Inter-service tests
mkdir -p "$OUTPUT_DIR/integration/services/communication"
mkdir -p "$OUTPUT_DIR/integration/services/orchestration"

# ============================================
# E2E TESTING STRUCTURE
# ============================================

# Complete Workflows - Full automation tests
mkdir -p "$OUTPUT_DIR/e2e/workflows/pr-review"
mkdir -p "$OUTPUT_DIR/e2e/workflows/agent-feedback"
mkdir -p "$OUTPUT_DIR/e2e/workflows/bulk-deployment"

# ============================================
# CONTRACT TESTING STRUCTURE
# ============================================

# API Contracts - Interface validation
mkdir -p "$OUTPUT_DIR/contract/api"
mkdir -p "$OUTPUT_DIR/contract/webhooks"
mkdir -p "$OUTPUT_DIR/contract/agentswarm"

# ============================================
# PERFORMANCE TESTING STRUCTURE
# ============================================

# Performance & Load - Scalability tests
mkdir -p "$OUTPUT_DIR/performance/load"
mkdir -p "$OUTPUT_DIR/performance/rate-limiting"

# ============================================
# UNIT TESTING STRUCTURE
# ============================================

# Core Logic - Isolated component tests
mkdir -p "$OUTPUT_DIR/unit/parsers"
mkdir -p "$OUTPUT_DIR/unit/validators"
mkdir -p "$OUTPUT_DIR/unit/routers"

# ============================================
# GENERATE TEST FILES WITH INTELLIGENT CONTEXT
# ============================================

# T020-T024: FastAPI Feedback System (Core API functionality)
cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T020/g' | \
sed 's/{{TASK_DESC}}/FastAPI feedback endpoint with GitHub webhook integration/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/backend/g' > "$OUTPUT_DIR/backend/api/endpoints/T020_feedback_endpoint.test.py"

cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T021/g' | \
sed 's/{{TASK_DESC}}/HMAC-SHA256 webhook signature validation/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/security/g' > "$OUTPUT_DIR/backend/security/validation/T021_webhook_validation.test.py"

cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T022/g' | \
sed 's/{{TASK_DESC}}/Token bucket rate limiting algorithm/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/security/g' > "$OUTPUT_DIR/backend/security/rate-limiting/T022_rate_limiting.test.py"

cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T023/g' | \
sed 's/{{TASK_DESC}}/Background task queue processing/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/backend/g' > "$OUTPUT_DIR/backend/workers/queue/T023_queue_handler.test.py"

cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T024/g' | \
sed 's/{{TASK_DESC}}/Authentication and security layers/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/security/g' > "$OUTPUT_DIR/backend/security/auth/T024_authentication.test.py"

# T010-T012: PR Feedback Router (Core routing logic)
cat "$TEMPLATES_DIR/integration_template.test.js" | \
sed 's/{{TASK_ID}}/T010/g' | \
sed 's/{{TASK_DESC}}/PR feedback router agent with intelligent parsing/g' | \
sed 's/{{LAYER}}/2/g' | \
sed 's/{{CATEGORY}}/integration/g' > "$OUTPUT_DIR/integration/services/communication/T010_pr_feedback_router.test.js"

cat "$TEMPLATES_DIR/unit_template.test.js" | \
sed 's/{{TASK_ID}}/T011/g' | \
sed 's/{{TASK_DESC}}/Feedback parsing and routing logic/g' | \
sed 's/{{LAYER}}/2/g' | \
sed 's/{{CATEGORY}}/unit/g' > "$OUTPUT_DIR/unit/parsers/T011_feedback_parser.test.js"

# T029-T032: AgentSwarm Integration (Critical integration points)
cat "$TEMPLATES_DIR/integration_template.test.js" | \
sed 's/{{TASK_ID}}/T029/g' | \
sed 's/{{TASK_DESC}}/AgentSwarm integration bridge with branch detection/g' | \
sed 's/{{LAYER}}/4/g' | \
sed 's/{{CATEGORY}}/integration/g' > "$OUTPUT_DIR/integration/agentswarm/routing/T029_agentswarm_bridge.test.js"

cat "$TEMPLATES_DIR/integration_template.test.js" | \
sed 's/{{TASK_ID}}/T030/g' | \
sed 's/{{TASK_DESC}}/Bulk agent deployment orchestration/g' | \
sed 's/{{LAYER}}/4/g' | \
sed 's/{{CATEGORY}}/integration/g' > "$OUTPUT_DIR/integration/agentswarm/deployment/T030_bulk_deployment.test.js"

cat "$TEMPLATES_DIR/backend_template.test.py" | \
sed 's/{{TASK_ID}}/T031/g' | \
sed 's/{{TASK_DESC}}/Deployment API endpoints for bulk operations/g' | \
sed 's/{{LAYER}}/4/g' | \
sed 's/{{CATEGORY}}/backend/g' > "$OUTPUT_DIR/backend/api/deployment/T031_deployment_api.test.py"

# T001-T003: GitHub Actions and Automation (CI/CD tests)
cat "$TEMPLATES_DIR/integration_template.test.js" | \
sed 's/{{TASK_ID}}/T001/g' | \
sed 's/{{TASK_DESC}}/GitHub Actions workflow setup and triggers/g' | \
sed 's/{{LAYER}}/1/g' | \
sed 's/{{CATEGORY}}/integration/g' > "$OUTPUT_DIR/integration/github/actions/T001_github_actions.test.js"

cat "$TEMPLATES_DIR/integration_template.test.js" | \
sed 's/{{TASK_ID}}/T003/g' | \
sed 's/{{TASK_DESC}}/Claude review automation with approval logic/g' | \
sed 's/{{LAYER}}/1/g' | \
sed 's/{{CATEGORY}}/integration/g' > "$OUTPUT_DIR/integration/github/pr-automation/T003_claude_automation.test.js"

# E2E Complete Workflow Tests
cat "$TEMPLATES_DIR/e2e_template.test.js" | \
sed 's/{{TASK_ID}}/E2E001/g' | \
sed 's/{{TASK_DESC}}/Complete PR review workflow from commit to merge/g' | \
sed 's/{{LAYER}}/5/g' | \
sed 's/{{CATEGORY}}/e2e/g' > "$OUTPUT_DIR/e2e/workflows/pr-review/complete_pr_workflow.test.js"

cat "$TEMPLATES_DIR/e2e_template.test.js" | \
sed 's/{{TASK_ID}}/E2E002/g' | \
sed 's/{{TASK_DESC}}/Agent feedback loop with automatic fixes/g' | \
sed 's/{{LAYER}}/5/g' | \
sed 's/{{CATEGORY}}/e2e/g' > "$OUTPUT_DIR/e2e/workflows/agent-feedback/feedback_loop.test.js"

# Contract Tests for API Interfaces
cat "$TEMPLATES_DIR/contract_template.test.yaml" | \
sed 's/{{TASK_ID}}/CONTRACT001/g' | \
sed 's/{{TASK_DESC}}/GitHub webhook payload contract/g' | \
sed 's/{{LAYER}}/3/g' | \
sed 's/{{CATEGORY}}/contract/g' > "$OUTPUT_DIR/contract/webhooks/github_webhook.test.yaml"

cat "$TEMPLATES_DIR/contract_template.test.yaml" | \
sed 's/{{TASK_ID}}/CONTRACT002/g' | \
sed 's/{{TASK_DESC}}/AgentSwarm API contract/g' | \
sed 's/{{LAYER}}/4/g' | \
sed 's/{{CATEGORY}}/contract/g' > "$OUTPUT_DIR/contract/agentswarm/api_contract.test.yaml"

# Performance Tests for Critical Paths
echo "// Performance test for rate limiting" > "$OUTPUT_DIR/performance/rate-limiting/token_bucket_performance.test.js"
echo "// Load test for webhook processing" > "$OUTPUT_DIR/performance/load/webhook_load.test.js"

# Generate README files with intelligent context
cat > "$OUTPUT_DIR/backend/README.md" << EOF
# Backend Tests

## Structure
- **api/endpoints**: Core API endpoint tests (T020, T025, T031)
- **api/webhooks**: GitHub webhook handling tests (T021)
- **api/deployment**: Bulk deployment API tests (T031)
- **security/auth**: Authentication tests (T024)
- **security/validation**: HMAC validation tests (T021)
- **security/rate-limiting**: Token bucket tests (T022)
- **workers/queue**: Background task processing tests (T023)

## Test Strategy
- Mock external dependencies (GitHub API, AgentSwarm)
- Test security boundaries thoroughly
- Validate async operations with proper timeouts
- Ensure rate limiting accuracy under load
EOF

cat > "$OUTPUT_DIR/integration/README.md" << EOF
# Integration Tests

## Structure
- **github/**: GitHub integration tests (webhooks, actions, PR automation)
- **agentswarm/**: AgentSwarm bridge and deployment tests
- **services/**: Inter-service communication tests

## Test Strategy
- Test complete data flow between services
- Validate webhook → router → agent pipeline
- Ensure proper branch detection and routing
- Test bulk deployment orchestration
EOF

cat > "$OUTPUT_DIR/e2e/README.md" << EOF
# End-to-End Tests

## Structure
- **workflows/pr-review**: Complete PR review automation
- **workflows/agent-feedback**: Agent feedback loop testing
- **workflows/bulk-deployment**: Multi-agent deployment tests

## Test Strategy
- Test complete user journeys
- Validate automation from commit to merge
- Test failure recovery and retries
- Ensure no human intervention required
EOF

echo "✅ Intelligent test structure created based on task analysis!"
echo ""
echo "Key Intelligence Applied:"
echo "1. Grouped T020-T024 as core API system requiring comprehensive backend tests"
echo "2. Recognized T029-T032 as critical integration points needing integration tests"
echo "3. Identified security tasks (T021, T022, T024) needing dedicated security tests"
echo "4. Created workflow tests for complete automation validation"
echo "5. Added performance tests for rate limiting and load handling"
echo "6. Structured by feature domain, not just file type"