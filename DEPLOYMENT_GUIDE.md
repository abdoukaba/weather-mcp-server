# Weather MCP Server - Complete Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Claude Desktop Integration](#claude-desktop-integration)
5. [Production Deployment](#production-deployment)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows (with WSL2 for Docker)
- **Python**: 3.10 or higher
- **RAM**: 256MB minimum, 512MB recommended
- **Network**: Internet access for Open-Meteo API

### For Docker Deployment
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher

---

## Local Development Setup

### 1. Clone or Extract the Project

```bash
cd /path/to/weather_mcp_server
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test imports
python -c "from weather_mcp import server; print('✓ Installation successful')"
```

### 4. Run in STDIO Mode (for Claude Desktop)

```bash
python server.py --stdio
```

### 5. Run in HTTP Mode (for API access)

```bash
python server.py --http
```

The server will start on `http://0.0.0.0:3000/mcp`

---

## Docker Deployment

### Quick Start

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f weather-mcp

# Stop
docker-compose down
```

### Step-by-Step Docker Setup

#### 1. Build the Image

```bash
docker build -t weather-mcp-server:latest .
```

Expected output:
```
[+] Building 45.2s (14/14) FINISHED
Successfully built weather-mcp-server:latest
```

#### 2. Run Container (Manual)

```bash
docker run -d \
  --name weather-mcp \
  -p 3000:3000 \
  --restart unless-stopped \
  --health-cmd "curl -f http://localhost:3000/health || exit 1" \
  --health-interval 30s \
  weather-mcp-server:latest
```

#### 3. Check Health

```bash
# Wait for healthy status
docker ps

# Should show: "(healthy)" in STATUS column
```

#### 4. Test the Server

```bash
# Check health endpoint
curl http://localhost:3000/health

# Expected response:
# {"status":"healthy","service":"weather-mcp-server","version":"1.0.0",...}
```

### Using Docker Compose (Recommended)

#### 1. Review Configuration

Edit `docker-compose.yml` if needed:
- Port mapping (default: 3000)
- Resource limits (CPU, memory)
- Environment variables

#### 2. Start Services

```bash
# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Start with production profile (includes Nginx)
docker-compose --profile production up -d
```

#### 3. Monitor

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Check resource usage
docker stats weather-mcp-server
```

#### 4. Update and Restart

```bash
# Pull changes and rebuild
docker-compose build --no-cache

# Restart services
docker-compose restart

# Or rebuild and restart
docker-compose up -d --build
```

---

## Claude Desktop Integration

### For macOS

1. **Locate Config File**:
   ```bash
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Edit Configuration**:
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "python",
         "args": [
           "/absolute/path/to/weather_mcp_server/server.py",
           "--stdio"
         ],
         "env": {
           "MCP_TRANSPORT": "stdio",
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### For Windows

1. **Locate Config File**:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Edit Configuration**:
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "python",
         "args": [
           "C:\\path\\to\\weather_mcp_server\\server.py",
           "--stdio"
         ],
         "env": {
           "MCP_TRANSPORT": "stdio",
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### For Linux

1. **Locate Config File**:
   ```bash
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Follow macOS instructions above**

### Verification

1. Open Claude Desktop
2. Start a new conversation
3. Type: "What's the weather in London?"
4. Claude should use the weather MCP server to respond

---

## Production Deployment

### Option 1: Docker with Systemd

1. **Create systemd service file**: `/etc/systemd/system/weather-mcp.service`

```ini
[Unit]
Description=Weather MCP Server
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/weather_mcp_server
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:
```bash
sudo systemctl enable weather-mcp
sudo systemctl start weather-mcp
sudo systemctl status weather-mcp
```

### Option 2: Docker with Auto-Restart

Already configured in `docker-compose.yml`:
```yaml
restart: unless-stopped
```

### Option 3: Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: weather-mcp
  template:
    metadata:
      labels:
        app: weather-mcp
    spec:
      containers:
      - name: weather-mcp
        image: weather-mcp-server:latest
        ports:
        - containerPort: 3000
        resources:
          limits:
            memory: "512Mi"
            cpu: "1000m"
          requests:
            memory: "128Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: weather-mcp-service
spec:
  selector:
    app: weather-mcp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

### Monitoring Setup

#### Prometheus Metrics (Optional Enhancement)

Add to `docker-compose.yml`:
```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

#### Log Aggregation

Logs are JSON formatted. Use with ELK stack, Splunk, or DataDog:

```bash
# Forward to centralized logging
docker logs weather-mcp-server | your-log-forwarder
```

---

## Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=weather_mcp --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
# Start server in HTTP mode
python server.py --http &
SERVER_PID=$!

# Test endpoints
curl http://localhost:3000/health

# Cleanup
kill $SERVER_PID
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:3000/health

# Expected: 0% failed requests
```

### Docker Health Check

```bash
# Manual health check
docker exec weather-mcp-server curl -f http://localhost:3000/health

# Should return: {"status":"healthy",...}
```

---

## Troubleshooting

### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Port Already in Use

**Symptoms**: `Error: bind: address already in use`

**Solution**:
```bash
# Find process using port 3000
lsof -i :3000

# Kill process or change port
export MCP_PORT=3001
docker-compose up -d
```

### Issue: Health Check Failing

**Symptoms**: Container status shows `(unhealthy)`

**Solutions**:
1. Check logs: `docker logs weather-mcp-server`
2. Verify port access: `netstat -tlnp | grep 3000`
3. Test manually: `curl http://localhost:3000/health`
4. Restart: `docker-compose restart`

### Issue: API Timeouts

**Symptoms**: Requests timeout or return 504

**Solutions**:
1. Check Open-Meteo API status: https://open-meteo.com
2. Verify network connectivity
3. Increase timeout in `weather_mcp/api.py`:
   ```python
   async with httpx.AsyncClient(timeout=60.0) as client:
   ```

### Issue: Claude Desktop Not Finding Server

**Symptoms**: Tools not available in Claude

**Solutions**:
1. Verify absolute path in config
2. Check Python in PATH: `which python`
3. Test server manually: `python server.py --stdio`
4. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### Issue: Docker Build Fails

**Symptoms**: Build errors during `docker build`

**Solutions**:
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker build --no-cache -t weather-mcp-server:latest .

# Check disk space
df -h
```

### Issue: Memory Issues

**Symptoms**: Container killed or OOM errors

**Solutions**:
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M
```

### Issue: Network Restrictions

**Symptoms**: Cannot access Open-Meteo API

**Solutions**:
1. Check firewall rules
2. Verify DNS resolution: `nslookup api.open-meteo.com`
3. Test with curl: `curl https://api.open-meteo.com/v1/forecast?latitude=51&longitude=0&current=temperature_2m`
4. Configure proxy if needed

---

## Performance Optimization

### 1. Enable Response Caching

Add Redis for caching (optional):

```yaml
# Add to docker-compose.yml
  redis:
    image: redis:alpine
    networks:
      - weather-network
```

### 2. Horizontal Scaling

```bash
# Scale to 3 instances
docker-compose up -d --scale weather-mcp=3
```

### 3. Load Balancing

Use Nginx (already configured) or HAProxy:

```bash
# Start with production profile
docker-compose --profile production up -d
```

---

## Security Checklist

- [ ] Running as non-root user (✓ configured)
- [ ] Read-only filesystem (✓ configured)
- [ ] Resource limits set (✓ configured)
- [ ] Security updates applied (✓ in Dockerfile)
- [ ] HTTPS enabled (configure in nginx.conf)
- [ ] Rate limiting active (✓ in nginx.conf)
- [ ] Logs being monitored
- [ ] Health checks configured (✓)
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented

---

## Maintenance

### Regular Tasks

**Daily**:
- Check health status
- Review error logs

**Weekly**:
- Review resource usage
- Check for security updates

**Monthly**:
- Update dependencies
- Review and rotate logs
- Performance testing

### Backup

```bash
# Backup configuration
tar -czf weather-mcp-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  nginx.conf

# Backup database (if added later)
docker exec weather-mcp-server pg_dump -U user db > backup.sql
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:3000/health
```

---

## Support Resources

- **Open-Meteo API Docs**: https://open-meteo.com/en/docs
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **Docker Documentation**: https://docs.docker.com
- **MCP Specification**: https://modelcontextprotocol.io

---

## Quick Reference Commands

```bash
# Development
make install          # Install dependencies
make test            # Run tests
make run-stdio       # Run with STDIO
make run-http        # Run with HTTP

# Docker
make docker-build    # Build image
make docker-run      # Start containers
make docker-stop     # Stop containers
make docker-logs     # View logs

# Health Check
curl http://localhost:3000/health

# View Logs
docker logs -f weather-mcp-server

# Restart
docker-compose restart

# Clean Up
make clean
make docker-clean
```
