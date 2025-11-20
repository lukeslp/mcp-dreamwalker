# Cursor/Codex Setup for Dreamwalker MCP

**Quick Setup**: 3 steps to connect Cursor to your remote Dreamwalker MCP server

---

## The Problem

Your Dreamwalker MCP server is running on `dr.eamer.dev` (remote), but Cursor expects local MCP servers via stdio. The bridge script (`mcp_http_bridge.py`) solves this by translating between protocols.

✅ **Bridge tested and working** - returns all 26 tools from remote server

---

## Quick Setup (3 Steps)

### Step 1: Copy the Cursor MCP Configuration

The configuration file is ready at:
```
/home/coolhand/shared/mcp/cursor_mcp_config.json
```

**Content**:
```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/coolhand/shared/mcp/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ],
      "env": {},
      "description": "Dreamwalker - 26 tools for orchestration, data, cache, utilities"
    }
  }
}
```

### Step 2: Add to Cursor Settings

**Find your Cursor config location**:

- **Linux**: `~/.config/Cursor/User/settings.json` or create `~/.config/Cursor/mcp.json`
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
- **Windows**: `%APPDATA%\Cursor\User\settings.json`

**Add the mcpServers section** to your Cursor settings.json:

```json
{
  // ... your existing settings ...
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/coolhand/shared/mcp/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ]
    }
  }
}
```

**OR** if Cursor supports separate MCP config file, create `~/.config/Cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/coolhand/shared/mcp/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ]
    }
  }
}
```

### Step 2.5: Verify Connectivity (optional but recommended)

Before restarting Cursor, confirm the bridge can reach the remote Dreamwalker server:

```bash
python /home/coolhand/shared/mcp/mcp_http_bridge.py --check
```

This prints a summary (should show ~26 tools and 9 resources). If it fails, double-check network access to `https://dr.eamer.dev/mcp`.

### Step 3: Restart Cursor

1. Close Cursor completely
2. Reopen Cursor
3. Check MCP status (usually shows in status bar or settings)

---

## Verification

### In Cursor

Once configured, you should see:
- ✅ MCP server "dreamwalker" connected
- ✅ 26 tools available
- ✅ Status indicator showing "Connected"

### Test It

Try asking Cursor:
```
"Use the search_arxiv tool to find 3 papers about large language models"
```

Cursor should call the `search_arxiv` tool and return results!

### Manual Test

```bash
# From terminal, test the bridge
cd /home/coolhand/shared/mcp

echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 mcp_http_bridge.py --url https://dr.eamer.dev/mcp
  
# Should return JSON with 26 tools
```

---

## Available Tools in Cursor

Once connected, you can use these in natural language:

**Orchestration**:
- "Orchestrate a research task about [topic]" → `orchestrate_research`
- "Search for information about [query]" → `orchestrate_search`
- "Check status of task [task_id]" → `get_orchestration_status`

**Data Fetching**:
- "Search arXiv for papers about [topic]" → `search_arxiv`
- "Find research papers about [query]" → `search_semantic_scholar`
- "Get Census data for [variables]" → `fetch_census_acs`
- "Find archived version of [url]" → `wayback_search`

**Caching**:
- "Cache this data as [key]" → `cache_set`
- "Get cached value for [key]" → `cache_get`
- "Delete cache key [key]" → `cache_delete`

**Utilities**:
- "Parse this document [path]" → `parse_document`
- "Do multi-provider research on [topic]" → `multi_provider_search`
- "Format this citation as BibTeX" → `format_citation_bibtex`

---

## Troubleshooting

### Cursor Shows "MCP Server Failed to Start"

**Check**:
1. Python3 is in PATH: `which python3`
2. Bridge script is executable: `ls -l /home/coolhand/shared/mcp/mcp_http_bridge.py`
3. Remote server is running: `curl https://dr.eamer.dev/mcp/health`

**Fix**:
```bash
# Make sure script is executable
chmod +x /home/coolhand/shared/mcp/mcp_http_bridge.py

# Test bridge manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  python3 /home/coolhand/shared/mcp/mcp_http_bridge.py
```

### Cursor Shows "No Tools Available"

**Check**:
1. Bridge is running: Look for logs in Cursor MCP output
2. Remote server has tools: `curl https://dr.eamer.dev/mcp/tools | jq '.count'`

### Tool Calls Fail

**Check**:
1. Remote server is healthy: `curl https://dr.eamer.dev/mcp/health`
2. Specific tool works: `curl -X POST https://dr.eamer.dev/mcp/tools/search_arxiv -d '{"query":"test","max_results":1}'`

---

## Alternative: SSH Tunnel Method

If the bridge doesn't work, use SSH port forwarding:

**On your local machine**:
```bash
# Forward remote port 5060 to local
ssh -L 5060:localhost:5060 coolhand@dr.eamer.dev -N &
```

**Then configure Cursor**:
```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/coolhand/shared/mcp/mcp_http_bridge.py",
        "--url",
        "http://localhost:5060"
      ]
    }
  }
}
```

---

## What You Get

Once connected, Cursor can:

✅ **Search arXiv** for academic papers  
✅ **Orchestrate multi-agent research** with Beltalowda/Swarm  
✅ **Fetch Census data** programmatically  
✅ **Parse documents** (PDF, DOCX, etc.)  
✅ **Cache data** in Redis  
✅ **Multi-provider search** across sources  
✅ **Format citations** as BibTeX  

All without you writing API client code!

---

## Next Steps After Connection

### 1. Test Basic Tool
```
In Cursor: "Search arXiv for 3 papers about transformers"
```

### 2. Try Orchestration
```
In Cursor: "Use orchestrate_research to analyze quantum computing applications"
```

### 3. Use Caching
```
In Cursor: "Cache this data with key 'config' for 1 hour"
```

---

## Configuration Files

**Bridge Script**: `/home/coolhand/shared/mcp/mcp_http_bridge.py` ✅ Created  
**Example Config**: `/home/coolhand/shared/mcp/cursor_mcp_config.json` ✅ Created  
**Setup Guide**: This file

---

## Support

**Bridge not working?**
- Check logs in Cursor MCP panel
- Test manually: `python3 mcp_http_bridge.py --verbose`
- Verify remote server: `curl https://dr.eamer.dev/mcp/tools`

**Tools not showing?**
- Restart Cursor
- Check MCP configuration syntax
- Verify Python3 path

---

**Status**: Bridge script ready and tested ✅  
**Next**: Add config to Cursor and test connection

