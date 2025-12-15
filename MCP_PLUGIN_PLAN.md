# MCP Plugin Development and Deployment Plan

## Overview
This document outlines the comprehensive plan to get the MCP (Model Context Protocol) servers working with Claude Code and package them for the Claude plugin marketplace.

## Current Status

### ❌ Critical Issues
1. **All MCP servers are failing** with error: `Unknown method: initialize`
2. **Missing MCP protocol implementation** - servers don't implement required protocol methods
3. **No proper MCP server base class** - using custom implementation instead of MCP SDK

### ✅ What's Working
1. **Server infrastructure** - Flask HTTP endpoints are functional
2. **Orchestrator logic** - Core orchestration functionality is implemented
3. **Provider compatibility** - Fixed chat() method for all LLM providers
4. **Anti-hallucination measures** - Updated prompts and temperature settings

## Phase 1: Fix MCP Protocol Implementation (URGENT)

### 1.1 Implement Required MCP Methods
Each stdio server must implement:
- `initialize` - Required handshake method
- `initialized` - Confirmation method
- `tools/list` - List available tools
- `tools/call` - Execute tool calls
- `resources/list` - List available resources (optional)
- `resources/read` - Read resource content (optional)

### 1.2 Use Official MCP SDK
Replace custom implementation with official MCP Python SDK:
```bash
pip install mcp
```

### 1.3 Update Stdio Servers
Convert each server to use MCP SDK:
- `/dreamwalker_mcp/mcp/stdio_servers/unified_stdio.py`
- `/dreamwalker_mcp/mcp/stdio_servers/cache_stdio.py`
- `/dreamwalker_mcp/mcp/stdio_servers/data_stdio.py`
- `/dreamwalker_mcp/mcp/stdio_servers/providers_stdio.py`
- `/dreamwalker_mcp/mcp/stdio_servers/utility_stdio.py`
- `/dreamwalker_mcp/mcp/stdio_servers/web_search_stdio.py`

## Phase 2: MCP Server Structure

### 2.1 Proper MCP Server Template
```python
import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("server-name")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="tool_name",
            description="Tool description",
            inputSchema={
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Tool implementation
    return [types.TextContent(type="text", text="Result")]

async def run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="server-name",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(run())
```

### 2.2 Server Configuration Structure
```
dreamwalker-mcp/
├── pyproject.toml                    # Python package configuration
├── README.md                         # Documentation
├── .mcp.json                        # MCP server definitions
├── .claude-plugin/
│   └── plugin.json                  # Plugin metadata
├── dreamwalker_mcp/
│   ├── __init__.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── servers/                 # MCP server implementations
│   │   │   ├── __init__.py
│   │   │   ├── unified.py          # Unified orchestrator server
│   │   │   ├── cache.py            # Cache server
│   │   │   ├── data.py             # Data server
│   │   │   ├── providers.py        # LLM providers server
│   │   │   ├── utility.py          # Utility server
│   │   │   └── web_search.py       # Web search server
│   │   └── tools/                   # Shared tool implementations
│   └── orchestration/               # Orchestrator implementations
└── tests/                           # Test suite
```

## Phase 3: Plugin Packaging

### 3.1 Create .mcp.json
```json
{
  "mcpServers": {
    "dreamwalker-unified": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/coolhand/dreamwalker-mcp",
        "run",
        "dreamwalker-unified"
      ],
      "env": {
        "PYTHONPATH": "/home/coolhand/shared:$PYTHONPATH"
      }
    },
    "dreamwalker-cache": {
      "command": "uv",
      "args": ["--directory", "/home/coolhand/dreamwalker-mcp", "run", "dreamwalker-cache"]
    },
    "dreamwalker-data": {
      "command": "uv",
      "args": ["--directory", "/home/coolhand/dreamwalker-mcp", "run", "dreamwalker-data"]
    },
    "dreamwalker-providers": {
      "command": "uv",
      "args": ["--directory", "/home/coolhand/dreamwalker-mcp", "run", "dreamwalker-providers"]
    },
    "dreamwalker-utility": {
      "command": "uv",
      "args": ["--directory", "/home/coolhand/dreamwalker-mcp", "run", "dreamwalker-utility"]
    },
    "dreamwalker-websearch": {
      "command": "uv",
      "args": ["--directory", "/home/coolhand/dreamwalker-mcp", "run", "dreamwalker-websearch"]
    }
  }
}
```

### 3.2 Create .claude-plugin/plugin.json
```json
{
  "name": "dreamwalker-orchestrator",
  "version": "1.0.0",
  "description": "Advanced multi-agent orchestration system with Dream Cascade and Dream Swarm patterns",
  "author": {
    "name": "Luke Steuber",
    "email": "luke@example.com"
  },
  "keywords": [
    "orchestration",
    "multi-agent",
    "research",
    "synthesis",
    "llm",
    "mcp"
  ],
  "homepage": "https://github.com/lukesteuber/dreamwalker-mcp",
  "license": "MIT"
}
```

### 3.3 Create pyproject.toml
```toml
[project]
name = "dreamwalker-mcp"
version = "1.0.0"
description = "Advanced multi-agent orchestration MCP servers"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=0.1.0",
    "flask>=3.0.0",
    "aiohttp>=3.9.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
]

[project.scripts]
dreamwalker-unified = "dreamwalker_mcp.mcp.servers.unified:main"
dreamwalker-cache = "dreamwalker_mcp.mcp.servers.cache:main"
dreamwalker-data = "dreamwalker_mcp.mcp.servers.data:main"
dreamwalker-providers = "dreamwalker_mcp.mcp.servers.providers:main"
dreamwalker-utility = "dreamwalker_mcp.mcp.servers.utility:main"
dreamwalker-websearch = "dreamwalker_mcp.mcp.servers.web_search:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Phase 4: Testing & Validation

### 4.1 Local Testing
1. **Test MCP protocol compliance**:
   ```bash
   echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "0.1.0", "capabilities": {}}, "id": 1}' | python -m dreamwalker_mcp.mcp.servers.unified
   ```

2. **Test with Claude CLI**:
   ```bash
   claude --debug
   ```

3. **Validate plugin structure**:
   ```bash
   # Use Puerto marketplace validation
   node /home/coolhand/.claude/plugins/marketplaces/puerto/scripts/validate-plugin.js /home/coolhand/dreamwalker-mcp
   ```

### 4.2 Integration Testing
1. Test each MCP server individually
2. Test orchestration workflows
3. Test with different LLM providers
4. Verify anti-hallucination measures

## Phase 5: Documentation

### 5.1 README.md Updates
- Installation instructions
- Configuration guide
- API key setup
- Usage examples
- Troubleshooting

### 5.2 API Documentation
- Tool descriptions
- Parameter schemas
- Response formats
- Error handling

### 5.3 Architecture Documentation
- System overview
- Orchestration patterns
- Provider integration
- Performance considerations

## Phase 6: Distribution

### 6.1 Package for PyPI
```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### 6.2 Submit to Claude Plugin Marketplace
1. **Prepare submission**:
   - Clean code
   - Complete documentation
   - Test coverage
   - Security review

2. **Create marketplace entry**:
   - Plugin metadata
   - Screenshots/demos
   - Usage examples
   - Support information

3. **Follow marketplace guidelines**:
   - Code quality standards
   - Security requirements
   - Documentation standards
   - Update procedures

## Phase 7: Deployment & Monitoring

### 7.1 Cloud Deployment Options
1. **Hosted MCP servers**:
   - Deploy to cloud platform
   - Use HTTPS transport
   - Implement authentication

2. **Hybrid approach**:
   - Local stdio for sensitive operations
   - Cloud for public APIs

### 7.2 Monitoring & Analytics
1. **Usage tracking**:
   - Tool invocation counts
   - Error rates
   - Performance metrics

2. **User feedback**:
   - Issue tracking
   - Feature requests
   - Community support

## Implementation Timeline

### Week 1 (URGENT)
- [ ] Fix MCP protocol implementation
- [ ] Convert to official MCP SDK
- [ ] Test basic functionality

### Week 2
- [ ] Complete plugin structure
- [ ] Add comprehensive tests
- [ ] Update documentation

### Week 3
- [ ] Package for distribution
- [ ] Submit to marketplace
- [ ] Deploy cloud options

### Week 4
- [ ] Monitor deployment
- [ ] Gather feedback
- [ ] Plan updates

## Success Criteria

1. ✅ All MCP servers start without errors
2. ✅ Tools are accessible in Claude Code
3. ✅ Orchestration workflows complete successfully
4. ✅ Plugin passes marketplace validation
5. ✅ Documentation is comprehensive
6. ✅ Users can install and use the plugin

## Resources

### Official Documentation
- [MCP Specification](https://modelcontextprotocol.io/docs)
- [Claude Code Plugin Guide](https://docs.anthropic.com/claude-code/plugins)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### Examples
- [Chrome DevTools MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [Filesystem MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Puerto Marketplace](file:///home/coolhand/.claude/plugins/marketplaces/puerto)

### Tools
- Puerto validation scripts
- MCP debugging tools
- Claude CLI with --debug flag

## Next Steps

1. **Immediate action**: Fix the initialize method error in all stdio servers
2. **Priority**: Get at least one MCP server working end-to-end
3. **Focus**: Start with unified orchestrator as the main server
4. **Iterate**: Add other servers once the pattern is established

---

This plan provides a clear roadmap from the current broken state to a fully functional, marketplace-ready MCP plugin system. The immediate priority is fixing the protocol implementation to get the servers working with Claude Code.