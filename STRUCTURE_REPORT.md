# Dreamwalker MCP Plugin Directory Structure Report

**Date**: 2025-11-19  
**Author**: Luke Steuber  
**Purpose**: Claude Code marketplace submission

## Directory Structure

```
/home/coolhand/dreamwalker-mcp/
├── .claude-plugin/
│   └── plugin.json                     # Plugin metadata for Claude Code marketplace
│
├── dreamwalker_mcp/                    # Main Python package
│   ├── __init__.py
│   ├── config.py                       # Configuration management
│   │
│   ├── mcp/                            # MCP servers
│   │   ├── __init__.py
│   │   ├── unified_server.py           # Unified orchestrator server
│   │   ├── providers_server.py         # LLM providers server
│   │   ├── data_server.py              # Data fetching server
│   │   ├── cache_server.py             # Cache management server
│   │   ├── utility_server.py           # Utilities server
│   │   ├── web_search_server.py        # Web search server
│   │   ├── app.py                      # HTTP bridge (legacy)
│   │   ├── streaming.py                # SSE streaming utilities
│   │   ├── tool_registry.py            # Tool registration system
│   │   │
│   │   └── stdio_servers/              # Stdio implementations for Claude Code
│   │       ├── __init__.py
│   │       ├── unified_stdio.py        # Unified orchestrator (stdio)
│   │       ├── providers_stdio.py      # LLM providers (stdio)
│   │       ├── data_stdio.py           # Data fetching (stdio)
│   │       ├── cache_stdio.py          # Cache management (stdio)
│   │       ├── utility_stdio.py        # Utilities (stdio)
│   │       └── web_search_stdio.py     # Web search (stdio)
│   │
│   ├── orchestration/                  # Multi-agent orchestrators
│   │   ├── __init__.py
│   │   ├── base_orchestrator.py
│   │   ├── beltalowda_orchestrator.py  # Hierarchical research
│   │   ├── swarm_orchestrator.py       # Multi-agent search
│   │   ├── conditional_orchestrator.py
│   │   ├── iterative_orchestrator.py
│   │   ├── sequential_orchestrator.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── streaming.py
│   │   └── utils.py
│   │
│   ├── llm_providers/                  # LLM provider abstractions
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── anthropic_provider.py       # Claude
│   │   ├── openai_provider.py          # GPT-4, DALL-E
│   │   ├── xai_provider.py             # Grok-3
│   │   ├── mistral_provider.py
│   │   ├── cohere_provider.py
│   │   ├── gemini_provider.py
│   │   ├── perplexity_provider.py
│   │   ├── groq_provider.py
│   │   ├── huggingface_provider.py
│   │   ├── elevenlabs_provider.py      # TTS
│   │   └── manus_provider.py
│   │
│   ├── tools/                          # Tool modules (32 files)
│   │   ├── __init__.py
│   │   ├── module_base.py              # Base class for tools
│   │   ├── registry.py                 # Tool registry
│   │   ├── provider_registry.py
│   │   ├── example_tool.py
│   │   │
│   │   ├── Provider tools:
│   │   ├── anthropic_tools.py
│   │   ├── openai_tools.py
│   │   ├── xai_tools.py
│   │   ├── mistral_tools.py
│   │   ├── cohere_tools.py
│   │   ├── gemini_tools.py
│   │   ├── perplexity_tools.py
│   │   ├── groq_tools.py
│   │   ├── huggingface_tools.py
│   │   ├── elevenlabs_tools.py
│   │   │
│   │   ├── Data tools:
│   │   ├── wikipedia_tool.py
│   │   ├── youtube_tool.py
│   │   ├── finance_tool.py
│   │   ├── weather_tool.py
│   │   ├── github_tool.py
│   │   ├── nasa_tool.py
│   │   ├── news_tool.py
│   │   ├── openlibrary_tool.py
│   │   ├── arxiv_tool.py
│   │   ├── semantic_scholar_tool.py
│   │   ├── census_tool.py
│   │   ├── archive_tool.py
│   │   │
│   │   ├── Utility tools:
│   │   ├── web_search_tool.py
│   │   ├── image_generation_tools.py
│   │   ├── vision_tools.py
│   │   ├── tts_tools.py
│   │   └── data_tool_base.py
│   │
│   ├── data_fetching/                  # Data fetching clients
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── wikipedia_client.py
│   │   ├── youtube_client.py
│   │   ├── finance_client.py
│   │   ├── weather_client.py
│   │   ├── github_client.py
│   │   ├── nasa_client.py
│   │   ├── news_client.py
│   │   ├── openlibrary_client.py
│   │   ├── census_client.py
│   │   ├── arxiv_client.py
│   │   ├── semantic_scholar.py
│   │   └── archive_client.py
│   │
│   ├── utils/                          # Utilities
│   │   ├── __init__.py
│   │   ├── async_adapter.py
│   │   ├── citation.py
│   │   ├── crypto.py
│   │   ├── data_validation.py
│   │   ├── document_parsers.py
│   │   ├── embeddings.py
│   │   ├── execution.py
│   │   ├── file_utils.py
│   │   ├── multi_search.py
│   │   ├── progress.py
│   │   ├── rate_limiter.py
│   │   ├── retry_logic.py
│   │   ├── text_processing.py
│   │   ├── time_utils.py
│   │   ├── tts.py
│   │   └── vision.py
│   │
│   └── web/                            # Web components (Flask blueprints)
│       ├── __init__.py
│       └── dreamwalker/
│
├── Configuration Files:
├── .mcp.json                           # MCP server configurations (stdio)
├── .env.example                        # Example environment variables
├── .gitignore                          # Git ignore patterns
├── setup.py                            # Setup configuration (setuptools)
├── pyproject.toml                      # Modern Python packaging config
├── requirements.txt                    # Core dependencies
├── requirements-all.txt                # All optional dependencies
├── LICENSE                             # MIT License
├── MANIFEST.in                         # Package manifest
└── README.md                           # Plugin documentation
```

## File Counts

- **MCP Servers**: 6 servers x 2 implementations (HTTP + stdio) = 13 files
- **Stdio Servers**: 6 files in `stdio_servers/`
- **Orchestrators**: 11 files
- **LLM Providers**: 13 provider implementations
- **Tools**: 32 tool modules
- **Data Fetching**: 14 client implementations
- **Utilities**: 17 utility modules
- **Total Python Files**: ~100+ files

## MCP Servers (Stdio Mode)

### 1. Unified Orchestrator (`unified`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.unified_stdio`
- **Tools**: 
  - `orchestrate_research` (Beltalowda)
  - `orchestrate_search` (Swarm)
  - `get_orchestration_status`
  - `cancel_orchestration`
  - `list_orchestrator_patterns`
- **Env Vars**: All LLM provider API keys

### 2. LLM Providers (`providers`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.providers_stdio`
- **Tools**:
  - `create_provider`
  - `chat_completion`
  - `generate_image`
  - `analyze_image`
  - `list_provider_models`
- **Providers**: Anthropic, OpenAI, xAI, Mistral, Cohere, Gemini, Perplexity, Groq, HuggingFace
- **Env Vars**: All LLM provider API keys

### 3. Data Fetching (`data`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.data_stdio`
- **Tools** (8 clients):
  - Wikipedia search/summaries
  - YouTube video metadata
  - Finance (stocks, company info)
  - Weather (current/forecast)
  - GitHub (repos, issues, commits)
  - NASA (APOD, Mars Rover)
  - News (article search)
  - OpenLibrary (book search)
- **Env Vars**: YOUTUBE_API_KEY, GITHUB_TOKEN, NASA_API_KEY, NEWS_API_KEY, OPENWEATHER_API_KEY, ALPHA_VANTAGE_API_KEY

### 4. Cache Manager (`cache`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.cache_stdio`
- **Tools**:
  - `cache_get`
  - `cache_set`
  - `cache_delete`
  - `cache_clear`
  - `cache_keys`
- **Env Vars**: REDIS_HOST, REDIS_PORT

### 5. Utilities (`utility`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.utility_stdio`
- **Tools**:
  - ArXiv paper search
  - Semantic Scholar citations
  - Text-to-speech (gTTS)
  - Citation management (BibTeX)
- **Env Vars**: None required

### 6. Web Search (`web_search`)
- **Command**: `python -m dreamwalker_mcp.mcp.stdio_servers.web_search_stdio`
- **Tools**:
  - Multi-engine web search
  - Search result parsing
- **Env Vars**: SERP_API_KEY, BRAVE_API_KEY

## Plugin Metadata (`.claude-plugin/plugin.json`)

```json
{
  "name": "dreamwalker-mcp",
  "version": "1.0.0",
  "displayName": "Dreamwalker MCP",
  "description": "Multi-agent orchestration and LLM provider abstraction",
  "author": "Luke Steuber",
  "license": "MIT",
  "icon": "🌊",
  "mcpServers": [
    {"id": "unified", "name": "Unified Orchestrator"},
    {"id": "providers", "name": "LLM Providers"},
    {"id": "data", "name": "Data Fetching"},
    {"id": "cache", "name": "Cache Manager"},
    {"id": "utility", "name": "Utilities"},
    {"id": "web_search", "name": "Web Search"}
  ]
}
```

## Key Features

### Multi-Agent Orchestration
- **Beltalowda**: Hierarchical research (Belters → Drummer → Camina)
- **Swarm**: Domain-specific multi-agent search
- SSE streaming for real-time progress
- Task status tracking and cancellation
- Webhook notifications

### LLM Provider Support
- 9 providers with unified interface
- Chat completion with streaming
- Vision analysis (Claude, GPT-4, Grok)
- Image generation (DALL-E 3, Aurora)
- Consistent error handling

### Data Access
- 29+ tool modules
- 8 data fetching clients
- Automatic caching
- Rate limiting

### Utilities
- Text-to-speech
- Citation management
- Document generation (PDF, DOCX, Markdown)
- Web search
- Redis caching

## Installation Options

### Core (minimal)
```bash
pip install dreamwalker-mcp
```

### All Features
```bash
pip install dreamwalker-mcp[all]
```

### Selective
```bash
pip install dreamwalker-mcp[anthropic,openai,xai,arxiv,redis]
```

## Package Information

- **Package Name**: `dreamwalker-mcp`
- **Python Version**: >=3.8
- **License**: MIT
- **Author**: Luke Steuber
- **Homepage**: https://github.com/yourusername/dreamwalker-mcp

## Next Steps

1. Test installation: `pip install -e .`
2. Test stdio servers: Each server can be run with `python -m dreamwalker_mcp.mcp.stdio_servers.<server>_stdio`
3. Verify MCP protocol compliance
4. Update README with examples
5. Submit to Claude Code marketplace

## File Locations

All files are located at: `/home/coolhand/dreamwalker-mcp/`

Key files:
- Plugin metadata: `.claude-plugin/plugin.json`
- MCP config: `.mcp.json`
- Package config: `setup.py`, `pyproject.toml`
- Documentation: `README.md`, `LICENSE`
- Environment: `.env.example`
- Ignore patterns: `.gitignore`

