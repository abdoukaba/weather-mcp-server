# Weather MCP Server - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.10+ OR Docker
- Internet connection

---

## Option 1: Docker (Recommended)

### 1. Start the Server
```bash
docker-compose up -d
```

### 2. Verify It's Running
```bash
curl http://localhost:3000/health
```

Expected output:
```json
{"status":"healthy","service":"weather-mcp-server","version":"1.0.0"}
```

### 3. Test Weather Query
The server is now running on port 3000!

---

## Option 2: Python (Local Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
# For Claude Desktop (STDIO mode)
python server.py --stdio

# For HTTP API
python server.py --http
```

---

## Using with Claude Desktop

### 1. Find Your Config File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Add This Configuration

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/weather_mcp_server/server.py",
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

**Important:** Replace `/ABSOLUTE/PATH/TO/` with the actual path!

### 3. Restart Claude Desktop

### 4. Test It
Open Claude and ask:
```
"What's the weather in London?"
```

Claude will use your weather server to respond!

---

## Available Tools

### 🌡️ Current Weather
```
get_current_weather(city: "london")
```
Returns: Temperature, conditions, humidity, wind

### 📅 Forecast
```
get_forecast(city: "paris", days: 7)
```
Returns: Multi-day forecast with detailed conditions

### ⚠️ Weather Alerts
```
get_weather_alerts(city: "miami")
```
Returns: Active weather warnings and advisories

---

## Supported Cities (26 Total)

**North America:** new_york, los_angeles, chicago, san_francisco, toronto, vancouver, mexico_city

**Europe:** london, paris, berlin, madrid, rome, amsterdam

**Asia:** tokyo, beijing, shanghai, singapore, seoul, mumbai, dubai

**Oceania:** sydney, melbourne, auckland

**South America:** sao_paulo, buenos_aires, rio_de_janeiro

**Africa:** cairo, cape_town

---

## Common Commands

### Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

### Python
```bash
# Run tests
pytest tests/ -v

# Check health (HTTP mode only)
curl http://localhost:3000/health

# View logs
python server.py --http 2>&1 | tail -f
```

---

## Troubleshooting

### ❌ "Port 3000 already in use"
```bash
# Find what's using port 3000
lsof -i :3000

# Change port
export MCP_PORT=3001
docker-compose up -d
```

### ❌ "City not supported"
Check the list of supported cities above. Use lowercase with underscores:
- ✅ `new_york`
- ❌ `New York`

### ❌ Claude Desktop not finding server
1. Check that you used the **absolute path** in config
2. Verify Python is in PATH: `which python`
3. Test manually: `python server.py --stdio`

### ❌ Docker health check failing
```bash
# Check logs
docker logs weather-mcp-server

# Restart
docker-compose restart
```

---

## Next Steps

📖 **Full Documentation:** See `README.md`
🏗️ **Architecture:** See `ARCHITECTURE.md`
🚀 **Deployment:** See `DEPLOYMENT_GUIDE.md`

---

## Need Help?

1. Check troubleshooting section above
2. Review full README.md
3. Check Open-Meteo API status: https://open-meteo.com

---

## Example Usage

Once configured with Claude Desktop:

**You:** "What's the weather in Tokyo right now?"

**Claude:** *Uses get_current_weather("tokyo")* 
"In Tokyo, it's currently 18°C (64°F) with partly cloudy skies. Humidity is at 65%, and there's a light wind from the northwest at 12 km/h."

**You:** "Give me a 5-day forecast for Paris"

**Claude:** *Uses get_forecast("paris", days=5)*
"Here's your 5-day forecast for Paris..."

---

## Quick Reference

| Task | Command |
|------|---------|
| Start (Docker) | `docker-compose up -d` |
| Start (Python HTTP) | `python server.py --http` |
| Start (Python STDIO) | `python server.py --stdio` |
| Check health | `curl localhost:3000/health` |
| View logs | `docker-compose logs -f` |
| Run tests | `pytest tests/ -v` |
| Stop | `docker-compose down` |

---

**Congratulations! Your Weather MCP Server is ready to use! 🎉**
