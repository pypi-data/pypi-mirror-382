#!/bin/bash

# Deployment Generation Script - Creates deployment artifacts based on project analysis
# Usage: ./generate-deployment.sh <spec-dir> [output-dir]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SPEC_DIR="${1:-specs/001-build-a-complete}"
OUTPUT_DIR="${2:-deployment}"
TEMPLATES_DIR=".multiagent/deployment/templates"
MEMORY_DIR=".multiagent/deployment/memory"
LOGS_DIR=".multiagent/deployment/logs"

# Create session ID
SESSION_ID="deploy-$(basename "$SPEC_DIR")-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOGS_DIR/$SESSION_ID.log"

# Ensure directories exist
mkdir -p "$OUTPUT_DIR"/{docker,k8s,configs,scripts}
mkdir -p "$MEMORY_DIR"
mkdir -p "$LOGS_DIR"

echo -e "${BLUE}=== Deployment Generation ===${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}Output: $OUTPUT_DIR${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to analyze complete spec directory
analyze_complete_spec() {
    local CONTEXT_FILE="/tmp/deployment-context.txt"

    echo -e "${YELLOW}=== Analyzing Complete Spec Directory ===${NC}" | tee -a "$LOG_FILE"
    echo "Creating comprehensive context at: $CONTEXT_FILE" | tee -a "$LOG_FILE"

    # Initialize context file
    {
        echo "=== DEPLOYMENT CONTEXT ANALYSIS ==="
        echo "Generated: $(date)"
        echo "Spec Directory: $SPEC_DIR"
        echo ""
        echo "=== FILES ANALYZED ==="
    } > "$CONTEXT_FILE"

    # List all files being analyzed
    find "$SPEC_DIR" -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) | while read -r file; do
        echo "  - $(realpath --relative-to="$SPEC_DIR" "$file")" >> "$CONTEXT_FILE"
        echo "  Analyzing: $(basename "$file")" | tee -a "$LOG_FILE"
    done

    echo "" >> "$CONTEXT_FILE"

    # 1. Analyze layered-tasks.md for components and services
    if [[ -f "$SPEC_DIR/agent-tasks/layered-tasks.md" ]]; then
        echo "  Extracting components from layered-tasks.md..." | tee -a "$LOG_FILE"
        {
            echo "=== COMPONENTS FROM LAYERED TASKS ==="
            grep -E "implement|create|build|develop" "$SPEC_DIR/agent-tasks/layered-tasks.md" | \
                grep -v "^#" | head -30
            echo ""
        } >> "$CONTEXT_FILE"
    fi

    # 2. Analyze plan.md for architecture
    if [[ -f "$SPEC_DIR/plan.md" ]]; then
        echo "  Extracting architecture from plan.md..." | tee -a "$LOG_FILE"
        {
            echo "=== ARCHITECTURE FROM PLAN ==="
            grep -E "architecture|framework|stack|technology|deployment" "$SPEC_DIR/plan.md" | \
                grep -v "^#" | head -20
            echo ""
        } >> "$CONTEXT_FILE"
    fi

    # 3. Analyze data-model.md for database
    if [[ -f "$SPEC_DIR/data-model.md" ]]; then
        echo "  Extracting database schema from data-model.md..." | tee -a "$LOG_FILE"
        {
            echo "=== DATABASE SCHEMA ==="
            grep -E "table|model|schema|field|relation" "$SPEC_DIR/data-model.md" | \
                grep -v "^#" | head -20
            echo ""
        } >> "$CONTEXT_FILE"
    fi

    # 4. Analyze contracts for APIs
    if [[ -d "$SPEC_DIR/contracts" ]]; then
        echo "  Extracting API definitions from contracts/..." | tee -a "$LOG_FILE"
        {
            echo "=== API ENDPOINTS FROM CONTRACTS ==="
            find "$SPEC_DIR/contracts" -type f \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" \) -exec grep -H -E "POST|GET|PUT|DELETE|PATCH|endpoint|route" {} \; | head -20
            echo ""
        } >> "$CONTEXT_FILE"
    fi

    # 5. Extract services and deployment requirements
    echo "  Identifying services and deployment needs..." | tee -a "$LOG_FILE"
    {
        echo "=== SERVICES & DEPLOYMENT ==="
        find "$SPEC_DIR" -name "*.md" -exec grep -h -E "docker|kubernetes|service|container|deploy|production" {} \; | \
            grep -v "^#" | sort -u | head -20
        echo ""
    } >> "$CONTEXT_FILE"

    echo "Context analysis complete: $(wc -l < "$CONTEXT_FILE") lines generated" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Function to detect COMPLETE technology stack
detect_stack() {
    local stack="unknown"
    local frontend=""
    local backend=""
    local database=""
    local deployment_platform=""
    local services=""
    local auth=""

    # First, analyze the complete spec directory
    analyze_complete_spec

    echo -e "${YELLOW}Detecting technology stack from analysis...${NC}" | tee -a "$LOG_FILE"

    # Read the context file for comprehensive analysis
    local CONTEXT_FILE="/tmp/deployment-context.txt"
    local all_spec_content=""

    if [[ -f "$CONTEXT_FILE" ]]; then
        all_spec_content=$(cat "$CONTEXT_FILE")
    fi

    # Also read all spec files directly for pattern matching
    if [[ -d "$SPEC_DIR" ]]; then
        # Find and concatenate all markdown files for analysis
        find "$SPEC_DIR" -type f -name "*.md" | while read -r file; do
            all_spec_content="${all_spec_content}$(cat "$file" 2>/dev/null)"
        done

        # Also check YAML files in contracts directory
        find "$SPEC_DIR" -type f \( -name "*.yml" -o -name "*.yaml" \) | while read -r file; do
            all_spec_content="${all_spec_content}$(cat "$file" 2>/dev/null)"
        done
    fi

    # 1. Check deployment platform mentioned (now checking ALL content)
    if [[ -f "$SPEC_DIR/spec.md" ]]; then
        # Deployment platforms
        if grep -qi "vercel\|next\.js.*deploy" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="vercel"
        elif grep -qi "aws\|elastic beanstalk\|ec2\|ecs\|fargate" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="aws"
        elif grep -qi "google cloud\|gcp\|cloud run" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="gcp"
        elif grep -qi "digitalocean\|do apps" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="digitalocean"
        elif grep -qi "heroku" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="heroku"
        elif grep -qi "kubernetes\|k8s\|helm" "$SPEC_DIR/spec.md" 2>/dev/null; then
            deployment_platform="kubernetes"
        fi

        # Backend framework
        if grep -qi "fastapi\|python.*api" "$SPEC_DIR/spec.md" 2>/dev/null; then
            backend="fastapi"
        elif grep -qi "django" "$SPEC_DIR/spec.md" 2>/dev/null; then
            backend="django"
        elif grep -qi "express\|node.*api" "$SPEC_DIR/spec.md" 2>/dev/null; then
            backend="express"
        elif grep -qi "nestjs" "$SPEC_DIR/spec.md" 2>/dev/null; then
            backend="nestjs"
        elif grep -qi "spring boot\|java.*api" "$SPEC_DIR/spec.md" 2>/dev/null; then
            backend="springboot"
        fi

        # Frontend framework
        if grep -qi "react\|next\.js" "$SPEC_DIR/spec.md" 2>/dev/null; then
            frontend="react"
        elif grep -qi "vue\|nuxt" "$SPEC_DIR/spec.md" 2>/dev/null; then
            frontend="vue"
        elif grep -qi "angular" "$SPEC_DIR/spec.md" 2>/dev/null; then
            frontend="angular"
        elif grep -qi "svelte\|sveltekit" "$SPEC_DIR/spec.md" 2>/dev/null; then
            frontend="svelte"
        fi

        # Additional services
        if grep -qi "redis\|cache" "$SPEC_DIR/spec.md" 2>/dev/null; then
            services="$services,redis"
        fi
        if grep -qi "rabbitmq\|amqp\|message queue" "$SPEC_DIR/spec.md" 2>/dev/null; then
            services="$services,rabbitmq"
        fi
        if grep -qi "elasticsearch\|search" "$SPEC_DIR/spec.md" 2>/dev/null; then
            services="$services,elasticsearch"
        fi
        if grep -qi "celery\|background.*task\|worker" "$SPEC_DIR/spec.md" 2>/dev/null; then
            services="$services,celery"
        fi

        # Authentication
        if grep -qi "oauth\|auth0\|okta" "$SPEC_DIR/spec.md" 2>/dev/null; then
            auth="oauth"
        elif grep -qi "jwt\|json web token" "$SPEC_DIR/spec.md" 2>/dev/null; then
            auth="jwt"
        elif grep -qi "supabase.*auth\|firebase.*auth" "$SPEC_DIR/spec.md" 2>/dev/null; then
            auth="managed"
        fi
    fi

    # 2. Check data-tables.md for database AND ORM
    if [[ -f "$SPEC_DIR/data-tables.md" ]]; then
        if grep -qi "postgres\|postgresql" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            database="postgres"
        elif grep -qi "mysql\|mariadb" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            database="mysql"
        elif grep -qi "mongodb\|mongo" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            database="mongodb"
        elif grep -qi "supabase" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            database="supabase"
        elif grep -qi "firebase\|firestore" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            database="firebase"
        fi

        # Check for ORM/ODM
        if grep -qi "prisma" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            services="$services,prisma"
        elif grep -qi "sqlalchemy" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            services="$services,sqlalchemy"
        elif grep -qi "mongoose" "$SPEC_DIR/data-tables.md" 2>/dev/null; then
            services="$services,mongoose"
        fi
    fi

    # 3. Check api-endpoints.md for API patterns and integrations
    if [[ -f "$SPEC_DIR/api-endpoints.md" ]]; then
        # External integrations
        if grep -qi "stripe" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            services="$services,stripe"
        fi
        if grep -qi "twilio\|sendgrid" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            services="$services,communications"
        fi
        if grep -qi "webhook" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            services="$services,webhooks"
        fi
        if grep -qi "graphql" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            services="$services,graphql"
        fi
        if grep -qi "websocket\|socket\.io" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            services="$services,websockets"
        fi
    fi

    # 4. Check tasks for CI/CD and deployment hints from all_spec_content
    if echo "$all_spec_content" | grep -qi "github actions\|ci.cd"; then
        services="$services,github-actions"
    fi
    if echo "$all_spec_content" | grep -qi "docker\|container"; then
        services="$services,docker"
    fi
    if echo "$all_spec_content" | grep -qi "microservice"; then
        services="$services,microservices"
    fi
    if echo "$all_spec_content" | grep -qi "event.driven\|message.queue"; then
        services="$services,event-driven"
    fi

    # Check api-endpoints.md for API patterns
    if [[ -f "$SPEC_DIR/api-endpoints.md" ]]; then
        if grep -qi "POST.*api\|GET.*api\|webhook" "$SPEC_DIR/api-endpoints.md" 2>/dev/null; then
            [[ -z "$backend" ]] && backend="api"
        fi
    fi

    # ALSO check actual project files (fallback)
    if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        [[ -z "$backend" ]] && backend="python"
        if grep -q "fastapi" requirements.txt 2>/dev/null; then
            backend="fastapi"
        elif grep -q "django" requirements.txt 2>/dev/null; then
            backend="django"
        elif grep -q "flask" requirements.txt 2>/dev/null; then
            backend="flask"
        fi
    fi

    # Check for Node.js
    if [[ -f "package.json" ]]; then
        if [[ -d "src" ]] && [[ -f "src/App.js" || -f "src/App.jsx" || -f "src/App.tsx" ]]; then
            frontend="react"
        elif grep -q "vue" package.json 2>/dev/null; then
            frontend="vue"
        elif grep -q "angular" package.json 2>/dev/null; then
            frontend="angular"
        elif grep -q "express" package.json 2>/dev/null; then
            backend="express"
        fi
    fi

    # Check for database in tasks or env
    if [[ -f ".env.example" ]]; then
        if grep -q "POSTGRES\|DATABASE_URL.*postgres" .env.example 2>/dev/null; then
            database="postgres"
        elif grep -q "MYSQL" .env.example 2>/dev/null; then
            database="mysql"
        elif grep -q "MONGO" .env.example 2>/dev/null; then
            database="mongodb"
        fi
    fi

    # Log detected stack
    echo -e "  Backend: ${backend:-none}" | tee -a "$LOG_FILE"
    echo -e "  Frontend: ${frontend:-none}" | tee -a "$LOG_FILE"
    echo -e "  Database: ${database:-none}" | tee -a "$LOG_FILE"
    echo -e "  Platform: ${deployment_platform:-docker}" | tee -a "$LOG_FILE"
    echo -e "  Services: ${services:-none}" | tee -a "$LOG_FILE"
    echo -e "  Auth: ${auth:-none}" | tee -a "$LOG_FILE"

    # Determine overall stack with platform info
    if [[ -n "$backend" ]] && [[ -n "$frontend" ]]; then
        stack="fullstack"
        echo "fullstack:$backend:$frontend:$database:$deployment_platform:$services:$auth"
    elif [[ -n "$backend" ]]; then
        stack="backend"
        echo "backend:$backend:$database:$deployment_platform:$services:$auth"
    elif [[ -n "$frontend" ]]; then
        stack="frontend"
        echo "frontend:$frontend:$deployment_platform:$services:$auth"
    else
        echo "unknown:::::"
    fi
}

# Function to generate platform-specific configs
generate_platform_configs() {
    local platform="$1"

    echo -e "${GREEN}Generating platform-specific configs for: $platform${NC}" | tee -a "$LOG_FILE"

    case "$platform" in
        "vercel")
            cat > "$OUTPUT_DIR/vercel.json" << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/main.py"
    }
  ]
}
EOF
            echo -e "  ${GREEN}✓${NC} Created vercel.json" | tee -a "$LOG_FILE"
            ;;

        "heroku")
            cat > "$OUTPUT_DIR/heroku.yml" << 'EOF'
build:
  docker:
    web: deployment/docker/Dockerfile
run:
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
EOF
            cat > "$OUTPUT_DIR/Procfile" << 'EOF'
web: uvicorn main:app --host 0.0.0.0 --port $PORT
EOF
            echo -e "  ${GREEN}✓${NC} Created heroku.yml and Procfile" | tee -a "$LOG_FILE"
            ;;

        "aws")
            mkdir -p "$OUTPUT_DIR/.platform/hooks/prebuild"
            cat > "$OUTPUT_DIR/.platform/hooks/prebuild/01_install.sh" << 'EOF'
#!/bin/bash
# AWS Elastic Beanstalk prebuild hook
yum install -y python3-devel
EOF
            chmod +x "$OUTPUT_DIR/.platform/hooks/prebuild/01_install.sh"
            echo -e "  ${GREEN}✓${NC} Created AWS EB configuration" | tee -a "$LOG_FILE"
            ;;

        "kubernetes")
            # K8s configs already generated, add Helm chart
            mkdir -p "$OUTPUT_DIR/helm"
            cat > "$OUTPUT_DIR/helm/Chart.yaml" << EOF
apiVersion: v2
name: application
description: Helm chart for application
type: application
version: 0.1.0
appVersion: "1.0"
EOF
            echo -e "  ${GREEN}✓${NC} Created Helm chart structure" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Function to generate Dockerfile
generate_dockerfile() {
    local stack_info="$1"
    local stack_type=$(echo "$stack_info" | cut -d: -f1)
    local backend=$(echo "$stack_info" | cut -d: -f2)
    local frontend=$(echo "$stack_info" | cut -d: -f3)

    echo -e "${GREEN}Generating Dockerfile for $stack_type${NC}" | tee -a "$LOG_FILE"

    case "$stack_type" in
        "backend")
            if [[ "$backend" == "python" || "$backend" == "fastapi" ]]; then
                generate_python_dockerfile
            elif [[ "$backend" == "express" ]]; then
                generate_node_dockerfile
            fi
            ;;
        "frontend")
            generate_react_dockerfile
            ;;
        "fullstack")
            generate_python_dockerfile
            generate_react_dockerfile "frontend"
            ;;
        *)
            generate_generic_dockerfile
            ;;
    esac
}

# Generate Python Dockerfile
generate_python_dockerfile() {
    local suffix="${1:-}"
    local filename="$OUTPUT_DIR/docker/Dockerfile${suffix:+.$suffix}"

    cat > "$filename" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
EOF
    echo -e "  ${GREEN}✓${NC} Created: $filename" | tee -a "$LOG_FILE"
}

# Generate React Dockerfile
generate_react_dockerfile() {
    local suffix="${1:-}"
    local filename="$OUTPUT_DIR/docker/Dockerfile${suffix:+.$suffix}"

    cat > "$filename" << 'EOF'
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
    echo -e "  ${GREEN}✓${NC} Created: $filename" | tee -a "$LOG_FILE"
}

# Generate Node.js Dockerfile
generate_node_dockerfile() {
    cat > "$OUTPUT_DIR/docker/Dockerfile" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

EXPOSE 3000

CMD ["node", "server.js"]
EOF
    echo -e "  ${GREEN}✓${NC} Created: $OUTPUT_DIR/docker/Dockerfile" | tee -a "$LOG_FILE"
}

# Generate generic Dockerfile
generate_generic_dockerfile() {
    cat > "$OUTPUT_DIR/docker/Dockerfile" << 'EOF'
FROM ubuntu:22.04

WORKDIR /app

# Copy application
COPY . .

# Install dependencies based on what's detected
RUN if [ -f requirements.txt ]; then \
        apt-get update && apt-get install -y python3 python3-pip && \
        pip3 install -r requirements.txt; \
    elif [ -f package.json ]; then \
        apt-get update && apt-get install -y nodejs npm && \
        npm install; \
    fi

# Default command
CMD ["/bin/bash"]
EOF
    echo -e "  ${GREEN}✓${NC} Created: $OUTPUT_DIR/docker/Dockerfile" | tee -a "$LOG_FILE"
}

# Generate docker-compose.yml
generate_docker_compose() {
    local stack_info="$1"
    local stack_type=$(echo "$stack_info" | cut -d: -f1)
    local database=$(echo "$stack_info" | cut -d: -f4)

    echo -e "${GREEN}Generating docker-compose.yml${NC}" | tee -a "$LOG_FILE"

    cat > "$OUTPUT_DIR/docker/docker-compose.yml" << 'EOF'
version: '3.8'

services:
EOF

    # Add backend service
    if [[ "$stack_type" == "backend" || "$stack_type" == "fullstack" ]]; then
        cat >> "$OUTPUT_DIR/docker/docker-compose.yml" << 'EOF'
  backend:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    volumes:
      - ../../:/app
    depends_on:
      - db
      - redis
    networks:
      - app-network

EOF
    fi

    # Add frontend service
    if [[ "$stack_type" == "frontend" || "$stack_type" == "fullstack" ]]; then
        cat >> "$OUTPUT_DIR/docker/docker-compose.yml" << 'EOF'
  frontend:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - app-network

EOF
    fi

    # Add database service
    if [[ "$database" == "postgres" ]]; then
        cat >> "$OUTPUT_DIR/docker/docker-compose.yml" << 'EOF'
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app-network

EOF
    fi

    # Add Redis
    cat >> "$OUTPUT_DIR/docker/docker-compose.yml" << 'EOF'
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
EOF

    echo -e "  ${GREEN}✓${NC} Created: $OUTPUT_DIR/docker/docker-compose.yml" | tee -a "$LOG_FILE"
}

# Generate Kubernetes manifests
generate_k8s_manifests() {
    echo -e "${GREEN}Generating Kubernetes manifests${NC}" | tee -a "$LOG_FILE"

    # Deployment
    cat > "$OUTPUT_DIR/k8s/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    app: application
spec:
  replicas: 3
  selector:
    matchLabels:
      app: application
  template:
    metadata:
      labels:
        app: application
    spec:
      containers:
      - name: app
        image: application:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

    # Service
    cat > "$OUTPUT_DIR/k8s/service.yaml" << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: application
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
EOF

    # ConfigMap
    cat > "$OUTPUT_DIR/k8s/configmap.yaml" << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.conf: |
    LOG_LEVEL=info
    ENVIRONMENT=production
EOF

    echo -e "  ${GREEN}✓${NC} Created K8s manifests" | tee -a "$LOG_FILE"
}

# Generate environment templates
generate_env_templates() {
    echo -e "${GREEN}Generating environment templates${NC}" | tee -a "$LOG_FILE"

    # Development environment
    cat > "$OUTPUT_DIR/configs/.env.development" << 'EOF'
# Development Environment Variables
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/appdb_dev

# Redis
REDIS_URL=redis://localhost:6379

# API
API_PORT=8000
API_HOST=0.0.0.0

# Frontend
FRONTEND_URL=http://localhost:3000

# Security
JWT_SECRET=dev-secret-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF

    # Production environment template
    cat > "$OUTPUT_DIR/configs/.env.production" << 'EOF'
# Production Environment Variables
NODE_ENV=production
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_URL=${DATABASE_URL}

# Redis
REDIS_URL=${REDIS_URL}

# API
API_PORT=8000
API_HOST=0.0.0.0

# Frontend
FRONTEND_URL=${FRONTEND_URL}

# Security
JWT_SECRET=${JWT_SECRET}
CORS_ORIGINS=${CORS_ORIGINS}

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
EOF

    echo -e "  ${GREEN}✓${NC} Created environment templates" | tee -a "$LOG_FILE"
}

# Generate deployment scripts
generate_deployment_scripts() {
    echo -e "${GREEN}Generating deployment scripts${NC}" | tee -a "$LOG_FILE"

    # Deploy script
    cat > "$OUTPUT_DIR/scripts/deploy.sh" << 'EOF'
#!/bin/bash

# Deployment script
set -e

echo "🚀 Starting deployment..."

# Build Docker images
echo "📦 Building Docker images..."
docker-compose -f deployment/docker/docker-compose.yml build

# Run migrations
echo "🔄 Running database migrations..."
docker-compose -f deployment/docker/docker-compose.yml run --rm backend python manage.py migrate

# Start services
echo "▶️ Starting services..."
docker-compose -f deployment/docker/docker-compose.yml up -d

# Health check
echo "🏥 Checking health..."
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment complete!"
EOF
    chmod +x "$OUTPUT_DIR/scripts/deploy.sh"

    # Health check script
    cat > "$OUTPUT_DIR/scripts/health-check.sh" << 'EOF'
#!/bin/bash

# Health check script
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

check_service() {
    local url=$1
    local name=$2

    if curl -f -s "$url/health" > /dev/null; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name is unhealthy"
        return 1
    fi
}

echo "🏥 Running health checks..."

check_service "$BACKEND_URL" "Backend"
BACKEND_STATUS=$?

check_service "$FRONTEND_URL" "Frontend"
FRONTEND_STATUS=$?

if [[ $BACKEND_STATUS -eq 0 ]] && [[ $FRONTEND_STATUS -eq 0 ]]; then
    echo "✅ All services healthy!"
    exit 0
else
    echo "❌ Some services unhealthy!"
    exit 1
fi
EOF
    chmod +x "$OUTPUT_DIR/scripts/health-check.sh"

    echo -e "  ${GREEN}✓${NC} Created deployment scripts" | tee -a "$LOG_FILE"
}

# Main execution
echo -e "${BLUE}Detecting technology stack...${NC}" | tee -a "$LOG_FILE"
STACK=$(detect_stack)
echo -e "Detected stack: ${YELLOW}$STACK${NC}" | tee -a "$LOG_FILE"

# Parse stack info
IFS=':' read -r stack_type backend frontend database platform services auth <<< "$STACK"

# Generate artifacts based on stack
generate_dockerfile "$STACK"
generate_docker_compose "$STACK"
generate_k8s_manifests
generate_env_templates
generate_deployment_scripts

# Generate platform-specific configs if detected
if [[ -n "$platform" ]] && [[ "$platform" != "none" ]]; then
    generate_platform_configs "$platform"
fi

# Generate .dockerignore
cat > "$OUTPUT_DIR/docker/.dockerignore" << 'EOF'
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
*.cover
*.log
.pytest_cache/

# Node
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# IDE
.idea
.vscode
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.*
!.env.example

# Tests
tests/
test/
*.test.js
*.test.py

# Documentation
*.md
docs/
EOF

echo -e "  ${GREEN}✓${NC} Created .dockerignore" | tee -a "$LOG_FILE"

# Save session memory
MEMORY_FILE="$MEMORY_DIR/$SESSION_ID.json"
cat > "$MEMORY_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "timestamp": "$(date -Iseconds)",
  "spec_dir": "$SPEC_DIR",
  "output_dir": "$OUTPUT_DIR",
  "detected_stack": "$STACK",
  "files_generated": $(find "$OUTPUT_DIR" -type f 2>/dev/null | wc -l || echo 0)
}
EOF

# Summary
echo "" | tee -a "$LOG_FILE"
echo -e "${GREEN}=== Deployment Generation Complete ===${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Stack: $STACK${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Files generated: $(find $OUTPUT_DIR -type f | wc -l)${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Output: $OUTPUT_DIR/${NC}" | tee -a "$LOG_FILE"
echo -e "${GREEN}Session log: $LOG_FILE${NC}" | tee -a "$LOG_FILE"