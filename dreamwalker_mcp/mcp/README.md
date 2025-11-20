# Dreamwalker MCP Server

**Dreamwalker** - Master Orchestrator for complex AI workflows with comprehensive MCP tools.

Unified Model Context Protocol (MCP) server exposing orchestrator agents for complex, multi-step AI workflows with real-time streaming progress, plus comprehensive data fetching, caching, and utility tools.

**Author:** Luke Steuber  
**Version:** 2.0.0 (Phase 1 Complete)  
**Primary Orchestrator:** Dreamwalker

## Overview

The MCP Orchestrator Server provides a standardized HTTP/SSE interface to powerful orchestrator agents that coordinate multiple AI models to tackle complex research, search, and content generation tasks. Built on the BaseOrchestrator framework, it enables systematic creation of new orchestration patterns while providing production-ready deployment infrastructure.

### Key Features

- **Dual Orchestrator Patterns**
  - **Beltalowda**: Hierarchical research with 3-tier synthesis (Belters → Drummers → Camina)
  - **Swarm**: Multi-agent specialized search across 9 domain types (text, image, video, news, academic, social, product, technical, general)

- **Data Fetching Tools** 🆕
  - **Census Bureau**: ACS demographics, SAIPE poverty estimates
  - **Academic Research**: arXiv, Semantic Scholar paper search
  - **Web Archive**: Wayback Machine snapshot access

- **Caching & Memory** 🆕
  - **Redis Integration**: get, set, delete, increment operations
  - **Namespace Support**: Multi-tenant key isolation
  - **TTL Management**: Automatic expiration

- **Utility Functions** 🆕
  - **Document Parsing**: 50+ file formats (PDF, DOCX, Excel, etc.)
  - **Multi-Search**: Parallel multi-query research workflows
  - **Citations**: BibTeX formatting, citation management

- **Real-Time Streaming**
  - Server-Sent Events (SSE) for live workflow progress
  - Webhook notifications with HMAC signatures
  - Async task execution prevents HTTP timeouts

- **Document Generation**
  - Professional PDF reports (ReportLab)
  - DOCX documents (python-docx)
  - Enhanced Markdown with YAML frontmatter

- **Extensible Framework**
  - BaseOrchestrator abstract class for standardized patterns
  - Orchestrator template for building custom workflows
  - Tool registry for dynamic capability discovery

- **Production Ready**
  - Gunicorn WSGI server with 4 workers
  - Caddy reverse proxy with SSE optimization
  - Service manager integration
  - CORS support for web clients
  - 31+ MCP tools exposed

## Integration Options

This MCP server can be used in **two modes**:

### 1. Codex/Claude Code Integration (Recommended) ✅

The stdio bridge provides seamless integration with Codex:

```bash
# Already registered! Just start Codex
codex

# Or explicitly: codex mcp serve orchestrator
```

**See [CODEX_INTEGRATION.md](./CODEX_INTEGRATION.md) for complete guide with examples.**

📊 **[INTEGRATION_STATUS.md](./INTEGRATION_STATUS.md)** - Current status, agent findings, and 30-minute fix path

### 2. HTTP API Service

For web-based integrations and external applications:

```bash
SKIP_PIP_INSTALL=1 sm start mcp-server
```

HTTP endpoints available at `http://localhost:5060` or `https://dr.eamer.dev/mcp/`

## Quick Start

### Installation

```bash
cd /home/coolhand/shared/mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Starting the Server

**Via Service Manager (recommended):**
```bash
sm start mcp-server
sm status mcp-server
sm logs mcp-server
```

**Direct execution:**
```bash
# Development mode (Flask dev server)
python app.py

# Production mode (Gunicorn)
./start.sh
```

The server will be available at:
- **Local:** `http://localhost:5060`
- **Production:** `https://dr.eamer.dev/mcp/`

### Basic Usage

**1. Start a hierarchical research workflow:**

```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research the evolution of transformer architectures in NLP from 2017-2025",
    "num_agents": 8,
    "enable_synthesis": true,
    "generate_documents": true
  }'
```

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "status": "running",
  "stream_url": "/mcp/stream/belta-20251115-abc123",
  "message": "Research workflow started. Connect to stream_url for live progress."
}
```

**2. Stream real-time progress:**

```bash
curl -N https://dr.eamer.dev/mcp/stream/belta-20251115-abc123
```

**SSE events:**
```
event: workflow_started
data: {"task_id": "belta-20251115-abc123", "timestamp": "2025-11-15T10:00:00Z"}

event: task_decomposed
data: {"subtask_count": 8, "tasks": [...]}

event: agent_started
data: {"agent_id": "belter-001", "task": "Research BERT architecture"}

event: agent_completed
data: {"agent_id": "belter-001", "result": "...", "cost": 0.15}

event: synthesis_started
data: {"level": "drummer", "agent_count": 4}

event: synthesis_completed
data: {"level": "camina", "final_report": "..."}

event: workflow_completed
data: {"task_id": "belta-20251115-abc123", "documents": [...], "total_cost": 1.25}
```

**3. Multi-agent search workflow:**

```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing breakthroughs 2024",
    "num_agents": 5,
    "agent_types": ["academic", "news", "technical"]
  }'
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Client                              │
│                   (Claude, Web UI, CLI)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/SSE
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Application (app.py)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   MCP Tool   │  │  Streaming   │  │   Error Handlers     │  │
│  │  Endpoints   │  │  Blueprint   │  │   Health Checks      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              UnifiedMCPServer (unified_server.py)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  tool_orchestrate_research() → BeltalowdaOrchestrator    │  │
│  │  tool_orchestrate_search() → SwarmOrchestrator           │  │
│  │  tool_get_orchestration_status()                         │  │
│  │  tool_cancel_orchestration()                             │  │
│  │  tool_list_orchestrator_patterns()                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
│ StreamingBridge  │ │   Webhook    │ │  ToolRegistry   │
│   (streaming.py) │ │   Manager    │ │ (tool_registry) │
│                  │ │ (streaming)  │ │                 │
│  - SSE queues    │ │  - HMAC auth │ │  - Auto-discover│
│  - Task tracking │ │  - Retries   │ │  - Dynamic list │
└──────────────────┘ └──────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│            BaseOrchestrator (base_orchestrator.py)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  execute_workflow() - Standard template pattern:         │  │
│  │    1. decompose_task() → List[SubTask]                   │  │
│  │    2. execute_subtask() → AgentResult (parallel)         │  │
│  │    3. synthesize_results() → final output                │  │
│  │    4. generate_documents() → PDF/DOCX/MD                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
┌──────────────────────────┐        ┌───────────────────────────┐
│ BeltalowdaOrchestrator   │        │   SwarmOrchestrator       │
│ (beltalowda_orchestrator)│        │   (swarm_orchestrator)    │
│                          │        │                           │
│  - 3-tier hierarchy      │        │  - 9 agent types          │
│  - Belters (workers)     │        │  - Keyword detection      │
│  - Drummers (mid-synth)  │        │  - Parallel search        │
│  - Camina (executive)    │        │  - Result aggregation     │
└──────────────────────────┘        └───────────────────────────┘
         │                                       │
         └───────────────────┬───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         DocumentGenerationManager (document_generation/)        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  generate_reports() → PDF, DOCX, Markdown                │  │
│  │  - PDFGenerator (ReportLab)                              │  │
│  │  - DOCXGenerator (python-docx)                           │  │
│  │  - MarkdownGenerator (YAML frontmatter)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Client Request** → POST `/mcp/tools/orchestrate_research`
2. **UnifiedMCPServer** → Validates input, creates task_id
3. **Orchestrator** → Async execution begins, returns immediately
4. **Client Streams** → GET `/mcp/stream/{task_id}` (SSE connection)
5. **Workflow Events** → StreamingBridge queues events
6. **SSE Delivery** → Events sent to client in real-time
7. **Completion** → Final event with documents and results

### Orchestrator Patterns

#### Beltalowda (Hierarchical Research)

3-tier synthesis hierarchy inspired by The Expanse:

```
┌─────────────────────────────────────────────────────────────────┐
│                           Camina                                │
│                    (Executive Synthesis)                        │
│                                                                 │
│  Synthesizes 2+ Drummer reports into final comprehensive       │
│  research document with unified narrative.                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Drummer 1      │ │   Drummer 2  │ │   Drummer 3      │
│ (Mid-Synthesis)  │ │(Mid-Synthesis)│ │ (Mid-Synthesis)  │
│                  │ │              │ │                  │
│ Synthesizes 5    │ │ Synthesizes 5│ │ Synthesizes 5    │
│ Belter reports   │ │ Belter reports│ │ Belter reports   │
└─────────┬────────┘ └──────┬───────┘ └────────┬─────────┘
          │                 │                  │
   ┌──────┴─────┐    ┌──────┴─────┐     ┌─────┴──────┐
   ▼      ▼     ▼    ▼      ▼     ▼     ▼     ▼      ▼
┌────┐ ┌────┐ ┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐┌────┐
│B-1 │ │B-2 │ │B-3 ││B-4 ││B-5 ││B-6 ││B-7 ││B-8 ││B-9 │
└────┘ └────┘ └────┘└────┘└────┘└────┘└────┘└────┘└────┘
Belters (Worker Agents) - Each researches specific subtask
```

**Use Cases:**
- Comprehensive research reports (10-30 page depth)
- Literature reviews with multi-source synthesis
- Market analysis combining diverse data points
- Technical documentation from scattered sources

**Configuration:**
```json
{
  "num_agents": 9,                    // Belter count (3-15)
  "enable_synthesis": true,           // Enable hierarchical synthesis
  "synthesis_group_size": 5,          // Belters per Drummer
  "belter_timeout": 180,              // Belter timeout (seconds)
  "drummer_timeout": 240,             // Drummer timeout
  "camina_timeout": 300,              // Camina timeout
  "primary_model": "grok-3",          // Synthesis model
  "agent_model": "grok-4-fast"        // Belter model (faster)
}
```

#### Swarm (Multi-Agent Search)

9 specialized agent types with keyword-based activation:

| Agent Type | Icon | Color | Keywords | Use Case |
|-----------|------|-------|----------|----------|
| **text** | 📄 | Blue | documents, articles, text, writing | Text content analysis |
| **image** | 🖼️ | Red | images, photos, pictures, visual | Image search and analysis |
| **video** | 🎥 | Orange | videos, clips, streaming | Video content discovery |
| **news** | 📰 | Green | news, current, latest, breaking | Breaking news aggregation |
| **academic** | 🎓 | Purple | academic, research, papers, scholarly | Academic research |
| **social** | 👥 | Teal | social, twitter, reddit, discussions | Social media monitoring |
| **product** | 🛒 | Dark Orange | product, shopping, reviews, buy | Product research |
| **technical** | 💻 | Dark Gray | code, technical, programming, API | Technical documentation |
| **general** | 🔍 | Gray | (default fallback) | General web search |

**Use Cases:**
- Multi-source fact checking
- Trend analysis across platforms
- Product comparison research
- Technical documentation discovery

**Configuration:**
```json
{
  "num_agents": 5,                    // Agent count (1-20)
  "agent_types": ["news", "academic"], // Specific types (optional)
  "parallel_execution": true,         // Run agents concurrently
  "max_concurrent_agents": 10,        // Concurrency limit
  "timeout_seconds": 120              // Per-agent timeout
}
```

## API Reference

See [API.md](./API.md) for complete endpoint documentation.

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info and available endpoints |
| `/health` | GET | Health check with stats |
| `/tools` | GET | List all available MCP tools |
| `/resources` | GET | List all available MCP resources |
| `/tools/orchestrate_research` | POST | Execute Beltalowda workflow |
| `/tools/orchestrate_search` | POST | Execute Swarm workflow |
| `/tools/get_orchestration_status` | POST | Get workflow status |
| `/tools/cancel_orchestration` | POST | Cancel running workflow |
| `/stream/{task_id}` | GET | SSE stream for workflow progress |
| `/webhook/register` | POST | Register webhook for task |
| `/stats` | GET | Streaming bridge statistics |

## Configuration

### Environment Variables

Create `.env` file in `/home/coolhand/shared/mcp/`:

```bash
# Server
PORT=5060                              # Server port
WORKERS=4                              # Gunicorn worker count
TIMEOUT=300                            # Gunicorn timeout (seconds)

# Orchestrator Defaults
DEFAULT_NUM_AGENTS=5
DEFAULT_TIMEOUT=180
DEFAULT_PRIMARY_MODEL=grok-3
DEFAULT_AGENT_MODEL=grok-4-fast

# Document Generation
ENABLE_PDF_GENERATION=true
ENABLE_DOCX_GENERATION=true
DEFAULT_DOCUMENT_FORMATS=pdf,docx,markdown

# Streaming
MAX_STREAM_AGE=3600                    # Keep streams for 1 hour
STREAM_CLEANUP_INTERVAL=300            # Cleanup every 5 minutes

# Webhooks
WEBHOOK_TIMEOUT=10                     # Webhook delivery timeout
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=5

# API Keys (inherited from shared library)
XAI_API_KEY=your-xai-key
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
```

### Service Manager Configuration

Service is defined in `/home/coolhand/service_manager.py`:

```python
'mcp-server': {
    'name': 'MCP Orchestrator Server',
    'script': '/home/coolhand/shared/mcp/start.sh',
    'working_dir': '/home/coolhand/shared/mcp',
    'port': 5060,
    'health_endpoint': 'http://localhost:5060/health',
    'start_timeout': 20,
    'description': 'Unified MCP server for orchestrator agents',
    'env': {
        'PORT': '5060',
        'WORKERS': '4',
        'TIMEOUT': '300'
    }
}
```

### Caddy Reverse Proxy

Configuration in `/etc/caddy/Caddyfile`:

```caddyfile
handle_path /mcp/* {
    reverse_proxy localhost:5060 {
        header_up X-Forwarded-For {remote}
        header_up X-Real-IP {remote}

        # SSE streaming support
        flush_interval -1

        # Extended timeout for long workflows
        transport http {
            read_timeout 600s
            write_timeout 600s
        }
    }
}
```

## Usage Examples

See [EXAMPLES.md](./EXAMPLES.md) for detailed usage examples.

### Example 1: Academic Research

```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Comprehensive analysis of CRISPR gene editing ethical implications 2020-2025",
    "title": "CRISPR Ethics Review",
    "num_agents": 12,
    "enable_synthesis": true,
    "synthesis_group_size": 4,
    "generate_documents": true,
    "document_formats": ["pdf", "docx"],
    "primary_model": "grok-3",
    "agent_model": "grok-4-fast"
  }'
```

### Example 2: Multi-Platform Search

```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing error correction breakthroughs",
    "num_agents": 6,
    "agent_types": ["academic", "news", "technical"],
    "parallel_execution": true,
    "timeout_seconds": 120
  }'
```

### Example 3: Python Client with SSE Streaming

```python
import requests
import json

# Start research workflow
response = requests.post(
    'https://dr.eamer.dev/mcp/tools/orchestrate_research',
    json={
        'task': 'Research AI alignment approaches',
        'num_agents': 8,
        'generate_documents': True
    }
)

data = response.json()
task_id = data['task_id']
stream_url = f"https://dr.eamer.dev/mcp/stream/{task_id}"

# Stream progress
import sseclient
response = requests.get(stream_url, stream=True)
client = sseclient.SSEClient(response)

for event in client.events():
    print(f"Event: {event.event}")
    print(f"Data: {json.loads(event.data)}")

    if event.event == 'workflow_completed':
        result = json.loads(event.data)
        print(f"Documents: {result['documents']}")
        break
```

## Building Custom Orchestrators

See [/home/coolhand/shared/orchestration/ORCHESTRATOR_GUIDE.md](../orchestration/ORCHESTRATOR_GUIDE.md) for detailed guide.

### Quick Start

1. **Use the template:**

```bash
cp /home/coolhand/shared/orchestration/templates/orchestrator_template.py \
   /home/coolhand/shared/orchestration/my_orchestrator.py
```

2. **Implement 3 abstract methods:**

```python
from orchestration import BaseOrchestrator, SubTask, AgentResult

class MyOrchestrator(BaseOrchestrator):
    async def decompose_task(self, task, context):
        """Break task into subtasks"""
        # Your decomposition logic
        return [SubTask(...), SubTask(...)]

    async def execute_subtask(self, subtask, context):
        """Execute a single subtask"""
        # Your execution logic
        return AgentResult(...)

    async def synthesize_results(self, agent_results, context):
        """Synthesize results into final output"""
        # Your synthesis logic
        return final_report
```

3. **Register with MCP server:**

```python
# In unified_server.py
from orchestration.my_orchestrator import MyOrchestrator

async def tool_my_workflow(self, arguments: Dict[str, Any]):
    orchestrator = MyOrchestrator(config)
    result = await orchestrator.execute_workflow(
        task=arguments['task'],
        title=arguments.get('title'),
        stream_callback=callback
    )
    return result
```

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py

# Server runs on http://localhost:5060
```

### Production Deployment

```bash
# Start via service manager
sm start mcp-server

# Check status
sm status mcp-server

# View logs
sm logs mcp-server

# Restart after code changes
sm restart mcp-server
```

### Updating After Code Changes

```bash
# 1. Stop service
sm stop mcp-server

# 2. Update code
cd /home/coolhand/shared
git pull  # or make your changes

# 3. Update dependencies if needed
cd /home/coolhand/shared/mcp
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart service
sm start mcp-server

# 5. Verify
curl https://dr.eamer.dev/mcp/health
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl https://dr.eamer.dev/mcp/health

# Response
{
  "status": "healthy",
  "service": "mcp-orchestrator",
  "active_streams": 3,
  "registered_webhooks": 2
}
```

### Streaming Statistics

```bash
curl https://dr.eamer.dev/mcp/stats

# Response
{
  "active_streams": 3,
  "total_events_emitted": 1542,
  "oldest_stream_age": 145.2,
  "webhooks": {
    "registered": 2,
    "total_deliveries": 48,
    "failed_deliveries": 1,
    "retry_queue_size": 0
  }
}
```

### Service Manager Logs

```bash
# Real-time logs
sm logs mcp-server

# Last 50 lines
sm logs mcp-server | tail -50

# Search for errors
sm logs mcp-server | grep ERROR
```

## Troubleshooting

### Service Won't Start

**Check port availability:**
```bash
sudo lsof -i :5060
# If occupied, kill process or change PORT in .env
```

**Check dependencies:**
```bash
cd /home/coolhand/shared/mcp
source venv/bin/activate
pip install -r requirements.txt
```

**Check logs:**
```bash
sm logs mcp-server
# Look for startup errors
```

### SSE Streams Not Working

**Verify Caddy configuration:**
```bash
sudo caddy validate --config /etc/caddy/Caddyfile
```

**Check flush_interval setting:**
```caddyfile
# Must be -1 for SSE
flush_interval -1
```

**Test local endpoint:**
```bash
# Should work locally
curl -N http://localhost:5060/stream/{task_id}
```

### Workflows Timing Out

**Increase Gunicorn timeout:**
```bash
# In start.sh or .env
TIMEOUT=600  # 10 minutes
```

**Increase Caddy timeouts:**
```caddyfile
transport http {
    read_timeout 900s
    write_timeout 900s
}
```

**Check individual agent timeouts:**
```json
{
  "belter_timeout": 300,
  "drummer_timeout": 360,
  "camina_timeout": 420
}
```

### High Memory Usage

**Reduce concurrent agents:**
```json
{
  "max_concurrent_agents": 5  // Default is 10
}
```

**Increase Gunicorn workers (spreads load):**
```bash
WORKERS=8  # Default is 4
```

**Monitor with:**
```bash
ps aux | grep gunicorn
top -p $(pgrep -f "gunicorn.*app:app")
```

### Document Generation Fails

**Check optional dependencies:**
```bash
pip list | grep -E "(reportlab|python-docx)"
```

**Install if missing:**
```bash
pip install reportlab python-docx
```

**Verify in Python:**
```python
from document_generation import check_dependencies
check_dependencies()
# Shows: PDF: ✓  DOCX: ✓  Markdown: ✓
```

## Performance Tuning

### Gunicorn Workers

Rule of thumb: `workers = (2 × num_cores) + 1`

```bash
# 4-core machine
WORKERS=9

# 8-core machine
WORKERS=17
```

### Concurrent Agents

Balance speed vs. API rate limits:

```json
{
  "max_concurrent_agents": 10,  // Fast, high API usage
  "max_concurrent_agents": 5,   // Moderate
  "max_concurrent_agents": 2    // Slow, low API usage
}
```

### Model Selection

Balance quality vs. cost:

- **Grok-3** (primary_model): High quality, slower, more expensive
- **Grok-4-fast** (agent_model): Fast, cost-effective, good quality
- **Claude Sonnet**: Balanced quality and speed
- **GPT-4**: High quality, most expensive

### Caching Strategies

Implement result caching for repeated workflows:

```python
# In your custom orchestrator
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_research(task: str) -> str:
    # Cache common research tasks
    pass
```

## Security Considerations

### CORS Configuration

Current CORS policy allows:
- `http://localhost:*`
- `https://dr.eamer.dev`
- `https://d.reamwalker.com`
- `https://d.reamwalk.com`

**To restrict:**
```python
# In app.py
CORS(app, resources={
    r"/*": {
        "origins": ["https://trusted-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Webhook HMAC Signatures

Webhooks include HMAC-SHA256 signatures for verification:

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### API Key Management

API keys are loaded from environment variables, never hardcoded:

```bash
# In .env or environment
export XAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

**Never commit `.env` files to git!**

## Contributing

### Adding New Orchestrators

1. Create new file in `/home/coolhand/shared/orchestration/`
2. Inherit from `BaseOrchestrator`
3. Implement 3 abstract methods
4. Add tool endpoint in `unified_server.py`
5. Update documentation

### Code Style

- **PEP 8** compliance
- Type hints for all function signatures
- Docstrings (Google style)
- Async/await for I/O operations

### Testing

```bash
# Run tests (when implemented)
pytest /home/coolhand/shared/tests/

# Type checking
mypy /home/coolhand/shared/orchestration/
```

## License

Proprietary - Luke Steuber

## Support

For issues or questions:
- Check logs: `sm logs mcp-server`
- Review documentation: [EXAMPLES.md](./EXAMPLES.md), [API.md](./API.md)
- Check Caddy: `sudo journalctl -u caddy -f`

## Changelog

### Version 1.0.0 (2025-11-15)

**Initial Release:**
- Unified MCP server with dual orchestrators (Beltalowda, Swarm)
- SSE streaming infrastructure
- Webhook notifications with HMAC
- Document generation (PDF, DOCX, Markdown)
- BaseOrchestrator framework
- Production deployment with Gunicorn + Caddy
- Service manager integration
- Comprehensive documentation

## Related Documentation

- [EXAMPLES.md](./EXAMPLES.md) - Detailed usage examples
- [API.md](./API.md) - Complete API reference
- [ORCHESTRATOR_GUIDE.md](../orchestration/ORCHESTRATOR_GUIDE.md) - Building custom orchestrators
- [Service Manager README](/home/coolhand/SERVICE_MANAGER_README.md) - Service management
- [Shared Library README](/home/coolhand/shared/README.md) - LLM providers and utilities
