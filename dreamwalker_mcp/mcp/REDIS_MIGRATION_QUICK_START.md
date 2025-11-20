# Redis Migration Quick Start Guide

**Goal**: Add Redis persistence to MCP Orchestrator Server in 4 hours
**Estimated Time**: 4 hours
**Difficulty**: Medium
**Prerequisites**: Redis server running on localhost:6379

---

## Prerequisites Check

```bash
# 1. Check if Redis is installed
redis-cli ping
# Expected: PONG

# 2. If not installed, start Redis via Docker
docker run -d \
  --name mcp-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v mcp-redis-data:/data \
  redis:7 redis-server --appendonly yes

# 3. Verify RedisManager is available
python3 -c "from shared.memory import RedisManager; r = RedisManager(); print('OK')"
# Expected: OK
```

---

## Step 1: Modify WorkflowState Class (1 hour)

**File**: `/home/coolhand/shared/mcp/unified_server.py`

### 1.1 Add Redis Import (Line 27)

```python
# Add after other imports
from memory import RedisManager
```

### 1.2 Update __init__ Method (Line 64)

```python
class WorkflowState:
    """State management for running workflows with Redis persistence."""

    def __init__(self, redis_enabled=True, redis_host=None, redis_port=None):
        """
        Initialize workflow state manager.

        Args:
            redis_enabled: Enable Redis persistence (default: True)
            redis_host: Redis host (default: from env or localhost)
            redis_port: Redis port (default: from env or 6379)
        """
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: Dict[str, OrchestratorResult] = {}
        self.max_completed_retention = 100

        # Redis integration
        self.redis = None
        self.redis_enabled = redis_enabled

        if redis_enabled:
            try:
                self.redis = RedisManager(host=redis_host, port=redis_port)
                logger.info("✓ Redis connected - persistent state enabled")

                # Restore state from Redis on startup
                self._restore_from_redis()

            except Exception as e:
                logger.warning(f"⚠ Redis unavailable: {e}")
                logger.warning("→ Falling back to in-memory-only mode")
                self.redis_enabled = False
```

### 1.3 Add State Restoration (New Method)

```python
def _restore_from_redis(self):
    """Restore workflow state from Redis on server restart."""
    if not self.redis:
        return

    try:
        # Restore active workflows
        active_task_ids = self.redis.client.smembers("workflows:active")
        for task_id in active_task_ids:
            workflow_data = self.redis.get(f"workflow:{task_id}")
            if workflow_data:
                self.active_workflows[task_id] = workflow_data
                logger.info(f"↻ Restored active workflow: {task_id}")

        # Restore completed workflows (last 100)
        completed_task_ids = self.redis.client.zrevrange("results:by_time", 0, 99)
        for task_id in completed_task_ids:
            result_data = self.redis.get(f"result:{task_id}")
            if result_data:
                # Convert dict back to OrchestratorResult
                # TODO: Implement OrchestratorResult.from_dict() method
                self.completed_workflows[task_id] = result_data
                logger.info(f"↻ Restored completed workflow: {task_id}")

        logger.info(f"✓ Restored {len(self.active_workflows)} active, {len(self.completed_workflows)} completed")

    except Exception as e:
        logger.error(f"Error restoring from Redis: {e}")
```

### 1.4 Update create_workflow Method (Line 70)

```python
def create_workflow(
    self,
    task_id: str,
    orchestrator_type: str,
    task: str,
    config: OrchestratorConfig
) -> Dict[str, Any]:
    """Create new workflow state entry with Redis persistence."""

    workflow_info = {
        'task_id': task_id,
        'orchestrator_type': orchestrator_type,
        'task': task,
        'status': TaskStatus.PENDING,
        'created_at': datetime.utcnow().isoformat(),
        'started_at': None,
        'completed_at': None,
        'config': config.to_dict(),
        'error': None
    }

    # Write to memory (fast access)
    self.active_workflows[task_id] = workflow_info

    # Write to Redis (persistent)
    if self.redis_enabled and self.redis:
        try:
            # Store workflow data
            self.redis.set(
                f"workflow:{task_id}",
                workflow_info,
                ttl=86400  # 24 hour TTL
            )

            # Add to active set
            self.redis.client.sadd("workflows:active", task_id)

            # Track by orchestrator type
            self.redis.client.sadd(f"workflows:type:{orchestrator_type}", task_id)

            logger.debug(f"✓ Workflow {task_id} persisted to Redis")

        except Exception as e:
            logger.error(f"⚠ Redis write failed for {task_id}: {e}")
            # Continue anyway - we have in-memory copy

    return workflow_info
```

### 1.5 Update complete_workflow Method (Line 130)

```python
def complete_workflow(self, task_id: str, result: OrchestratorResult):
    """Mark workflow as completed and store result with Redis persistence."""

    if task_id in self.active_workflows:
        # Update status in memory
        self.update_workflow_status(task_id, result.status)
        self.completed_workflows[task_id] = result

        # Persist to Redis
        if self.redis_enabled and self.redis:
            try:
                # Store result
                result_dict = result.to_dict()
                self.redis.set(
                    f"result:{task_id}",
                    result_dict,
                    ttl=86400 * 7  # 7 day retention
                )

                # Update indexes
                self.redis.client.srem("workflows:active", task_id)
                self.redis.client.sadd("workflows:completed", task_id)

                # Add to time-sorted set for FIFO cleanup
                timestamp = time.time()
                self.redis.client.zadd("results:by_time", {task_id: timestamp})

                # Cleanup: keep only last 100 in sorted set
                total_count = self.redis.client.zcard("results:by_time")
                if total_count > 100:
                    # Remove oldest entries
                    to_remove = total_count - 100
                    old_task_ids = self.redis.client.zrange("results:by_time", 0, to_remove - 1)

                    # Delete old results
                    for old_task_id in old_task_ids:
                        self.redis.delete(f"result:{old_task_id}")
                        logger.debug(f"♻ Cleaned up old result: {old_task_id}")

                    # Remove from sorted set
                    self.redis.client.zremrangebyrank("results:by_time", 0, to_remove - 1)

                logger.info(f"✓ Result {task_id} persisted to Redis (7-day retention)")

            except Exception as e:
                logger.error(f"⚠ Redis result write failed for {task_id}: {e}")

        # Cleanup old in-memory workflows (FIXED BUG!)
        if len(self.completed_workflows) > self.max_completed_retention:
            # Sort by completion timestamp (not execution_time!)
            oldest_task_id = min(
                self.completed_workflows.keys(),
                key=lambda tid: self.active_workflows.get(tid, {}).get('completed_at', '')
            )
            del self.completed_workflows[oldest_task_id]
            logger.debug(f"♻ Evicted old workflow from memory: {oldest_task_id}")
```

### 1.6 Update get_workflow_result Method (Line 155)

```python
def get_workflow_result(self, task_id: str) -> Optional[OrchestratorResult]:
    """Get workflow result with Redis fallback."""

    # Try memory cache first
    if task_id in self.completed_workflows:
        logger.debug(f"↻ Result cache hit (memory): {task_id}")
        return self.completed_workflows[task_id]

    # Try Redis
    if self.redis_enabled and self.redis:
        try:
            result_dict = self.redis.get(f"result:{task_id}")
            if result_dict:
                logger.info(f"↻ Result cache hit (Redis): {task_id}")

                # Warm memory cache
                # TODO: Convert dict to OrchestratorResult object
                # self.completed_workflows[task_id] = OrchestratorResult.from_dict(result_dict)

                return result_dict  # Return dict for now

        except Exception as e:
            logger.error(f"⚠ Redis read failed for {task_id}: {e}")

    logger.debug(f"✗ Result not found: {task_id}")
    return None
```

---

## Step 2: Add from_dict() Method to OrchestratorResult (30 min)

**File**: `/home/coolhand/shared/orchestration/models.py`

### 2.1 Add Classmethod (After line 198)

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'OrchestratorResult':
    """
    Reconstruct OrchestratorResult from dictionary.

    Used for deserializing from Redis/database storage.

    Args:
        data: Dictionary from to_dict()

    Returns:
        OrchestratorResult instance
    """
    # Reconstruct agent results
    agent_results = [
        AgentResult(
            agent_id=r['agent_id'],
            agent_type=AgentType(r['agent_type']),
            subtask_id=r['subtask_id'],
            content=r['content'],
            status=TaskStatus(r['status']),
            execution_time=r['execution_time'],
            cost=r['cost'],
            metadata=r.get('metadata', {}),
            error=r.get('error'),
            citations=r.get('citations', [])
        )
        for r in data.get('agent_results', [])
    ]

    # Reconstruct synthesis results
    synthesis_results = [
        SynthesisResult(
            synthesis_id=s['synthesis_id'],
            synthesis_level=s['synthesis_level'],
            content=s['content'],
            source_agent_ids=s['source_agent_ids'],
            execution_time=s['execution_time'],
            cost=s['cost'],
            metadata=s.get('metadata', {})
        )
        for s in data.get('synthesis_results', [])
    ]

    return cls(
        task_id=data['task_id'],
        title=data['title'],
        status=TaskStatus(data['status']),
        agent_results=agent_results,
        synthesis_results=synthesis_results,
        final_synthesis=data.get('final_synthesis'),
        execution_time=data['execution_time'],
        total_cost=data['total_cost'],
        metadata=data.get('metadata', {}),
        generated_documents=data.get('generated_documents', []),
        artifacts=data.get('artifacts', []),
        error=data.get('error')
    )
```

### 2.2 Update get_workflow_result to Use from_dict

**File**: `/home/coolhand/shared/mcp/unified_server.py` (Line 155)

```python
def get_workflow_result(self, task_id: str) -> Optional[OrchestratorResult]:
    """Get workflow result with Redis fallback."""

    # Try memory cache first
    if task_id in self.completed_workflows:
        return self.completed_workflows[task_id]

    # Try Redis
    if self.redis_enabled and self.redis:
        try:
            result_dict = self.redis.get(f"result:{task_id}")
            if result_dict:
                # Convert dict to OrchestratorResult object
                result = OrchestratorResult.from_dict(result_dict)

                # Warm memory cache
                self.completed_workflows[task_id] = result

                logger.info(f"↻ Result loaded from Redis: {task_id}")
                return result

        except Exception as e:
            logger.error(f"⚠ Redis read failed for {task_id}: {e}")

    return None
```

---

## Step 3: Update UnifiedMCPServer Initialization (15 min)

**File**: `/home/coolhand/shared/mcp/unified_server.py`

### 3.1 Add Redis Config Parameters (Line 189)

```python
def __init__(
    self,
    config_manager: Optional[ConfigManager] = None,
    streaming_bridge: Optional[StreamingBridge] = None,
    webhook_manager: Optional[WebhookManager] = None,
    tool_registry: Optional[ToolRegistry] = None,
    redis_enabled: bool = True,  # NEW
    redis_host: Optional[str] = None,  # NEW
    redis_port: Optional[int] = None   # NEW
):
    """Initialize unified MCP server with optional Redis persistence."""

    self.config = config_manager or ConfigManager(app_name='mcp_orchestrator')
    self.streaming_bridge = streaming_bridge or get_streaming_bridge()
    self.webhook_manager = webhook_manager or get_webhook_manager()
    self.tool_registry = tool_registry or get_tool_registry()

    # NEW: Initialize WorkflowState with Redis
    self.workflow_state = WorkflowState(
        redis_enabled=redis_enabled,
        redis_host=redis_host,
        redis_port=redis_port
    )

    # Provider cache for orchestrators
    self.provider_cache = {}
```

---

## Step 4: Add Environment Variables (5 min)

**File**: `/home/coolhand/shared/mcp/.env` (create if not exists)

```bash
# Redis Configuration
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MCP Server
PORT=5060
DEBUG=false

# API Keys (reference from /home/coolhand/API_KEYS.md)
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Update app.py to Read Env Vars (Line 79)

```python
# Initialize MCP server with Redis config
redis_enabled = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

mcp_server = UnifiedMCPServer(
    redis_enabled=redis_enabled,
    redis_host=redis_host,
    redis_port=redis_port
)

logger.info(f"MCP Server initialized (Redis: {'enabled' if redis_enabled else 'disabled'})")
```

---

## Step 5: Add Analytics Endpoints (1 hour)

**File**: `/home/coolhand/shared/mcp/app.py`

### 5.1 Workflow Statistics Endpoint (After line 124)

```python
@app.route('/analytics/workflows')
def analytics_workflows():
    """Get workflow statistics from Redis."""

    redis = mcp_server.workflow_state.redis

    if not redis:
        return jsonify({
            'error': 'Redis not available',
            'message': 'Analytics require Redis persistence'
        }), 503

    try:
        # Count by status
        active_count = redis.client.scard("workflows:active")
        completed_count = redis.client.scard("workflows:completed")

        # Recent workflows (last 24 hours)
        now = time.time()
        yesterday = now - 86400
        recent_task_ids = redis.client.zrangebyscore(
            "results:by_time",
            yesterday,
            now
        )

        # Count by orchestrator type
        beltalowda_count = redis.client.scard("workflows:type:beltalowda")
        swarm_count = redis.client.scard("workflows:type:swarm")

        return jsonify({
            'active_workflows': active_count,
            'completed_workflows': completed_count,
            'recent_24h': len(recent_task_ids),
            'by_type': {
                'beltalowda': beltalowda_count,
                'swarm': swarm_count
            },
            'recent_task_ids': recent_task_ids[:20]  # Last 20
        })

    except Exception as e:
        logger.exception(f"Analytics error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/analytics/costs')
def analytics_costs():
    """Calculate costs from completed workflows."""

    workflows = mcp_server.workflow_state.completed_workflows

    if not workflows:
        return jsonify({
            'total_cost_usd': 0.0,
            'average_cost_usd': 0.0,
            'workflow_count': 0
        })

    total_cost = sum(w.total_cost for w in workflows.values())
    avg_cost = total_cost / len(workflows)

    # Find most expensive
    most_expensive = max(workflows.values(), key=lambda w: w.total_cost)

    return jsonify({
        'total_cost_usd': round(total_cost, 4),
        'average_cost_usd': round(avg_cost, 4),
        'workflow_count': len(workflows),
        'most_expensive': {
            'task_id': most_expensive.task_id,
            'cost': round(most_expensive.total_cost, 4),
            'execution_time': round(most_expensive.execution_time, 2)
        }
    })
```

---

## Step 6: Testing (1 hour)

### 6.1 Unit Tests

**File**: `/home/coolhand/shared/mcp/test_redis_persistence.py` (create new)

```python
#!/usr/bin/env python3
"""
Test Redis persistence for WorkflowState.

Run: python test_redis_persistence.py
"""

import sys
sys.path.insert(0, '/home/coolhand/shared')

from mcp.unified_server import WorkflowState
from orchestration import BeltalowdaConfig, OrchestratorResult, TaskStatus, AgentResult, AgentType

def test_workflow_persistence():
    """Test that workflows persist to Redis and can be restored."""

    print("🧪 Testing Redis persistence...")

    # Create WorkflowState with Redis
    state = WorkflowState(redis_enabled=True)

    if not state.redis:
        print("❌ Redis not available. Skipping test.")
        return

    # Create test workflow
    task_id = "test_workflow_12345"
    config = BeltalowdaConfig()

    workflow = state.create_workflow(
        task_id=task_id,
        orchestrator_type="beltalowda",
        task="Test research task",
        config=config
    )

    print(f"✓ Created workflow: {task_id}")

    # Verify in Redis
    redis_data = state.redis.get(f"workflow:{task_id}")
    assert redis_data is not None, "Workflow not found in Redis!"
    print(f"✓ Workflow persisted to Redis")

    # Verify in active set
    is_active = state.redis.client.sismember("workflows:active", task_id)
    assert is_active, "Workflow not in active set!"
    print(f"✓ Workflow in active set")

    # Complete workflow
    result = OrchestratorResult(
        task_id=task_id,
        title="Test Result",
        status=TaskStatus.COMPLETED,
        agent_results=[
            AgentResult(
                agent_id="agent_1",
                agent_type=AgentType.WORKER,
                subtask_id="subtask_1",
                content="Test content",
                cost=0.01,
                execution_time=1.5
            )
        ],
        final_synthesis="Test synthesis",
        execution_time=5.0,
        total_cost=0.05
    )

    state.complete_workflow(task_id, result)
    print(f"✓ Completed workflow: {task_id}")

    # Verify result in Redis
    redis_result = state.redis.get(f"result:{task_id}")
    assert redis_result is not None, "Result not found in Redis!"
    print(f"✓ Result persisted to Redis")

    # Verify in time-sorted set
    score = state.redis.client.zscore("results:by_time", task_id)
    assert score is not None, "Result not in time-sorted set!"
    print(f"✓ Result in time-sorted set (score: {score})")

    # Test retrieval
    retrieved = state.get_workflow_result(task_id)
    assert retrieved is not None, "Failed to retrieve result!"
    print(f"✓ Retrieved result from Redis")

    # Cleanup
    state.redis.delete(f"workflow:{task_id}")
    state.redis.delete(f"result:{task_id}")
    state.redis.client.srem("workflows:active", task_id)
    state.redis.client.srem("workflows:completed", task_id)
    state.redis.client.zrem("results:by_time", task_id)
    print(f"✓ Cleaned up test data")

    print("\n✅ All tests passed!")


if __name__ == '__main__':
    test_workflow_persistence()
```

### 6.2 Integration Test

```bash
# 1. Start Redis
docker start mcp-redis || docker run -d --name mcp-redis -p 6379:6379 redis:7

# 2. Run unit test
cd /home/coolhand/shared/mcp
python test_redis_persistence.py

# 3. Start MCP server
python app.py

# 4. In another terminal, create test workflow
curl -X POST http://localhost:5060/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Test Redis persistence",
    "num_agents": 2
  }'

# Expected response:
# {
#   "success": true,
#   "task_id": "research_abc123...",
#   "status": "running",
#   ...
# }

# 5. Check Redis directly
redis-cli KEYS "workflow:*"
redis-cli SMEMBERS "workflows:active"

# 6. Restart server to test state restoration
# Press Ctrl+C to stop server, then restart
python app.py

# Check logs for:
# "↻ Restored active workflow: research_abc123..."

# 7. Test analytics endpoint
curl http://localhost:5060/analytics/workflows

# Expected:
# {
#   "active_workflows": 1,
#   "completed_workflows": 0,
#   "recent_24h": 0,
#   ...
# }
```

---

## Step 7: Deploy to Production (30 min)

### 7.1 Update Service Manager

**File**: `/home/coolhand/service_manager.py`

```python
# Add Redis dependency to mcp-server service
{
    "name": "mcp-server",
    "type": "flask",
    "path": "/home/coolhand/shared/mcp",
    "file": "app.py",
    "port": 5060,
    "dependencies": ["redis"],  # NEW
    ...
}
```

### 7.2 Update Docker Compose (Optional)

**File**: `/home/coolhand/shared/mcp/docker-compose.yml` (create new)

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: mcp-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  mcp-server:
    build: .
    container_name: mcp-server
    ports:
      - "5060:5060"
    environment:
      - REDIS_ENABLED=true
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - PORT=5060
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis-data:
```

### 7.3 Restart Services

```bash
# Start Redis
sudo systemctl start redis
# or
docker start mcp-redis

# Restart MCP server
sm restart mcp-server

# Verify
curl http://localhost:5060/health
# Should show Redis stats in response
```

---

## Step 8: Monitoring & Verification (15 min)

### 8.1 Check Redis Memory Usage

```bash
redis-cli INFO memory | grep used_memory_human
# Example: used_memory_human:2.45M
```

### 8.2 Monitor Workflow Keys

```bash
# Count total workflow keys
redis-cli DBSIZE

# List all workflow keys
redis-cli KEYS "workflow:*" | wc -l

# Check specific workflow
redis-cli GET "workflow:research_abc123"
```

### 8.3 Check Logs

```bash
tail -f /var/log/mcp-server.log | grep -E "(Redis|↻|✓|⚠)"
# Look for:
# - "✓ Redis connected"
# - "↻ Restored active workflow"
# - "✓ Workflow persisted to Redis"
```

---

## Rollback Plan

If issues occur, disable Redis quickly:

```bash
# Option 1: Environment variable
export REDIS_ENABLED=false
sm restart mcp-server

# Option 2: Kill Redis (server will fall back to memory-only)
docker stop mcp-redis

# Option 3: Code change
# Edit /home/coolhand/shared/mcp/app.py, line 79:
redis_enabled = False  # Force disable
```

---

## Success Criteria

✅ **All must pass**:

1. [ ] Server starts without errors
2. [ ] Workflows persist to Redis (check with `redis-cli KEYS "workflow:*"`)
3. [ ] Server restart restores active workflows
4. [ ] Completed results retrievable after 7 days (within TTL)
5. [ ] Analytics endpoints return data
6. [ ] No memory leaks (monitor with `ps aux | grep app.py`)
7. [ ] Latency impact < 10ms (measure with `time curl ...`)

---

## Performance Benchmarks

**Before Redis** (baseline):
- Create workflow: ~1ms
- Complete workflow: ~2ms
- Get result: ~0.1ms (memory lookup)

**After Redis** (expected):
- Create workflow: ~5ms (+4ms for Redis write)
- Complete workflow: ~8ms (+6ms for Redis write + index updates)
- Get result (cache hit): ~0.1ms (memory)
- Get result (cache miss): ~3ms (Redis read)

**Acceptable overhead**: < 10ms per operation

---

## Troubleshooting

### Error: "Redis unavailable"

```bash
# Check if Redis is running
redis-cli ping

# If not, start it
docker start mcp-redis

# Check connectivity
telnet localhost 6379
```

### Error: "MISCONF Redis is configured to save RDB snapshots"

```bash
# Fix Redis config
redis-cli CONFIG SET stop-writes-on-bgsave-error no
```

### High Memory Usage

```bash
# Check Redis memory
redis-cli INFO memory

# Flush old data (WARNING: data loss!)
redis-cli FLUSHDB

# Or reduce TTLs in code (e.g., 3 days instead of 7)
```

---

## Next Steps After Redis Integration

1. **Add PostgreSQL for long-term storage** (see DATA_FLOW_ANALYSIS.md Section 8)
2. **Implement Redis Streams for SSE** (replace asyncio.Queue)
3. **Add distributed locks for multi-instance support**
4. **Build Grafana dashboard for analytics**
5. **Set up Redis backup/replication**

---

**Total Time**: ~4 hours
**Difficulty**: Medium
**Impact**: High - Eliminates data loss on server restart
**Author**: Luke Steuber
**Last Updated**: 2025-11-18
