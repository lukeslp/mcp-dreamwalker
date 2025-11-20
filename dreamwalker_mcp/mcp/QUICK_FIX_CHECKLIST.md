# MCP Orchestrator Server - Quick Fix Checklist

**Status**: 🔴 Service DOWN - 3 Critical Bugs
**Time to Fix**: ~30 minutes
**Date**: 2025-11-18

---

## Critical Issues Summary

| Issue | Impact | Fix Time | Priority |
|-------|--------|----------|----------|
| Import error (`Callable` not defined) | Workers crash on startup | 5 min | CRITICAL |
| Port binding permission error | Service won't start | 2 min | CRITICAL |
| Async routes in Flask | Runtime errors | 15 min | HIGH |

---

## Fix #1: Import Error ✅

**Problem**: `NameError: name 'Callable' is not defined` in `swarm_orchestrator.py:391`

**File**: `/home/coolhand/shared/orchestration/swarm_orchestrator.py`

**Fix**: Line 17, change from:
```python
from typing import List, Dict, Optional, Any, Callable
```

**To**:
```python
from typing import List, Dict, Optional, Any
from collections.abc import Callable
```

**Test**:
```bash
cd /home/coolhand/shared
python3 -c "from orchestration import SwarmOrchestrator; print('✓ Import successful')"
```

**Expected**: No errors, prints "✓ Import successful"

---

## Fix #2: Port Binding Error ✅

**Problem**: `[Errno 1] Operation not permitted` binding to `0.0.0.0:5060`

**File**: `/home/coolhand/shared/mcp/start.sh`

**Fix**: Line 39, change from:
```bash
-b "0.0.0.0:$PORT" \
```

**To**:
```bash
-b "127.0.0.1:$PORT" \
```

**Rationale**: Caddy proxies from localhost anyway, no need for 0.0.0.0

**Test**:
```bash
cd /home/coolhand/shared/mcp
source venv/bin/activate
gunicorn -w 1 -b 127.0.0.1:5060 --timeout 30 app:app
```

**Expected**: Gunicorn starts without permission errors

---

## Fix #3: Async Routes in Flask ✅

**Problem**: Flask (synchronous) can't handle `async def` routes

**File**: `/home/coolhand/shared/mcp/app.py`

**Fix**: Add `@async_to_sync` decorator to all async routes

**Before**:
```python
@app.route('/tools/orchestrate_research', methods=['POST'])
async def orchestrate_research():
    data = request.get_json()
    result = await mcp_server.tool_orchestrate_research(data)
    return jsonify(result)
```

**After**:
```python
from shared.utils.async_adapter import async_to_sync

@app.route('/tools/orchestrate_research', methods=['POST'])
@async_to_sync
async def orchestrate_research():
    data = request.get_json()
    result = await mcp_server.tool_orchestrate_research(data)
    return jsonify(result)
```

**Routes to fix** (lines 156, 168, 180, 192, 204, 215, 227):
- `orchestrate_research()`
- `orchestrate_search()`
- `get_orchestration_status()`
- `cancel_orchestration()`
- `list_orchestrator_patterns()`
- `list_registered_tools()`
- `execute_registered_tool()`

**Test**:
```bash
curl -X POST http://localhost:5060/tools/list_orchestrator_patterns
```

**Expected**: JSON response with patterns list, no RuntimeError

---

## Deployment Steps

### 1. Apply Fixes (10 minutes)

```bash
# Fix #1: Import error
cd /home/coolhand/shared/orchestration
# Edit swarm_orchestrator.py line 17 (see Fix #1 above)

# Fix #2: Port binding
cd /home/coolhand/shared/mcp
# Edit start.sh line 39 (see Fix #2 above)

# Fix #3: Async routes
cd /home/coolhand/shared/mcp
# Edit app.py (see Fix #3 above)
```

### 2. Test Imports (1 minute)

```bash
cd /home/coolhand/shared
python3 -c "from orchestration import SwarmOrchestrator"
python3 -c "from mcp import UnifiedMCPServer"
```

**Expected**: No errors

### 3. Start Service (2 minutes)

```bash
# Stop if running
python3 /home/coolhand/service_manager.py stop mcp-server

# Start service
python3 /home/coolhand/service_manager.py start mcp-server

# Watch logs in real-time
tail -f ~/.service_manager/logs/mcp-server.log
```

### 4. Verify Health (2 minutes)

```bash
# Test local health endpoint
curl http://localhost:5060/health

# Expected:
# {
#   "status": "healthy",
#   "service": "mcp-orchestrator",
#   "active_streams": 0,
#   "registered_webhooks": 0
# }

# Test through Caddy
curl https://dr.eamer.dev/mcp/health

# Expected: Same as above
```

### 5. Test Endpoints (5 minutes)

```bash
# List available tools
curl https://dr.eamer.dev/mcp/tools

# List orchestrator patterns
curl -X POST https://dr.eamer.dev/mcp/tools/list_orchestrator_patterns

# Test orchestration (lightweight)
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test deployment",
    "max_agents": 2,
    "timeout": 30
  }'

# Note task_id from response, then stream results:
# curl -N https://dr.eamer.dev/mcp/stream/{task_id}
```

### 6. Enable Monitoring (5 minutes)

```bash
# Enable auto-restart on failure
python3 /home/coolhand/service_manager.py start-monitor mcp-server

# Check monitor status
python3 /home/coolhand/service_manager.py monitor-status

# View service status
python3 /home/coolhand/service_manager.py status | grep -A 3 mcp-server
```

---

## Verification Checklist

- [ ] Import test passes (`python3 -c "from orchestration import SwarmOrchestrator"`)
- [ ] Gunicorn starts without permission errors
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Health endpoint accessible via Caddy (`https://dr.eamer.dev/mcp/health`)
- [ ] `/tools` endpoint returns list of available tools
- [ ] POST to `/tools/list_orchestrator_patterns` returns patterns
- [ ] Service listed as "Running" and "Healthy" in service manager
- [ ] No errors in logs (`tail ~/.service_manager/logs/mcp-server.log`)
- [ ] Monitor daemon enabled and tracking service

---

## Rollback Plan (If Issues Occur)

```bash
# 1. Stop service
python3 /home/coolhand/service_manager.py stop mcp-server

# 2. Restore from git (if committed)
cd /home/coolhand/shared
git checkout HEAD -- orchestration/swarm_orchestrator.py
git checkout HEAD -- mcp/start.sh
git checkout HEAD -- mcp/app.py

# 3. Restart stdio bridge for Claude Code
# (Stdio bridge is unaffected by HTTP service issues)
./start-mcp-server

# 4. Report issues in logs
tail -100 ~/.service_manager/logs/mcp-server.log
```

---

## Success Criteria

**Service is production-ready when**:
1. ✅ Gunicorn starts without errors
2. ✅ Health endpoint returns 200 OK
3. ✅ All tool endpoints respond correctly
4. ✅ No errors in logs for 5 minutes
5. ✅ Service accessible via Caddy proxy
6. ✅ Monitor daemon tracking service

---

## Next Steps (After Fixes)

### Phase 2 - Hardening (This Week)
- [ ] Add API key authentication
- [ ] Enable rate limiting (Flask-Limiter)
- [ ] Add structured JSON logging
- [ ] Set up Prometheus metrics
- [ ] Configure Sentry error tracking

### Phase 3 - Production (Next Week)
- [ ] Create systemd service
- [ ] Load testing with Apache Bench
- [ ] Create API documentation (Swagger)
- [ ] Set up CI/CD pipeline
- [ ] Create deployment runbook

---

## Troubleshooting

### Issue: "Import errors still occurring"
```bash
# Check Python path
cd /home/coolhand/shared/mcp
source venv/bin/activate
python3 -c "import sys; print('\n'.join(sys.path))"

# Should include /home/coolhand/shared
```

### Issue: "Port still unavailable"
```bash
# Check what's using port 5060
sudo netstat -tlnp | grep 5060

# Kill zombie processes
pkill -f "mcp"
rm ~/.service_manager/mcp-server.pid
```

### Issue: "Async routes still failing"
```bash
# Check decorator is imported
cd /home/coolhand/shared/mcp
grep -n "async_to_sync" app.py

# Should show import and decorators
```

---

## Contact and Support

**Logs**: `~/.service_manager/logs/mcp-server.log`
**Service Status**: `python3 service_manager.py status`
**Documentation**: `/home/coolhand/shared/mcp/PRODUCTION_DEPLOYMENT_REVIEW.md`

---

**Author**: DevOps Engineer
**Last Updated**: 2025-11-18
**Status**: Ready for deployment
