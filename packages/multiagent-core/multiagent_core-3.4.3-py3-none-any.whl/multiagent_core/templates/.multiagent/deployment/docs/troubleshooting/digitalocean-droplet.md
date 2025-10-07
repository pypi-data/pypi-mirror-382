# DigitalOcean Droplet Callback Server Troubleshooting

## Common Issues & Quick Fixes

### 1. **Firewall Blocking Incoming Connections** (Most Common!)
```bash
# Check UFW firewall status
sudo ufw status

# Allow your callback port (e.g., 8000)
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# Or temporarily disable to test
sudo ufw disable  # CAREFUL - only for testing!
```

### 2. **Server Binding to localhost Instead of 0.0.0.0**
```python
# WRONG - only accessible locally
uvicorn main:app --host localhost --port 8000

# CORRECT - accessible from outside
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. **DigitalOcean Cloud Firewall** (Often Missed!)
- Go to DigitalOcean Dashboard → Networking → Firewalls
- Check if droplet has a cloud firewall attached
- Add inbound rule for your port:
  - Type: Custom
  - Protocol: TCP
  - Port: 8000 (or your callback port)
  - Sources: 0.0.0.0/0

### 4. **Nginx Proxy Configuration** (If Using Nginx)
```nginx
server {
    listen 80;
    server_name your-droplet-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # For webhooks/callbacks
    location /webhook {
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_buffering off;  # Important for real-time callbacks
    }
}
```

### 5. **Environment Variables Not Set**
```bash
# Check if .env is loaded
export $(cat .env | xargs)

# Or use systemd service file
[Service]
EnvironmentFile=/home/user/app/.env
```

## Quick Debug Commands

```bash
# 1. Check if your app is running
ps aux | grep python
ps aux | grep uvicorn

# 2. Check if port is listening
sudo netstat -tlnp | grep 8000
sudo lsof -i :8000

# 3. Test locally first
curl http://localhost:8000/health

# 4. Test from outside
curl http://YOUR_DROPLET_IP:8000/health

# 5. Check logs
journalctl -u your-service -f
tail -f /var/log/nginx/error.log

# 6. Check DNS (if using domain)
dig your-domain.com
nslookup your-domain.com
```

## FastAPI Callback Server Quick Setup

```python
# main.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print(f"Received webhook: {body}")
    return {"received": True}

if __name__ == "__main__":
    # CRITICAL: Use 0.0.0.0 not localhost!
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Systemd Service Setup

```bash
# /etc/systemd/system/callback-server.service
[Unit]
Description=Callback Server
After=network.target

[Service]
Type=exec
User=youruser
WorkingDirectory=/home/youruser/app
Environment="PATH=/home/youruser/venv/bin"
ExecStart=/home/youruser/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable callback-server
sudo systemctl start callback-server
sudo systemctl status callback-server
```

## Docker Alternative (Often Easier!)

```yaml
# docker-compose.yml on droplet
version: '3.8'
services:
  app:
    image: your-app:latest
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    restart: always
```

```bash
# Run with Docker
docker-compose up -d
docker-compose logs -f
```

## Common Webhook/Callback Issues

1. **SSL/HTTPS Required**: Many services (Stripe, GitHub) require HTTPS
   ```bash
   # Use Caddy for automatic SSL
   sudo apt install caddy
   # Edit /etc/caddy/Caddyfile
   your-domain.com {
       reverse_proxy localhost:8000
   }
   ```

2. **Timeout Issues**: Callbacks timing out
   - Increase timeout in nginx: `proxy_read_timeout 300s;`
   - Return 200 immediately, process async

3. **IP Whitelisting**: Some services need IP validation
   - Check if service provides IP ranges to whitelist
   - Disable IP validation in development

## Test Your Callback Endpoint

```bash
# From another machine or locally
curl -X POST http://YOUR_DROPLET_IP:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Should return: {"received": true}
```

## If Nothing Works - Nuclear Option

```bash
# 1. Completely disable firewall (TEMPORARY!)
sudo ufw disable
sudo iptables -F

# 2. Run simple Python server to test
python3 -m http.server 8000 --bind 0.0.0.0

# 3. Try accessing http://DROPLET_IP:8000
# If this doesn't work, it's a DigitalOcean firewall issue

# 4. Re-enable security after testing!
sudo ufw enable
```

## Most Likely Culprits
1. ✅ UFW firewall not configured
2. ✅ Binding to localhost instead of 0.0.0.0
3. ✅ DigitalOcean cloud firewall blocking
4. ✅ No systemd service (app not running)
5. ✅ Wrong environment variables