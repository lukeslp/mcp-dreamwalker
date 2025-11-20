# MCP Orchestrator - Quick Fixes & Actionable Improvements

**Author:** Luke Steuber
**Date:** 2025-11-18

## Overview

This document highlights the most critical, actionable fixes that can be implemented quickly to significantly improve the MCP Orchestrator Server's reliability and production-readiness.

---

## 1. Fix Task Lifecycle Management (30 minutes)

**Problem:** Fire-and-forget tasks can't be properly cancelled or monitored.

**Current Code:** `unified_server.py:392-394`
```python
asyncio.create_task(
    self._execute_orchestrator(orchestrator, task, title, task_id)
)
```

**Fixed Code:**
```python
class UnifiedMCPServer:
    def __init__(self, ...):
        # Add task tracking
        self.active_tasks: Dict[str, asyncio.Task] = {}

    async def tool_orchestrate_research(self, arguments: Dict[str, Any]):
        # ... existing validation ...

        # Create and track task
        task = asyncio.create_task(
            self._execute_orchestrator(orchestrator, task, title, task_id)
        )
        self.active_tasks[task_id] = task

        # Auto-cleanup on completion
        def cleanup_task(t):
            self.active_tasks.pop(task_id, None)
            if t.exception():
                logger.error(f"Task {task_id} failed: {t.exception()}")

        task.add_done_callback(cleanup_task)

        return {...}

    async def tool_cancel_orchestration(self, arguments: Dict[str, Any]):
        task_id = arguments.get('task_id')

        # Actually cancel the task
        task = self.active_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Update state
        cancelled = self.workflow_state.cancel_workflow(task_id)
        await self.streaming_bridge.close_stream(task_id)

        return {"success": True, "task_id": task_id, "cancelled": cancelled}
```

**Impact:** Fixes memory leaks, enables proper cancellation, improves error tracking.

---

## 2. Add Thread Safety to WorkflowState (20 minutes)

**Problem:** Multi-worker deployments have race conditions accessing shared state.

**Current Code:** `unified_server.py:57-179`
```python
class WorkflowState:
    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: Dict[str, OrchestratorResult] = {}
        # NO LOCKS!
```

**Fixed Code:**
```python
import threading
from collections import OrderedDict

class WorkflowState:
    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.completed_workflows: OrderedDict[str, OrchestratorResult] = OrderedDict()
        self.max_completed_retention = 100
        self._lock = threading.RLock()  # Reentrant lock

    def create_workflow(self, task_id, orchestrator_type, task, config):
        with self._lock:
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
            self.active_workflows[task_id] = workflow_info
            return workflow_info

    def update_workflow_status(self, task_id, status, error=None):
        with self._lock:
            if task_id in self.active_workflows:
                self.active_workflows[task_id]['status'] = status

                if status == TaskStatus.RUNNING and not self.active_workflows[task_id]['started_at']:
                    self.active_workflows[task_id]['started_at'] = datetime.utcnow().isoformat()

                if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    self.active_workflows[task_id]['completed_at'] = datetime.utcnow().isoformat()

                if error:
                    self.active_workflows[task_id]['error'] = error

    def complete_workflow(self, task_id, result):
        with self._lock:
            if task_id in self.active_workflows:
                self.update_workflow_status(task_id, result.status)
                self.completed_workflows[task_id] = result
                self.completed_workflows.move_to_end(task_id)

                # Remove oldest efficiently (O(1))
                while len(self.completed_workflows) > self.max_completed_retention:
                    self.completed_workflows.popitem(last=False)

    def get_workflow_info(self, task_id):
        with self._lock:
            return self.active_workflows.get(task_id)

    def get_workflow_result(self, task_id):
        with self._lock:
            return self.completed_workflows.get(task_id)
```

**Impact:** Prevents race conditions, data corruption, and intermittent 404 errors.

---

## 3. Add Workflow Timeout Protection (15 minutes)

**Problem:** Workflows can run indefinitely if agents hang.

**Current Code:** `base_orchestrator.py:190-312`
```python
async def execute_workflow(self, task, title, context, stream_callback):
    # ... no overall timeout ...
```

**Fixed Code:**
```python
async def execute_workflow(self, task, title, context, stream_callback):
    # Calculate reasonable timeout
    workflow_timeout = getattr(self.config, 'workflow_timeout', None)
    if not workflow_timeout:
        # Default: num_agents × timeout_per_agent × 1.5 buffer
        workflow_timeout = self.config.num_agents * self.config.timeout_seconds * 1.5

    logger.info(f"Workflow timeout set to {workflow_timeout}s")

    try:
        return await asyncio.wait_for(
            self._execute_workflow_inner(task, title, context, stream_callback),
            timeout=workflow_timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Workflow timeout after {workflow_timeout}s")

        await self._emit_event(EventType.WORKFLOW_ERROR, {
            "error": f"Workflow exceeded maximum time limit ({workflow_timeout}s)"
        })

        return OrchestratorResult(
            task_id=self.task_id,
            title=title or task[:100],
            status=TaskStatus.FAILED,
            error=f"Workflow timeout after {workflow_timeout}s",
            execution_time=workflow_timeout,
            total_cost=self.total_cost
        )

async def _execute_workflow_inner(self, task, title, context, stream_callback):
    """Original execute_workflow logic extracted"""
    # Move all current execute_workflow code here
    self.task_id = str(uuid.uuid4())
    self.start_time = time.time()
    # ... rest of implementation ...
```

**Impact:** Prevents runaway workflows, improves resource management.

---

## 4. Improve Error Streaming (10 minutes)

**Problem:** Errors in fire-and-forget tasks don't reach clients.

**Current Code:** `unified_server.py:316-325`
```python
except Exception as e:
    logger.exception(f"Error executing orchestrator: {e}")
    self.workflow_state.update_workflow_status(task_id, TaskStatus.FAILED, str(e))
    await self.streaming_bridge.close_stream(task_id)
    raise  # Exception gets lost in create_task
```

**Fixed Code:**
```python
async def _execute_orchestrator(self, orchestrator, task, title, task_id, context=None):
    try:
        self.workflow_state.update_workflow_status(task_id, TaskStatus.RUNNING)
        stream_callback = self._create_stream_callback(task_id)

        result = await orchestrator.execute_workflow(
            task=task,
            title=title,
            context=context,
            stream_callback=stream_callback
        )

        self.workflow_state.complete_workflow(task_id, result)
        await self.streaming_bridge.close_stream(task_id)
        return result

    except Exception as e:
        logger.exception(f"Error executing orchestrator: {e}")

        # Update state
        self.workflow_state.update_workflow_status(task_id, TaskStatus.FAILED, str(e))

        # CRITICAL: Stream error to client before closing
        try:
            error_event = {
                'event_type': 'workflow_error',
                'task_id': task_id,
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            }
            await self.streaming_bridge.push_event(task_id, error_event)

            # Give client time to receive error
            await asyncio.sleep(0.5)

        except Exception as stream_error:
            logger.error(f"Failed to stream error: {stream_error}")

        finally:
            await self.streaming_bridge.close_stream(task_id)

        # Don't re-raise - error is handled and logged
        return OrchestratorResult(
            task_id=task_id,
            title=title,
            status=TaskStatus.FAILED,
            error=str(e),
            execution_time=time.time() - self.start_time if self.start_time else 0,
            total_cost=self.total_cost
        )
```

**Impact:** Clients receive error notifications, better debugging.

---

## 5. Add Provider Error Handling (15 minutes)

**Problem:** Provider initialization errors cause cryptic failures.

**Current Code:** `unified_server.py:214-241`
```python
def _get_provider(self, provider_name='xai', model=None):
    # ... no error handling around ProviderFactory ...
    provider = ProviderFactory.create_provider(...)
```

**Fixed Code:**
```python
def _get_provider(self, provider_name='xai', model=None):
    cache_key = f"{provider_name}:{model or 'default'}"

    if cache_key in self.provider_cache:
        return self.provider_cache[cache_key]

    try:
        api_key = self.config.get_api_key(provider_name)
        if not api_key:
            raise ValueError(
                f"No API key configured for provider: {provider_name}. "
                f"Set {provider_name.upper()}_API_KEY in environment."
            )

        logger.info(f"Initializing provider: {provider_name} (model: {model or 'default'})")

        provider = ProviderFactory.create_provider(
            provider_name=provider_name,
            api_key=api_key,
            model=model
        )

        # Validate provider is usable
        if not hasattr(provider, 'chat'):
            raise RuntimeError(
                f"Provider {provider_name} missing required 'chat' method"
            )

        self.provider_cache[cache_key] = provider
        logger.info(f"Provider {provider_name} initialized successfully")
        return provider

    except ImportError as e:
        raise RuntimeError(
            f"Provider {provider_name} not available. "
            f"Install required dependencies: pip install {provider_name}"
        ) from e

    except Exception as e:
        logger.error(f"Failed to initialize provider {provider_name}: {e}")
        raise RuntimeError(
            f"Provider initialization failed ({provider_name}): {str(e)}"
        ) from e
```

**Impact:** Clear error messages, easier troubleshooting, prevents cascade failures.

---

## 6. Add Input Validation (25 minutes)

**Problem:** No validation of user inputs, can cause runtime errors.

**Installation:**
```bash
cd /home/coolhand/shared/mcp
source venv/bin/activate
pip install pydantic
```

**New File:** `unified_server.py` (add after imports)
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ResearchRequest(BaseModel):
    task: str = Field(..., min_length=10, max_length=5000, description="Research task")
    title: Optional[str] = Field(None, max_length=200)
    num_agents: int = Field(8, ge=1, le=20)
    enable_drummer: bool = Field(True)
    enable_camina: bool = Field(True)
    generate_documents: bool = Field(True)
    document_formats: List[str] = Field(['markdown'])
    provider_name: str = Field('xai', regex='^[a-z_]+$')
    model: Optional[str] = None
    webhook_url: Optional[str] = Field(None, regex=r'^https?://')

    @validator('task')
    def sanitize_task(cls, v):
        return v.strip()

    @validator('document_formats')
    def validate_formats(cls, v):
        valid_formats = {'pdf', 'docx', 'markdown'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}. Must be one of {valid_formats}")
        return v


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000)
    title: Optional[str] = Field(None, max_length=200)
    num_agents: int = Field(5, ge=1, le=20)
    allowed_agent_types: Optional[List[str]] = None
    generate_documents: bool = Field(True)
    document_formats: List[str] = Field(['markdown'])
    provider_name: str = Field('xai')
    model: Optional[str] = None
    webhook_url: Optional[str] = None


class StatusRequest(BaseModel):
    task_id: str = Field(..., regex='^[a-z_]+_[a-f0-9]{12}$')
```

**Updated Tool Methods:**
```python
async def tool_orchestrate_research(self, arguments: Dict[str, Any]):
    try:
        # Validate input
        request = ResearchRequest(**arguments)
    except ValidationError as e:
        return {
            "success": False,
            "error": "Invalid request",
            "validation_errors": e.errors()
        }

    # Use validated request
    title = request.title or f"Research: {request.task[:50]}..."

    config = BeltalowdaConfig(
        num_agents=request.num_agents,
        enable_drummer=request.enable_drummer,
        enable_camina=request.enable_camina,
        generate_documents=request.generate_documents,
        document_formats=request.document_formats,
        parallel_execution=True
    )

    # ... rest of implementation using request.* instead of arguments.get() ...
```

**Impact:** Prevents invalid inputs, better error messages, type safety.

---

## 7. Add Graceful Shutdown (20 minutes)

**Problem:** Active workflows terminate abruptly on restart.

**Add to:** `app.py`
```python
import signal
import asyncio

# Track shutdown state
shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    shutdown_event.set()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


async def graceful_shutdown():
    """Shutdown handler for async cleanup"""
    logger.info("Starting graceful shutdown...")

    # Cancel all active workflows
    if hasattr(mcp_server, 'active_tasks'):
        logger.info(f"Cancelling {len(mcp_server.active_tasks)} active workflows...")

        for task_id, task in mcp_server.active_tasks.items():
            if not task.done():
                logger.info(f"Cancelling workflow {task_id}")
                task.cancel()

        # Wait for cancellation with timeout
        if mcp_server.active_tasks:
            await asyncio.wait(
                mcp_server.active_tasks.values(),
                timeout=30,
                return_when=asyncio.ALL_COMPLETED
            )

    # Close all streams
    logger.info("Closing active streams...")
    for task_id in list(mcp_server.workflow_state.active_workflows.keys()):
        await mcp_server.streaming_bridge.close_stream(task_id)

    # Stop cleanup loops
    await mcp_server.streaming_bridge.stop_cleanup_loop()

    logger.info("Graceful shutdown complete")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5060))

    logger.info(f"Starting MCP Orchestrator Server on port {port}")

    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('DEBUG', 'False').lower() == 'true'
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Run graceful shutdown
        asyncio.run(graceful_shutdown())
```

**Impact:** Clean shutdowns, no orphaned resources, better log messages.

---

## 8. Add Basic Metrics (15 minutes)

**Problem:** No visibility into system performance.

**Add to:** `unified_server.py`
```python
from collections import defaultdict
import time

class Metrics:
    def __init__(self):
        self.workflow_count = defaultdict(int)  # by orchestrator_type
        self.workflow_errors = defaultdict(int)  # by orchestrator_type
        self.workflow_durations = defaultdict(list)  # by orchestrator_type
        self.total_cost = 0.0

    def record_workflow(self, orchestrator_type, status, duration, cost):
        self.workflow_count[orchestrator_type] += 1
        if status == 'failed':
            self.workflow_errors[orchestrator_type] += 1
        self.workflow_durations[orchestrator_type].append(duration)
        self.total_cost += cost

    def get_stats(self):
        stats = {
            'total_workflows': sum(self.workflow_count.values()),
            'total_errors': sum(self.workflow_errors.values()),
            'total_cost': round(self.total_cost, 2),
            'by_orchestrator': {}
        }

        for orch_type in self.workflow_count:
            durations = self.workflow_durations[orch_type]
            stats['by_orchestrator'][orch_type] = {
                'count': self.workflow_count[orch_type],
                'errors': self.workflow_errors[orch_type],
                'avg_duration': round(sum(durations) / len(durations), 2) if durations else 0,
                'min_duration': round(min(durations), 2) if durations else 0,
                'max_duration': round(max(durations), 2) if durations else 0
            }

        return stats

# Add to UnifiedMCPServer
class UnifiedMCPServer:
    def __init__(self, ...):
        # ... existing code ...
        self.metrics = Metrics()

    async def _execute_orchestrator(self, orchestrator, task, title, task_id, context=None):
        start_time = time.time()
        orchestrator_type = orchestrator.__class__.__name__

        try:
            # ... existing execution logic ...

            duration = time.time() - start_time
            self.metrics.record_workflow(
                orchestrator_type,
                'success',
                duration,
                result.total_cost
            )
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_workflow(
                orchestrator_type,
                'failed',
                duration,
                0.0
            )
            # ... existing error handling ...
```

**Add Endpoint:** `app.py`
```python
@app.route('/metrics')
def metrics():
    """Get server metrics"""
    return jsonify({
        'uptime': time.time() - start_time,
        'workflows': mcp_server.metrics.get_stats(),
        'active_workflows': len(mcp_server.workflow_state.active_workflows),
        'streaming': {
            'active_streams': len(mcp_server.streaming_bridge.active_streams),
            'registered_webhooks': len(mcp_server.webhook_manager.registered_webhooks)
        }
    })
```

**Impact:** Performance monitoring, cost tracking, debugging insights.

---

## Implementation Checklist

### Phase 1: Critical Fixes (2 hours)
- [ ] Fix task lifecycle management (Issue 1)
- [ ] Add thread safety to WorkflowState (Issue 2)
- [ ] Add workflow timeout protection (Issue 3)
- [ ] Improve error streaming (Issue 4)

### Phase 2: Stability Improvements (1.5 hours)
- [ ] Add provider error handling (Issue 5)
- [ ] Add input validation (Issue 6)
- [ ] Add graceful shutdown (Issue 7)

### Phase 3: Observability (30 minutes)
- [ ] Add basic metrics (Issue 8)

### Testing After Implementation
```bash
# 1. Test cancellation
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{"task": "Long running research task"}'
# Get task_id, then:
curl -X POST https://dr.eamer.dev/mcp/tools/cancel_orchestration \
  -H "Content-Type: application/json" \
  -d '{"task_id": "research_abc123"}'

# 2. Test validation
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{"task": "x"}'  # Should fail validation (too short)

# 3. Test metrics
curl https://dr.eamer.dev/mcp/metrics

# 4. Test graceful shutdown
sm restart mcp-server
sm logs mcp-server | grep -i "graceful\|cancel"
```

---

## Deployment Instructions

```bash
# 1. Stop service
sm stop mcp-server

# 2. Install pydantic
cd /home/coolhand/shared/mcp
source venv/bin/activate
pip install pydantic
pip freeze > requirements.txt

# 3. Apply code changes (use the fixes above)

# 4. Restart service
sm start mcp-server

# 5. Verify
curl https://dr.eamer.dev/mcp/health
curl https://dr.eamer.dev/mcp/metrics

# 6. Monitor logs
sm logs mcp-server -f
```

---

## Expected Outcomes

After implementing these fixes:

1. **Reliability:** Proper task cancellation, no orphaned workflows
2. **Stability:** Thread-safe state management, no race conditions
3. **Safety:** Timeouts prevent runaway processes, clear error messages
4. **Visibility:** Metrics provide performance insights
5. **Maintainability:** Input validation catches bugs early
6. **Operations:** Graceful shutdown enables zero-downtime deployments

**Total Implementation Time:** ~4 hours
**Risk Level:** Low (mostly additive changes, minimal breaking changes)
**Testing Time:** ~30 minutes
**Deployment Time:** ~10 minutes

---

## Next Steps (Future Work)

After completing these quick fixes, consider:

1. **Redis Integration** - Migrate state to Redis for horizontal scaling
2. **ASGI Migration** - Switch from Gunicorn to Hypercorn
3. **Prometheus Metrics** - Full observability with Grafana dashboards
4. **API Versioning** - Add `/v1/` prefix for future compatibility
5. **Request Tracing** - Distributed tracing with request IDs
6. **Circuit Breakers** - Prevent cascade failures in provider errors

See [ARCHITECTURE_REVIEW.md](./ARCHITECTURE_REVIEW.md) for complete analysis.
