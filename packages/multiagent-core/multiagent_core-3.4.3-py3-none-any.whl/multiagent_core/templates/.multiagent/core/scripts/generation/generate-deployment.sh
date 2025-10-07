#!/bin/bash

# Generate Deployment Script
# Purpose: Create deployment configurations based on spec
# Invoked at: /deploy-prepare (called from /project-setup Step 7)
# Usage: ./generate-deployment.sh <spec-dir>

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SPEC_DIR="${1:-specs/001-*}"
DEPLOYMENT_DIR="deployment"

# Find spec directory
if [[ "$SPEC_DIR" == *"*"* ]]; then
    SPEC_DIR=$(find . -type d -path "./specs/001-*" | head -1)
fi

if [ ! -d "$SPEC_DIR" ]; then
    echo "Error: Spec directory not found: $SPEC_DIR"
    exit 1
fi

echo -e "${BLUE}=== Generating Deployment Configurations ===${NC}"
echo -e "${BLUE}Spec: $SPEC_DIR${NC}"
echo ""

# Create deployment directory structure
create_deployment_structure() {
    echo -e "${YELLOW}Creating deployment directory structure...${NC}"

    mkdir -p "$DEPLOYMENT_DIR/docker"
    mkdir -p "$DEPLOYMENT_DIR/k8s"
    mkdir -p "$DEPLOYMENT_DIR/configs"
    mkdir -p "$DEPLOYMENT_DIR/scripts"

    echo -e "${GREEN}✓${NC} Created deployment directory structure"
}

# Detect deployment target from spec
detect_deployment_target() {
    local target="docker"  # Default

    if [ -f "$SPEC_DIR/spec.md" ]; then
        if grep -qi "vercel" "$SPEC_DIR/spec.md"; then
            target="vercel"
        elif grep -qi "aws\|lambda" "$SPEC_DIR/spec.md"; then
            target="aws"
        elif grep -qi "kubernetes\|k8s" "$SPEC_DIR/spec.md"; then
            target="kubernetes"
        fi
    fi

    echo "$target"
}

# Generate Docker configuration
generate_docker_config() {
    echo -e "${YELLOW}Generating Docker configuration...${NC}"

    # Create Dockerfile
    cat > "$DEPLOYMENT_DIR/docker/Dockerfile" << 'EOF'
# Multi-stage build for production
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build || echo "No build step"

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy from builder
COPY --from=builder /app .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Start application
CMD ["node", "src/index.js"]
EOF

    # Create docker-compose.yml
    cat > "$DEPLOYMENT_DIR/docker/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    env_file:
      - ../configs/production.env
    restart: unless-stopped
    networks:
      - app-network

  # Add database service if needed
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: myapp
  #     POSTGRES_USER: myuser
  #     POSTGRES_PASSWORD: mypassword
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   networks:
  #     - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
EOF

    echo -e "${GREEN}✓${NC} Created Docker configuration"
}

# Generate Kubernetes configuration
generate_k8s_config() {
    echo -e "${YELLOW}Generating Kubernetes configuration...${NC}"

    # Create deployment.yaml
    cat > "$DEPLOYMENT_DIR/k8s/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    app: multiagent-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multiagent-app
  template:
    metadata:
      labels:
        app: multiagent-app
    spec:
      containers:
      - name: app
        image: multiagent-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

    # Create service.yaml
    cat > "$DEPLOYMENT_DIR/k8s/service.yaml" << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: multiagent-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
EOF

    # Create configmap.yaml
    cat > "$DEPLOYMENT_DIR/k8s/configmap.yaml" << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  API_VERSION: "v1"
EOF

    echo -e "${GREEN}✓${NC} Created Kubernetes configuration"
}

# Generate Vercel configuration
generate_vercel_config() {
    echo -e "${YELLOW}Generating Vercel configuration...${NC}"

    # Create vercel.json
    cat > "vercel.json" << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "src/index.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/src/index.js"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
EOF

    echo -e "${GREEN}✓${NC} Created vercel.json"
}

# Generate environment configs
generate_env_configs() {
    echo -e "${YELLOW}Generating environment configurations...${NC}"

    # Production environment
    cat > "$DEPLOYMENT_DIR/configs/production.env" << 'EOF'
# Production Environment Configuration
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

# Add production-specific values
# DATABASE_URL=
# REDIS_URL=
# API_KEY=
EOF

    # Staging environment
    cat > "$DEPLOYMENT_DIR/configs/staging.env" << 'EOF'
# Staging Environment Configuration
NODE_ENV=staging
PORT=3000
LOG_LEVEL=debug

# Add staging-specific values
# DATABASE_URL=
# REDIS_URL=
# API_KEY=
EOF

    echo -e "${GREEN}✓${NC} Created environment configurations"
}

# Generate deployment scripts
generate_deploy_scripts() {
    echo -e "${YELLOW}Generating deployment scripts...${NC}"

    # Deploy script
    cat > "$DEPLOYMENT_DIR/scripts/deploy.sh" << 'EOF'
#!/bin/bash

# Deployment Script
set -e

echo "Starting deployment..."

# Load environment
ENV="${1:-production}"
source "deployment/configs/${ENV}.env"

# Build and deploy based on target
if [ -f "vercel.json" ]; then
    echo "Deploying to Vercel..."
    vercel --prod
elif [ -f "deployment/docker/docker-compose.yml" ]; then
    echo "Deploying with Docker..."
    docker-compose -f deployment/docker/docker-compose.yml up -d
else
    echo "No deployment target configured"
    exit 1
fi

echo "Deployment complete!"
EOF

    # Rollback script
    cat > "$DEPLOYMENT_DIR/scripts/rollback.sh" << 'EOF'
#!/bin/bash

# Rollback Script
set -e

echo "Starting rollback..."

# Implement rollback logic based on deployment target
if [ -f "vercel.json" ]; then
    echo "Rolling back Vercel deployment..."
    # vercel rollback command
elif [ -f "deployment/docker/docker-compose.yml" ]; then
    echo "Rolling back Docker deployment..."
    docker-compose -f deployment/docker/docker-compose.yml down
    # Restore previous version
fi

echo "Rollback complete!"
EOF

    chmod +x "$DEPLOYMENT_DIR/scripts/deploy.sh"
    chmod +x "$DEPLOYMENT_DIR/scripts/rollback.sh"

    echo -e "${GREEN}✓${NC} Created deployment scripts"
}

# Main execution
main() {
    local deployment_target=$(detect_deployment_target)

    echo -e "${BLUE}Detected deployment target: $deployment_target${NC}"
    echo ""

    # Create structure
    create_deployment_structure

    # Generate configurations based on target
    case "$deployment_target" in
        vercel)
            generate_vercel_config
            generate_env_configs
            ;;
        kubernetes)
            generate_k8s_config
            generate_docker_config
            generate_env_configs
            ;;
        aws)
            generate_docker_config
            generate_env_configs
            # AWS-specific configs would go here
            ;;
        *)
            generate_docker_config
            generate_env_configs
            ;;
    esac

    # Always generate deployment scripts
    generate_deploy_scripts

    echo ""
    echo -e "${GREEN}=== Deployment Configuration Complete ===${NC}"
    echo -e "${GREEN}Generated configurations in $DEPLOYMENT_DIR/${NC}"
    echo ""
    echo -e "${BLUE}Files created:${NC}"
    find "$DEPLOYMENT_DIR" -type f -exec basename {} \; | sort | uniq | sed 's/^/  /'
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review generated configurations"
    echo "2. Update environment variables in deployment/configs/"
    echo "3. Test deployment locally with deployment/scripts/deploy.sh"
}

main "$@"