#!/bin/bash

# Extract Values Script - Extracts deployment values from specs and project
# Usage: ./extract-values.sh <spec-dir>

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SPEC_DIR="${1:-specs/001-build-a-complete}"

echo -e "${BLUE}=== Extracting Deployment Values ===${NC}"
echo ""

# Extract database info
echo -e "${YELLOW}Database Configuration:${NC}"
if [[ -f "$SPEC_DIR/data-tables.md" ]]; then
    # Look for database type
    if grep -qi "postgres" "$SPEC_DIR/data-tables.md"; then
        echo "  Database Type: PostgreSQL"
        # Extract table names for database name hint
        DB_NAME=$(grep -i "table\|database" "$SPEC_DIR/data-tables.md" | head -1 | sed 's/.*database[: ]*\([a-zA-Z0-9_]*\).*/\1/' || echo "appdb")
        echo "  Suggested DB Name: ${DB_NAME}_dev"
        echo "  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/${DB_NAME}_dev"
    fi
fi
echo ""

# Extract API configuration
echo -e "${YELLOW}API Configuration:${NC}"
if [[ -f "$SPEC_DIR/api-endpoints.md" ]]; then
    # Count endpoints to estimate load
    ENDPOINT_COUNT=$(grep -c "^##\|^###" "$SPEC_DIR/api-endpoints.md" 2>/dev/null || echo 0)
    echo "  Total Endpoints: $ENDPOINT_COUNT"

    # Look for port specifications
    if grep -q "port\|:8" "$SPEC_DIR/api-endpoints.md"; then
        PORT=$(grep -o ":[0-9]\{4\}" "$SPEC_DIR/api-endpoints.md" | head -1 | tr -d ':' || echo "8000")
        echo "  API Port: $PORT"
    else
        echo "  API Port: 8000 (default)"
    fi

    # Check for webhook endpoints
    if grep -qi "webhook" "$SPEC_DIR/api-endpoints.md"; then
        echo "  Webhooks: Yes (needs WEBHOOK_SECRET)"
    fi
fi
echo ""

# Extract service requirements
echo -e "${YELLOW}Required Services:${NC}"
if [[ -f "$SPEC_DIR/spec.md" ]]; then
    # Check for Redis
    if grep -qi "redis\|cache\|session" "$SPEC_DIR/spec.md"; then
        echo "  Redis: Required"
        echo "  REDIS_URL: redis://localhost:6379"
    fi

    # Check for queue/celery
    if grep -qi "celery\|queue\|background" "$SPEC_DIR/spec.md"; then
        echo "  Queue: Celery/RabbitMQ"
        echo "  CELERY_BROKER_URL: redis://localhost:6379/0"
    fi

    # Check for external APIs
    if grep -qi "stripe\|payment" "$SPEC_DIR/spec.md"; then
        echo "  Stripe: Required (needs STRIPE_KEY)"
    fi
    if grep -qi "openai\|gpt" "$SPEC_DIR/spec.md"; then
        echo "  OpenAI: Required (needs OPENAI_API_KEY)"
    fi
fi
echo ""

# Extract from existing .env.example if present
if [[ -f ".env.example" ]]; then
    echo -e "${YELLOW}Existing Environment Variables:${NC}"
    # Show non-secret variables
    grep -v "SECRET\|KEY\|PASSWORD" .env.example | grep -v "^#" | grep -v "^$" | head -10
    echo ""
fi

# Generate suggested .env content
echo -e "${GREEN}Suggested .env content:${NC}"
cat << EOF
# Generated from specs analysis
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/${DB_NAME:-app}_dev

# Redis
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=${PORT:-8000}
LOG_LEVEL=debug

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Security (generate these!)
JWT_SECRET=change-this-to-secure-secret-$(date +%s)
SESSION_SECRET=change-this-to-secure-secret-$(date +%s)

# External Services (add your keys)
# STRIPE_KEY=
# OPENAI_API_KEY=
# WEBHOOK_SECRET=
EOF
echo ""

echo -e "${GREEN}✓ Analysis complete!${NC}"
echo "Copy the suggested content to deployment/configs/.env.development and update with real values"