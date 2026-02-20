# Dreamwalker MCP User Guide

**Version:** 1.0.0  
**Date:** November 20, 2025  
**Author:** Luke Steuber

---

## What is Dreamwalker MCP?

Dreamwalker MCP is a comprehensive Model Context Protocol (MCP) server that provides coding tools (like Cursor and Claude Code) with access to:

- **31+ Tools** across 5 categories
- **14 LLM Providers** (Anthropic, OpenAI, xAI, and more)
- **12 Data Sources** (Census Bureau, arXiv, GitHub, YouTube, and more)
- **Redis Caching** for performance optimization
- **Document Parsing** for 50+ file formats
- **Orchestration Workflows** for complex multi-agent research

---

## Quick Start

### Installation

1. **Clone or install the package:**
```bash
pip install -e /path/to/dreamwalker-mcp
```

2. **Set up API keys:**
Create a `.env` file with your API keys:
```bash
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
XAI_API_KEY=your-key-here
MISTRAL_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
PERPLEXITY_API_KEY=your-key-here
CENSUS_API_KEY=your-key-here
```

3. **Configure your IDE:**

**For Cursor:**
Create `~/.cursor/config.json`:
```json
{
  "mcpServers": {
    "dreamwalker-mcp": {
      "command": "python3",
      "args": ["/path/to/dreamwalker-mcp/stdio_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

**For Claude Code:**
Create `~/.config/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "dreamwalker-mcp": {
      "command": "python3",
      "args": ["/path/to/dreamwalker-mcp/stdio_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

4. **Restart your IDE**

---

## Available Tools

### LLM Provider Tools (5 tools)

#### `create_provider`
Create and cache an LLM provider instance.

**Arguments:**
- `provider_name` (required): Provider to use (anthropic, openai, xai, mistral, etc.)
- `model` (optional): Specific model to use

**Example:**
```
Use create_provider with provider_name "anthropic" and model "claude-sonnet-4-5"
```

#### `list_provider_models`
List available models for a provider.

**Arguments:**
- `provider_name` (required): Provider name

**Example:**
```
Use list_provider_models with provider "openai"
```

#### `chat_completion`
Generate a chat completion using any LLM provider.

**Arguments:**
- `provider_name` (required): Provider to use
- `messages` (required): Array of message objects [{role, content}]
- `model` (optional): Specific model
- `max_tokens` (optional): Maximum tokens
- `temperature` (optional): Temperature (0-2)

**Example:**
```
Use chat_completion with provider "anthropic" and message "Explain quantum computing"
```

#### `generate_image`
Generate an image using DALL-E or Aurora.

**Arguments:**
- `provider_name` (required): "openai" or "xai"
- `prompt` (required): Image description
- `size` (optional): Image size (e.g., "1024x1024")

**Example:**
```
Use generate_image with provider "openai" and prompt "a serene mountain landscape at sunset"
```

#### `analyze_image`
Analyze an image using vision capabilities.

**Arguments:**
- `provider_name` (required): Provider with vision (anthropic, openai, xai)
- `image_data` (required): Base64-encoded image
- `prompt` (required): Analysis question

**Example:**
```
Use analyze_image with provider "anthropic" to describe the image
```

---

### Data Fetching Tools (8 tools)

#### `dream_of_census_acs`
Fetch American Community Survey demographics data.

**Arguments:**
- `year` (required): Data year (e.g., 2022)
- `variables` (optional): Variable mapping dict
- `geography` (optional): Geographic level (default: "county:*")
- `state` (optional): State FIPS code filter

**Example:**
```
Use dream_of_census_acs with year 2022 to get poverty rates by county
```

#### `dream_of_census_saipe`
Fetch poverty estimates from SAIPE dataset.

**Example:**
```
Use dream_of_census_saipe with year 2022 for state-level poverty data
```

#### `dream_of_arxiv`
Search arXiv for academic papers.

**Arguments:**
- `query` (required): Search query
- `max_results` (optional): Number of results (default: 10)

**Example:**
```
Use dream_of_arxiv to find 10 papers on "transformer neural networks"
```

#### `dream_of_semantic_scholar`
Search research papers via Semantic Scholar.

**Example:**
```
Use dream_of_semantic_scholar to search "machine learning ethics"
```

#### `dream_of_wayback`
Get archived snapshots from Wayback Machine.

**Arguments:**
- `url` (required): URL to look up
- `timestamp` (optional): Specific timestamp

**Example:**
```
Use dream_of_wayback to get a snapshot of example.com from 2020
```

---

### Caching Tools (7 tools)

#### `cache_get`
Retrieve a value from Redis cache.

**Arguments:**
- `key` (required): Cache key

#### `cache_set`
Store a value in Redis cache.

**Arguments:**
- `key` (required): Cache key
- `value` (required): Value to store
- `ttl` (optional): Time-to-live in seconds

**Example:**
```
Use cache_set with key "research_data" value "..." and ttl 3600
```

#### `cache_delete`
Delete a key from cache.

#### `cache_increment`
Increment a counter in cache.

#### `cache_exists`
Check if a key exists in cache.

#### `cache_clear_namespace`
Clear all keys in a namespace.

#### `cache_list_keys`
List keys matching a pattern.

---

### Utility Tools (4 tools)

#### `parse_document`
Extract text from 50+ file formats (PDF, DOCX, Excel, code files, notebooks).

**Arguments:**
- `file_path` (required): Path to file
- `extract_metadata` (optional): Include metadata (default: false)

**Example:**
```
Use parse_document on ~/Documents/report.pdf
```

#### `multi_provider_search`
Execute parallel searches across multiple providers.

**Arguments:**
- `queries` (required): Array of query strings
- `providers` (optional): List of providers to use

**Example:**
```
Use multi_provider_search with queries ["AI ethics", "AGI timeline", "AI safety"]
```

#### `format_citation_bibtex`
Format academic citation in BibTeX format.

#### `format_citation_apa`
Format academic citation in APA format.

---

### Orchestration Tools (7+ tools)

#### `dream_research`
Execute Dream Cascade hierarchical research workflow.

**Arguments:**
- `task` (required): Research task description
- `num_agents` (optional): Number of agents (default: 12)
- `provider` (optional): LLM provider to use
- `stream` (optional): Enable streaming (default: true)

**Example:**
```
Use dream_research to investigate "AI alignment approaches" with 12 agents
```

**Process:**
1. Belters (8-15 agents): Gather information from specific domains
2. Drummers (3-5 agents): Synthesize findings across domains
3. Camina (1 agent): Executive synthesis and final report

**Duration:** 2-10 minutes depending on complexity

#### `dream_search`
Execute Dream Swarm multi-agent search workflow.

**Arguments:**
- `task` (required): Search task description
- `num_agents` (optional): Number of agents (default: 9)
- `domain_types` (optional): Domains to search (text, image, video, news, academic, social, product, technical, general)

**Example:**
```
Use dream_search to verify facts about "quantum computing breakthroughs 2024"
```

#### `dreamwalker_status`
Check status of a running workflow.

**Arguments:**
- `task_id` (required): Workflow task ID

#### `dreamwalker_cancel`
Cancel a running workflow.

#### `dreamwalker_patterns`
List available orchestration patterns.

#### `dreamwalker_list_tools`
List all registered tools.

#### `dreamwalker_execute_tool`
Execute a registered tool by name.

---

## Usage Examples

### Example 1: Research Paper Analysis

```
1. Use dream_of_arxiv to find papers on "transformers in NLP"
2. Use cache_set to store the results with key "arxiv_transformers"
3. For each paper:
   - Use parse_document to extract text from PDF
   - Use chat_completion to summarize key findings
4. Use multi_provider_search to verify claims
5. Use format_citation_bibtex to generate citations
```

### Example 2: Census Data Analysis

```
1. Use dream_of_census_acs with year 2022 for poverty data
2. Use cache_set to store the dataset
3. Use chat_completion with GPT-4 to analyze trends
4. Generate visualizations
5. Use parse_document to compare with historical reports
```

### Example 3: Comprehensive Research Report

```
1. Use dream_research to investigate "renewable energy adoption"
2. Monitor progress with dreamwalker_status
3. When complete, extract final report
4. Use generate_image to create infographics
5. Use cache_set to store the complete report
```

---

## Best Practices

### 1. API Key Management
- Store keys in environment variables, never in code
- Use different keys for development and production
- Rotate keys periodically

### 2. Cost Optimization
- Use cheaper models (mini, haiku) for simple tasks
- Cache expensive API results with appropriate TTLs
- Use batch operations when possible
- Monitor costs using the cost tracking features

### 3. Performance
- Cache frequently accessed data
- Use appropriate TTLs (short for dynamic data, long for static)
- Leverage parallel operations (multi_provider_search)
- Stream long-running operations

### 4. Error Handling
- Always check if required API keys are set before making calls
- Use try-catch patterns in your code
- Monitor logs for failures
- Implement retry logic with exponential backoff

### 5. Orchestration
- Start with smaller num_agents for testing
- Use streaming to monitor progress
- Cancel long-running tasks if needed
- Cache intermediate results

---

## Troubleshooting

### Tool Not Found
**Problem:** IDE says tool doesn't exist  
**Solution:**
1. Restart your IDE completely
2. Check that MCP server config is in the right location
3. Verify the stdio_server.py path is correct

### ImportError
**Problem:** Import errors when running  
**Solution:**
```bash
cd /path/to/dreamwalker-mcp
pip install -e .
```

### API Key Errors
**Problem:** "API key not found" or authentication errors  
**Solution:**
1. Check that keys are in .env file or environment
2. Verify key format (correct prefix: sk-, xai-, etc.)
3. Test key validity with a simple API call

### Cache Connection Failed
**Problem:** Redis connection errors  
**Solution:**
1. Ensure Redis is running: `redis-cli ping`
2. Check REDIS_HOST and REDIS_PORT environment variables
3. Install Redis if not present: `sudo apt install redis-server`

### Slow Performance
**Problem:** Tools taking too long  
**Solution:**
1. Check network connectivity
2. Reduce num_agents for orchestration
3. Use caching to avoid repeated API calls
4. Use faster models for non-critical tasks

---

## Advanced Topics

### Custom Tool Integration

You can extend Dreamwalker MCP with your own tools. See the developer documentation for details.

### Monitoring & Observability

The system includes built-in cost tracking and metrics collection:

```python
from shared.observability import get_cost_tracker, get_metrics_collector

# View costs
tracker = get_cost_tracker()
print(tracker.get_daily_costs(date.today()))

# View metrics
metrics = get_metrics_collector()
print(metrics.get_stats())
```

### Webhook Integration

For long-running workflows, you can register webhooks to receive progress notifications:

```python
# In your application code
from shared.mcp.streaming import get_webhook_manager

webhook_mgr = get_webhook_manager()
webhook_mgr.register_webhook(
    task_id="my-task",
    url="https://your-app.com/webhook",
    secret="your-webhook-secret"
)
```

---

## Support & Community

- **Documentation:** See the main README.md and other guides
- **Issues:** Report bugs and feature requests via GitHub
- **Contributing:** Pull requests welcome!

---

## License

See LICENSE file for terms and conditions.

---

**Made by Luke Steuber**  
**Version 1.0.0 | November 2025**

