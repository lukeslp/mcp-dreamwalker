# MCP Orchestrator Server - API Reference

Complete API documentation for the MCP Orchestrator Server.

**Author:** Luke Steuber
**Base URL (Production):** `https://dr.eamer.dev/mcp`
**Base URL (Local):** `http://localhost:5060`
**Version:** 1.0.0

## Table of Contents

- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Server Information](#server-information)
  - [Orchestrator Tools](#orchestrator-tools)
  - [Workflow Management](#workflow-management)
  - [Streaming](#streaming)
  - [Webhooks](#webhooks)
  - [Tool Registry](#tool-registry)
- [Data Models](#data-models)
- [Event Types](#event-types)

## Authentication

Currently, the MCP Orchestrator Server does not require authentication for local/trusted deployments. All endpoints are publicly accessible.

**For production deployments**, consider adding authentication:

```python
# Example: API key authentication
from flask import request

@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or not verify_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
```

## Response Format

All endpoints return JSON responses.

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }  // Optional additional details
}
```

## Error Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Missing required fields, invalid parameters |
| 404 | Not Found | Invalid task_id, endpoint doesn't exist |
| 500 | Internal Server Error | Orchestrator failure, database error |
| 503 | Service Unavailable | Server overloaded, maintenance mode |

## Rate Limiting

**Current limits:**
- No enforced rate limits (trusted deployment)
- Recommended: Max 10 concurrent workflows per client
- Long-running workflows (15-30 min) may impact capacity

**To add rate limiting:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/tools/orchestrate_research', methods=['POST'])
@limiter.limit("5 per minute")
async def orchestrate_research():
    ...
```

## Endpoints

### Server Information

#### GET `/`

Get server information and available endpoints.

**Request:**
```bash
curl https://dr.eamer.dev/mcp/
```

**Response:**
```json
{
  "name": "MCP Orchestrator Server",
  "version": "1.0.0",
  "description": "Unified MCP server for orchestrator agents with SSE streaming",
  "author": "Luke Steuber",
  "endpoints": {
    "health": "/health",
    "tools": "/tools",
    "resources": "/resources",
    "orchestrate_research": "/tools/orchestrate_research",
    "orchestrate_search": "/tools/orchestrate_search",
    "stream": "/stream/{task_id}",
    "webhook_register": "/webhook/register",
    "stats": "/stats"
  },
  "orchestrators": ["beltalowda", "swarm"]
}
```

#### GET `/health`

Health check endpoint for monitoring.

**Request:**
```bash
curl https://dr.eamer.dev/mcp/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "mcp-orchestrator",
  "active_streams": 3,
  "registered_webhooks": 2,
  "timestamp": "2025-11-15T10:00:00Z"
}
```

**Health States:**
- `healthy`: All systems operational
- `degraded`: Partial functionality (e.g., Redis unavailable)
- `unhealthy`: Critical failure

#### GET `/tools`

List all available MCP tools.

**Request:**
```bash
curl https://dr.eamer.dev/mcp/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "orchestrate_research",
      "description": "Execute Beltalowda hierarchical research workflow",
      "parameters": {
        "task": {"type": "string", "required": true},
        "title": {"type": "string", "required": false},
        "num_agents": {"type": "integer", "default": 5}
      },
      "category": "orchestrator"
    },
    {
      "name": "orchestrate_search",
      "description": "Execute Swarm multi-agent search workflow",
      "parameters": {
        "query": {"type": "string", "required": true},
        "num_agents": {"type": "integer", "default": 5}
      },
      "category": "orchestrator"
    }
  ],
  "count": 7
}
```

#### GET `/resources`

List all available MCP resources.

**Request:**
```bash
curl https://dr.eamer.dev/mcp/resources
```

**Response:**
```json
{
  "resources": [
    {
      "name": "orchestrator_patterns",
      "description": "Available orchestration patterns",
      "type": "list",
      "uri": "mcp://orchestrator-patterns"
    },
    {
      "name": "workflow_templates",
      "description": "Workflow configuration templates",
      "type": "list",
      "uri": "mcp://workflow-templates"
    }
  ],
  "count": 2
}
```

### Orchestrator Tools

#### POST `/tools/orchestrate_research`

Execute Beltalowda hierarchical research workflow.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research transformer architectures in NLP",
    "title": "Transformer Architectures Review",
    "num_agents": 10,
    "enable_synthesis": true,
    "synthesis_group_size": 5,
    "generate_documents": true,
    "document_formats": ["pdf", "docx", "markdown"],
    "primary_model": "grok-3",
    "agent_model": "grok-4-fast",
    "belter_timeout": 180,
    "drummer_timeout": 240,
    "camina_timeout": 300,
    "context": {}
  }'
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task` | string | Yes | - | Research task description |
| `title` | string | No | (auto-generated) | Workflow title for documents |
| `num_agents` | integer | No | 5 | Number of Belter agents (3-20) |
| `enable_synthesis` | boolean | No | true | Enable hierarchical synthesis |
| `synthesis_group_size` | integer | No | 5 | Belters per Drummer |
| `generate_documents` | boolean | No | true | Generate PDF/DOCX/MD |
| `document_formats` | array | No | ["markdown"] | Output formats |
| `primary_model` | string | No | "grok-3" | Synthesis model |
| `agent_model` | string | No | "grok-4-fast" | Belter model |
| `belter_timeout` | integer | No | 180 | Belter timeout (seconds) |
| `drummer_timeout` | integer | No | 240 | Drummer timeout |
| `camina_timeout` | integer | No | 300 | Camina timeout |
| `parallel_execution` | boolean | No | true | Run agents in parallel |
| `max_concurrent_agents` | integer | No | 10 | Concurrency limit |
| `context` | object | No | {} | Additional context data |

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "running",
  "stream_url": "/mcp/stream/belta-20251115-abc123",
  "webhook_url": null,
  "message": "Research workflow started with 10 Belter agents",
  "estimated_completion": "2025-11-15T10:25:00Z"
}
```

**Errors:**
- `400`: Missing `task` parameter
- `400`: Invalid `num_agents` (must be 3-20)
- `500`: Orchestrator initialization failed

#### POST `/tools/orchestrate_search`

Execute Swarm multi-agent search workflow.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing breakthroughs 2024",
    "num_agents": 6,
    "agent_types": ["news", "academic", "technical"],
    "parallel_execution": true,
    "timeout_seconds": 120,
    "enable_synthesis": true,
    "context": {}
  }'
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `num_agents` | integer | No | 5 | Number of agents (1-20) |
| `agent_types` | array | No | (auto-detect) | Agent types to use |
| `parallel_execution` | boolean | No | true | Run agents in parallel |
| `timeout_seconds` | integer | No | 120 | Per-agent timeout |
| `enable_synthesis` | boolean | No | true | Synthesize results |
| `max_concurrent_agents` | integer | No | 10 | Concurrency limit |
| `context` | object | No | {} | Additional context |

**Agent Types:**
- `text`: Text content analysis
- `image`: Image search
- `video`: Video content
- `news`: Breaking news
- `academic`: Research papers
- `social`: Social media
- `product`: Product search
- `technical`: Code/docs
- `general`: General web search

**Response:**
```json
{
  "success": true,
  "task_id": "swarm-20251115-xyz789",
  "status": "running",
  "stream_url": "/mcp/stream/swarm-20251115-xyz789",
  "webhook_url": null,
  "message": "Search workflow started with 6 agents (news, academic, technical)",
  "estimated_completion": "2025-11-15T10:05:00Z"
}
```

**Errors:**
- `400`: Missing `query` parameter
- `400`: Invalid `agent_types` (unknown type)
- `500`: Orchestrator initialization failed

### Workflow Management

#### POST `/tools/get_orchestration_status`

Get status of a running or completed workflow.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/get_orchestration_status \
  -H "Content-Type: application/json" \
  -d '{"task_id": "belta-20251115-abc123"}'
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes | Task identifier |

**Response (Running):**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "running",
  "progress": {
    "current_stage": "agent_execution",
    "completed_agents": 7,
    "total_agents": 10,
    "percent_complete": 70
  },
  "started_at": "2025-11-15T10:00:00Z",
  "estimated_completion": "2025-11-15T10:25:00Z"
}
```

**Response (Completed):**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "completed",
  "result": {
    "title": "Transformer Architectures Review",
    "final_synthesis": "Comprehensive analysis of transformer architectures...",
    "agent_results": [...],
    "synthesis_results": [...],
    "generated_documents": [
      {
        "format": "pdf",
        "path": "/path/to/report.pdf",
        "size_bytes": 245678,
        "url": "https://dr.eamer.dev/mcp/download/belta-20251115-abc123/report.pdf"
      }
    ],
    "total_cost": 2.45,
    "execution_time": 1234.5
  },
  "started_at": "2025-11-15T10:00:00Z",
  "completed_at": "2025-11-15T10:20:34Z"
}
```

**Response (Failed):**
```json
{
  "success": false,
  "task_id": "belta-20251115-abc123",
  "status": "failed",
  "error": "Agent timeout after 180 seconds",
  "failed_at": "2025-11-15T10:15:00Z"
}
```

**Errors:**
- `400`: Missing `task_id`
- `404`: Task not found

#### POST `/tools/cancel_orchestration`

Cancel a running workflow.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/cancel_orchestration \
  -H "Content-Type: application/json" \
  -d '{"task_id": "belta-20251115-abc123"}'
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes | Task identifier |

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "cancelled",
  "message": "Workflow cancelled successfully",
  "partial_results": {
    "completed_agents": 3,
    "total_agents": 10
  }
}
```

**Errors:**
- `400`: Missing `task_id`
- `404`: Task not found
- `409`: Task already completed

#### POST `/tools/list_orchestrator_patterns`

List available orchestration patterns.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/list_orchestrator_patterns \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "name": "beltalowda",
      "display_name": "Beltalowda Hierarchical Research",
      "description": "3-tier synthesis: Belters → Drummers → Camina",
      "use_cases": [
        "Comprehensive research reports",
        "Literature reviews",
        "Market analysis"
      ],
      "typical_agents": "8-15",
      "typical_duration": "15-30 minutes",
      "cost_range": "$2-5"
    },
    {
      "name": "swarm",
      "display_name": "Swarm Multi-Agent Search",
      "description": "9 specialized agent types for diverse searches",
      "use_cases": [
        "Multi-source fact checking",
        "Trend analysis",
        "Product research"
      ],
      "agent_types": ["text", "image", "video", "news", "academic", "social", "product", "technical", "general"],
      "typical_agents": "4-8",
      "typical_duration": "2-5 minutes",
      "cost_range": "$0.30-1.00"
    }
  ],
  "count": 2
}
```

### Streaming

#### GET `/stream/{task_id}`

Server-Sent Events (SSE) stream for real-time workflow progress.

**Request:**
```bash
curl -N https://dr.eamer.dev/mcp/stream/belta-20251115-abc123
```

**Response (SSE stream):**
```
event: workflow_started
data: {"task_id": "belta-20251115-abc123", "timestamp": "2025-11-15T10:00:00Z", "num_agents": 10}

event: task_decomposed
data: {"subtask_count": 10, "subtasks": ["Research BERT", "Research GPT-2", ...]}

event: agent_started
data: {"agent_id": "belter-001", "agent_type": "research", "task": "Research BERT architecture"}

event: agent_progress
data: {"agent_id": "belter-001", "progress": 0.5, "message": "Analyzing attention mechanisms"}

event: agent_completed
data: {"agent_id": "belter-001", "status": "success", "tokens_used": 1523, "cost": 0.08, "execution_time": 12.3}

event: synthesis_started
data: {"level": "drummer", "input_count": 5, "drummer_id": "drummer-001"}

event: synthesis_completed
data: {"level": "drummer", "drummer_id": "drummer-001", "output_length": 2340}

event: documents_generated
data: {"formats": ["pdf", "markdown"], "documents": [{"format": "pdf", "size_bytes": 245678}]}

event: workflow_completed
data: {"task_id": "belta-20251115-abc123", "status": "completed", "total_cost": 2.45, "execution_time": 1234.5}

event: error
data: {"task_id": "belta-20251115-abc123", "error": "Agent timeout", "timestamp": "2025-11-15T10:15:00Z"}
```

**Connection:**
- Protocol: Server-Sent Events (SSE)
- Encoding: UTF-8
- Content-Type: `text/event-stream`
- Auto-reconnect: Client should reconnect on disconnect

**JavaScript Client:**
```javascript
const eventSource = new EventSource('https://dr.eamer.dev/mcp/stream/belta-20251115-abc123');

eventSource.addEventListener('agent_completed', (e) => {
  const data = JSON.parse(e.data);
  console.log(`Agent ${data.agent_id} completed: $${data.cost}`);
});

eventSource.addEventListener('workflow_completed', (e) => {
  const data = JSON.parse(e.data);
  console.log('Workflow complete!', data);
  eventSource.close();
});
```

**Errors:**
- `404`: Task not found
- Connection closed after workflow completion

#### GET `/stats`

Get streaming bridge statistics.

**Request:**
```bash
curl https://dr.eamer.dev/mcp/stats
```

**Response:**
```json
{
  "active_streams": 3,
  "total_events_emitted": 1542,
  "oldest_stream_age_seconds": 145.2,
  "streams": [
    {
      "task_id": "belta-20251115-abc123",
      "connected_at": "2025-11-15T10:00:00Z",
      "events_sent": 42,
      "last_event_at": "2025-11-15T10:02:25Z"
    }
  ],
  "webhooks": {
    "registered": 2,
    "total_deliveries": 48,
    "failed_deliveries": 1,
    "retry_queue_size": 0
  }
}
```

### Webhooks

#### POST `/webhook/register`

Register webhook for async notifications.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/webhook/register \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "belta-20251115-abc123",
    "webhook_url": "https://myapp.com/webhooks/mcp",
    "secret": "my-webhook-secret",
    "events": ["workflow_completed", "workflow_failed"]
  }'
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes | Task identifier |
| `webhook_url` | string | Yes | HTTPS URL for delivery |
| `secret` | string | Yes | HMAC secret for verification |
| `events` | array | No | Event types to receive (default: all) |

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "webhook_url": "https://myapp.com/webhooks/mcp",
  "registered_at": "2025-11-15T10:00:00Z",
  "events": ["workflow_completed", "workflow_failed"]
}
```

**Webhook Delivery:**
```http
POST /webhooks/mcp HTTP/1.1
Host: myapp.com
Content-Type: application/json
X-MCP-Signature: a1b2c3d4e5f6...
X-MCP-Task-ID: belta-20251115-abc123
X-MCP-Event: workflow_completed

{
  "event": "workflow_completed",
  "task_id": "belta-20251115-abc123",
  "timestamp": "2025-11-15T10:20:34Z",
  "data": {
    "status": "completed",
    "total_cost": 2.45,
    "execution_time": 1234.5,
    "documents": [...]
  }
}
```

**HMAC Verification:**
```python
import hmac
import hashlib

def verify_webhook(payload_bytes, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

**Retry Policy:**
- Max retries: 3
- Backoff: 5s, 10s, 20s
- Timeout: 10 seconds per attempt

**Errors:**
- `400`: Missing required fields
- `400`: Invalid webhook_url (must be HTTPS)
- `404`: Task not found

#### POST `/webhook/unregister`

Unregister webhook for a task.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/webhook/unregister \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "belta-20251115-abc123",
    "webhook_url": "https://myapp.com/webhooks/mcp"
  }'
```

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "webhook_url": "https://myapp.com/webhooks/mcp",
  "unregistered_at": "2025-11-15T10:30:00Z"
}
```

### Tool Registry

#### POST `/tools/list_registered_tools`

List tools registered in the dynamic tool registry.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/list_registered_tools \
  -H "Content-Type: application/json" \
  -d '{"category": "orchestrator"}'
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Filter by category |

**Response:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "orchestrate_research",
      "description": "Execute Beltalowda hierarchical research workflow",
      "category": "orchestrator",
      "parameters": {
        "task": {
          "type": "string",
          "description": "Research task description",
          "required": true
        }
      },
      "tags": ["research", "synthesis", "hierarchical"]
    }
  ],
  "count": 7
}
```

#### POST `/tools/execute_registered_tool`

Execute a registered tool by name.

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/execute_registered_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "orchestrate_research",
    "arguments": {
      "task": "Research quantum computing applications",
      "num_agents": 8
    }
  }'
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tool_name` | string | Yes | Registered tool name |
| `arguments` | object | Yes | Tool-specific arguments |

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "running",
  "stream_url": "/mcp/stream/belta-20251115-abc123"
}
```

## Data Models

### SubTask

```typescript
interface SubTask {
  id: string;
  description: string;
  context: object;
  agent_type: AgentType;
  specialization?: string;
  priority: number;
  dependencies: string[];
}
```

### AgentResult

```typescript
interface AgentResult {
  agent_id: string;
  agent_type: AgentType;
  specialization?: string;
  status: 'success' | 'failed' | 'timeout';
  result: string;
  tokens_used: number;
  cost: number;
  execution_time: number;
  error?: string;
  metadata: object;
}
```

### SynthesisResult

```typescript
interface SynthesisResult {
  level: 'drummer' | 'camina';
  synthesis_id: string;
  input_results: AgentResult[];
  synthesis: string;
  tokens_used: number;
  cost: number;
  execution_time: number;
  metadata: object;
}
```

### OrchestratorResult

```typescript
interface OrchestratorResult {
  task_id: string;
  title: string;
  status: TaskStatus;
  agent_results: AgentResult[];
  synthesis_results: SynthesisResult[];
  final_synthesis?: string;
  execution_time: number;
  total_cost: number;
  generated_documents: GeneratedDocument[];
  metadata: object;
}
```

### GeneratedDocument

```typescript
interface GeneratedDocument {
  format: 'pdf' | 'docx' | 'markdown';
  path: string;
  size_bytes: number;
  url?: string;
  metadata: {
    title: string;
    author: string;
    created_at: string;
  };
}
```

### StreamEvent

```typescript
interface StreamEvent {
  event: EventType;
  task_id: string;
  timestamp: string;
  data: object;
}
```

### TaskStatus

```typescript
type TaskStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';
```

### AgentType

```typescript
type AgentType =
  | 'research'      // Beltalowda Belter
  | 'synthesis'     // Beltalowda Drummer/Camina
  | 'text'          // Swarm text specialist
  | 'image'         // Swarm image specialist
  | 'video'         // Swarm video specialist
  | 'news'          // Swarm news specialist
  | 'academic'      // Swarm academic specialist
  | 'social'        // Swarm social media specialist
  | 'product'       // Swarm product specialist
  | 'technical'     // Swarm technical specialist
  | 'general';      // Swarm general search
```

## Event Types

Events emitted via SSE stream and webhooks.

| Event | Description | Data Fields |
|-------|-------------|-------------|
| `workflow_started` | Workflow execution begins | `task_id`, `timestamp`, `num_agents` |
| `task_decomposed` | Task broken into subtasks | `subtask_count`, `subtasks[]` |
| `agent_started` | Individual agent begins work | `agent_id`, `agent_type`, `task` |
| `agent_progress` | Agent progress update | `agent_id`, `progress` (0-1), `message` |
| `agent_completed` | Agent finishes work | `agent_id`, `status`, `cost`, `execution_time` |
| `synthesis_started` | Synthesis stage begins | `level` (drummer/camina), `input_count` |
| `synthesis_completed` | Synthesis stage finishes | `level`, `output_length`, `cost` |
| `documents_generated` | Documents created | `formats[]`, `documents[]` |
| `workflow_completed` | Workflow finishes successfully | `status`, `total_cost`, `execution_time`, `documents[]` |
| `workflow_failed` | Workflow fails | `error`, `failed_at` |
| `workflow_cancelled` | Workflow cancelled by user | `cancelled_at`, `partial_results` |
| `error` | Error during workflow | `error`, `details` |

## Example Workflows

### Complete Workflow Sequence

1. **Start Workflow**
   ```
   POST /tools/orchestrate_research
   → {task_id, stream_url}
   ```

2. **Stream Progress**
   ```
   GET /stream/{task_id}
   → workflow_started
   → task_decomposed
   → agent_started (×10)
   → agent_completed (×10)
   → synthesis_started (drummer)
   → synthesis_completed (drummer ×2)
   → synthesis_started (camina)
   → synthesis_completed (camina)
   → documents_generated
   → workflow_completed
   ```

3. **Get Final Result**
   ```
   POST /tools/get_orchestration_status
   → {result: {...}, documents: [...]}
   ```

### Error Handling Workflow

1. **Start Workflow**
   ```
   POST /tools/orchestrate_research
   → {task_id, stream_url}
   ```

2. **Agent Fails**
   ```
   GET /stream/{task_id}
   → workflow_started
   → agent_started (belter-001)
   → error (Agent timeout after 180s)
   → agent_started (belter-001-retry)
   → agent_completed (belter-001-retry)
   ```

3. **Check Status**
   ```
   POST /tools/get_orchestration_status
   → {status: "running", progress: {...}}
   ```

---

**Author:** Luke Steuber
**Last Updated:** 2025-11-15
**Version:** 1.0.0
