# Dreamwalker Tool Inventory

## Naming Convention
All tools follow the pattern: `dreamwalker.{type}.{name}`

## Available Tools by Category

### 🎭 Orchestrators (`dreamwalker.orchestrate.*`)
Execute multi-agent workflows

| Tool | Description | Status |
|------|-------------|---------|
| `dreamwalker.orchestrate.cascade` | Dream Cascade - Hierarchical 3-tier research (workers→synthesis→executive) | ✅ Implemented |
| `dreamwalker.orchestrate.swarm` | Dream Swarm - Parallel multi-domain search agents | ✅ Implemented |

### 🤖 Agents (`dreamwalker.agent.*`)
Specialized agents that coordinate multiple tools

| Tool | Description | Status |
|------|-------------|---------|
| `dreamwalker.agent.researcher` | Research agent using arxiv, scholar, wikipedia, etc. | 🔄 Mapped |
| `dreamwalker.agent.writer` | Writing agent with style adaptation | 📋 Planned |
| `dreamwalker.agent.analyst` | Data analysis agent | 📋 Planned |
| `dreamwalker.agent.janitor` | Cleanup and organization agent | 📋 Planned |

### 🔧 Individual Tools (`dreamwalker.tool.*`)
Direct access to data sources

| Tool | Description | Server |
|------|-------------|---------|
| `dreamwalker.tool.arxiv` | ArXiv paper search | data |
| `dreamwalker.tool.census.acs` | US Census ACS data | data |
| `dreamwalker.tool.census.saipe` | US Census poverty estimates | data |
| `dreamwalker.tool.census.variables` | Census variable catalog | data |
| `dreamwalker.tool.scholar` | Semantic Scholar search | data |
| `dreamwalker.tool.scholar.paper` | Semantic Scholar paper details | data |
| `dreamwalker.tool.wayback` | Internet Archive snapshots | data |
| `dreamwalker.tool.wayback.snapshots` | List all snapshots | data |
| `dreamwalker.tool.finance.stock` | Stock market data (Alpha Vantage) | data |
| `dreamwalker.tool.github` | GitHub repository search | data |
| `dreamwalker.tool.nasa.apod` | NASA Picture of the Day | data |
| `dreamwalker.tool.news` | News headlines | data |
| `dreamwalker.tool.books` | OpenLibrary book search | data |
| `dreamwalker.tool.weather` | Current weather (OpenWeather) | data |
| `dreamwalker.tool.wikipedia` | Wikipedia search & content | data |
| `dreamwalker.tool.youtube` | YouTube video search | data |

### 🎨 Generation (`dreamwalker.generate.*`)
Multi-modal content generation

| Tool | Description | Provider | Modalities |
|------|-------------|----------|------------|
| `dreamwalker.generate.anthropic` | Claude models | Anthropic | Text |
| `dreamwalker.generate.openai` | GPT, DALL-E, TTS | OpenAI | Text, Image, Audio |
| `dreamwalker.generate.xai` | Grok models | xAI | Text |
| `dreamwalker.generate.mistral` | Mistral models | Mistral | Text |
| `dreamwalker.generate.cohere` | Command models | Cohere | Text |
| `dreamwalker.generate.gemini` | Gemini models | Google | Text, Vision |
| `dreamwalker.generate.perplexity` | Perplexity models | Perplexity | Text |
| `dreamwalker.generate.groq` | Fast inference | Groq | Text |
| `dreamwalker.generate.huggingface` | Open models | HuggingFace | Text |
| `dreamwalker.generate.elevenlabs` | Voice synthesis | ElevenLabs | Audio |
| `dreamwalker.generate.stability` | Stable Diffusion | Stability AI | Image |
| `dreamwalker.generate.runway` | Video generation | Runway | Video |

### 🛠️ Utilities (`dreamwalker.utility.*`)
Support tools and infrastructure

| Tool | Description | Server |
|------|-------------|---------|
| `dreamwalker.utility.status` | Check workflow status | unified |
| `dreamwalker.utility.cancel` | Cancel running workflow | unified |
| `dreamwalker.utility.patterns` | List orchestrator patterns | unified |
| `dreamwalker.utility.registry.list` | List all registered tools | unified |
| `dreamwalker.utility.registry.execute` | Execute any registered tool | unified |
| `dreamwalker.utility.cache.get` | Get from Redis cache | cache |
| `dreamwalker.utility.cache.set` | Store in cache with TTL | cache |
| `dreamwalker.utility.cache.delete` | Delete from cache | cache |
| `dreamwalker.utility.cache.increment` | Increment counter | cache |
| `dreamwalker.utility.cache.exists` | Check key existence | cache |
| `dreamwalker.utility.cache.expire` | Set expiration | cache |
| `dreamwalker.utility.cache.list` | List keys by pattern | cache |
| `dreamwalker.utility.parse.document` | Parse 50+ file formats | utility |
| `dreamwalker.utility.citations.extract` | Extract citations from text | utility |
| `dreamwalker.utility.citations.bibtex` | Format as BibTeX | utility |
| `dreamwalker.utility.search.web` | Multi-engine web search | web_search |
| `dreamwalker.utility.providers.list` | List available LLM providers | providers |
| `dreamwalker.utility.providers.create` | Create provider instance | providers |
| `dreamwalker.utility.providers.models` | List models for provider | providers |

## MCP Server Configuration

### In Claude Desktop (`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dreamwalker-unified": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.unified_stdio"]
    },
    "dreamwalker-providers": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.providers_stdio"]
    },
    "dreamwalker-data": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.data_stdio"]
    },
    "dreamwalker-cache": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.cache_stdio"]
    },
    "dreamwalker-utility": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.utility_stdio"]
    },
    "dreamwalker-web-search": {
      "command": "python3",
      "args": ["-m", "dreamwalker_mcp.mcp.stdio_servers.web_search_stdio"]
    }
  }
}
```

### In Claude Code
Tools appear as: `mcp__<server-name>__<tool-name>`

Examples:
- `mcp__dreamwalker-unified__dreamwalker.orchestrate.cascade`
- `mcp__dreamwalker-data__dreamwalker.tool.arxiv`
- `mcp__dreamwalker-providers__dreamwalker.generate.anthropic`

## Status Legend
- ✅ Implemented - Fully working with new naming
- 🔄 Mapped - Legacy name mapped, needs server update
- 📋 Planned - Defined but not yet implemented

## Next Steps

1. **Update remaining servers** to use new naming pattern
2. **Implement agents** (researcher, writer, analyst, janitor)
3. **Add generation tools** with proper provider mapping
4. **Create conductors** above orchestrators for meta-coordination