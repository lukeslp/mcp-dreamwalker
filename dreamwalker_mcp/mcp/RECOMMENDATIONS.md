# MCP Orchestrator - Data Engineering Recommendations

**Priority-Ordered Action Plan**
**Author**: Luke Steuber
**Date**: 2025-11-18

---

## Executive Summary

The MCP Orchestrator Server currently uses **in-memory-only state management**, making it vulnerable to total data loss on restart. This analysis provides a prioritized roadmap to transition to a **durable, scalable, and queryable** data architecture.

**Critical Finding**: A bug in the eviction logic (line 143-149 of `unified_server.py`) sorts by execution duration instead of completion timestamp, causing incorrect FIFO cleanup.

**Recommended Path**: Implement Redis for persistence (4 hours), then PostgreSQL for analytics (2 weeks), then S3 for archival (optional).

---

## Priority 1: IMMEDIATE FIXES (Today - 2 Hours)

**Impact**: Critical bugs, data loss prevention
**Effort**: 2 hours
**Risk**: Low

### 1.1 Fix Eviction Bug ⚠️ CRITICAL

**Problem**: Eviction sorts by `execution_time` (duration) instead of completion timestamp.

**File**: `/home/coolhand/shared/mcp/unified_server.py` (Line 143-149)

**Current Code**:
```python
# WRONG: Sorts by execution duration
oldest = sorted(
    self.completed_workflows.items(),
    key=lambda x: x[1].execution_time  # ❌ This is DURATION!
)[0][0]
```

**Fixed Code**:
```python
# CORRECT: Sort by completion timestamp
oldest_task_id = min(
    self.completed_workflows.keys(),
    key=lambda tid: self.active_workflows.get(tid, {}).get('completed_at', '')
)
del self.completed_workflows[oldest_task_id]
```

**Test**:
```bash
# Create test to verify FIFO behavior
cd /home/coolhand/shared/mcp
python -c "
from unified_server import WorkflowState
from orchestration import OrchestratorResult, TaskStatus
import time

state = WorkflowState()

# Create 3 workflows with different durations
for i in range(3):
    result = OrchestratorResult(
        task_id=f'test_{i}',
        title=f'Test {i}',
        status=TaskStatus.COMPLETED,
        execution_time=100 - i * 10,  # Decreasing duration
        total_cost=0.01
    )
    state.completed_workflows[f'test_{i}'] = result
    time.sleep(0.1)  # Small delay to ensure timestamp order

# Verify FIFO: test_0 should be oldest by time
assert list(state.completed_workflows.keys())[0] == 'test_0'
print('✓ FIFO test passed')
"
```

---

### 1.2 Add Active Workflow Limit

**Problem**: Unbounded growth of `active_workflows` dict.

**File**: `/home/coolhand/shared/mcp/unified_server.py` (After line 68)

**Code**:
```python
class WorkflowState:
    MAX_ACTIVE_WORKFLOWS = 50  # Prevent unbounded growth

    def create_workflow(self, task_id, orchestrator_type, task, config):
        # Check limit
        if len(self.active_workflows) >= self.MAX_ACTIVE_WORKFLOWS:
            raise ValueError(
                f"Maximum active workflows ({self.MAX_ACTIVE_WORKFLOWS}) exceeded. "
                f"Please wait for existing workflows to complete or cancel them."
            )

        # ... rest of method
```

**Impact**: Prevents memory exhaustion from hung workflows.

---

### 1.3 Implement Graceful Shutdown

**Problem**: No state preservation on SIGTERM/SIGINT.

**File**: `/home/coolhand/shared/mcp/app.py` (Add at end)

**Code**:
```python
import signal
import json
import atexit

def save_state_on_shutdown():
    """Save workflow state to disk before exit."""
    state_file = "/home/coolhand/shared/mcp/state_backup.json"

    try:
        state_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'active_workflows': mcp_server.workflow_state.active_workflows,
            'completed_workflows': {
                k: v.to_dict()
                for k, v in mcp_server.workflow_state.completed_workflows.items()
            }
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

        logger.info(f"✓ State saved to {state_file} ({len(state_data['active_workflows'])} active, {len(state_data['completed_workflows'])} completed)")

    except Exception as e:
        logger.error(f"Failed to save state: {e}")

# Register shutdown handler
signal.signal(signal.SIGTERM, lambda s, f: (save_state_on_shutdown(), sys.exit(0)))
signal.signal(signal.SIGINT, lambda s, f: (save_state_on_shutdown(), sys.exit(0)))
atexit.register(save_state_on_shutdown)
```

**Test**:
```bash
# Start server
python app.py &
PID=$!

# Trigger shutdown
kill -TERM $PID

# Verify backup created
ls -lh /home/coolhand/shared/mcp/state_backup.json
cat /home/coolhand/shared/mcp/state_backup.json | jq '.timestamp'
```

---

## Priority 2: REDIS PERSISTENCE (This Week - 4 Hours)

**Impact**: Eliminates data loss on restart
**Effort**: 4 hours
**Risk**: Low (dual-write pattern, graceful fallback)

### 2.1 Quick Start Guide

**Follow**: `/home/coolhand/shared/mcp/REDIS_MIGRATION_QUICK_START.md`

**Steps Summary**:
1. Start Redis: `docker run -d --name mcp-redis -p 6379:6379 redis:7`
2. Modify `WorkflowState` class (1 hour)
3. Add `OrchestratorResult.from_dict()` method (30 min)
4. Update `UnifiedMCPServer` initialization (15 min)
5. Add environment variables (5 min)
6. Test persistence (1 hour)
7. Deploy to production (30 min)

### 2.2 Benefits

✅ **Before**: All state lost on restart
✅ **After**: State automatically restored from Redis

✅ **Before**: 100 result limit (memory)
✅ **After**: 7-day retention (Redis TTL)

✅ **Before**: No webhook persistence
✅ **After**: Webhooks survive restart

### 2.3 Monitoring

**Add health check**:
```python
@app.route('/health')
def health():
    redis_status = "healthy" if mcp_server.workflow_state.redis else "unavailable"

    return jsonify({
        'status': 'healthy',
        'redis': redis_status,
        'active_workflows': len(mcp_server.workflow_state.active_workflows),
        'redis_keys': mcp_server.workflow_state.redis.client.dbsize() if redis_status == "healthy" else 0
    })
```

---

## Priority 3: ANALYTICS ENDPOINTS (Next Week - 8 Hours)

**Impact**: Business insights, cost tracking
**Effort**: 8 hours
**Risk**: Low

### 3.1 Workflow Statistics

**File**: `/home/coolhand/shared/mcp/app.py`

**Endpoints to Add**:

```python
@app.route('/analytics/workflows')
def analytics_workflows():
    """Get workflow statistics."""
    redis = mcp_server.workflow_state.redis

    if not redis:
        return jsonify({'error': 'Redis required'}), 503

    return jsonify({
        'active': redis.client.scard("workflows:active"),
        'completed': redis.client.scard("workflows:completed"),
        'by_type': {
            'beltalowda': redis.client.scard("workflows:type:beltalowda"),
            'swarm': redis.client.scard("workflows:type:swarm")
        },
        'recent_24h': len(redis.client.zrangebyscore(
            "results:by_time",
            time.time() - 86400,
            time.time()
        ))
    })


@app.route('/analytics/costs')
def analytics_costs():
    """Calculate total costs."""
    workflows = mcp_server.workflow_state.completed_workflows

    total_cost = sum(w.total_cost for w in workflows.values())
    total_time = sum(w.execution_time for w in workflows.values())

    return jsonify({
        'total_cost_usd': round(total_cost, 4),
        'total_execution_hours': round(total_time / 3600, 2),
        'workflow_count': len(workflows),
        'average_cost_usd': round(total_cost / len(workflows), 4) if workflows else 0
    })


@app.route('/analytics/performance')
def analytics_performance():
    """Performance metrics."""
    workflows = mcp_server.workflow_state.completed_workflows

    if not workflows:
        return jsonify({'error': 'No data'}), 404

    execution_times = [w.execution_time for w in workflows.values()]

    return jsonify({
        'avg_execution_time': round(sum(execution_times) / len(execution_times), 2),
        'min_execution_time': round(min(execution_times), 2),
        'max_execution_time': round(max(execution_times), 2),
        'success_rate': round(
            100 * sum(1 for w in workflows.values() if w.status == TaskStatus.COMPLETED) / len(workflows),
            2
        )
    })
```

### 3.2 Simple Dashboard (HTML)

**File**: `/home/coolhand/shared/mcp/templates/dashboard.html` (new)

```html
<!DOCTYPE html>
<html>
<head>
    <title>MCP Orchestrator Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
        .metric { display: inline-block; margin: 20px; padding: 20px; background: #2a2a2a; border-radius: 8px; }
        .metric h3 { margin: 0 0 10px 0; color: #888; }
        .metric .value { font-size: 48px; font-weight: bold; color: #4CAF50; }
        .error { color: #f44336; }
    </style>
    <script>
        async function loadMetrics() {
            const workflows = await fetch('/analytics/workflows').then(r => r.json());
            const costs = await fetch('/analytics/costs').then(r => r.json());
            const performance = await fetch('/analytics/performance').then(r => r.json());

            document.getElementById('active').textContent = workflows.active;
            document.getElementById('completed').textContent = workflows.completed;
            document.getElementById('total_cost').textContent = '$' + costs.total_cost_usd;
            document.getElementById('success_rate').textContent = performance.success_rate + '%';
        }

        setInterval(loadMetrics, 5000);  // Refresh every 5 seconds
        loadMetrics();
    </script>
</head>
<body>
    <h1>MCP Orchestrator Dashboard</h1>

    <div class="metric">
        <h3>Active Workflows</h3>
        <div class="value" id="active">-</div>
    </div>

    <div class="metric">
        <h3>Completed</h3>
        <div class="value" id="completed">-</div>
    </div>

    <div class="metric">
        <h3>Total Cost</h3>
        <div class="value" id="total_cost">-</div>
    </div>

    <div class="metric">
        <h3>Success Rate</h3>
        <div class="value" id="success_rate">-</div>
    </div>
</body>
</html>
```

**Route**:
```python
from flask import render_template

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
```

**Access**: `http://localhost:5060/dashboard`

---

## Priority 4: POSTGRESQL INTEGRATION (Month 2 - 2 Weeks)

**Impact**: Long-term storage, advanced analytics
**Effort**: 2 weeks
**Risk**: Medium

### 4.1 Schema Setup

**File**: `/home/coolhand/shared/mcp/schema.sql` (new)

```sql
-- Create database
CREATE DATABASE mcp_orchestrator;

-- Connect
\c mcp_orchestrator

-- Workflows table
CREATE TABLE workflows (
    task_id TEXT PRIMARY KEY,
    orchestrator_type TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    config JSONB,
    error TEXT
);

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_type ON workflows(orchestrator_type);
CREATE INDEX idx_workflows_created ON workflows(created_at DESC);

-- Results table
CREATE TABLE results (
    task_id TEXT PRIMARY KEY,
    result JSONB NOT NULL,
    execution_time REAL,
    total_cost REAL,
    agent_count INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (task_id) REFERENCES workflows(task_id) ON DELETE CASCADE
);

CREATE INDEX idx_results_metadata USING GIN (result);
CREATE INDEX idx_results_cost ON results(total_cost DESC);

-- Events table (audit log)
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (task_id) REFERENCES workflows(task_id) ON DELETE CASCADE
);

CREATE INDEX idx_events_task_time ON events(task_id, timestamp);
```

### 4.2 Async Writer Service

**File**: `/home/coolhand/shared/mcp/postgres_writer.py` (new)

```python
import asyncio
import asyncpg
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PostgresWriter:
    """Async PostgreSQL writer for workflow persistence."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def connect(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=2,
            max_size=10
        )
        logger.info("✓ PostgreSQL connection pool created")

    async def write_workflow(self, workflow_info: Dict[str, Any]):
        """Write workflow to database."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO workflows (task_id, orchestrator_type, task, status, created_at, config)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (task_id) DO UPDATE
                SET status = $4, started_at = COALESCE(workflows.started_at, NOW())
                """,
                workflow_info['task_id'],
                workflow_info['orchestrator_type'],
                workflow_info['task'],
                workflow_info['status'].value if hasattr(workflow_info['status'], 'value') else workflow_info['status'],
                workflow_info['created_at'],
                workflow_info['config']
            )

    async def write_result(self, task_id: str, result: Dict[str, Any]):
        """Write result to database."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO results (task_id, result, execution_time, total_cost, agent_count)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (task_id) DO UPDATE
                SET result = $2, execution_time = $3, total_cost = $4
                """,
                task_id,
                result,
                result.get('execution_time', 0),
                result.get('total_cost', 0),
                len(result.get('agent_results', []))
            )

    async def close(self):
        """Close connection pool."""
        await self.pool.close()
```

### 4.3 Integration with WorkflowState

**File**: `/home/coolhand/shared/mcp/unified_server.py`

```python
class WorkflowState:
    def __init__(self, redis_enabled=True, postgres_writer=None):
        # ... existing code ...
        self.postgres_writer = postgres_writer

    def create_workflow(self, task_id, orchestrator_type, task, config):
        # ... existing Redis write ...

        # Async write to Postgres
        if self.postgres_writer:
            asyncio.create_task(
                self.postgres_writer.write_workflow(workflow_info)
            )

        return workflow_info

    def complete_workflow(self, task_id, result):
        # ... existing code ...

        # Async write to Postgres
        if self.postgres_writer:
            asyncio.create_task(
                self.postgres_writer.write_result(task_id, result.to_dict())
            )
```

---

## Priority 5: MONITORING & OBSERVABILITY (Month 3 - 1 Week)

**Impact**: Production readiness, debugging
**Effort**: 1 week
**Risk**: Low

### 5.1 Prometheus Metrics

**File**: `/home/coolhand/shared/mcp/metrics.py` (new)

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
workflows_created = Counter('workflows_created_total', 'Total workflows created', ['orchestrator_type'])
workflows_completed = Counter('workflows_completed_total', 'Total workflows completed', ['orchestrator_type', 'status'])

# Histograms
workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution time', ['orchestrator_type'])
workflow_cost = Histogram('workflow_cost_usd', 'Workflow API cost', ['orchestrator_type'])

# Gauges
active_workflows_gauge = Gauge('active_workflows', 'Current active workflows')
redis_memory_usage = Gauge('redis_memory_bytes', 'Redis memory usage')
```

**Integration**:
```python
# In create_workflow()
workflows_created.labels(orchestrator_type=orchestrator_type).inc()

# In complete_workflow()
workflows_completed.labels(
    orchestrator_type=workflow_info['orchestrator_type'],
    status=result.status.value
).inc()

workflow_duration.labels(
    orchestrator_type=workflow_info['orchestrator_type']
).observe(result.execution_time)

workflow_cost.labels(
    orchestrator_type=workflow_info['orchestrator_type']
).observe(result.total_cost)
```

### 5.2 Grafana Dashboard

**File**: `/home/coolhand/shared/mcp/grafana/dashboard.json`

```json
{
  "dashboard": {
    "title": "MCP Orchestrator Metrics",
    "panels": [
      {
        "title": "Active Workflows",
        "targets": [{"expr": "active_workflows"}]
      },
      {
        "title": "Workflow Completion Rate",
        "targets": [{"expr": "rate(workflows_completed_total[5m])"}]
      },
      {
        "title": "Average Cost per Workflow",
        "targets": [{"expr": "avg(workflow_cost_usd)"}]
      }
    ]
  }
}
```

---

## Priority 6: COST OPTIMIZATION (Ongoing)

### 6.1 Result Compression

**File**: `/home/coolhand/shared/mcp/unified_server.py`

```python
import zlib
import json

class WorkflowState:
    def complete_workflow(self, task_id, result):
        if self.redis_enabled and self.redis:
            # Compress result before storing
            result_json = json.dumps(result.to_dict())
            compressed = zlib.compress(result_json.encode('utf-8'))

            self.redis.client.set(
                f"result:{task_id}",
                compressed,
                ex=86400 * 7
            )

            logger.info(f"✓ Result compressed: {len(result_json)} → {len(compressed)} bytes ({100 * len(compressed) / len(result_json):.1f}%)")

    def get_workflow_result(self, task_id):
        if self.redis_enabled and self.redis:
            compressed = self.redis.client.get(f"result:{task_id}")
            if compressed:
                result_json = zlib.decompress(compressed).decode('utf-8')
                result_dict = json.loads(result_json)
                return OrchestratorResult.from_dict(result_dict)
```

**Savings**: ~60-80% storage reduction

### 6.2 S3 Archival

**File**: `/home/coolhand/shared/mcp/archival.py` (new)

```python
import boto3
import json
from datetime import datetime, timedelta

def archive_old_results(postgres_conn, s3_bucket, days_old=90):
    """Archive results older than N days to S3."""

    cutoff = datetime.utcnow() - timedelta(days=days_old)

    # Query old results
    old_results = postgres_conn.execute(
        "SELECT task_id, result FROM results WHERE created_at < %s",
        (cutoff,)
    ).fetchall()

    s3 = boto3.client('s3')

    for task_id, result in old_results:
        # Upload to S3
        key = f"archived-results/{cutoff.year}/{cutoff.month}/{task_id}.json"
        s3.put_object(
            Bucket=s3_bucket,
            Key=key,
            Body=json.dumps(result),
            StorageClass='GLACIER'  # Cheap long-term storage
        )

        # Delete from Postgres
        postgres_conn.execute(
            "DELETE FROM results WHERE task_id = %s",
            (task_id,)
        )

    return len(old_results)
```

**Savings**: PostgreSQL storage ~90% reduction

---

## Summary: Timeline & ROI

### Quick Wins (This Week)

| Task | Time | Impact | ROI |
|------|------|--------|-----|
| Fix eviction bug | 30 min | High | Immediate |
| Add workflow limit | 30 min | Medium | Prevent OOM |
| Graceful shutdown | 1 hour | High | Data recovery |
| Redis integration | 4 hours | Critical | Eliminate data loss |

**Total**: 6 hours
**Benefit**: No more data loss on restart

### Medium-term (This Month)

| Task | Time | Impact |
|------|------|--------|
| Analytics endpoints | 8 hours | High |
| Simple dashboard | 4 hours | Medium |
| PostgreSQL schema | 2 hours | High |
| Async writer | 6 hours | High |

**Total**: 20 hours
**Benefit**: Historical analytics, cost tracking

### Long-term (3 Months)

| Task | Time | Impact |
|------|------|--------|
| Multi-instance support | 32 hours | High |
| Grafana dashboards | 16 hours | Medium |
| S3 archival | 8 hours | Low |
| Cost optimization | 8 hours | Medium |

**Total**: 64 hours
**Benefit**: Production-grade platform

---

## Next Steps

**Immediate Actions** (Do Today):
1. ✅ Fix eviction bug (30 min)
2. ✅ Add workflow limit (30 min)
3. ✅ Test fixes (1 hour)

**This Week**:
4. ✅ Implement Redis persistence (4 hours)
5. ✅ Test on staging (2 hours)
6. ✅ Deploy to production (1 hour)

**Next Week**:
7. ✅ Add analytics endpoints (8 hours)
8. ✅ Build simple dashboard (4 hours)

**Next Month**:
9. ✅ Design PostgreSQL schema (2 hours)
10. ✅ Implement async writer (6 hours)
11. ✅ Test and deploy (4 hours)

---

## Resources

- **Full Analysis**: `/home/coolhand/shared/mcp/DATA_FLOW_ANALYSIS.md`
- **Redis Guide**: `/home/coolhand/shared/mcp/REDIS_MIGRATION_QUICK_START.md`
- **Architecture Summary**: `/home/coolhand/shared/mcp/DATA_ARCHITECTURE_SUMMARY.md`
- **Shared Library**: `/home/coolhand/shared/CLAUDE.md`

---

**Status**: Ready for Implementation
**Approved by**: Luke Steuber
**Last Updated**: 2025-11-18
