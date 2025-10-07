#!/bin/bash

# Local Deployment Runner - Starts and monitors local deployment
# Usage: ./run-local-deployment.sh [up|down|restart|logs|status]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMMAND="${1:-up}"
DEPLOYMENT_DIR="deployment/docker"

# Functions
check_docker() {
    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker is not running!${NC}"
        echo "Please start Docker and try again."
        exit 1
    fi
}

setup_env() {
    # Copy env file if it doesn't exist
    if [[ ! -f ".env" ]] && [[ -f "deployment/configs/.env.development" ]]; then
        echo -e "${YELLOW}Copying .env.development to .env${NC}"
        cp deployment/configs/.env.development .env
    fi

    # Generate secrets if needed
    if grep -q "change-this\|generate-this" .env 2>/dev/null; then
        echo -e "${YELLOW}Generating secure secrets...${NC}"
        JWT_SECRET=$(openssl rand -base64 32)
        SESSION_SECRET=$(openssl rand -base64 32)

        # Update .env with generated secrets
        sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
        sed -i.bak "s/SESSION_SECRET=.*/SESSION_SECRET=$SESSION_SECRET/" .env
        echo -e "${GREEN}✓ Secrets generated${NC}"
    fi
}

start_deployment() {
    echo -e "${BLUE}=== Starting Local Deployment ===${NC}"
    echo ""

    check_docker
    setup_env

    cd "$DEPLOYMENT_DIR"

    echo -e "${YELLOW}Building images...${NC}"
    docker-compose build

    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d

    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 10

    # Check service health
    echo ""
    echo -e "${BLUE}Checking service health...${NC}"

    # Backend health check
    if curl -f -s http://localhost:8000/health &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Backend is healthy"
    else
        echo -e "  ${RED}✗${NC} Backend not responding"
        echo "  Check logs: docker-compose logs backend"
    fi

    # Frontend check
    if curl -f -s http://localhost:3000 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Frontend is running"
    else
        echo -e "  ${YELLOW}⚠${NC} Frontend not responding (may still be building)"
    fi

    # Database check
    if docker-compose exec -T db psql -U postgres -c "SELECT 1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Database is running"
    else
        echo -e "  ${RED}✗${NC} Database not ready"
    fi

    # Redis check
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Redis is running"
    else
        echo -e "  ${YELLOW}⚠${NC} Redis not responding"
    fi

    echo ""
    echo -e "${GREEN}=== Deployment Started ===${NC}"
    echo ""
    echo "Access points:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    $0 logs"
    echo "  Check status: $0 status"
    echo "  Stop all:     $0 down"
    echo "  Restart:      $0 restart"
}

stop_deployment() {
    echo -e "${BLUE}=== Stopping Deployment ===${NC}"

    cd "$DEPLOYMENT_DIR"
    docker-compose down

    echo -e "${GREEN}✓ All services stopped${NC}"
}

restart_deployment() {
    echo -e "${BLUE}=== Restarting Deployment ===${NC}"
    stop_deployment
    sleep 2
    start_deployment
}

show_logs() {
    cd "$DEPLOYMENT_DIR"

    if [[ -n "$2" ]]; then
        # Show logs for specific service
        docker-compose logs -f --tail=100 "$2"
    else
        # Show all logs
        docker-compose logs -f --tail=50
    fi
}

show_status() {
    echo -e "${BLUE}=== Deployment Status ===${NC}"
    echo ""

    cd "$DEPLOYMENT_DIR"

    # Show running containers
    echo -e "${YELLOW}Running services:${NC}"
    docker-compose ps

    echo ""
    echo -e "${YELLOW}Service health:${NC}"

    # Check each service
    services=("backend" "frontend" "db" "redis")
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "${service}.*Up"; then
            echo -e "  ${GREEN}✓${NC} $service is running"
        else
            echo -e "  ${RED}✗${NC} $service is not running"
        fi
    done

    echo ""
    echo -e "${YELLOW}Port usage:${NC}"
    for port in 8000 3000 5432 6379; do
        if lsof -i :$port &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} Port $port is in use"
        else
            echo -e "  ${YELLOW}○${NC} Port $port is free"
        fi
    done
}

# Main command switch
case "$COMMAND" in
    up|start)
        start_deployment
        ;;
    down|stop)
        stop_deployment
        ;;
    restart)
        restart_deployment
        ;;
    logs)
        show_logs "$@"
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 [up|down|restart|logs|status]"
        echo ""
        echo "Commands:"
        echo "  up/start  - Start all services"
        echo "  down/stop - Stop all services"
        echo "  restart   - Restart all services"
        echo "  logs      - Show logs (optionally specify service)"
        echo "  status    - Show deployment status"
        exit 1
        ;;
esac