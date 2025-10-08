#!/usr/bin/env bash
# Security Tool: Secret Pattern Scanner
# Called by: security-auth-compliance agent during validation
# Purpose: Scan files for exposed secrets using pattern matching

set -euo pipefail

SCAN_DIR="${1:-.}"
FOUND_SECRETS=0

# Secret patterns to detect (prevents $2,300 disasters!)
declare -A PATTERNS=(
    ["Google API Key"]="AIzaSy[0-9A-Za-z_-]{33}"
    ["Google OAuth"]="ya29\.[0-9A-Za-z_-]+"
    ["OpenAI API Key"]="sk-[0-9A-Za-z]{48}"
    ["OpenAI Project Key"]="sk-proj-[0-9A-Za-z_-]{43}"
    ["OpenAI Org ID"]="org-[0-9A-Za-z_-]{24}"
    ["GitHub Personal Token"]="ghp_[0-9A-Za-z]{36}"
    ["GitHub OAuth Token"]="gho_[0-9A-Za-z]{36}"
    ["GitHub User Token"]="ghu_[0-9A-Za-z]{36}"
    ["GitHub Server Token"]="ghs_[0-9A-Za-z]{36}"
    ["GitHub Refresh Token"]="ghr_[0-9A-Za-z]{36}"
    ["AWS Access Key"]="AKIA[0-9A-Z]{16}"
    ["Slack Token"]="xoxb-[0-9]+-[0-9]+-[0-9A-Za-z]+"
    ["Slack Webhook"]="https://hooks\.slack\.com/services/T[0-9A-Z]{8,10}/B[0-9A-Z]{8,10}/[0-9A-Za-z]{24}"
    ["Azure Storage Key"]="AccountKey=[0-9A-Za-z+/]{88}=="
    ["Private Key Header"]="-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"
    ["Postman API Key"]="PMAK-[0-9A-Za-z]{24,60}"
    ["Generic API Assignment"]="(api[_-]?key|api[_-]?token|api[_-]?secret|access[_-]?token)\\s*=\\s*['\\\"][^'\\\"]+['\\\"]"
)

# Dangerous files (specific patterns)
DANGEROUS_FILES=(
    "GEMINI.md"
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    "id_rsa"
    "id_dsa"
)

echo "[SCAN] Scanning for exposed secrets in: $SCAN_DIR"
echo ""

# Scan for dangerous files
for pattern in "${DANGEROUS_FILES[@]}"; do
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            echo "[DANGER] Found dangerous file: $file"
            FOUND_SECRETS=1
        fi
    done < <(find "$SCAN_DIR" -name "$pattern" -type f 2>/dev/null || true)
done

# Scan for secret patterns in files
for secret_type in "${!PATTERNS[@]}"; do
    pattern="${PATTERNS[$secret_type]}"

    while IFS=: read -r file line content; do
        if [[ -n "$file" ]]; then
            echo "[SECRET] $secret_type detected:"
            echo "         File: $file"
            echo "         Line: $line"
            echo "         Content: ${content:0:80}..."
            echo ""
            FOUND_SECRETS=1
        fi
    done < <(grep -rEn "$pattern" "$SCAN_DIR" 2>/dev/null || true)
done

# Report results
if [[ $FOUND_SECRETS -eq 1 ]]; then
    echo "[BLOCKED] ❌ Secrets detected! Fix before proceeding."
    exit 1
else
    echo "[OK] ✅ No secrets detected in codebase"
    exit 0
fi