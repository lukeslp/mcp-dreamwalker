# Dreamwalker MCP Naming Convention - Final

## Hierarchy

1. **CONDUCTOR**: `dreamwalker` (the top-level conductor that orchestrates everything)
2. **ORCHESTRATOR**: `cascade`, `swarm`, `providers`, `research` (coordinate multiple agents)
3. **AGENT**: `llm`, `wikipedia`, `arxiv`, `github`, etc. (individual workers)
4. **UTILITY**: `cache`, `registry`, `parser`, `citations` (support tools)

## Tool Naming Pattern

Format: `{role}.{slug}.{action}`

### Examples:
- `dreamwalker.cascade.orchestrate` - Run Dream Cascade workflow
- `dreamwalker.swarm.orchestrate` - Run Dream Swarm workflow
- `dreamwalker.status` - Check workflow status
- `dreamwalker.patterns` - List available patterns
- `orchestrator.providers.list` - List LLM providers
- `agent.llm.complete` - Complete text with LLM
- `agent.wikipedia.search` - Search Wikipedia
- `utility.cache.get` - Get from cache

## Resource URI Pattern

Format: `dreamwalker://{role}.{slug}/{path}`

### Examples:
- `dreamwalker://orchestrator.cascade/info` - Cascade pattern info
- `dreamwalker://orchestrator.swarm/info` - Swarm pattern info
- `dreamwalker://{task_id}/status` - Workflow status
- `dreamwalker://{task_id}/results` - Workflow results

## In Claude Code

The tools appear with the server prefix:
- `mcp__dreamwalker-unified__dreamwalker.cascade.orchestrate`
- `mcp__dreamwalker-unified__dreamwalker.status`
- `mcp__dreamwalker-providers__agent.llm.complete`

## Pattern Names

- **cascade** (formerly dream-cascade, beltalowda) - Hierarchical research
- **swarm** (formerly dream-swarm) - Multi-agent search

## Key Points

1. **dreamwalker** is the conductor name (not "conductor")
2. **beltalowda** is completely removed - use **cascade**
3. Resources use `dreamwalker://` prefix for all URIs
4. Top-level dreamwalker tools don't need "conductor" in the path
5. Backward compatibility maintained for legacy names