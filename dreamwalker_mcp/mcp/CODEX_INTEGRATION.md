# Codex/Claude Code MCP Integration Guide

## Overview

The shared MCP orchestrator server provides seamless integration between Codex/Claude Code and the Beltalowda/Swarm orchestrator agents through the Model Context Protocol (MCP).

**Status**: ✅ Fully operational via stdio bridge
**Registered as**: `orchestrator` in Codex
**HTTP Service**: Port 5060 (requires running outside sandbox)

## Quick Start

### Using with Codex

The orchestrator MCP server is **already registered** with Codex. Just launch Codex and the tools will be available:

```bash
# Start Codex (MCP server loads automatically)
codex

# Or explicitly serve the orchestrator
codex mcp serve orchestrator
```

### Available Tools

#### 1. `orchestrate_research` - Beltalowda Hierarchical Research

Execute multi-tier research with Belters (workers), Drummers (mid-synthesis), and Camina (executive synthesis).

**Use cases:**
- Comprehensive research tasks
- Academic literature review
- Market analysis
- Strategic planning

**Example:**
```json
{
  "task": "Analyze the impact of AI on software development practices",
  "num_agents": 8,
  "enable_drummer": true,
  "enable_camina": true,
  "generate_documents": true,
  "document_formats": ["markdown"]
}
```

**Returns:**
```json
{
  "success": true,
  "task_id": "research_a1b2c3d4e5f6",
  "status": "running",
  "stream_url": "/stream/research_a1b2c3d4e5f6",
  "orchestrator_type": "beltalowda"
}
```

#### 2. `orchestrate_search` - Swarm Multi-Agent Search

Execute specialized agent search across multiple domains (text, image, video, news, academic, social, product, technical).

**Use cases:**
- Multi-source information gathering
- Comparative analysis
- Trend analysis
- Content discovery

**Example:**
```json
{
  "query": "Best practices for microservices architecture in 2024",
  "num_agents": 5,
  "allowed_agent_types": ["text", "technical", "academic"],
  "generate_documents": true
}
```

**Returns:**
```json
{
  "success": true,
  "task_id": "search_f6e5d4c3b2a1",
  "status": "running",
  "stream_url": "/stream/search_f6e5d4c3b2a1",
  "orchestrator_type": "swarm"
}
```

#### 3. `get_orchestration_status` - Check Workflow Status

Get real-time status of a running or completed orchestration.

**Example:**
```json
{
  "task_id": "research_a1b2c3d4e5f6"
}
```

**Returns:**
```json
{
  "success": true,
  "task_id": "research_a1b2c3d4e5f6",
  "status": "running",
  "orchestrator_type": "beltalowda",
  "task": "Analyze the impact of AI...",
  "created_at": "2024-11-18T05:30:00",
  "started_at": "2024-11-18T05:30:02",
  "completed_at": null
}
```

#### 4. `cancel_orchestration` - Cancel Running Workflow

Cancel a running orchestration task.

**Example:**
```json
{
  "task_id": "research_a1b2c3d4e5f6"
}
```

#### 5. `list_orchestrator_patterns` - List Available Patterns

Get metadata about all available orchestrator patterns (Beltalowda, Swarm).

**Example:**
```json
{}
```

**Returns:** Full configuration details for each pattern including default configs, use cases, and agent types.

#### 6. `list_registered_tools` - List Tools in Registry

List all tools registered in the shared tool registry.

**Example:**
```json
{
  "category": "search",
  "tags": ["web"]
}
```

#### 7. `execute_registered_tool` - Execute Registry Tool

Execute a tool from the shared tool registry.

**Example:**
```json
{
  "tool_name": "web_search",
  "tool_arguments": {
    "query": "latest AI research papers"
  }
}
```

## Resources

The MCP server also exposes resources for querying orchestrator metadata and workflow results:

### 1. `orchestrator://{pattern}/info`

Get metadata about an orchestrator pattern.

**Examples:**
- `orchestrator://beltalowda/info`
- `orchestrator://swarm/info`

### 2. `orchestrator://{task_id}/status`

Get status of a specific workflow.

**Example:**
- `orchestrator://research_a1b2c3d4e5f6/status`

### 3. `orchestrator://{task_id}/results`

Get full results of a completed workflow.

**Example:**
- `orchestrator://research_a1b2c3d4e5f6/results`

**Returns:**
```json
{
  "uri": "orchestrator://research_a1b2c3d4e5f6/results",
  "task_id": "research_a1b2c3d4e5f6",
  "title": "AI Impact Research",
  "status": "completed",
  "execution_time": 147.5,
  "total_cost": 0.42,
  "final_synthesis": "...",
  "agent_results": [...],
  "generated_documents": [...]
}
```

## Configuration

### Provider Configuration

By default, orchestrations use the `xai` provider (Grok-3) configured in your environment. You can override this:

```json
{
  "task": "Research task...",
  "provider_name": "anthropic",
  "model": "claude-sonnet-4"
}
```

**Supported providers:**
- `xai` (default) - Grok-3
- `anthropic` - Claude models
- `openai` - GPT models
- `mistral` - Mistral models
- `cohere` - Command models
- `gemini` - Gemini models
- `perplexity` - Perplexity models

### API Keys

Ensure your API keys are configured in `/home/coolhand/API_KEYS.md` or `.env` files:

```bash
XAI_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## HTTP Service (Optional)

For web-based integrations, you can run the HTTP service:

```bash
# Start via service manager (outside sandbox)
SKIP_PIP_INSTALL=1 sm start mcp-server

# Or manually
cd /home/coolhand/shared/mcp
./start.sh
```

**Endpoints:**
- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/{tool_name}` - Execute a tool
- `GET /resources` - List resources
- `GET /resources/{uri}` - Read a resource
- `GET /stream/{task_id}` - SSE stream for workflow events

**Base URL:** `http://localhost:5060`

## Streaming Events

Orchestrations support real-time streaming via Server-Sent Events (SSE):

```bash
# Connect to stream after starting orchestration
curl http://localhost:5060/stream/research_a1b2c3d4e5f6
```

**Event types:**
- `agent_started` - Agent begins work
- `agent_progress` - Agent provides progress update
- `agent_completed` - Agent finishes work
- `synthesis_started` - Synthesis phase begins
- `synthesis_completed` - Synthesis finishes
- `workflow_completed` - Entire workflow done

## Webhook Integration

Configure webhooks for async notifications:

```json
{
  "task": "Research task...",
  "webhook_url": "https://your-app.com/orchestration-webhook"
}
```

All streaming events will be POST'ed to your webhook URL with the same event format as SSE.

## Example Workflows

### 1. Simple Research Task

```python
# Via Codex MCP picker or:
import subprocess
import json

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "orchestrate_research",
        "arguments": {
            "task": "Compare React vs Vue.js for enterprise applications",
            "num_agents": 6
        }
    }
}

proc = subprocess.Popen(
    ['./start-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

response = proc.communicate(json.dumps(request))[0]
print(json.loads(response))
```

### 2. Multi-Domain Search

```python
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "orchestrate_search",
        "arguments": {
            "query": "Sustainable energy solutions 2024",
            "num_agents": 8,
            "allowed_agent_types": ["news", "academic", "technical"],
            "document_formats": ["markdown", "pdf"]
        }
    }
}
```

### 3. Check Status and Get Results

```python
# Check status
status_request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get_orchestration_status",
        "arguments": {
            "task_id": "research_a1b2c3d4e5f6"
        }
    }
}

# Get full results via resources
results_request = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "resources/read",
    "params": {
        "uri": "orchestrator://research_a1b2c3d4e5f6/results"
    }
}
```

## Troubleshooting

### MCP Server Not Showing in Codex

```bash
# Re-register the MCP server
codex mcp add orchestrator ./start-mcp-server

# Verify registration
codex mcp list
```

### Import Errors

```bash
# Ensure shared library is installed
pip install -e /home/coolhand/shared

# Clear Python cache
find /home/coolhand/shared -name "__pycache__" -type d -exec rm -rf {} +
```

### HTTP Service Won't Start

The HTTP service requires socket permissions that aren't available in sandboxed environments. Run it on the host:

```bash
# Outside Claude Code sandbox
cd /home/coolhand/shared/mcp
SKIP_PIP_INSTALL=1 ./start.sh
```

### Orchestrations Fail with API Errors

Verify API keys are configured:

```bash
# Check config
python3 -c "from shared.config import ConfigManager; c = ConfigManager(); c.print_config()"
```

## Architecture Notes

### Threading Model

The stdio bridge uses a **daemon event loop thread** to enable:
- Synchronous stdio JSON-RPC communication
- Async orchestrator workflow execution
- Non-blocking tool calls
- Clean shutdown on SIGTERM/SIGINT

### State Management

The `WorkflowState` class tracks:
- Active workflows (in-progress)
- Completed workflows (last 100 retained)
- Streaming connections
- Webhook registrations

### Provider Caching

LLM providers are cached per `(provider_name, model)` tuple to avoid recreating expensive HTTP clients on every tool call.

## Next Steps

1. **Try it**: Launch Codex and explore the MCP tools in the picker
2. **Configure Caddy**: Add reverse proxy for HTTP service (see below)
3. **Build integrations**: Use webhooks to trigger orchestrations from your apps
4. **Monitor logs**: Check `~/.codex/log/mcp-orchestrator.log` for debugging

## Caddy Configuration (TODO)

Add to `/etc/caddy/Caddyfile`:

```
dr.eamer.dev {
    # ... existing config ...

    # MCP Orchestrator HTTP API
    handle /mcp/* {
        reverse_proxy localhost:5060
    }
}
```

Then reload: `sudo caddy reload --config /etc/caddy/Caddyfile`

## Related Documentation

- **Full MCP spec**: `/home/coolhand/shared/mcp/README.md`
- **API examples**: `/home/coolhand/shared/mcp/EXAMPLES.md`
- **Shared library docs**: `/home/coolhand/shared/CLAUDE.md`
- **Orchestrator patterns**: `/home/coolhand/shared/orchestration/`

---

**Author**: Luke Steuber
**Last Updated**: 2024-11-18
