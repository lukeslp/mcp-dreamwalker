# MCP Orchestrator - Data Architecture Summary

**Quick Reference**: Key insights from data flow analysis
**Author**: Luke Steuber
**Date**: 2025-11-18

---

## Current State: In-Memory Only

```
┌───────────────────────────────────────────────┐
│         UnifiedMCPServer (Process)            │
├───────────────────────────────────────────────┤
│                                               │
│  WorkflowState (In-Memory Dicts)             │
│  ┌─────────────────────────────────────────┐ │
│  │ active_workflows: {}     [Unbounded]    │ │
│  │ completed_workflows: {}  [Max 100]      │ │
│  └─────────────────────────────────────────┘ │
│                                               │
│  StreamingBridge (AsyncIO Queues)            │
│  ┌─────────────────────────────────────────┐ │
│  │ active_streams: {}      [Max 100]       │ │
│  │ Queue per stream        [1000 events]   │ │
│  └─────────────────────────────────────────┘ │
│                                               │
│  WebhookManager (In-Memory Dict)             │
│  ┌─────────────────────────────────────────┐ │
│  │ registered_webhooks: {}                 │ │
│  └─────────────────────────────────────────┘ │
│                                               │
└───────────────────────────────────────────────┘
         │
         │ Server Restart / Crash
         ↓
    ALL DATA LOST ❌
```

**Memory Footprint**:
- 10 active workflows: ~15 KB
- 100 completed workflows: ~2.5 MB
- 20 active streams: ~20 MB
- **Total**: ~22.5 MB (low)

**Critical Issues**:
- ❌ No persistence
- ❌ No horizontal scaling
- ❌ No historical analytics
- ❌ Webhook registrations lost on restart
- ❌ Eviction bug (sorts by duration, not time)

---

## Proposed Architecture: Redis + PostgreSQL

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Orchestrator Cluster                     │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │ Instance 1 │  │ Instance 2 │  │ Instance 3 │                │
│  │  (Memory)  │  │  (Memory)  │  │  (Memory)  │                │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                │
│        │                │                │                        │
│        └────────────────┼────────────────┘                       │
│                         │                                         │
│              ┌──────────▼──────────┐                             │
│              │      Redis          │ 🔥 Hot Data                 │
│              │  (In-Memory Cache)  │                             │
│              │   - Active: 1h TTL  │                             │
│              │   - Results: 7d TTL │                             │
│              └──────────┬──────────┘                             │
│                         │                                         │
│                         │ Async Write                             │
│                         ↓                                         │
│              ┌──────────────────────┐                            │
│              │    PostgreSQL        │ ❄️  Cold Data              │
│              │  (Persistent Store)  │                             │
│              │   - History: 90 days │                             │
│              │   - Analytics        │                             │
│              │   - Audit Log        │                             │
│              └──────────┬───────────┘                            │
│                         │                                         │
│                         │ Archive (>90d)                          │
│                         ↓                                         │
│              ┌──────────────────────┐                            │
│              │    S3 / MinIO        │ 🧊 Archive                 │
│              │   (Object Storage)   │                             │
│              │   - Long-term: Years │                             │
│              │   - Compliance       │                             │
│              └──────────────────────┘                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Timeline

```
Time         Location      TTL        Purpose
─────────────────────────────────────────────────────────────
0-5 min   → Memory       -          Active execution
5 min-1h  → Redis        1 hour     Fast access, resume
1h-7d     → Redis        7 days     Recent results cache
7d-90d    → PostgreSQL   90 days    Analytics, queries
90d+      → S3/MinIO     Years      Compliance, archive
```

---

## Critical Code Locations

### WorkflowState Class
**File**: `/home/coolhand/shared/mcp/unified_server.py`

| Method | Line | Purpose | Issue |
|--------|------|---------|-------|
| `__init__` | 64 | Initialize state dicts | No Redis |
| `create_workflow` | 70 | Create new workflow | Memory only |
| `complete_workflow` | 130 | Store result | **BUG: Wrong sort key** |
| `get_workflow_result` | 155 | Retrieve result | No persistence fallback |

**Eviction Bug** (Line 143-149):
```python
# WRONG: Sorts by execution_time (duration)
oldest = sorted(
    self.completed_workflows.items(),
    key=lambda x: x[1].execution_time  # ❌ This is DURATION, not timestamp!
)[0][0]

# CORRECT: Sort by completion timestamp
oldest_task_id = min(
    self.completed_workflows.keys(),
    key=lambda tid: self.active_workflows.get(tid, {}).get('completed_at', '')
)
```

### StreamingBridge
**File**: `/home/coolhand/shared/mcp/streaming.py`

| Component | Line | Limit | Impact |
|-----------|------|-------|--------|
| `active_streams` | 47 | 100 streams | Max 100 concurrent SSE clients |
| `Queue(maxsize=1000)` | 84 | 1000 events | Slow consumers lose events |
| `stream_ttl` | 44 | 3600s (1h) | Auto-cleanup idle streams |

---

## Data Retention Strategy

### Current (In-Memory)
```
Active Workflows     → Unbounded (RISK!)
Completed Workflows  → Max 100 (FIFO eviction)
Stream Events        → 1000 per stream
Stream Lifetime      → 1 hour TTL
Webhooks             → In-memory only
```

### Proposed (Multi-Tier)

**Tier 1: Memory** (nanosecond access)
- Active workflows
- Recent 100 results
- Provider cache

**Tier 2: Redis** (millisecond access)
- Active workflows (1h TTL)
- Results (7d TTL)
- Stream events (Redis Streams)
- Webhook registrations (1d TTL)

**Tier 3: PostgreSQL** (10-100ms access)
- All completed workflows (90d)
- Analytics aggregates
- Audit log
- Cost tracking

**Tier 4: S3/MinIO** (second access)
- Archived workflows (years)
- Large documents
- Compliance backups

---

## Memory Scaling Estimates

### Single Workflow Footprint

**Beltalowda (8 agents)**:
```
Workflow Info:      1.5 KB
Agent Results:      200 KB  (8 agents × 25 KB)
Synthesis:          50 KB   (2 Drummers + 1 Camina)
Final Synthesis:    10 KB
Documents:          2 KB    (metadata only)
─────────────────────────
Total:             ~264 KB per workflow
```

### Concurrent Load

| Workload | Active | Completed | Streams | Total Memory |
|----------|--------|-----------|---------|--------------|
| Light    | 5      | 100       | 10      | ~27 MB       |
| Medium   | 25     | 100       | 50      | ~56 MB       |
| Heavy    | 100    | 100       | 100     | ~126 MB      |
| Extreme  | 500    | 100       | 200     | ~332 MB      |

**Bottleneck**: Not memory, but **API rate limits** and **CPU**.

---

## Data Loss Scenarios

| Event | Likelihood | Impact | Recovery |
|-------|-----------|--------|----------|
| **Server Restart** | High | Total loss | ❌ None |
| **Docker Recreate** | High | Total loss | ❌ None |
| **Process Crash** | Medium | Total loss | ❌ None |
| **OOM Kill** | Low | Total loss | ❌ None |
| **Power Failure** | Low | Total loss | ❌ None |
| **Network Partition** | Medium | Webhook loss | ❌ None |
| **101st Workflow** | High | Oldest evicted | ❌ Silent |

**With Redis**: All reduced to "Transient" with automatic recovery.

---

## Redis Schema Design

### Keys Pattern

```
# Workflow metadata
workflow:{task_id}                 → Hash (workflow_info)
                                      TTL: 24h

# Results
result:{task_id}                   → JSON (compressed)
                                      TTL: 7 days

# Indexes
workflows:active                   → Set (task_id)
workflows:completed                → Set (task_id)
workflows:type:{orchestrator_type} → Set (task_id)
results:by_time                    → Sorted Set (task_id → timestamp)

# Streaming
stream:{task_id}                   → Redis Stream
                                      MAXLEN: 1000

# Webhooks
webhooks:{task_id}                 → String (webhook_url)
                                      TTL: 24h

# Statistics
stats:costs                        → Hash (daily_cost)
stats:executions                   → Hash (daily_count)
```

### Example Commands

```bash
# Create workflow
HSET workflow:research_abc123 orchestrator_type "beltalowda" task "..." status "pending"
SADD workflows:active research_abc123
SADD workflows:type:beltalowda research_abc123
EXPIRE workflow:research_abc123 86400

# Complete workflow
SET result:research_abc123 '{"task_id": "...", ...}' EX 604800
SREM workflows:active research_abc123
SADD workflows:completed research_abc123
ZADD results:by_time 1732145678 research_abc123

# Query recent workflows
ZREVRANGE results:by_time 0 9  # Last 10

# Cleanup old results
ZREMRANGEBYRANK results:by_time 0 -101  # Keep last 100
```

---

## PostgreSQL Schema Design

### Tables

```sql
-- Workflows
CREATE TABLE workflows (
    task_id TEXT PRIMARY KEY,
    orchestrator_type TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    config JSONB,
    error TEXT,

    -- Indexes
    INDEX idx_status (status),
    INDEX idx_type (orchestrator_type),
    INDEX idx_created (created_at DESC)
);

-- Results
CREATE TABLE results (
    task_id TEXT PRIMARY KEY,
    result JSONB NOT NULL,
    execution_time REAL,
    total_cost REAL,
    agent_count INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (task_id) REFERENCES workflows(task_id) ON DELETE CASCADE,

    -- JSONB index for fast queries
    INDEX idx_result_metadata USING GIN (result)
);

-- Audit log
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    INDEX idx_events_task_time (task_id, timestamp)
);

-- Cost tracking
CREATE TABLE daily_costs (
    date DATE PRIMARY KEY,
    orchestrator_type TEXT,
    total_cost REAL,
    workflow_count INT,

    INDEX idx_costs_date (date DESC)
);
```

### Analytics Queries

```sql
-- Success rate (last 7 days)
SELECT
    orchestrator_type,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM workflows
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY orchestrator_type;

-- Average execution time by type
SELECT
    w.orchestrator_type,
    COUNT(*) as count,
    ROUND(AVG(r.execution_time), 2) as avg_time,
    ROUND(AVG(r.total_cost), 4) as avg_cost
FROM workflows w
JOIN results r ON w.task_id = r.task_id
WHERE w.completed_at > NOW() - INTERVAL '30 days'
GROUP BY w.orchestrator_type;

-- Most expensive workflows (all time)
SELECT
    w.task_id,
    w.task,
    r.total_cost,
    r.execution_time,
    r.agent_count
FROM workflows w
JOIN results r ON w.task_id = r.task_id
ORDER BY r.total_cost DESC
LIMIT 10;

-- Daily usage trend
SELECT
    DATE(created_at) as date,
    COUNT(*) as workflows,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
FROM workflows
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

---

## Implementation Roadmap

### Phase 1: Quick Wins (1 week)
✅ **Goal**: Fix critical bugs, add basic persistence

1. Fix eviction bug (2 hours)
2. Add active workflow limit (1 hour)
3. Implement graceful shutdown (2 hours)
4. Redis dual-write integration (4 hours)
5. Test on staging (8 hours)

**Deliverable**: Redis-backed MCP server with state restoration

### Phase 2: Analytics (2 weeks)
✅ **Goal**: Historical querying and reporting

1. PostgreSQL schema design (4 hours)
2. Async writer service (8 hours)
3. Analytics endpoints (8 hours)
4. Grafana dashboard (16 hours)
5. Testing (16 hours)

**Deliverable**: Analytics dashboard with 90-day history

### Phase 3: Scale (1 month)
✅ **Goal**: Multi-instance support

1. Redis distributed locks (8 hours)
2. Task queue (Celery/RQ) (16 hours)
3. Load balancer config (4 hours)
4. Sticky sessions for SSE (8 hours)
5. Testing (24 hours)

**Deliverable**: Horizontal scaling to 3+ instances

### Phase 4: Advanced (2 months)
✅ **Goal**: Production-grade features

1. S3 archival (16 hours)
2. Workflow resumption (32 hours)
3. Cost optimization (16 hours)
4. Audit logging (16 hours)
5. Observability (24 hours)

**Deliverable**: Enterprise-ready orchestrator platform

---

## Quick Reference Commands

### Check Current State
```bash
# Active workflows count
curl http://localhost:5060/health | jq '.active_streams'

# Get workflow status
curl -X POST http://localhost:5060/tools/get_orchestration_status \
  -H "Content-Type: application/json" \
  -d '{"task_id": "research_abc123"}'
```

### Redis Commands (After Migration)
```bash
# Count active workflows
redis-cli SCARD "workflows:active"

# List recent results
redis-cli ZREVRANGE "results:by_time" 0 9

# Get workflow info
redis-cli HGETALL "workflow:research_abc123"

# Check memory usage
redis-cli INFO memory | grep used_memory_human
```

### PostgreSQL Queries (Future)
```sql
-- Count workflows by status
SELECT status, COUNT(*) FROM workflows GROUP BY status;

-- Total cost (all time)
SELECT SUM(total_cost) FROM results;

-- Failed workflows
SELECT task_id, error FROM workflows WHERE status = 'failed' LIMIT 10;
```

---

## Cost-Benefit Analysis

### Current Architecture (In-Memory Only)

**Costs**:
- Development: 0 hours (already built)
- Infrastructure: $0/month
- Maintenance: 1 hour/week

**Benefits**:
- Low latency (< 1ms)
- Simple to understand
- No external dependencies

**Risks**:
- ❌ Data loss on restart (HIGH)
- ❌ No analytics (MEDIUM)
- ❌ Can't scale horizontally (LOW)

### Proposed Architecture (Redis + PostgreSQL)

**Costs**:
- Development: 80 hours (2 weeks)
- Infrastructure: $50/month (Redis + Postgres on cloud)
- Maintenance: 2 hours/week

**Benefits**:
- ✅ Survives restarts (eliminates data loss)
- ✅ Historical analytics (business insights)
- ✅ Horizontal scaling (3-10x throughput)
- ✅ Compliance ready (audit logs)

**ROI**:
- Prevent 1 data loss incident = saves hours of re-work
- Analytics enable cost optimization = saves $100+/month
- **Payback period**: < 1 month

---

## Resources

### Documentation
- [Full Analysis](/home/coolhand/shared/mcp/DATA_FLOW_ANALYSIS.md)
- [Redis Migration Guide](/home/coolhand/shared/mcp/REDIS_MIGRATION_QUICK_START.md)
- [MCP API Docs](/home/coolhand/shared/mcp/API.md)

### Code Files
- WorkflowState: `/home/coolhand/shared/mcp/unified_server.py`
- StreamingBridge: `/home/coolhand/shared/mcp/streaming.py`
- Base Orchestrator: `/home/coolhand/shared/orchestration/base_orchestrator.py`
- Data Models: `/home/coolhand/shared/orchestration/models.py`

### External Dependencies
- Redis: `pip install redis` (already in `/home/coolhand/shared/memory/`)
- PostgreSQL: `pip install psycopg2-binary sqlalchemy`
- S3: `pip install boto3` (for archival)

---

**Last Updated**: 2025-11-18
**Author**: Luke Steuber
**Status**: Ready for Implementation
