# MCP Orchestrator Server - Usage Examples

Comprehensive examples demonstrating the capabilities of the MCP Orchestrator Server.

**Author:** Luke Steuber

## Table of Contents

- [Beltalowda Examples](#beltalowda-examples)
- [Swarm Examples](#swarm-examples)
- [Streaming Examples](#streaming-examples)
- [Webhook Examples](#webhook-examples)
- [Python Client Examples](#python-client-examples)
- [Advanced Workflows](#advanced-workflows)

## Beltalowda Examples

Beltalowda orchestrates hierarchical research with 3-tier synthesis: Belters (workers) → Drummers (mid-level synthesis) → Camina (executive synthesis).

### Example 1: Academic Literature Review

**Task:** Comprehensive review of transformer architectures in NLP (2017-2025)

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Conduct a comprehensive literature review of transformer architectures in natural language processing from 2017-2025. Cover: original Transformer (Vaswani 2017), BERT, GPT series, T5, Switch Transformers, and recent innovations like Llama 3, GPT-4, Claude.",
    "title": "Transformer Architectures Evolution (2017-2025)",
    "num_agents": 12,
    "enable_synthesis": true,
    "synthesis_group_size": 4,
    "generate_documents": true,
    "document_formats": ["pdf", "docx", "markdown"],
    "primary_model": "grok-3",
    "agent_model": "grok-4-fast",
    "belter_timeout": 180,
    "drummer_timeout": 240,
    "camina_timeout": 300
  }'
```

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-transformer-review",
  "status": "running",
  "stream_url": "/mcp/stream/belta-20251115-transformer-review",
  "webhook_url": null,
  "message": "Research workflow started with 12 Belter agents. Connect to stream_url for real-time progress."
}
```

**Workflow:**
1. **Decomposition**: Creates 12 subtasks (Attention mechanisms, BERT architecture, GPT evolution, T5 architecture, etc.)
2. **Belters Execute**: 12 parallel research agents gather information
3. **Drummers Synthesize**: 3 Drummers synthesize 4 Belter reports each
4. **Camina Synthesizes**: Executive synthesis of 3 Drummer reports
5. **Documents Generated**: PDF (professional report), DOCX (editable), Markdown (web-ready)

**Expected Execution Time:** 15-25 minutes
**Expected Cost:** $2-4 (12 × Grok-4-fast + 3 × Grok-3 + 1 × Grok-3)

### Example 2: Market Analysis

**Task:** Competitive analysis of AI coding assistants

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze the competitive landscape of AI coding assistants. Compare GitHub Copilot, Cursor, Replit Ghostwriter, Tabnine, Amazon CodeWhisperer, and Claude Code. Evaluate: features, pricing, IDE integrations, language support, accuracy, user satisfaction, market share.",
    "title": "AI Coding Assistants Competitive Analysis",
    "num_agents": 8,
    "enable_synthesis": true,
    "generate_documents": true,
    "document_formats": ["pdf", "markdown"],
    "primary_model": "claude-sonnet-4.5",
    "agent_model": "claude-haiku-4"
  }'
```

**Workflow Output:**
- 8 Belter reports (1 per product + pricing/market analysis)
- 2 Drummer syntheses (features comparison + market positioning)
- 1 Camina executive summary
- **Documents:**
  - PDF: Professional slide-deck style report
  - Markdown: Blog-ready content with tables

**Use Case:** Strategic planning, competitive intelligence, market entry analysis

### Example 3: Technical Documentation Synthesis

**Task:** Aggregate API documentation from scattered sources

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create comprehensive API documentation for our microservices architecture. Synthesize information from: /servers/coca/README.md (COCA API), /servers/planner/README.md (Lesson Planner), /servers/studio/README.md (Studio), /shared/llm_providers/ (LLM providers), service_manager.py (service orchestration).",
    "title": "Unified API Documentation",
    "num_agents": 5,
    "enable_synthesis": true,
    "generate_documents": true,
    "document_formats": ["markdown"],
    "context": {
      "file_paths": [
        "/servers/coca/README.md",
        "/servers/planner/README.md",
        "/servers/studio/README.md"
      ]
    }
  }'
```

**Workflow:**
- Each Belter analyzes 1-2 services
- Drummers create unified sections (Authentication, Endpoints, Error Handling)
- Camina creates master API guide
- Output: Single comprehensive Markdown file

### Example 4: Historical Research

**Task:** Evolution of web frameworks (1990s-2025)

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Trace the evolution of web application frameworks from early CGI scripts through modern full-stack frameworks. Cover: CGI/Perl (1990s), PHP/ASP (late 90s), Ruby on Rails (2005), Django (2005), Node.js/Express (2009), React/Angular/Vue (2013+), Next.js/Remix (2020+). Analyze design philosophy shifts, developer experience improvements, and performance evolution.",
    "title": "Web Frameworks: 35 Years of Evolution",
    "num_agents": 15,
    "enable_synthesis": true,
    "synthesis_group_size": 5,
    "generate_documents": true,
    "document_formats": ["pdf", "docx"],
    "primary_model": "grok-3"
  }'
```

**Workflow:**
- 15 Belters cover 1-2 frameworks each with historical context
- 3 Drummers synthesize by era (1990s-2005, 2005-2015, 2015-2025)
- Camina creates chronological narrative with trend analysis
- **Documents:** Professional historical analysis report

**Expected Execution Time:** 20-30 minutes
**Expected Cost:** $3-6

### Example 5: Quick Research (No Synthesis)

**Task:** Fast fact gathering without hierarchical synthesis

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Gather current statistics on global renewable energy adoption: solar capacity, wind capacity, hydroelectric, nuclear, by top 10 countries.",
    "title": "Renewable Energy Statistics 2025",
    "num_agents": 5,
    "enable_synthesis": false,
    "generate_documents": true,
    "document_formats": ["markdown"],
    "agent_model": "grok-4-fast"
  }'
```

**Workflow:**
- 5 Belters gather data (no Drummers or Camina)
- Agent results returned as structured list
- Markdown document with data tables
- **Fast:** 3-5 minutes, **Cheap:** $0.50-1.00

## Swarm Examples

Swarm orchestrates multi-agent specialized search across 9 domain types: text, image, video, news, academic, social, product, technical, general.

### Example 1: Breaking News Aggregation

**Task:** Multi-source news coverage of a developing story

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing breakthrough December 2024",
    "num_agents": 6,
    "agent_types": ["news", "academic", "social"],
    "parallel_execution": true,
    "timeout_seconds": 120,
    "enable_synthesis": true
  }'
```

**Workflow:**
1. **News agents** (2): Scan Reuters, AP, BBC, tech news
2. **Academic agents** (2): Check arXiv, Nature, Science preprints
3. **Social agents** (2): Monitor Twitter/X, Reddit, HackerNews
4. **Synthesis**: Aggregate timeline, key claims, expert reactions
5. **Output**: Unified report with multi-source verification

**Agent Distribution:**
- 🟢 News: 33% (2 agents)
- 🟣 Academic: 33% (2 agents)
- 🟦 Social: 33% (2 agents)

**Expected Execution Time:** 2-4 minutes
**Expected Cost:** $0.30-0.60

### Example 2: Product Research

**Task:** Compare smartphones for purchase decision

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "best smartphone under $800 2025 camera battery performance",
    "num_agents": 8,
    "agent_types": ["product", "technical", "social", "news"],
    "parallel_execution": true,
    "enable_synthesis": true
  }'
```

**Workflow:**
- **Product agents** (3): Specs, pricing, availability
- **Technical agents** (2): Benchmark scores, teardowns
- **Social agents** (2): User reviews, Reddit discussions
- **News agents** (1): Recent launches, deals

**Output:**
```json
{
  "synthesis": "Top recommendations: Pixel 9 ($699, best camera), Galaxy S24 ($799, best screen), iPhone 15 ($799, best ecosystem)",
  "agent_results": [
    {
      "agent_type": "product",
      "findings": "Pixel 9: $699, 50MP camera, 5000mAh battery..."
    },
    {
      "agent_type": "social",
      "findings": "Reddit r/Android consensus: Pixel 9 wins for photography..."
    }
  ]
}
```

### Example 3: Academic Literature Search

**Task:** Find papers on a specific research topic

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "few-shot learning computer vision 2023-2025",
    "num_agents": 4,
    "agent_types": ["academic"],
    "parallel_execution": true,
    "enable_synthesis": true
  }'
```

**Workflow:**
- All 4 agents are academic specialists
- Search: arXiv, Google Scholar, Semantic Scholar, Papers with Code
- Synthesis: Chronological overview, key methods, benchmarks
- Output: Structured bibliography with summaries

### Example 4: Social Media Trend Analysis

**Task:** Gauge public sentiment on a topic

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI regulation EU AI Act reactions sentiment",
    "num_agents": 5,
    "agent_types": ["social", "news"],
    "parallel_execution": true,
    "enable_synthesis": true
  }'
```

**Workflow:**
- **Social agents** (3): Twitter/X, Reddit, HackerNews, LinkedIn
- **News agents** (2): Coverage analysis, official statements
- **Synthesis**: Sentiment breakdown (support/opposition), key arguments
- Output: Sentiment report with representative quotes

### Example 5: Technical Documentation Discovery

**Task:** Find API documentation and code examples

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FastAPI WebSocket authentication examples",
    "num_agents": 4,
    "agent_types": ["technical"],
    "parallel_execution": true
  }'
```

**Workflow:**
- Technical agents search: GitHub, Stack Overflow, official docs, dev.to
- Findings: Code snippets, best practices, common patterns
- Output: Curated examples with explanations

### Example 6: Auto-Detected Agent Types

**Task:** Let Swarm auto-detect agent types from query keywords

**Request:**
```bash
curl -X POST https://dr.eamer.dev/mcp/tools/orchestrate_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest quantum computing research papers with code examples and news coverage",
    "num_agents": 9
  }'
```

**Auto-Detection:**
- "research papers" → **academic** (3 agents)
- "code examples" → **technical** (2 agents)
- "news coverage" → **news** (2 agents)
- General fallback → **general** (2 agents)

**Note:** When `agent_types` is not specified, Swarm uses keyword detection to assign agent types.

## Streaming Examples

Real-time SSE (Server-Sent Events) streaming for workflow progress.

### Example 1: Bash/curl Streaming

```bash
# Start workflow
RESPONSE=$(curl -s -X POST https://dr.eamer.dev/mcp/tools/orchestrate_research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research machine learning interpretability methods",
    "num_agents": 5
  }')

# Extract task_id
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

# Stream progress
curl -N https://dr.eamer.dev/mcp/stream/$TASK_ID
```

**Output:**
```
event: workflow_started
data: {"task_id": "belta-20251115-abc123", "timestamp": "2025-11-15T10:00:00Z", "num_agents": 5}

event: task_decomposed
data: {"subtask_count": 5, "subtasks": ["SHAP values", "LIME", "Attention visualization", "Grad-CAM", "Counterfactual explanations"]}

event: agent_started
data: {"agent_id": "belter-001", "agent_type": "research", "task": "Research SHAP (SHapley Additive exPlanations) values"}

event: agent_progress
data: {"agent_id": "belter-001", "progress": 0.5, "message": "Analyzing Shapley value theory"}

event: agent_completed
data: {"agent_id": "belter-001", "status": "success", "tokens_used": 1523, "cost": 0.08, "execution_time": 12.3}

event: synthesis_started
data: {"level": "drummer", "input_count": 5}

event: synthesis_completed
data: {"level": "camina", "output_length": 8420}

event: documents_generated
data: {"formats": ["pdf", "markdown"], "sizes": {"pdf": 245678, "markdown": 18234}}

event: workflow_completed
data: {"task_id": "belta-20251115-abc123", "status": "completed", "total_cost": 1.25, "execution_time": 145.2, "documents": ["/path/to/report.pdf"]}
```

### Example 2: JavaScript/Browser Streaming

```javascript
// Start workflow
const response = await fetch('https://dr.eamer.dev/mcp/tools/orchestrate_research', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    task: 'Research AI safety approaches',
    num_agents: 6,
    generate_documents: true
  })
});

const {task_id, stream_url} = await response.json();

// Stream progress with EventSource
const eventSource = new EventSource(`https://dr.eamer.dev${stream_url}`);

eventSource.addEventListener('workflow_started', (e) => {
  const data = JSON.parse(e.data);
  console.log('Workflow started:', data);
  updateUI({status: 'running', started_at: data.timestamp});
});

eventSource.addEventListener('agent_started', (e) => {
  const data = JSON.parse(e.data);
  addAgentCard(data.agent_id, data.task);
});

eventSource.addEventListener('agent_completed', (e) => {
  const data = JSON.parse(e.data);
  updateAgentCard(data.agent_id, {
    status: 'completed',
    cost: data.cost,
    time: data.execution_time
  });
});

eventSource.addEventListener('synthesis_started', (e) => {
  const data = JSON.parse(e.data);
  showSynthesisStage(data.level); // 'drummer' or 'camina'
});

eventSource.addEventListener('workflow_completed', (e) => {
  const data = JSON.parse(e.data);
  eventSource.close();

  displayResults({
    documents: data.documents,
    total_cost: data.total_cost,
    execution_time: data.execution_time
  });
});

eventSource.addEventListener('error', (e) => {
  const data = JSON.parse(e.data);
  console.error('Workflow error:', data);
  eventSource.close();
});
```

### Example 3: React Component with SSE

```jsx
import React, {useState, useEffect} from 'react';

function ResearchWorkflow({task}) {
  const [taskId, setTaskId] = useState(null);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState('idle');
  const [agents, setAgents] = useState([]);

  const startWorkflow = async () => {
    const response = await fetch('/mcp/tools/orchestrate_research', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({task, num_agents: 8})
    });

    const {task_id, stream_url} = await response.json();
    setTaskId(task_id);
    setStatus('running');

    // Connect to SSE stream
    const eventSource = new EventSource(stream_url);

    eventSource.onmessage = (e) => {
      const event = JSON.parse(e.data);
      setEvents(prev => [...prev, event]);
    };

    eventSource.addEventListener('agent_started', (e) => {
      const data = JSON.parse(e.data);
      setAgents(prev => [...prev, {id: data.agent_id, status: 'running', ...data}]);
    });

    eventSource.addEventListener('agent_completed', (e) => {
      const data = JSON.parse(e.data);
      setAgents(prev => prev.map(agent =>
        agent.id === data.agent_id
          ? {...agent, status: 'completed', ...data}
          : agent
      ));
    });

    eventSource.addEventListener('workflow_completed', (e) => {
      const data = JSON.parse(e.data);
      setStatus('completed');
      eventSource.close();
    });
  };

  return (
    <div>
      <button onClick={startWorkflow} disabled={status === 'running'}>
        Start Research
      </button>

      <div>Status: {status}</div>

      <div className="agents-grid">
        {agents.map(agent => (
          <div key={agent.id} className={`agent-card ${agent.status}`}>
            <h4>{agent.agent_id}</h4>
            <p>{agent.task}</p>
            {agent.cost && <span>Cost: ${agent.cost.toFixed(2)}</span>}
          </div>
        ))}
      </div>

      <div className="event-log">
        {events.map((event, i) => (
          <div key={i}>{event.type}: {JSON.stringify(event.data)}</div>
        ))}
      </div>
    </div>
  );
}
```

## Webhook Examples

Async notifications delivered to your server with HMAC authentication.

### Example 1: Register Webhook

```bash
curl -X POST https://dr.eamer.dev/mcp/webhook/register \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "belta-20251115-abc123",
    "webhook_url": "https://myapp.com/webhooks/mcp",
    "secret": "my-webhook-secret-key"
  }'
```

**Response:**
```json
{
  "success": true,
  "task_id": "belta-20251115-abc123",
  "webhook_url": "https://myapp.com/webhooks/mcp",
  "registered_at": "2025-11-15T10:00:00Z"
}
```

### Example 2: Receive and Verify Webhook

**Flask webhook receiver:**

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = "my-webhook-secret-key"

@app.route('/webhooks/mcp', methods=['POST'])
def mcp_webhook():
    # Get signature from header
    signature = request.headers.get('X-MCP-Signature')
    if not signature:
        return jsonify({'error': 'Missing signature'}), 401

    # Verify HMAC signature
    payload = request.get_data()
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return jsonify({'error': 'Invalid signature'}), 401

    # Process event
    event = request.json
    event_type = event['event']
    data = event['data']

    if event_type == 'workflow_completed':
        # Download generated documents
        for doc in data['documents']:
            download_document(doc['url'])

        # Update database
        update_research_status(data['task_id'], 'completed')

        # Notify user
        send_notification(f"Research '{data['title']}' completed!")

    return jsonify({'status': 'received'})

if __name__ == '__main__':
    app.run(port=8080)
```

### Example 3: Webhook with Retries

Webhooks auto-retry on failure with exponential backoff.

**Webhook delivery timeline:**
```
Attempt 1: Immediate (0s)         → Failed (connection timeout)
Attempt 2: 5 seconds later        → Failed (500 Internal Server Error)
Attempt 3: 10 seconds later       → Success
```

**Configure retry behavior:**
```bash
# In .env
WEBHOOK_TIMEOUT=10
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=5
```

## Python Client Examples

Complete Python client implementations for common workflows.

### Example 1: Synchronous Client (Blocking)

```python
import requests
import json
import time

class MCPClient:
    def __init__(self, base_url='https://dr.eamer.dev/mcp'):
        self.base_url = base_url

    def orchestrate_research(
        self,
        task: str,
        title: str = None,
        num_agents: int = 5,
        **kwargs
    ):
        """Start research workflow and wait for completion."""

        # Start workflow
        response = requests.post(
            f'{self.base_url}/tools/orchestrate_research',
            json={
                'task': task,
                'title': title,
                'num_agents': num_agents,
                **kwargs
            }
        )
        response.raise_for_status()
        data = response.json()
        task_id = data['task_id']

        print(f"Workflow started: {task_id}")

        # Poll status until complete
        while True:
            status_response = requests.post(
                f'{self.base_url}/tools/get_orchestration_status',
                json={'task_id': task_id}
            )
            status_data = status_response.json()

            if status_data['status'] == 'completed':
                return status_data['result']
            elif status_data['status'] == 'failed':
                raise Exception(f"Workflow failed: {status_data.get('error')}")

            print(f"Status: {status_data['status']}")
            time.sleep(10)  # Poll every 10 seconds

# Usage
client = MCPClient()
result = client.orchestrate_research(
    task="Research quantum computing applications in drug discovery",
    num_agents=8,
    generate_documents=True
)

print(f"Research complete!")
print(f"Cost: ${result['total_cost']:.2f}")
print(f"Documents: {result['generated_documents']}")
```

### Example 2: Async Client with SSE Streaming

```python
import aiohttp
import asyncio
import json

class AsyncMCPClient:
    def __init__(self, base_url='https://dr.eamer.dev/mcp'):
        self.base_url = base_url

    async def orchestrate_research(
        self,
        task: str,
        on_event=None,
        **kwargs
    ):
        """Start research with streaming progress."""

        async with aiohttp.ClientSession() as session:
            # Start workflow
            async with session.post(
                f'{self.base_url}/tools/orchestrate_research',
                json={'task': task, **kwargs}
            ) as response:
                data = await response.json()
                task_id = data['task_id']
                stream_url = f"{self.base_url}{data['stream_url']}"

            # Stream events
            async with session.get(stream_url) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if line.startswith('event:'):
                        event_type = line.split(':', 1)[1].strip()
                    elif line.startswith('data:'):
                        event_data = json.loads(line.split(':', 1)[1].strip())

                        if on_event:
                            await on_event(event_type, event_data)

                        if event_type == 'workflow_completed':
                            return event_data

# Usage
async def main():
    client = AsyncMCPClient()

    async def handle_event(event_type, data):
        if event_type == 'agent_started':
            print(f"  → Agent {data['agent_id']}: {data['task']}")
        elif event_type == 'agent_completed':
            print(f"  ✓ Agent {data['agent_id']}: ${data['cost']:.2f}")
        elif event_type == 'synthesis_started':
            print(f"  🔄 Synthesis ({data['level']})...")

    result = await client.orchestrate_research(
        task="Analyze the impact of LLMs on software development practices",
        num_agents=10,
        on_event=handle_event
    )

    print(f"\n✓ Complete! Cost: ${result['total_cost']:.2f}")

asyncio.run(main())
```

### Example 3: Batch Processing Client

```python
import requests
import concurrent.futures

class BatchMCPClient:
    def __init__(self, base_url='https://dr.eamer.dev/mcp'):
        self.base_url = base_url

    def batch_research(self, tasks: list[str], max_workers=3):
        """Process multiple research tasks in parallel."""

        def process_task(task):
            response = requests.post(
                f'{self.base_url}/tools/orchestrate_research',
                json={'task': task, 'num_agents': 5}
            )
            data = response.json()
            return {'task': task, 'task_id': data['task_id']}

        # Start all tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_task, task) for task in tasks]
            task_ids = [f.result() for f in concurrent.futures.as_completed(futures)]

        print(f"Started {len(task_ids)} research tasks")
        return task_ids

# Usage
client = BatchMCPClient()
tasks = [
    "Research transformer attention mechanisms",
    "Analyze reinforcement learning algorithms",
    "Study neural network optimization techniques"
]

task_ids = client.batch_research(tasks)
print(f"Task IDs: {[t['task_id'] for t in task_ids]}")
```

## Advanced Workflows

Complex multi-stage workflows combining Beltalowda and Swarm.

### Example 1: Research → Search → Validate

**Workflow:**
1. Beltalowda: Deep research on a topic
2. Swarm: Fact-check claims with news/academic sources
3. Beltalowda: Synthesize validated findings

```python
async def research_and_validate(topic: str):
    client = AsyncMCPClient()

    # Stage 1: Initial research
    print(f"Stage 1: Researching {topic}...")
    research_result = await client.orchestrate_research(
        task=f"Comprehensive research on {topic}",
        num_agents=10
    )

    # Extract key claims
    claims = extract_claims(research_result['final_synthesis'])

    # Stage 2: Fact-check each claim
    print(f"Stage 2: Fact-checking {len(claims)} claims...")
    validations = []
    for claim in claims:
        validation = await client.orchestrate_search(
            query=f"verify: {claim}",
            agent_types=['academic', 'news'],
            num_agents=4
        )
        validations.append({
            'claim': claim,
            'validation': validation
        })

    # Stage 3: Synthesize validated research
    print("Stage 3: Synthesizing validated findings...")
    final_result = await client.orchestrate_research(
        task=f"Synthesize research on {topic} with fact-checking results",
        context={'validations': validations},
        num_agents=5
    )

    return final_result

# Usage
result = asyncio.run(research_and_validate(
    "Impact of microplastics on ocean ecosystems"
))
```

### Example 2: Content Creation Pipeline

**Workflow:**
1. Swarm: Gather content ideas from social trends
2. Beltalowda: Research each idea in depth
3. Generate multiple content pieces with documents

```python
async def content_pipeline(theme: str, num_pieces=5):
    client = AsyncMCPClient()

    # Discovery: Find trending topics
    print(f"Discovering trending topics for: {theme}")
    trends = await client.orchestrate_search(
        query=f"{theme} trending topics discussions 2025",
        agent_types=['social', 'news'],
        num_agents=6
    )

    # Extract top topics
    topics = extract_top_topics(trends['synthesis'], limit=num_pieces)

    # Research: Deep dive on each topic
    print(f"Researching {len(topics)} topics...")
    content_pieces = []
    for topic in topics:
        research = await client.orchestrate_research(
            task=f"Create comprehensive content on: {topic}",
            title=topic,
            num_agents=6,
            generate_documents=True,
            document_formats=['markdown']
        )
        content_pieces.append(research)

    return {
        'theme': theme,
        'topics': topics,
        'content_pieces': content_pieces
    }

# Usage
pipeline = asyncio.run(content_pipeline(
    theme="AI in healthcare",
    num_pieces=5
))

for piece in pipeline['content_pieces']:
    print(f"✓ {piece['title']}: {piece['generated_documents'][0]}")
```

### Example 3: Competitive Intelligence Dashboard

**Workflow:**
1. Swarm: Monitor competitor news/social/products
2. Beltalowda: Analyze competitive positioning
3. Auto-refresh every 6 hours with webhooks

```python
class CompetitiveIntelligence:
    def __init__(self, competitors: list[str]):
        self.competitors = competitors
        self.client = AsyncMCPClient()

    async def monitor_competitor(self, competitor: str):
        """Monitor single competitor across all channels."""

        # Multi-channel search
        search_result = await self.client.orchestrate_search(
            query=f"{competitor} news products updates launches",
            agent_types=['news', 'product', 'social'],
            num_agents=9
        )

        return {
            'competitor': competitor,
            'findings': search_result,
            'timestamp': datetime.now()
        }

    async def analyze_landscape(self):
        """Analyze entire competitive landscape."""

        # Monitor all competitors in parallel
        monitoring_tasks = [
            self.monitor_competitor(comp)
            for comp in self.competitors
        ]
        competitor_data = await asyncio.gather(*monitoring_tasks)

        # Synthesize competitive analysis
        analysis = await self.client.orchestrate_research(
            task=f"Analyze competitive landscape for {', '.join(self.competitors)}",
            context={'competitor_data': competitor_data},
            num_agents=8,
            generate_documents=True,
            document_formats=['pdf', 'markdown']
        )

        return analysis

# Usage
intelligence = CompetitiveIntelligence([
    'Anthropic Claude',
    'OpenAI ChatGPT',
    'Google Gemini',
    'xAI Grok'
])

# Run analysis
analysis = asyncio.run(intelligence.analyze_landscape())
print(f"Analysis complete: {analysis['generated_documents']}")
```

## Performance Tips

### Optimize Agent Count

**Too few agents:**
- Slower execution
- Less comprehensive coverage
- Lower cost

**Too many agents:**
- Higher cost
- Diminishing returns
- Longer synthesis time

**Sweet spots:**
- Quick research: 3-5 agents
- Standard research: 8-12 agents
- Comprehensive: 15-20 agents
- Swarm search: 4-8 agents

### Choose Models Wisely

**Model tiers:**
- **Fast/Cheap:** Grok-4-fast, Claude Haiku (agent_model)
- **Balanced:** Claude Sonnet (primary_model)
- **High-Quality:** Grok-3, GPT-4 (synthesis only)

**Cost optimization:**
```json
{
  "agent_model": "grok-4-fast",      // Fast agents: $0.05/call
  "primary_model": "grok-3"          // Quality synthesis: $0.30/call
}
```

### Parallel vs. Sequential

**Parallel (default):**
- Faster execution (all agents run simultaneously)
- Higher concurrent API usage
- Best for independent research tasks

**Sequential:**
- Slower but more controlled
- Lower API rate limit impact
- Best when agents build on each other

```json
{
  "parallel_execution": false,
  "max_concurrent_agents": 2  // Limit concurrency
}
```

### Document Generation Optimization

**Generate only needed formats:**
```json
{
  "generate_documents": true,
  "document_formats": ["markdown"]  // Skip PDF/DOCX if not needed
}
```

**Disable for quick results:**
```json
{
  "generate_documents": false  // Just get synthesis text
}
```

---

**Author:** Luke Steuber
**Last Updated:** 2025-11-15
**Version:** 1.0.0
