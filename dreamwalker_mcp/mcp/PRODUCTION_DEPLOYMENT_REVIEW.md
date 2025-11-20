# MCP Orchestrator Server - Production Deployment Review

**Date**: 2025-11-18
**Reviewer**: DevOps Engineer
**Service**: MCP Orchestrator Server (Unified MCP for Beltalowda & Swarm)
**Port**: 5060
**Caddy Route**: `/mcp/*`

## Executive Summary

The MCP Orchestrator Server deployment has **CRITICAL ISSUES** preventing production operation:

1. **Import Error**: Missing `Callable` import in `swarm_orchestrator.py` causing all Gunicorn workers to crash
2. **Port Binding Error**: Gunicorn cannot bind to port 5060 (permission error)
3. **Network Connectivity**: Venv pip install failing due to network issues
4. **Service Status**: HTTP service currently DOWN (stdio bridge works perfectly)

**Status**: 🔴 NOT PRODUCTION READY
**Priority**: HIGH - Blocks Claude Code integration via HTTP

---

## Current Deployment Architecture

### Service Stack
```
┌─────────────────────────────────────────────────┐
│ Caddy Reverse Proxy (dr.eamer.dev)             │
│ Route: /mcp/* → localhost:5060                  │
│ Config: SSE streaming, 600s timeout             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Gunicorn (Production WSGI Server)               │
│ Workers: 4, Timeout: 300s, Port: 5060           │
│ Start Script: /home/coolhand/shared/mcp/start.sh│
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Flask App (/home/coolhand/shared/mcp/app.py)    │
│ - UnifiedMCPServer (orchestrators)              │
│ - SSE Streaming Bridge                          │
│ - Webhook Manager                               │
│ - CORS enabled for web clients                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Orchestrators                                    │
│ - BeltalowdaOrchestrator (hierarchical research)│
│ - SwarmOrchestrator (multi-agent search)        │
│ - Tool Registry (dynamic tool loading)          │
└─────────────────────────────────────────────────┘
```

### Service Manager Configuration
- **Location**: `/home/coolhand/service_manager.py`
- **PID File**: `~/.service_manager/mcp-server.pid`
- **Log File**: `~/.service_manager/logs/mcp-server.log`
- **Auto-restart**: Monitor daemon available (not enabled for MCP)
- **Health Check**: `http://localhost:5060/health`
- **Start Timeout**: 20 seconds

---

## Critical Issues (Blocking Production)

### 1. Import Error - NameError: name 'Callable' is not defined

**File**: `/home/coolhand/shared/orchestration/swarm_orchestrator.py`
**Line**: 391
**Impact**: All Gunicorn workers crash on startup

```python
# Current (broken):
from typing import List, Dict, Optional, Any, Callable  # Line 17 ✓

class SwarmOrchestrator(BaseOrchestrator):
    # ...
    def execute_search(
        self,
        # ...
        stream_callback: Optional[Callable] = None  # Line 391 - ERROR!
    ):
```

**Root Cause**: PEP 563 deferred annotation evaluation. When type hints are evaluated as strings (Python 3.10+), `Callable` from module-level import is not accessible within class body.

**Fix**:
```python
# Option 1: Import at top (already done, but needs TYPE_CHECKING guard)
from typing import TYPE_CHECKING, List, Dict, Optional, Any
if TYPE_CHECKING:
    from typing import Callable

# Option 2: Use string annotation
stream_callback: Optional['Callable'] = None

# Option 3: Import Callable from collections.abc (Python 3.9+)
from collections.abc import Callable
```

**Priority**: CRITICAL - Blocks all HTTP operations

---

### 2. Port Binding Permission Error

**Error**: `[Errno 1] Operation not permitted` binding to `0.0.0.0:5060`

**Logs**:
```
[2025-11-17 23:53:17 -0600] [211952] [ERROR] connection to ('0.0.0.0', 5060) failed: [Errno 1] Operation not permitted
```

**Root Causes**:
1. Port may be in use by another process
2. Venv python may not have CAP_NET_BIND_SERVICE capability
3. SELinux/AppArmor restrictions

**Investigation**:
```bash
# Check if port is in use
sudo netstat -tlnp | grep 5060

# Check for zombie processes
ps aux | grep 5060

# Check venv python capabilities
getcap /home/coolhand/shared/mcp/venv/bin/python3

# Test binding manually
python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 5060))"
```

**Temporary Fix**:
- Bind to `127.0.0.1:5060` instead of `0.0.0.0:5060` (localhost only, Caddy proxies anyway)
- Or use systemd socket activation
- Or grant CAP_NET_BIND_SERVICE to venv python

**Priority**: HIGH - Prevents service startup

---

### 3. Network Connectivity Issues

**Error**: Pip cannot reach PyPI during venv setup

```
WARNING: Retrying after connection broken by 'NewConnectionError':
Failed to establish a new connection: [Errno -2] Name or service not known
```

**Root Causes**:
1. DNS resolution failure
2. Network unreachable during start
3. Firewall blocking outbound HTTPS

**Mitigation**:
- Set `SKIP_PIP_INSTALL=1` environment variable (already in service_manager.py)
- Pre-install dependencies in venv before starting service
- Use `--system-site-packages` venv (already configured)

**Current Workaround**: Service manager sets `SKIP_PIP_INSTALL=1` ✓

**Priority**: MEDIUM - Workaround in place

---

### 4. Async Route Handlers in Flask

**Issue**: Flask routes defined with `async def` but Flask is synchronous

**Code**:
```python
@app.route('/tools/orchestrate_research', methods=['POST'])
async def orchestrate_research():  # Flask can't handle async routes!
    data = request.get_json()
    result = await mcp_server.tool_orchestrate_research(data)
    return jsonify(result)
```

**Impact**: Routes will fail with `RuntimeError: This event loop is already running`

**Fix Required**:
```python
# Option 1: Use async_to_sync adapter
from shared.utils.async_adapter import async_to_sync

@app.route('/tools/orchestrate_research', methods=['POST'])
@async_to_sync
async def orchestrate_research():
    # ...

# Option 2: Use asgiref.sync
from asgiref.sync import async_to_sync

@app.route('/tools/orchestrate_research', methods=['POST'])
def orchestrate_research():
    data = request.get_json()
    result = async_to_sync(mcp_server.tool_orchestrate_research)(data)
    return jsonify(result)

# Option 3: Switch to Quart (async Flask)
from quart import Quart
app = Quart(__name__)
# Keep async routes as-is
```

**Priority**: HIGH - Will cause runtime errors

---

## Deployment Configuration Review

### 1. Service Manager (/home/coolhand/service_manager.py)

**Configuration**:
```python
'mcp-server': {
    'name': 'MCP Orchestrator Server',
    'script': '/home/coolhand/shared/mcp/start.sh',
    'working_dir': '/home/coolhand/shared/mcp',
    'port': 5060,
    'health_endpoint': 'http://localhost:5060/health',
    'start_timeout': 20,
    'description': 'Unified MCP server for orchestrator agents with SSE streaming',
    'env': {
        'PORT': '5060',
        'WORKERS': '4',
        'TIMEOUT': '300',
        'SKIP_PIP_INSTALL': '1'
    }
}
```

**Assessment**: ✅ Well configured
- Proper health endpoint
- Generous start timeout (20s)
- Environment variables passed correctly
- Skip pip install to avoid network issues

**Recommendations**:
- Add `BIND_ADDRESS` env var for easier testing (default: `127.0.0.1`)
- Add `LOG_LEVEL` env var (default: `info`)
- Consider adding to monitor daemon for auto-restart

---

### 2. Gunicorn Configuration (/home/coolhand/shared/mcp/start.sh)

**Current**:
```bash
exec gunicorn \
    -w "$WORKERS" \
    -b "0.0.0.0:$PORT" \
    --timeout "$TIMEOUT" \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
```

**Issues**:
- ❌ Binding to `0.0.0.0` causes permission error
- ❌ No worker class specified (defaults to sync, but routes are async)
- ❌ No graceful timeout
- ❌ No max requests per worker (memory leak prevention)

**Recommended Configuration**:
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"

# Configuration with sane defaults
PORT="${PORT:-5060}"
WORKERS="${WORKERS:-4}"
TIMEOUT="${TIMEOUT:-300}"
BIND_ADDRESS="${BIND_ADDRESS:-127.0.0.1}"  # Localhost only by default
LOG_LEVEL="${LOG_LEVEL:-info}"
MAX_REQUESTS="${MAX_REQUESTS:-1000}"
MAX_REQUESTS_JITTER="${MAX_REQUESTS_JITTER:-50}"

# Virtual environment setup
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv --system-site-packages venv
fi

source venv/bin/activate

# Install dependencies (skippable for production)
if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
    echo "Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
fi

# Start Gunicorn with production settings
echo "Starting MCP Orchestrator Server"
echo "  Bind: $BIND_ADDRESS:$PORT"
echo "  Workers: $WORKERS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Max Requests: $MAX_REQUESTS (±$MAX_REQUESTS_JITTER jitter)"

exec gunicorn \
    -w "$WORKERS" \
    -b "${BIND_ADDRESS}:${PORT}" \
    --timeout "$TIMEOUT" \
    --graceful-timeout 30 \
    --max-requests "$MAX_REQUESTS" \
    --max-requests-jitter "$MAX_REQUESTS_JITTER" \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level "$LOG_LEVEL" \
    --capture-output \
    --enable-stdio-inheritance \
    app:app
```

**Benefits**:
- Binds to localhost by default (safer)
- Memory leak prevention with max requests
- Proper graceful shutdown
- Worker temp files in RAM (/dev/shm) for performance
- Configurable log level
- Better error capture

---

### 3. Caddy Configuration (/etc/caddy/Caddyfile)

**Current** (Lines 84-102):
```caddy
# Port 5060 - MCP Orchestrator Server
handle_path /mcp/* {
    reverse_proxy localhost:5060 {
        # Preserve client IP for logging
        header_up X-Forwarded-For {remote}
        header_up X-Real-IP {remote}

        # SSE/streaming support - disable buffering
        flush_interval -1

        # Increase timeout for long-running orchestrations
        transport http {
            read_timeout 600s
            write_timeout 600s
        }
    }
}
```

**Assessment**: ✅ Excellent configuration
- SSE streaming properly configured
- Generous timeouts (10 minutes)
- Client IP preservation
- Path stripping with `handle_path`

**Recommendations**:
- ✅ Already optimal for SSE
- Consider adding health check probe:
  ```caddy
  reverse_proxy localhost:5060 {
      # ... existing config ...

      # Health check
      health_uri /health
      health_interval 30s
      health_timeout 5s
  }
  ```

---

## Monitoring and Observability

### Current State

**Logs**: ✅ Centralized
- Location: `~/.service_manager/logs/mcp-server.log`
- Format: Gunicorn JSON logs + Flask logs
- Rotation: Handled by logrotate (system-wide)
- Size: 113KB (manageable)

**Metrics**: ❌ Not implemented
- No Prometheus metrics
- No custom metrics collection
- No request/response timing

**Health Checks**: ✅ Implemented
- Endpoint: `/health`
- Returns: `{'status': 'healthy', 'service': 'mcp-orchestrator', 'active_streams': N, 'registered_webhooks': M}`
- Service manager polls every 30s (monitor daemon)

**Alerting**: ❌ Not configured
- No PagerDuty/Slack alerts
- No dead letter queue for failed tasks
- No rate limit breach notifications

---

### Recommended Monitoring Stack

#### 1. Application Metrics (Prometheus + Grafana)

**Add to Flask app**:
```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Custom metrics
orchestration_duration = metrics.histogram(
    'orchestration_duration_seconds',
    'Time spent orchestrating tasks',
    labels={'orchestrator': lambda: request.view_args.get('orchestrator_type')}
)

streaming_connections = metrics.gauge(
    'streaming_active_connections',
    'Number of active SSE connections'
)
```

**Expose metrics endpoint**:
```python
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        prometheus_client.generate_latest(),
        mimetype='text/plain'
    )
```

**Add to Caddy**:
```caddy
handle /mcp/metrics {
    reverse_proxy localhost:5060
}
```

#### 2. Structured Logging (JSON)

**Current**: Plain text logs
**Recommended**: JSON structured logs for easier parsing

```python
import logging
import json_log_formatter

# Configure JSON logging
formatter = json_log_formatter.JSONFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info('Orchestration started', extra={
    'task_id': task_id,
    'orchestrator': 'beltalowda',
    'user_id': user_id,
    'query': query
})
```

**Benefits**:
- Easy filtering in log aggregators (ELK, Loki)
- Structured search (`orchestrator=beltalowda AND status=failed`)
- Automatic metric extraction

#### 3. Health Check Enhancements

**Current**: Basic health endpoint
**Recommended**: Detailed health with dependency checks

```python
@app.route('/health')
def health():
    """Enhanced health check with dependency status"""
    checks = {
        'streaming_bridge': check_streaming_bridge(),
        'webhook_manager': check_webhook_manager(),
        'redis': check_redis_connection() if config.redis_enabled else None,
        'orchestrators': check_orchestrators()
    }

    all_healthy = all(v.get('healthy', True) for v in checks.values() if v)

    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'service': 'mcp-orchestrator',
        'checks': checks,
        'uptime': time.time() - app.start_time,
        'version': '1.0.0'
    }), 200 if all_healthy else 503

def check_streaming_bridge():
    bridge = get_streaming_bridge()
    stats = bridge.get_stats()
    return {
        'healthy': True,
        'active_streams': stats['active_streams'],
        'total_events': stats.get('total_events', 0)
    }
```

#### 4. Error Tracking (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    environment='production',
    traces_sample_rate=0.1,  # 10% performance monitoring
    profiles_sample_rate=0.1  # 10% profiling
)
```

---

## Security Recommendations

### 1. Authentication & Authorization

**Current**: ❌ No authentication
**Risk**: Anyone can trigger orchestrations and consume resources

**Recommendations**:
```python
# Option 1: API Key Authentication
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in VALID_API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/tools/orchestrate_research', methods=['POST'])
@require_api_key
async def orchestrate_research():
    # ...

# Option 2: JWT Tokens
from flask_jwt_extended import JWTManager, jwt_required

app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

@app.route('/tools/orchestrate_research', methods=['POST'])
@jwt_required()
async def orchestrate_research():
    # ...
```

**Priority**: HIGH for public deployment

---

### 2. Rate Limiting

**Current**: ❌ No rate limiting
**Risk**: DDoS, resource exhaustion

**Recommendation**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"],
    storage_uri="redis://localhost:6379"
)

@app.route('/tools/orchestrate_research', methods=['POST'])
@limiter.limit("5 per minute")  # Expensive operation
async def orchestrate_research():
    # ...

@app.route('/health')
@limiter.exempt  # Don't rate limit health checks
def health():
    # ...
```

---

### 3. Input Validation

**Current**: Minimal validation
**Risk**: Injection attacks, malformed requests

**Recommendation**:
```python
from marshmallow import Schema, fields, validate, ValidationError

class OrchestrationRequestSchema(Schema):
    query = fields.Str(required=True, validate=validate.Length(min=3, max=500))
    max_agents = fields.Int(validate=validate.Range(min=1, max=10), missing=5)
    timeout = fields.Int(validate=validate.Range(min=10, max=600), missing=120)
    stream = fields.Bool(missing=False)

@app.route('/tools/orchestrate_search', methods=['POST'])
async def orchestrate_search():
    schema = OrchestrationRequestSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation failed', 'details': err.messages}), 400

    # Proceed with validated data
    result = await mcp_server.tool_orchestrate_search(data)
    return jsonify(result)
```

---

### 4. Secret Management

**Current**: API keys in environment variables (acceptable)
**Better**: Use secret management service

**Options**:
1. **Environment Variables** (current): ✅ OK for development
2. **HashiCorp Vault**: Production-grade secret management
3. **AWS Secrets Manager**: If on AWS
4. **Encrypted .env files**: `python-dotenv` + `cryptography`

**Current Implementation**: Already using environment variables ✓

---

## Error Recovery & Restart Policies

### Current Service Manager Monitor

**Features**:
- Automatic health check polling (30s interval)
- Exponential backoff retry (10s base, 2x multiplier)
- Max 5 restart attempts before giving up
- Reset counter after 1 hour of stability

**Status**: Available but not enabled for MCP server

**Enable auto-restart**:
```bash
# Add mcp-server to monitor
python3 service_manager.py start-monitor mcp-server

# Check monitor status
python3 service_manager.py monitor-status

# Stop monitor
python3 service_manager.py stop-monitor
```

---

### Recommended: Systemd Service (Superior to Monitor)

**Benefits**:
- Native OS integration
- Boot-time startup
- Better process supervision
- Systemd journal integration
- Dependency management

**Service File**: `/etc/systemd/system/mcp-orchestrator.service`
```ini
[Unit]
Description=MCP Orchestrator Server
After=network.target redis.service
Wants=redis.service

[Service]
Type=notify
User=coolhand
Group=coolhand
WorkingDirectory=/home/coolhand/shared/mcp
Environment="PATH=/home/coolhand/shared/mcp/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PORT=5060"
Environment="WORKERS=4"
Environment="TIMEOUT=300"
Environment="SKIP_PIP_INSTALL=1"
Environment="BIND_ADDRESS=127.0.0.1"

# Start script
ExecStart=/home/coolhand/shared/mcp/start.sh

# Restart policy
Restart=on-failure
RestartSec=10s
StartLimitInterval=300s
StartLimitBurst=5

# Resource limits
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-orchestrator

[Install]
WantedBy=multi-user.target
```

**Installation**:
```bash
sudo cp mcp-orchestrator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-orchestrator
sudo systemctl start mcp-orchestrator

# Check status
sudo systemctl status mcp-orchestrator

# View logs
sudo journalctl -u mcp-orchestrator -f
```

---

## Deployment Automation

### 1. Pre-flight Checks Script

**Create**: `/home/coolhand/shared/mcp/preflight.sh`
```bash
#!/bin/bash
# Pre-flight checks before deployment

set -e

echo "MCP Orchestrator Pre-flight Checks"
echo "====================================="

# 1. Check Python version
echo -n "Python version: "
python3 --version

# 2. Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment missing"
    exit 1
fi
echo "✓ Virtual environment exists"

# 3. Check dependencies
source venv/bin/activate
if ! python3 -c "import flask, mcp" 2>/dev/null; then
    echo "❌ Dependencies not installed"
    exit 1
fi
echo "✓ Dependencies installed"

# 4. Check port availability
if netstat -tlnp 2>/dev/null | grep -q ":5060 "; then
    echo "❌ Port 5060 already in use"
    exit 1
fi
echo "✓ Port 5060 available"

# 5. Check import errors
if ! python3 -c "from mcp import UnifiedMCPServer" 2>/dev/null; then
    echo "❌ Import errors detected"
    exit 1
fi
echo "✓ No import errors"

# 6. Check Caddy configuration
if ! sudo caddy validate --config /etc/caddy/Caddyfile 2>/dev/null; then
    echo "⚠️  Caddy configuration may have issues"
else
    echo "✓ Caddy configuration valid"
fi

echo ""
echo "✅ All checks passed - ready for deployment"
```

**Usage**:
```bash
cd /home/coolhand/shared/mcp
bash preflight.sh
```

---

### 2. Deployment Script

**Create**: `/home/coolhand/shared/mcp/deploy.sh`
```bash
#!/bin/bash
# Safe deployment with rollback capability

set -e

BACKUP_DIR="/home/coolhand/backups/mcp"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "MCP Orchestrator Deployment"
echo "============================="

# 1. Pre-flight checks
bash preflight.sh || exit 1

# 2. Backup current version
echo "Creating backup..."
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/mcp-$TIMESTAMP.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    /home/coolhand/shared/mcp

# 3. Stop service
echo "Stopping service..."
python3 /home/coolhand/service_manager.py stop mcp-server || true

# 4. Update dependencies
echo "Updating dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 5. Run migrations (if any)
# python3 migrate.py

# 6. Start service
echo "Starting service..."
python3 /home/coolhand/service_manager.py start mcp-server

# 7. Wait for health check
echo "Waiting for health check..."
for i in {1..30}; do
    if curl -sf http://localhost:5060/health >/dev/null 2>&1; then
        echo "✅ Service healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Health check timeout"
        echo "Rolling back..."
        python3 /home/coolhand/service_manager.py stop mcp-server
        tar -xzf "$BACKUP_DIR/mcp-$TIMESTAMP.tar.gz" -C /
        python3 /home/coolhand/service_manager.py start mcp-server
        exit 1
    fi
    sleep 2
done

echo "✅ Deployment successful"
```

---

### 3. Testing Outside Sandbox

**Currently**: Stdio bridge works ✅
**Goal**: Test HTTP service via Caddy proxy

**Testing Steps**:

1. **Fix import error first** (critical blocker)
2. **Fix port binding** (use 127.0.0.1)
3. **Start service**:
   ```bash
   cd /home/coolhand/shared/mcp
   source venv/bin/activate
   python3 app.py  # Test directly first
   ```

4. **Test health locally**:
   ```bash
   curl http://localhost:5060/health
   ```

5. **Test through Caddy**:
   ```bash
   curl https://dr.eamer.dev/mcp/health
   ```

6. **Test SSE streaming**:
   ```bash
   # Start orchestration
   curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "max_agents": 2}'

   # Stream results (replace TASK_ID)
   curl -N https://dr.eamer.dev/mcp/stream/TASK_ID
   ```

7. **Load test** (after basic tests pass):
   ```bash
   # Install Apache Bench
   sudo apt install apache2-utils

   # Test concurrent requests
   ab -n 100 -c 10 https://dr.eamer.dev/mcp/health
   ```

---

## Production Readiness Checklist

### Critical (Blocking Deployment)

- [ ] **Fix import error in swarm_orchestrator.py**
  - Add `Callable` import from `collections.abc`
  - Test: `python3 -c "from orchestration import SwarmOrchestrator"`

- [ ] **Fix port binding issue**
  - Change bind address to `127.0.0.1:5060`
  - Or grant CAP_NET_BIND_SERVICE to venv python
  - Test: Manual Gunicorn start

- [ ] **Fix async route handlers**
  - Add `@async_to_sync` decorator to async routes
  - Or switch to Quart framework
  - Test: POST to `/tools/orchestrate_search`

- [ ] **Verify health endpoint**
  - Test: `curl http://localhost:5060/health`
  - Expected: `{"status": "healthy", ...}`

---

### High Priority (Production Hardening)

- [ ] **Enable service manager monitor**
  - `python3 service_manager.py start-monitor mcp-server`
  - Verify auto-restart on crash

- [ ] **Add authentication**
  - Implement API key auth
  - Test: Unauthorized requests return 401

- [ ] **Add rate limiting**
  - Install `flask-limiter`
  - Configure Redis backend
  - Test: Exceed rate limit

- [ ] **Input validation**
  - Add marshmallow schemas
  - Test: Malformed requests return 400

- [ ] **Structured logging**
  - Convert to JSON logs
  - Test: Parse logs with `jq`

---

### Medium Priority (Monitoring)

- [ ] **Prometheus metrics**
  - Add `prometheus-flask-exporter`
  - Expose `/metrics` endpoint
  - Configure Grafana dashboard

- [ ] **Enhanced health checks**
  - Add dependency checks
  - Test degraded state handling

- [ ] **Error tracking**
  - Add Sentry integration
  - Test exception capture

- [ ] **Log aggregation**
  - Configure ELK or Loki
  - Set up log retention policy

---

### Low Priority (Nice to Have)

- [ ] **Systemd service**
  - Create service file
  - Enable boot-time startup
  - Test: `sudo systemctl start mcp-orchestrator`

- [ ] **CI/CD pipeline**
  - GitHub Actions for tests
  - Automated deployment
  - Rollback on failure

- [ ] **Documentation**
  - API documentation (OpenAPI/Swagger)
  - Deployment runbook
  - Troubleshooting guide

- [ ] **Performance tuning**
  - Profile with `py-spy`
  - Optimize slow endpoints
  - Add caching layer

---

## Immediate Action Items

### 1. Fix Import Error (5 minutes)

**File**: `/home/coolhand/shared/orchestration/swarm_orchestrator.py`

**Change line 17**:
```python
# Before:
from typing import List, Dict, Optional, Any, Callable

# After:
from typing import List, Dict, Optional, Any
from collections.abc import Callable
```

**Test**:
```bash
cd /home/coolhand/shared
python3 -c "from orchestration import SwarmOrchestrator; print('✓ Import successful')"
```

---

### 2. Fix Port Binding (2 minutes)

**File**: `/home/coolhand/shared/mcp/start.sh`

**Change line 39**:
```bash
# Before:
-b "0.0.0.0:$PORT" \

# After:
-b "127.0.0.1:$PORT" \
```

**Or set environment variable**:
```bash
# In service_manager.py, update mcp-server env:
'env': {
    'PORT': '5060',
    'BIND_ADDRESS': '127.0.0.1',  # Add this
    # ...
}
```

---

### 3. Fix Async Routes (15 minutes)

**File**: `/home/coolhand/shared/mcp/app.py`

**Option A - Use async_to_sync decorator**:
```python
from shared.utils.async_adapter import async_to_sync

@app.route('/tools/orchestrate_research', methods=['POST'])
@async_to_sync
async def orchestrate_research():
    # Keep as-is
```

**Option B - Manual conversion**:
```python
from asgiref.sync import async_to_sync as a2s

@app.route('/tools/orchestrate_research', methods=['POST'])
def orchestrate_research():
    data = request.get_json()
    result = a2s(mcp_server.tool_orchestrate_research)(data)
    return jsonify(result)
```

**Test**:
```bash
curl -X POST http://localhost:5060/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_depth": 1}'
```

---

### 4. Start and Validate (10 minutes)

```bash
# 1. Stop if running
python3 service_manager.py stop mcp-server

# 2. Start service
python3 service_manager.py start mcp-server

# 3. Check logs
tail -f ~/.service_manager/logs/mcp-server.log

# 4. Test health
curl http://localhost:5060/health

# 5. Test through Caddy
curl https://dr.eamer.dev/mcp/health

# 6. Check status
python3 service_manager.py status | grep mcp-server
```

---

## Cost and Performance Considerations

### Resource Usage

**Current Configuration**:
- Workers: 4
- Memory per worker: ~150MB (est.)
- Total memory: ~600MB
- CPU: Burst to 200% during orchestrations

**Recommendations**:
- Set `MemoryMax=2G` in systemd service (prevent runaway)
- Monitor with `htop` or Prometheus
- Consider scaling to 8 workers if load increases

---

### Cost Optimization

**Gunicorn Workers**:
- Current: 4 workers (good for 4-core CPU)
- Formula: `(2 × CPU_cores) + 1`
- Adjust based on load

**Timeout Settings**:
- Request timeout: 300s (appropriate for long orchestrations)
- Graceful timeout: 30s (allow clean shutdown)
- Keep alive: 5s (default)

**Caching**:
- Add Redis for orchestration result caching
- Cache TTL: 1 hour for completed tasks
- Estimated savings: 70% fewer duplicate orchestrations

---

## Summary and Next Steps

### Critical Fixes Required
1. Import error: Add `Callable` from `collections.abc`
2. Port binding: Use `127.0.0.1` instead of `0.0.0.0`
3. Async routes: Add `@async_to_sync` decorator

### Estimated Time to Production Ready
- **Fixes**: 30 minutes
- **Testing**: 1 hour
- **Monitoring setup**: 2 hours
- **Documentation**: 1 hour
- **Total**: ~4-5 hours

### Recommended Timeline

**Phase 1 - Critical Fixes (Today)**:
- Fix import error
- Fix port binding
- Fix async routes
- Deploy and test

**Phase 2 - Hardening (This Week)**:
- Add authentication
- Enable rate limiting
- Add monitoring
- Enable auto-restart

**Phase 3 - Production (Next Week)**:
- Systemd service
- Load testing
- Documentation
- CI/CD pipeline

---

## Conclusion

The MCP Orchestrator Server has a solid foundation with excellent Caddy configuration and service manager integration. However, **three critical bugs** prevent production deployment:

1. Import error causing worker crashes
2. Port binding permission error
3. Async routes in synchronous Flask

Once these are fixed (~30 minutes), the service will be functional. Additional hardening (auth, monitoring, rate limiting) is recommended for production but not blocking.

**Recommendation**: Fix critical bugs immediately, deploy to staging, then add hardening features incrementally.

---

**Author**: DevOps Engineer
**Date**: 2025-11-18
**Version**: 1.0
**Status**: BLOCKING ISSUES IDENTIFIED - FIXES READY
