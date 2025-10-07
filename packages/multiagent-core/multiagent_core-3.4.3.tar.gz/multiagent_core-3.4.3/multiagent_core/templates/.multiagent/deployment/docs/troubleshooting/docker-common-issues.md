# Docker Deployment Common Issues

## Container Won't Start

### Issue: "Cannot connect to the Docker daemon"
```bash
# Start Docker service
sudo systemctl start docker
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "Port already in use"
```bash
# Find what's using the port
sudo lsof -i :8000
sudo netstat -tlnp | grep 8000

# Kill the process
sudo kill -9 <PID>

# Or change port in docker-compose
ports:
  - "8001:8000"  # Use different external port
```

## Build Issues

### Issue: "No space left on device"
```bash
# Clean up Docker
docker system prune -a
docker volume prune
docker image prune -a

# Check disk space
df -h
```

### Issue: Build takes forever
```dockerfile
# Use .dockerignore
node_modules
.git
*.log
__pycache__
.pytest_cache
venv/
.env

# Use build cache effectively
# Copy dependency files first
COPY requirements.txt .
RUN pip install -r requirements.txt
# Then copy code (changes more often)
COPY . .
```

## Networking Issues

### Issue: Container can't reach database
```yaml
# Ensure on same network
services:
  app:
    networks:
      - mynet
  db:
    networks:
      - mynet

networks:
  mynet:
    driver: bridge
```

### Issue: Can't access from host
```yaml
# Bind to 0.0.0.0 not localhost inside container
command: uvicorn main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

### Issue: Env vars not loading
```yaml
# docker-compose.yml
services:
  app:
    env_file:
      - .env
    # OR explicitly
    environment:
      - DATABASE_URL=${DATABASE_URL}
```

### Issue: Different envs for dev/prod
```bash
# Use different compose files
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Performance Issues

### Issue: Container using too much memory
```yaml
# Set resource limits
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Issue: Slow builds on M1 Mac
```dockerfile
# Specify platform
FROM --platform=linux/amd64 python:3.11
```

## Debugging Containers

### Quick debugging commands
```bash
# Execute commands in running container
docker exec -it container_name bash
docker exec container_name ps aux

# View logs
docker logs -f container_name --tail 100

# Inspect container
docker inspect container_name

# Copy files from container
docker cp container_name:/app/logs ./local-logs

# Run with debugging
docker run -it --rm --entrypoint bash image_name
```

## Docker Compose Issues

### Issue: "Version in docker-compose.yml is unsupported"
```yaml
# Use version 3.8 for most compatibility
version: '3.8'
```

### Issue: Changes not reflecting
```bash
# Force rebuild
docker-compose up --build --force-recreate

# Or completely clean start
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```