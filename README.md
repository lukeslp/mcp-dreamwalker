# Dreamwalker MCP

**Turn Claude Code into a research team, not just a chatbot.**

Multi-agent orchestration and LLM provider abstraction for Claude Code via the Model Context Protocol (MCP). Deploy 8 specialized researchers in parallel, synthesize findings through executive tiers, and generate publication-ready reports—all from Claude Code's interface.

**Version:** 1.0.0
**Author:** Luke Steuber
**Landing Page:** https://dr.eamer.dev/dreamwalker/
**License:** MIT

---

## Why Orchestration > Individual Tools

Most MCP plugins give you isolated tools. Dreamwalker gives you **coordinated intelligence**.

| Traditional Approach | Dreamwalker Orchestration |
|---------------------|--------------------------|
| Ask 1 LLM 1 question | Deploy 8 agents in parallel, each with specialized research angles |
| Manual synthesis | Automatic hierarchical synthesis (Belters → Drummer → Camina) |
| Copy/paste between tools | Seamless data flow: research → synthesis → document generation |
| One-shot answers | Iterative refinement with success predicates |
| Generic responses | Domain-specific agents (Academic, News, Technical, Financial, etc.) |
| Text output only | Professional PDF/DOCX/Markdown reports with citations |

**Real-world impact:**
- Academic literature review that took 6 hours → 12 minutes with Beltalowda
- Market research requiring 5 different tools → Single orchestrated Swarm query
- Technical decision requiring cross-domain research → Automated synthesis with 8 specialized agents

---

## Quick Start

### 1. Install the Plugin

```bash
# Install via Claude Code plugin manager
# Or install manually:
pip install dreamwalker-mcp

# With all provider dependencies (recommended)
pip install dreamwalker-mcp[all]
```

### 2. Configure API Keys

Create `.env` file in your project directory:

```bash
# Core providers (at least one required)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...

# Optional providers
MISTRAL_API_KEY=...
COHERE_API_KEY=...
GEMINI_API_KEY=...

# Optional: Redis for caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. Start Orchestrating

In Claude Code, the MCP tools are automatically available:

```
You: Research quantum computing breakthroughs in 2025 using Beltalowda orchestration

Claude: I'll deploy 8 Belter agents to research different aspects:
- Academic papers (arXiv, Semantic Scholar)
- Industry news (news APIs)
- Technical implementations (GitHub)
- Financial impacts (stock data)
[orchestration proceeds with real-time progress updates...]
```

**That's it.** No manual tool chaining, no copy/paste, no synthesis headaches.

---

## Power User Examples

### Example 1: Academic Research Pipeline

**Scenario:** You're writing a paper on AI safety and need a comprehensive literature review.

**Without orchestration:**
1. Search arXiv manually
2. Search Semantic Scholar
3. Check Wikipedia for background
4. Read each paper individually
5. Manually synthesize findings
6. Format citations
7. Write summary (2-3 hours)

**With Dreamwalker:**

```
orchestrate_research(
    task="Comprehensive literature review on AI safety alignment research,
          focusing on papers from 2023-2025",
    num_agents=8,
    enable_drummer=True,      # Mid-level synthesis
    enable_camina=True,       # Executive summary
    generate_documents=True,
    document_formats=["pdf", "docx", "markdown"],
    provider_name="xai"
)
```

**Result:** 12 minutes. Full report with:
- 8 specialized research angles
- Drummer mid-level synthesis identifying themes
- Camina executive summary with key findings
- Properly formatted citations (BibTeX)
- PDF + DOCX + Markdown output
- Cost tracking and token usage

---

### Example 2: Market Research for Product Launch

**Scenario:** Your startup is launching an AI-powered health monitoring device. You need competitive analysis, market trends, regulatory landscape, and technical feasibility.

**Without orchestration:**
- Search Google (generic results)
- Check news sites manually
- Research competitors one by one
- Find academic papers on health monitoring
- Check GitHub for similar implementations
- Manual synthesis (4-6 hours)

**With Dreamwalker:**

```
orchestrate_search(
    query="AI health monitoring wearables market analysis 2025:
           competitors, regulations, technical approaches, user adoption",
    num_agents=5,
    allowed_agent_types=["news", "academic", "technical", "financial"],
    generate_documents=True,
    document_formats=["pdf", "markdown"]
)
```

**Result:** 8 minutes. Full report with:
- News agent: Latest product launches and trends
- Academic agent: Research papers on health monitoring algorithms
- Technical agent: GitHub repos and technical implementations
- Financial agent: Market size, funding rounds, stock performance
- Auto-generated executive summary

---

### Example 3: Technical Decision: Which LLM Provider?

**Scenario:** You need to choose an LLM provider for your production app. You want to compare pricing, performance, features, and reliability.

**Without orchestration:**
- Visit each provider's website manually
- Compare pricing pages
- Search for benchmarks
- Read Hacker News threads
- Check Reddit discussions
- Manual spreadsheet comparison (2-3 hours)

**With Dreamwalker:**

```
# Use Swarm for multi-source research
orchestrate_search(
    query="LLM provider comparison 2025: OpenAI vs Anthropic vs xAI vs Mistral
           - pricing, performance, reliability, features",
    num_agents=6,
    allowed_agent_types=["technical", "news", "financial"],
    provider_name="claude-sonnet-4"
)

# Then use vision analysis for docs comparison
analyze_image(
    provider_name="xai",
    image_data=<screenshot of pricing pages>,
    prompt="Extract and compare pricing tiers across all providers"
)
```

**Result:** 10 minutes. Comprehensive analysis with:
- Technical specs from docs and GitHub
- Recent news and announcements
- User feedback from multiple sources
- Pricing comparison table
- Performance benchmarks
- Final recommendation with rationale

---

### Example 4: Daily News Digest on Specialized Topic

**Scenario:** You're tracking developments in quantum computing and want a daily digest of relevant news, papers, and discussions.

**With Dreamwalker:**

```
# Morning routine automation
orchestrate_search(
    query="Quantum computing developments in the last 24 hours:
           academic papers, industry news, GitHub projects",
    num_agents=4,
    allowed_agent_types=["academic", "news", "technical"],
    generate_documents=True,
    document_formats=["markdown"]
)
```

**Result:** 3-5 minutes. Daily digest with:
- New arXiv papers published yesterday
- Industry announcements and news
- Active GitHub projects with recent commits
- Formatted markdown for easy scanning

---

### Example 5: Due Diligence for Investment

**Scenario:** Evaluating a startup for potential investment. Need financial health, market position, technical capabilities, and team background.

**With Dreamwalker:**

```
orchestrate_research(
    task="Due diligence on [Company Name]:
          financial analysis, market position, technical assessment,
          competitive landscape, team background",
    num_agents=8,
    enable_drummer=True,
    enable_camina=True,
    provider_name="gpt-4"
)
```

**Result:** 15 minutes. Investment memo with:
- Financial metrics and funding history
- Competitive analysis with market positioning
- Technical architecture assessment (GitHub analysis)
- Team backgrounds (LinkedIn, news mentions)
- Risk factors identified
- Executive summary with investment recommendation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code Client                      │
│                    (Your conversation)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol (stdio)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dreamwalker MCP Plugin                     │
│                      (6 MCP Servers)                         │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│  Unified   │  │ Providers  │  │    Data    │  │   Cache    │
│Orchestrator│  │   Server   │  │  Fetching  │  │  Manager   │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ Utilities  │  │Web Search  │  │  Document  │  │   Redis    │
│   Server   │  │   Server   │  │ Generator  │  │   Cache    │
└────────────┘  └────────────┘  └────────────┘  └────────────┘

Orchestration Flow (Beltalowda Example):
═══════════════════════════════════════════════

1. Task Decomposition
   └─> Break research task into 8 specialized angles

2. Parallel Agent Execution (Belters)
   ├─> Agent 1: Academic papers (arXiv, Semantic Scholar)
   ├─> Agent 2: News sources (News API, RSS)
   ├─> Agent 3: Wikipedia background
   ├─> Agent 4: GitHub technical implementations
   ├─> Agent 5: YouTube educational content
   ├─> Agent 6: Financial data (if relevant)
   ├─> Agent 7: Weather/environmental data (if relevant)
   └─> Agent 8: Open Library references

3. Mid-Level Synthesis (Drummer)
   └─> Identify patterns, themes, contradictions across all findings

4. Executive Synthesis (Camina)
   └─> Generate executive summary with key insights and recommendations

5. Document Generation
   ├─> PDF report (formatted with citations)
   ├─> DOCX document (editable)
   └─> Markdown file (portable)

6. Return OrchestratorResult
   └─> Structured data with all outputs + metadata
```

---

## Server Breakdown

Don't let 6 servers and 32+ tools overwhelm you. Here's how to think about them:

### 🎭 Orchestration Layer (Start Here)

**Unified Orchestrator Server** - Your command center
- `orchestrate_research` - Beltalowda hierarchical research (8 agents → Drummer → Camina)
- `orchestrate_search` - Swarm multi-agent search (5+ specialized agents)
- `get_orchestration_status` - Check progress of running workflows
- `cancel_orchestration` - Stop a workflow mid-execution
- `list_orchestrator_patterns` - See available patterns (Sequential, Conditional, Iterative)
- `list_registered_tools` - Browse 32+ available tool modules
- `execute_registered_tool` - Run any tool directly

**When to use:** Any research, analysis, or multi-source task. Start here 90% of the time.

**Resources:**
- `orchestrator://beltalowda/info` - Beltalowda pattern documentation
- `orchestrator://swarm/info` - Swarm pattern documentation
- `orchestrator://{task_id}/status` - Real-time workflow status
- `orchestrator://{task_id}/results` - Download generated reports

---

### 🤖 LLM Providers Server (Under the Hood)

**What it does:** Unified interface to 9 LLM providers. Orchestrators use this automatically, but you can call directly for specific use cases.

**Providers:**
- **Anthropic** (Claude Opus, Sonnet, Haiku)
- **OpenAI** (GPT-4, GPT-3.5-Turbo)
- **xAI** (Grok-3, vision support)
- **Mistral** (Mistral Large, Medium, Small)
- **Cohere** (Command R+)
- **Google** (Gemini Pro, Ultra)
- **Perplexity** (pplx-70b-online with web search)
- **Groq** (Llama 3.1 - ultra-fast inference)
- **HuggingFace** (Various open models)

**Tools:**
- `create_provider` - Initialize a provider (usually automatic)
- `chat_completion` - Direct chat with any provider
- `list_provider_models` - See available models
- `generate_image` - DALL-E 3, Aurora image generation
- `analyze_image` - Vision analysis (Claude, GPT-4, Grok)

**When to use directly:**
- You need a specific model (e.g., "use GPT-4 for this, Grok for that")
- Testing provider performance
- Building custom workflows
- Vision/image tasks

**Resources:**
- `provider://anthropic/info` - Claude models, pricing, capabilities
- `provider://openai/models` - Available GPT models
- `provider://xai/info` - Grok models and vision features

---

### 📊 Data Fetching Server (The Research Team)

**What it does:** 32+ specialized tool modules for gathering information from APIs and services.

**Categories:**

**Academic & Research:**
- `arxiv_search` - Search academic papers on arXiv
- `semantic_scholar_search` - Citation analysis and paper discovery
- `openlibrary_search` - Book metadata and references
- `wikipedia_search` - Background information and summaries
- `wikipedia_summary` - Quick article summaries

**News & Media:**
- `news_search` - Search news articles (NewsAPI)
- `news_headlines` - Latest headlines by category
- `youtube_search` - Video metadata and transcripts
- `youtube_video_details` - Detailed video information

**Technical & Code:**
- `github_repo_info` - Repository details and stats
- `github_search_repos` - Find repositories by topic
- `github_user_info` - User/organization profiles
- `github_repo_commits` - Commit history and activity

**Financial & Markets:**
- `stock_quote` - Real-time stock data
- `company_overview` - Company fundamentals
- `market_news` - Financial news and analysis

**Science & Space:**
- `nasa_apod` - Astronomy Picture of the Day
- `nasa_mars_photos` - Mars Rover images
- `nasa_earth_imagery` - Satellite imagery

**Location & Weather:**
- `weather_current` - Current weather conditions
- `weather_forecast` - Multi-day forecasts
- `weather_air_quality` - Air quality index

**When to use directly:**
- You need specific data from one source
- Building custom tools
- Testing API connectivity
- Debugging orchestration results

**Pro tip:** Most of the time, let orchestrators call these automatically. They're smart about which tools to use based on your query.

---

### 🗄️ Cache Manager Server (Performance Optimization)

**What it does:** Redis-based caching to avoid redundant API calls and speed up repeated queries.

**Tools:**
- `cache_get` - Retrieve cached value
- `cache_set` - Store value with TTL
- `cache_delete` - Remove cached entry
- `cache_clear` - Clear entire cache (or by pattern)

**When to use:**
- Building applications with repeated queries
- Performance optimization
- Workflow state persistence
- Session management

**Auto-caching:** Many data fetching tools cache automatically. You usually don't need to manage this manually.

---

### 🛠️ Utilities Server (Supporting Cast)

**What it does:** Miscellaneous utilities that don't fit other categories.

**Tools:**
- `text_to_speech` - Convert text to speech (gTTS)
- `parse_citation` - Parse BibTeX citations
- `format_citation` - Format citations in various styles
- `validate_citation` - Check citation completeness

**When to use:**
- Accessibility features (TTS)
- Academic writing assistance
- Citation management
- Document processing

---

### 🔍 Web Search Server (General Search)

**What it does:** Web search capabilities when you need broader internet access beyond specialized APIs.

**Tools:**
- `web_search` - Generic web search
- `brave_search` - Brave Search API (privacy-focused)
- `serp_search` - SerpAPI integration (Google results)

**When to use:**
- General queries not covered by specialized tools
- Real-time information needs
- Broader internet context
- Verification of specialized tool results

---

## Installation & Configuration

### Prerequisites

- Python 3.8 or higher
- Claude Code desktop application
- (Optional) Redis for caching

### Installation Methods

#### Method 1: Claude Code Plugin Manager (Recommended)

1. Open Claude Code
2. Go to Settings → Plugins
3. Search for "dreamwalker-mcp"
4. Click Install
5. Configure API keys in Settings

#### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/dreamwalker-mcp.git
cd dreamwalker-mcp

# Install in development mode
pip install -e .

# Install with all dependencies
pip install -e .[all]

# Or install from PyPI
pip install dreamwalker-mcp[all]
```

#### Method 3: Selective Installation

Install only what you need:

```bash
# Core + specific providers
pip install dreamwalker-mcp[anthropic,openai,xai]

# Core + data tools
pip install dreamwalker-mcp[arxiv,wikipedia,youtube,github]

# Core + utilities
pip install dreamwalker-mcp[tts,citations,documents]

# Everything
pip install dreamwalker-mcp[all]
```

### Configuration

#### API Keys

Create `.env` file in your project root:

```bash
# === LLM Providers (at least one required) ===
ANTHROPIC_API_KEY=sk-ant-...          # Claude models
OPENAI_API_KEY=sk-...                 # GPT-4, GPT-3.5, DALL-E
XAI_API_KEY=xai-...                   # Grok models
MISTRAL_API_KEY=...                   # Mistral models
COHERE_API_KEY=...                    # Cohere Command R+
GEMINI_API_KEY=...                    # Google Gemini
PERPLEXITY_API_KEY=...                # Perplexity online search
GROQ_API_KEY=...                      # Groq (fast Llama inference)
HUGGINGFACE_API_KEY=...               # HuggingFace models

# === Data Fetching (optional) ===
YOUTUBE_API_KEY=...                   # YouTube API
GITHUB_TOKEN=ghp_...                  # GitHub API
NASA_API_KEY=...                      # NASA APIs
NEWS_API_KEY=...                      # NewsAPI
ALPHAVANTAGE_API_KEY=...              # Stock market data
OPENWEATHER_API_KEY=...               # Weather data

# === Caching (optional) ===
REDIS_HOST=localhost                  # Redis host
REDIS_PORT=6379                       # Redis port
REDIS_PASSWORD=...                    # Redis password (if required)

# === Document Generation (optional) ===
DEFAULT_DOCUMENT_FORMAT=pdf           # pdf, docx, or markdown
CITATION_STYLE=apa                    # apa, mla, chicago, ieee
```

#### Claude Code MCP Configuration

The plugin uses `.mcp.json` for server registration. This is auto-configured, but you can customize:

```json
{
  "mcpServers": {
    "dreamwalker-unified": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.unified_server"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "XAI_API_KEY": "${XAI_API_KEY}"
      }
    },
    "dreamwalker-providers": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.providers_server"]
    },
    "dreamwalker-data": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.data_server"]
    },
    "dreamwalker-cache": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.cache_server"]
    },
    "dreamwalker-utility": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.utility_server"]
    },
    "dreamwalker-websearch": {
      "command": "python",
      "args": ["-m", "dreamwalker_mcp.mcp.web_search_server"]
    }
  }
}
```

### Verification

Test your installation:

```bash
# Check Python package
python -c "import dreamwalker_mcp; print(dreamwalker_mcp.__version__)"

# Test MCP servers (should show tool listings)
python -m dreamwalker_mcp.mcp.unified_server --list-tools

# Test provider connectivity
python -m dreamwalker_mcp.test_providers
```

In Claude Code, test by asking:

```
List available orchestrator patterns
```

You should see Beltalowda, Swarm, Sequential, Conditional, and Iterative patterns.

---

## Advanced Usage

### Custom Orchestrator Patterns

Dreamwalker includes 5 built-in patterns, but you can create custom ones:

```python
from dreamwalker_mcp.orchestration import BaseOrchestrator, OrchestratorConfig

class MyCustomOrchestrator(BaseOrchestrator):
    async def decompose_task(self, task, context=None):
        # Break task into subtasks
        return [
            SubTask(id="step1", description="First step", agent_type=AgentType.RESEARCHER),
            SubTask(id="step2", description="Second step", agent_type=AgentType.SYNTHESIZER)
        ]

    async def execute_subtask(self, subtask, context=None):
        # Execute individual subtask
        result = await self.provider.complete(subtask.description)
        return SubTaskResult(subtask_id=subtask.id, output=result)

    async def synthesize_results(self, results, context=None):
        # Combine all results
        combined = "\n".join([r.output for r in results])
        return SynthesisResult(output=combined)
```

See `ORCHESTRATOR_GUIDE.md` for full custom pattern documentation.

### Workflow State Management

Track long-running orchestrations:

```python
# Start workflow
result = orchestrate_research(
    task="Long research task",
    webhook_url="https://myapp.com/webhook"  # Async notifications
)

# Check status later
status = get_orchestration_status(task_id=result.task_id)
print(f"Progress: {status.progress}%")
print(f"Current step: {status.current_step}")

# Cancel if needed
cancel_orchestration(task_id=result.task_id)
```

### Streaming Progress Updates

Orchestrations emit real-time events via Server-Sent Events (SSE):

```python
# In your application
from dreamwalker_mcp.orchestration import streaming

async for event in streaming.subscribe(task_id):
    if event.type == "agent_start":
        print(f"Agent {event.agent_id} started: {event.description}")
    elif event.type == "agent_complete":
        print(f"Agent {event.agent_id} completed")
    elif event.type == "synthesis_start":
        print("Starting synthesis...")
    elif event.type == "complete":
        print("Workflow complete!")
```

### Cost Tracking

All orchestrations include cost tracking:

```python
result = orchestrate_research(task="My research task")

print(f"Total cost: ${result.metadata.total_cost}")
print(f"Total tokens: {result.metadata.total_tokens}")
print(f"Breakdown by provider:")
for provider, cost in result.metadata.cost_by_provider.items():
    print(f"  {provider}: ${cost}")
```

---

## Troubleshooting

### Common Issues

**1. "No module named 'dreamwalker_mcp'"**

Solution:
```bash
pip install dreamwalker-mcp
# Or for development:
pip install -e /path/to/dreamwalker-mcp
```

**2. "Provider not available: anthropic"**

Solution:
```bash
# Install provider dependencies
pip install dreamwalker-mcp[anthropic]

# Or install all providers
pip install dreamwalker-mcp[all]

# Check API key is set
echo $ANTHROPIC_API_KEY
```

**3. "Tool not found: arxiv_search"**

Solution:
```bash
# Install utility dependencies
pip install dreamwalker-mcp[arxiv]

# Verify server is running
python -m dreamwalker_mcp.mcp.utility_server --list-tools
```

**4. "Rate limit exceeded"**

Solutions:
- Add delays between requests (use `timeout_seconds` config)
- Enable caching to reduce redundant calls
- Use different providers (rotate API keys)
- Check provider pricing/limits

**5. "Redis connection failed"**

Solutions:
```bash
# Start Redis
redis-server

# Or disable caching
export REDIS_ENABLED=false

# Or use different Redis host
export REDIS_HOST=your-redis-host.com
```

**6. "Document generation failed"**

Solution:
```bash
# Install document generation dependencies
pip install dreamwalker-mcp[documents]

# Or install manually
pip install reportlab python-docx markdown
```

### Debug Mode

Enable verbose logging:

```bash
export DREAMWALKER_DEBUG=true
export LOG_LEVEL=DEBUG

# Run orchestration and check logs
python -m dreamwalker_mcp.test_orchestration
```

### Getting Help

- **Documentation:** https://dr.eamer.dev/dreamwalker/
- **GitHub Issues:** https://github.com/yourusername/dreamwalker-mcp/issues
- **API Reference:** https://dr.eamer.dev/dreamwalker/api/
- **Examples:** https://github.com/yourusername/dreamwalker-mcp/tree/main/examples
- **Community:** Join discussions in GitHub Discussions

**Related Documentation:**
- `ORCHESTRATOR_GUIDE.md` - Building custom orchestrators
- `ORCHESTRATOR_SELECTION_GUIDE.md` - Choosing the right pattern
- `ORCHESTRATOR_BENCHMARKS.md` - Performance expectations
- `IMAGE_VISION_GUIDE.md` - Vision and image generation
- `DATA_FETCHING_GUIDE.md` - Using data tools
- `LLM_PROVIDER_MATRIX.md` - Provider comparison
- `MIGRATION_ROADMAP.md` - Upgrading from older versions

---

## Performance & Benchmarks

### Beltalowda (8 agents, Drummer + Camina)

- **Average execution time:** 8-15 minutes
- **Token usage:** ~50,000-150,000 tokens (depending on depth)
- **Cost (xAI Grok):** $0.50-$2.00 per workflow
- **Document quality:** Production-ready reports with citations
- **Best for:** Deep research requiring multiple sources and synthesis

### Swarm (5 agents, specialized domains)

- **Average execution time:** 5-10 minutes
- **Token usage:** ~30,000-80,000 tokens
- **Cost (Claude Sonnet):** $0.30-$1.50 per workflow
- **Coverage:** 5+ specialized domains per query
- **Best for:** Broad exploratory research, market analysis

### Sequential Orchestrator

- **Execution time:** 3-8 minutes (depends on step count)
- **Token usage:** ~20,000-60,000 tokens
- **Best for:** Deterministic pipelines, content workflows

### Conditional Orchestrator

- **Execution time:** 2-10 minutes (depends on branch)
- **Token usage:** ~15,000-50,000 tokens
- **Best for:** Decision trees, branching logic

### Iterative Orchestrator

- **Execution time:** 5-20 minutes (depends on refinement cycles)
- **Token usage:** ~40,000-120,000 tokens
- **Best for:** Quality-driven workflows, iterative refinement

See `ORCHESTRATOR_BENCHMARKS.md` for detailed performance analysis.

---

## Contributing

Contributions welcome! Here's how to get started:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/dreamwalker-mcp.git
cd dreamwalker-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all deps
pip install -e .[all,dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Type checking
mypy dreamwalker_mcp/
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create a branch:** `git checkout -b feature/my-feature`
3. **Make changes** with clear commit messages
4. **Add tests** for new features
5. **Update documentation** as needed
6. **Run tests:** `pytest tests/`
7. **Submit PR** with description of changes

### Areas We Need Help

- **New orchestrator patterns** (graph-based, recursive, hybrid)
- **Additional data sources** (more tool modules)
- **Provider integrations** (new LLM providers)
- **Performance optimizations** (caching strategies, parallel execution)
- **Documentation improvements** (tutorials, examples)
- **Testing** (integration tests, edge cases)
- **Accessibility** (screen reader support, alternative outputs)

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused (single responsibility)
- Avoid "Created with Claude" comments (credit Luke Steuber instead)

---

## License

MIT License

Copyright (c) 2025 Luke Steuber

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgments

Built with:
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Claude](https://www.anthropic.com/) by Anthropic
- [OpenAI GPT](https://openai.com/)
- [xAI Grok](https://x.ai/)
- And many other open-source libraries (see `requirements.txt`)

**Author:** Luke Steuber
**Landing Page:** https://dr.eamer.dev/dreamwalker/
**Version:** 1.0.0
**License:** MIT

---

**Remember:** Orchestration > Individual tools. Deploy a research team, not just a chatbot.
