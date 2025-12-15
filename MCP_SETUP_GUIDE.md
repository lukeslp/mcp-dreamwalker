# Dreamwalker MCP Setup Guide for Claude Code

## Overview
This guide helps you connect the Dreamwalker MCP servers to Claude Code. The servers are now configured in your Claude Desktop configuration file.

## Status
✅ MCP servers added to Claude Desktop config at: `/home/coolhand/.config/Claude/claude_desktop_config.json`
✅ All 6 stdio servers tested and working
⚠️  Environment variables need to be configured
⚠️  Claude Code needs restart to detect new servers

## Available MCP Servers

1. **dreamwalker-unified** - Unified Orchestrator Server
   - Tools: dream_orchestrate_research, dream_orchestrate_search, dreamwalker_status, etc.
   - Required keys: LLM provider API keys

2. **dreamwalker-providers** - LLM Providers Server  
   - Tools: list_available_providers, chat_completion, generate_image, analyze_image
   - Supports: Anthropic, OpenAI, xAI, Mistral, Cohere, Gemini, Perplexity, Groq, HuggingFace

3. **dreamwalker-data** - Data Fetching Server
   - Tools: Wikipedia, YouTube, Finance, Weather, GitHub, NASA, News, OpenLibrary, ArXiv, Census
   - Required keys: Various data source API keys

4. **dreamwalker-cache** - Cache Manager Server
   - Tools: cache_get, cache_set, cache_delete, cache_increment
   - Requires: Redis server running on localhost:6379

5. **dreamwalker-utility** - Utilities Server
   - Tools: parse_document, multi_provider_search, extract_citations
   - No API keys required

6. **dreamwalker-web-search** - Web Search Server
   - Tools: web_search with SerpAPI, Tavily, or Brave
   - Required keys: SERP_API_KEY or BRAVE_API_KEY

## Environment Setup

### Option 1: Set in shell profile (Recommended)
Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Core LLM Provider Keys
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"  
export XAI_API_KEY="your-key-here"
export MISTRAL_API_KEY="your-key-here"
export COHERE_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
export PERPLEXITY_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
export HUGGINGFACE_API_KEY="your-key-here"

# Data Source Keys
export YOUTUBE_API_KEY="your-key-here"
export GITHUB_TOKEN="your-key-here"
export NASA_API_KEY="your-key-here"
export NEWS_API_KEY="your-key-here"
export OPENWEATHER_API_KEY="your-key-here"
export ALPHA_VANTAGE_API_KEY="your-key-here"
export CENSUS_API_KEY="your-key-here"

# Search Provider Keys
export SERP_API_KEY="your-key-here"
export BRAVE_API_KEY="your-key-here"

# Redis Configuration (defaults shown)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

Then reload your shell:
```bash
source ~/.bashrc
```

### Option 2: Use .env file
Create `/home/coolhand/.env` and Claude Code will load it automatically.

## Next Steps

1. **Configure Environment Variables**
   - Add your API keys using one of the options above
   - At minimum, configure ANTHROPIC_API_KEY and XAI_API_KEY for orchestration

2. **Ensure Redis is Running** (for cache server)
   ```bash
   sudo systemctl start redis-server
   ```

3. **Restart Claude Code**
   - Fully quit Claude Code (not just close window)
   - Start Claude Code again
   - The MCP servers will be available automatically

4. **Verify Connection**
   - In Claude Code, you should see new tools prefixed with `mcp__`
   - Try: `@mcp__dreamwalker-unified__dreamwalker_patterns` to list orchestrator patterns

## Tool Naming Convention

The tools follow this pattern in Claude Code:
- `mcp__<server-name>__<tool-name>`

Examples:
- `mcp__dreamwalker-unified__dream_orchestrate_research`
- `mcp__dreamwalker-providers__chat_completion`
- `mcp__dreamwalker-data__dream_of_wikipedia`

## Troubleshooting

1. **Tools not appearing**: Ensure Claude Code is fully restarted
2. **Authentication errors**: Check API keys are properly exported
3. **Redis connection errors**: Ensure Redis server is running
4. **Module not found**: Ensure dreamwalker-mcp is installed: `pip install -e /home/coolhand/dreamwalker-mcp`

## Testing Individual Servers

Test a server manually:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 -m dreamwalker_mcp.mcp.stdio_servers.unified_stdio
```