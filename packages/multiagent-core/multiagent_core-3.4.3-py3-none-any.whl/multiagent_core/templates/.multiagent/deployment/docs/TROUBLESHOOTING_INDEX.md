# Deployment Troubleshooting Guide

Quick reference for common deployment issues across platforms.

## By Platform

### ☁️ Cloud Providers
- [DigitalOcean Droplet Issues](troubleshooting/digitalocean-droplet.md) - Firewall, callbacks, networking
- [AWS Issues](troubleshooting/aws-common-issues.md) - EB, ECS, Lambda issues
- Vercel - Usually "just works", check build logs
- Heroku - Check `heroku logs --tail`

### 🐳 Container Platforms
- [Docker Issues](troubleshooting/docker-common-issues.md) - Build, run, networking
- [Kubernetes Issues](troubleshooting/kubernetes-common-issues.md) - Pods, services, storage

## By Problem Type

### 🔥 "App Won't Start"
1. Check logs first
2. Verify environment variables
3. Check port binding (0.0.0.0 not localhost)
4. Verify health checks

### 🚫 "Can't Connect"
1. **Firewall** - Most common culprit
2. **Port binding** - Use 0.0.0.0
3. **Network/Security Groups** - Cloud provider settings
4. **DNS** - If using domain names

### 💾 "Database Connection Failed"
1. Connection string format
2. Network access (same VPC/network?)
3. Firewall rules
4. Credentials/environment variables

### 📦 "Build/Deploy Fails"
1. Check build logs
2. Verify Dockerfile/configs
3. Resource limits (memory/disk)
4. Dependencies/versions

### 🐌 "Performance Issues"
1. Resource limits too low
2. Cold starts (serverless)
3. Database connection pooling
4. Caching not configured

## Universal Debug Commands

```bash
# Check if app is running
ps aux | grep your-app
systemctl status your-app
docker ps

# Check ports
netstat -tlnp | grep 8000
lsof -i :8000

# Check logs
journalctl -u your-app -f
docker logs container-name -f
kubectl logs pod-name -f

# Test connectivity
curl http://localhost:8000/health
nc -zv hostname 8000

# Resource usage
htop
docker stats
kubectl top pods
```

## Quick Fix Checklist

- [ ] **Firewall** - Allow your ports
- [ ] **Bind address** - Use 0.0.0.0 not localhost
- [ ] **Environment variables** - All loaded?
- [ ] **Health checks** - Endpoint responding?
- [ ] **Logs** - Any error messages?
- [ ] **Resources** - Enough memory/CPU?
- [ ] **Network** - Same network/VPC?
- [ ] **Secrets** - Properly configured?
- [ ] **DNS** - Resolving correctly?
- [ ] **SSL/HTTPS** - Certificate valid?

## Emergency Recovery

### "Nothing works, need it up NOW"

1. **Simplify** - Remove everything except core
2. **Local test** - Does it work on your machine?
3. **Basic HTTP server** - Can you reach the server at all?
4. **Disable security temporarily** - Firewall/auth off (careful!)
5. **Use proven config** - Copy from working example
6. **Fresh start** - Sometimes easier than debugging

## Platform-Specific Quick Start

### DigitalOcean
```bash
ufw allow 8000/tcp
systemctl restart your-app
```

### AWS EB
```bash
eb logs
eb deploy --timeout 30
```

### Docker
```bash
docker-compose down -v
docker-compose up --build
```

### Kubernetes
```bash
kubectl rollout restart deployment/app
kubectl describe pod $(kubectl get pods | grep app | head -1 | awk '{print $1}')
```

## Still Stuck?

1. **Check platform status** - Is the service down?
2. **Search error message** - Exact error in quotes
3. **Minimal reproduction** - Simplest case that fails
4. **Platform support** - They've seen it before
5. **Community forums** - Stack Overflow, Reddit

Remember: It's almost always one of:
- 🔥 Firewall
- 🔌 Wrong port/host binding
- 🔑 Missing environment variable
- 💰 Resource limits