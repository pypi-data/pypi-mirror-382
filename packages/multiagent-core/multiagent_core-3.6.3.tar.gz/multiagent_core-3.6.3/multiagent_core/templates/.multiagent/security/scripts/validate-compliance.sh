#!/usr/bin/env bash
# Security Tool: Compliance Validator
# Called by: security-auth-compliance agent after setup
# Purpose: Verify all security measures are in place

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
COMPLIANCE_PASS=true

echo "[VALIDATE] Checking security compliance for: $PROJECT_ROOT"
echo ""

# Check 1: .gitignore exists with security patterns
echo "[CHECK 1/5] Verifying .gitignore protection..."
if [[ -f "$PROJECT_ROOT/.gitignore" ]]; then
    # Check for critical security patterns
    required_patterns=(".env" "*.key" "*.pem" "secrets/" "GEMINI.md" "api_keys.*")
    missing_patterns=()

    for pattern in "${required_patterns[@]}"; do
        if ! grep -q "$pattern" "$PROJECT_ROOT/.gitignore" 2>/dev/null; then
            missing_patterns+=("$pattern")
        fi
    done

    if [[ ${#missing_patterns[@]} -eq 0 ]]; then
        echo "✅ .gitignore has all required security patterns"
    else
        echo "❌ .gitignore missing patterns: ${missing_patterns[*]}"
        COMPLIANCE_PASS=false
    fi
else
    echo "❌ .gitignore not found"
    COMPLIANCE_PASS=false
fi
echo ""

# Check 2: .env not committed
echo "[CHECK 2/5] Verifying .env not committed..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "❌ CRITICAL: .env is tracked by git!"
    COMPLIANCE_PASS=false
else
    echo "✅ .env not committed to git"
fi
echo ""

# Check 3: Git hooks installed
echo "[CHECK 3/5] Verifying git hooks installed..."
hooks=("pre-push" "post-commit")
for hook in "${hooks[@]}"; do
    hook_path="$PROJECT_ROOT/.git/hooks/$hook"
    if [[ -f "$hook_path" && -x "$hook_path" ]]; then
        echo "✅ $hook hook installed and executable"
    else
        echo "❌ $hook hook missing or not executable"
        COMPLIANCE_PASS=false
    fi
done
echo ""

# Check 4: .env.example exists
echo "[CHECK 4/5] Verifying .env.example exists..."
if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
    echo "✅ .env.example present (safe to commit)"
else
    echo "❌ .env.example not found"
    COMPLIANCE_PASS=false
fi
echo ""

# Check 5: GitHub workflows present
echo "[CHECK 5/5] Verifying GitHub security workflows..."
if [[ -d "$PROJECT_ROOT/.github/workflows" ]]; then
    workflows=("security-scan.yml" "security-scanning.yml")
    for workflow in "${workflows[@]}"; do
        if [[ -f "$PROJECT_ROOT/.github/workflows/$workflow" ]]; then
            echo "✅ $workflow present"
        else
            echo "⚠️  $workflow not found (optional if not using GitHub Actions)"
        fi
    done
else
    echo "⚠️  .github/workflows/ not found (optional)"
fi
echo ""

# Final report
if [[ "$COMPLIANCE_PASS" = true ]]; then
    echo "[RESULT] ✅ Security compliance: PASS"
    echo "All critical security measures are in place."
    exit 0
else
    echo "[RESULT] ❌ Security compliance: FAIL"
    echo "Fix the issues above before proceeding."
    exit 1
fi