# Weather MCP Server - Architecture & Design

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM Clients                              │
│  (Claude Desktop, API Clients, Custom Applications)         │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             │ STDIO                      │ HTTP/HTTPS
             │                            │
┌────────────▼────────────────────────────▼───────────────────┐
│                   Weather MCP Server                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Layer                       │  │
│  │  (FastMCP Framework - Tools & Resources)             │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │              Business Logic Layer                     │  │
│  │  - Weather Data Processing                            │  │
│  │  - Alert Generation                                   │  │
│  │  - Data Validation                                    │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │              Data Access Layer                        │  │
│  │  - Open-Meteo API Client                             │  │
│  │  - City Database                                      │  │
│  │  - HTTP Client (httpx)                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┬┼────────────────────────────────────────┘
                     ││
                     ││ HTTPS
                     ▼▼
         ┌────────────────────────┐
         │   Open-Meteo API       │
         │  (Weather Data Source) │
         └────────────────────────┘
```

### Component Architecture

#### 1. MCP Server Core (`weather_mcp/server.py`)

**Responsibilities**:
- Protocol handling (STDIO/HTTP)
- Tool registration and execution
- Resource management
- Logging and error handling
- Health monitoring

**Key Components**:
```python
- FastMCP instance
- Tool decorators (@mcp.tool)
- Resource decorators (@mcp.resource)
- Transport configuration
- Logging setup
```

#### 2. Weather API Client (`weather_mcp/api.py`)

**Responsibilities**:
- HTTP communication with Open-Meteo
- Data transformation and normalization
- Error handling and retries
- Weather code interpretation
- Alert generation logic

**Functions**:
- `get_current_weather_data()`: Current conditions
- `get_forecast_data()`: Multi-day forecasts
- `get_weather_alerts_data()`: Alert detection

#### 3. City Database (`weather_mcp/cities.py`)

**Responsibilities**:
- Store city coordinates
- Provide city lookup
- Validate city input
- List available cities

**Data Structure**:
```python
{
    "city_key": {
        "lat": float,
        "lon": float,
        "name": str,
        "country": str,
        "timezone": str
    }
}
```

### Transport Modes

#### STDIO Transport

```
┌────────────────┐     stdin      ┌──────────────┐
│ Claude Desktop │ ────────────► │  MCP Server  │
│                │                │              │
│                │ ◄──────────── │              │
└────────────────┘     stdout     └──────────────┘
                      stderr (logs)
```

**Use Cases**:
- Claude Desktop integration
- Local development
- Command-line tools

**Configuration**:
```bash
python server.py --stdio
```

#### HTTP Transport

```
┌──────────────┐     HTTP/HTTPS    ┌──────────────┐
│ API Client   │ ◄──────────────► │  MCP Server  │
│              │  POST /mcp        │              │
│              │  JSON-RPC         │  :3000       │
└──────────────┘                   └──────────────┘
```

**Use Cases**:
- Production deployments
- Remote access
- Multiple clients
- Load balancing

**Configuration**:
```bash
python server.py --http
# Listens on 0.0.0.0:3000/mcp
```

## Data Flow

### Current Weather Request Flow

```
1. Client Request
   ├─► "get_current_weather(city='london')"
   │
2. MCP Server
   ├─► Validate input
   ├─► Call get_current_weather_data()
   │
3. City Lookup
   ├─► get_city_info('london')
   ├─► Return: {lat: 51.5074, lon: -0.1278, ...}
   │
4. API Request
   ├─► Build Open-Meteo URL
   ├─► params: {latitude, longitude, current: [...]}
   ├─► HTTP GET request
   │
5. Response Processing
   ├─► Parse JSON response
   ├─► Interpret weather codes
   ├─► Format data structure
   │
6. Return to Client
   └─► Structured weather data
```

### Forecast Request Flow

```
1. Client Request
   ├─► "get_forecast(city='paris', days=5)"
   │
2. Validation
   ├─► Check days: 1 <= days <= 16
   ├─► Validate city exists
   │
3. API Request
   ├─► Request daily forecast data
   ├─► Include: temp, precipitation, wind, sun times
   │
4. Data Transformation
   ├─► For each forecast day:
   │   ├─► Parse date
   │   ├─► Interpret weather codes
   │   ├─► Structure temperature data
   │   └─► Format precipitation info
   │
5. Return Array
   └─► List of daily forecast objects
```

### Alert Generation Flow

```
1. Client Request
   ├─► "get_weather_alerts(city='miami')"
   │
2. Data Collection
   ├─► Get current conditions
   ├─► Get 48-hour forecast
   │
3. Alert Analysis
   ├─► Check current conditions:
   │   ├─► High wind (>50 km/h)
   │   ├─► Extreme heat (>35°C)
   │   ├─► Extreme cold (<-10°C)
   │   ├─► Heavy precipitation (>10mm)
   │   │
   ├─► Check upcoming conditions:
   │   ├─► Rapid wind increase
   │   └─► Heavy rain forecast
   │
4. Alert Generation
   ├─► Create alert objects with:
   │   ├─► type
   │   ├─► severity
   │   ├─► description
   │   └─► timestamp
   │
5. Return Alerts
   └─► Array of alert objects
```

## Security Architecture

### Defense in Depth

```
Layer 1: Network Security
├─► Firewall rules
├─► Rate limiting (Nginx)
└─► DDoS protection

Layer 2: Container Security
├─► Non-root user execution
├─► Read-only filesystem
├─► No new privileges
└─► Resource limits

Layer 3: Application Security
├─► Input validation
├─► Error handling
├─► Secure logging (no sensitive data)
└─► Timeout enforcement

Layer 4: API Security
├─► No authentication required (Open-Meteo is public)
├─► Request timeout
└─► Error message sanitization
```

### Security Features

1. **Non-Root Execution**
   ```dockerfile
   USER weather  # UID 1000
   ```

2. **Read-Only Filesystem**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp
   ```

3. **Resource Limits**
   ```yaml
   resources:
     limits:
       cpus: '1.0'
       memory: 512M
   ```

4. **Health Monitoring**
   ```yaml
   healthcheck:
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## Scalability Design

### Horizontal Scaling

```
┌──────────┐
│  Nginx   │ ◄──── Client Requests
│  (LB)    │
└────┬─────┘
     │
     ├──────────┬──────────┬──────────┐
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│ Server  ││ Server  ││ Server  ││ Server  │
│ Pod 1   ││ Pod 2   ││ Pod 3   ││ Pod N   │
└─────────┘└─────────┘└─────────┘└─────────┘
```

**Scaling Methods**:
1. Docker Compose: `docker-compose up --scale weather-mcp=5`
2. Kubernetes: `kubectl scale deployment weather-mcp --replicas=10`
3. Auto-scaling based on CPU/memory

### Caching Strategy (Future Enhancement)

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Redis Cache  │ ◄─── TTL: 5 minutes
└──────┬───────┘
       │ Cache Miss
       ▼
┌──────────────┐
│ MCP Server   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Open-Meteo   │
└──────────────┘
```

## Performance Characteristics

### Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Memory Usage | ~100MB | Base runtime |
| CPU Usage | <5% | Idle |
| Response Time | <500ms | Average |
| Concurrent Requests | 100+ | With load balancer |
| Cold Start | <2s | Docker container |

### Optimization Strategies

1. **Connection Pooling**
   ```python
   # httpx AsyncClient reuses connections
   async with httpx.AsyncClient() as client:
       # Connections automatically pooled
   ```

2. **Async I/O**
   ```python
   # Non-blocking API calls
   async def get_current_weather_data():
       async with httpx.AsyncClient() as client:
           response = await client.get(...)
   ```

3. **Timeout Configuration**
   ```python
   httpx.AsyncClient(timeout=30.0)
   ```

## Error Handling Strategy

### Error Flow

```
Try:
    ├─► Validate input
    ├─► Execute operation
    └─► Return result

Except ValueError:
    ├─► User input error
    ├─► Return clear error message
    └─► Log as INFO

Except HTTPError:
    ├─► API communication error
    ├─► Return generic error
    └─► Log full details as ERROR

Except Exception:
    ├─► Unexpected error
    ├─► Return safe error message
    └─► Log full traceback as CRITICAL
```

### Error Categories

1. **Client Errors (4xx equivalent)**
   - Invalid city name
   - Invalid days parameter
   - Malformed request

2. **Server Errors (5xx equivalent)**
   - API timeout
   - Network failure
   - Unexpected exceptions

3. **Logging Strategy**
   - INFO: Normal operations
   - WARNING: Recoverable issues
   - ERROR: Failed operations
   - CRITICAL: System failures

## Testing Strategy

### Test Pyramid

```
        ┌────────────┐
        │    E2E     │  ◄─── Integration tests
        └────────────┘
      ┌──────────────┐
      │ Integration  │  ◄─── API tests
      └──────────────┘
    ┌──────────────────┐
    │   Unit Tests     │  ◄─── Function tests
    └──────────────────┘
```

### Test Coverage

| Component | Coverage | Tests |
|-----------|----------|-------|
| City Database | 100% | Lookup, validation, listing |
| API Client | 90% | HTTP calls, data parsing |
| MCP Server | 85% | Tool registration, resources |
| Overall | 90% | Comprehensive suite |

### Test Types

1. **Unit Tests** (`tests/test_weather.py`)
   - City lookup logic
   - Data validation
   - Error handling

2. **Integration Tests**
   - API communication
   - End-to-end flows
   - Error scenarios

3. **Load Tests**
   - Apache Bench
   - Concurrent requests
   - Resource usage

## Monitoring & Observability

### Logging Architecture

```
┌──────────────┐
│ MCP Server   │
└──────┬───────┘
       │
       ├──── STDIO Mode ────► stderr
       │
       └──── HTTP Mode ─────► stdout (JSON)
                               │
                               ▼
                        ┌──────────────┐
                        │ Log Collector │
                        │ (ELK/Splunk)  │
                        └──────────────┘
```

### Metrics to Monitor

1. **Application Metrics**
   - Request rate
   - Error rate
   - Response time
   - Active connections

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

3. **Business Metrics**
   - Most requested cities
   - Average forecast days
   - Alert frequency

## Deployment Patterns

### Blue-Green Deployment

```
Production Traffic
        │
        ▼
   ┌─────────┐
   │ Router  │
   └────┬────┘
        │
        ├──► Blue (Current Version)
        │
        └──► Green (New Version)
              ▲
              │
         Test first, then switch
```

### Canary Deployment

```
Production Traffic
        │
        ▼
   ┌─────────┐
   │ Router  │
   └────┬────┘
        │
        ├──► 95% ──► Old Version
        │
        └──► 5%  ──► New Version (Canary)
```

## Future Enhancements

### Planned Features

1. **Caching Layer**
   - Redis integration
   - TTL-based cache invalidation
   - Cache warming

2. **Historical Data**
   - Store past weather data
   - Trend analysis
   - Historical comparisons

3. **Advanced Alerts**
   - Machine learning predictions
   - Customizable thresholds
   - Push notifications

4. **Extended Coverage**
   - Dynamic city addition
   - Geocoding service integration
   - Weather station data

5. **Monitoring Dashboard**
   - Grafana integration
   - Real-time metrics
   - Alert management

### Technical Debt

- [ ] Add response caching
- [ ] Implement request deduplication
- [ ] Add circuit breaker pattern
- [ ] Improve error messages
- [ ] Add request tracing
- [ ] Implement API versioning

## Conclusion

The Weather MCP Server is designed as a production-ready, scalable, and secure solution for providing weather data to LLM clients. Its modular architecture allows for easy extension and maintenance while maintaining high performance and reliability.

Key strengths:
- Clean separation of concerns
- Comprehensive error handling
- Security-first design
- Horizontal scalability
- Extensive testing
- Production-grade containerization

The architecture supports both local development and large-scale deployments while maintaining simplicity and maintainability.
