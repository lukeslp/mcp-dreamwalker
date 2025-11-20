# Cursor/Codex Remote MCP Connection Setup

**Date**: November 18, 2025  
**Status**: Configuration Guide

---

## Problem

You're SSH'd into your server where Dreamwalker MCP is running on port 5060, but Cursor/Codex can't pick it up because:
1. MCP server is running remotely (on dr.eamer.dev)
2. Cursor expects local stdio MCP servers by default
3. Need to bridge remote HTTP MCP to local stdio interface

---

## Solution Options

### Option 1: MCP Stdio Bridge (Recommended)

Create a local bridge script that connects Cursor's stdio interface to your remote HTTP MCP server.

**File**: `/home/coolhand/shared/mcp/mcp_http_bridge.py`

```python
#!/usr/bin/env python3
"""
MCP HTTP-to-Stdio Bridge

Bridges Cursor/Codex stdio MCP interface to remote HTTP MCP server.
Allows Cursor to use remote Dreamwalker MCP server as if it were local.

Usage:
    python mcp_http_bridge.py [--url https://dr.eamer.dev/mcp]
"""

import sys
import json
import requests
import argparse
from typing import Dict, Any

# MCP server URL
DEFAULT_MCP_URL = "https://dr.eamer.dev/mcp"


class MCPHttpBridge:
    """Bridge between MCP stdio and HTTP protocols."""
    
    def __init__(self, mcp_url: str):
        self.mcp_url = mcp_url.rstrip('/')
        self.session = requests.Session()
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from remote MCP server."""
        response = self.session.get(f"{self.mcp_url}/tools")
        response.raise_for_status()
        return response.json()
    
    def list_resources(self) -> Dict[str, Any]:
        """List available resources from remote MCP server."""
        response = self.session.get(f"{self.mcp_url}/resources")
        response.raise_for_status()
        return response.json()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the remote MCP server."""
        response = self.session.post(
            f"{self.mcp_url}/tools/{tool_name}",
            json=arguments,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP stdio request and route to HTTP endpoint."""
        method = request.get('method')
        
        if method == 'tools/list':
            tools_data = self.list_tools()
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "tools": tools_data.get('tools', [])
                }
            }
        
        elif method == 'resources/list':
            resources_data = self.list_resources()
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "resources": resources_data.get('resources', [])
                }
            }
        
        elif method == 'tools/call':
            params = request.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            result = self.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def run(self):
        """Run the stdio bridge - read from stdin, write to stdout."""
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                
                # Handle request
                response = self.handle_request(request)
                
                # Write response to stdout
                sys.stdout.write(json.dumps(response) + '\n')
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON decode error: {e}\n")
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")
                sys.stderr.flush()


def main():
    parser = argparse.ArgumentParser(description='MCP HTTP-to-stdio bridge')
    parser.add_argument(
        '--url',
        default=DEFAULT_MCP_URL,
        help=f'MCP server URL (default: {DEFAULT_MCP_URL})'
    )
    args = parser.parse_args()
    
    bridge = MCPHttpBridge(args.url)
    bridge.run()


if __name__ == '__main__':
    main()
```

**Then configure in Cursor settings**:

```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python",
      "args": ["/home/coolhand/shared/mcp/mcp_http_bridge.py"],
      "env": {}
    }
  }
}
```

### Option 2: SSH Tunnel + Local MCP Server

Forward the remote port to your local machine, then configure Cursor to use it.

**Step 1: Create SSH tunnel**
```bash
# On your local machine
ssh -L 5060:localhost:5060 coolhand@dr.eamer.dev -N
```

**Step 2: Configure Cursor to use local forwarded port**
```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python",
      "args": ["/path/to/local/mcp_http_bridge.py", "--url", "http://localhost:5060"]
    }
  }
}
```

### Option 3: Direct HTTP MCP (If Supported)

Some MCP clients support direct HTTP connections (this is experimental).

**Cursor Settings** (if supported):
```json
{
  "mcpServers": {
    "dreamwalker": {
      "type": "http",
      "url": "https://dr.eamer.dev/mcp",
      "headers": {}
    }
  }
}
```

---

## Recommended Approach

**Use Option 1** (MCP HTTP Bridge) because:
- ✅ Works with standard Cursor MCP expectations (stdio)
- ✅ No need to keep SSH tunnel open
- ✅ Clean integration
- ✅ Can run locally on your machine

---

## Step-by-Step Setup

### 1. Create the Bridge Script

Copy the bridge script above and save it:

```bash
cat > /home/coolhand/shared/mcp/mcp_http_bridge.py << 'EOF'
[paste the bridge script here]
EOF

chmod +x /home/coolhand/shared/mcp/mcp_http_bridge.py
```

### 2. Test the Bridge Locally

```bash
cd /home/coolhand/shared/mcp

# Test it reads from remote
python mcp_http_bridge.py --url https://dr.eamer.dev/mcp &
BRIDGE_PID=$!

# Send MCP request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp_http_bridge.py --url https://dr.eamer.dev/mcp

# Should return list of 26 tools
```

### 3. Configure Cursor

Find your Cursor config location:

**Linux**: `~/.config/cursor/mcp.json` or `~/.config/Cursor/User/globalStorage/mcp.json`  
**macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`  
**Windows**: `%APPDATA%\Cursor\User\globalStorage\mcp.json`

Create/edit the MCP configuration:

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
      "env": {}
    }
  }
}
```

### 4. Restart Cursor

Close and reopen Cursor. It should now detect the Dreamwalker MCP server.

### 5. Verify in Cursor

In Cursor, you should see:
- MCP server "dreamwalker" connected
- 26 tools available
- Can call tools like `search_arxiv`, `cache_set`, `orchestrate_research`

---

## Alternative: Local Development Setup

If you want to run the MCP server locally (not on the remote server):

```bash
# On your local machine
cd ~
git clone your-repo
cd shared/mcp

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export XAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key

# Run locally
python app.py

# Configure Cursor to use local server
# ... use http://localhost:5060 instead
```

---

## Troubleshooting

### Cursor Can't Find MCP Server

**Check**:
1. Bridge script is executable: `chmod +x mcp_http_bridge.py`
2. Python is in PATH: `which python3`
3. Cursor config path is correct
4. Restart Cursor after config changes

**Debug**:
```bash
# Test bridge manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 mcp_http_bridge.py --url https://dr.eamer.dev/mcp
```

### Connection Errors

**Check**:
1. MCP server is running: `curl https://dr.eamer.dev/mcp/health`
2. Firewall allows HTTPS
3. URL is correct in bridge script

### Tools Not Showing Up

**Check**:
1. MCP server has tools: `curl https://dr.eamer.dev/mcp/tools`
2. Bridge is forwarding requests correctly
3. Cursor logs for MCP errors

---

## What's Next?

Once MCP connection is working in Cursor:

### Immediate Usage

1. **Search arXiv from Cursor**:
   - Use tool: `search_arxiv`
   - Arguments: `{"query": "transformers", "max_results": 5}`

2. **Cache data**:
   - Use tool: `cache_set`
   - Arguments: `{"key": "config", "value": {...}, "ttl": 3600}`

3. **Orchestrate research**:
   - Use tool: `orchestrate_research`
   - Arguments: `{"task": "Research topic", "num_agents": 9}`

### Phase 2: Service Migrations

Once MCP is working, proceed with Phase 2:
- Migrate studio to shared orchestrators
- Migrate swarm to shared orchestrators
- Refactor planner orchestrator

See `MIGRATION_ROADMAP.md` for details.

---

## Quick Test

```bash
# In Cursor, try this command:
# "Use the search_arxiv tool to find 3 papers about large language models"

# Should call:
POST https://dr.eamer.dev/mcp/tools/search_arxiv
{
  "query": "large language models",
  "max_results": 3
}

# And return paper results
```

---

**Status**: Ready for Cursor/Codex integration  
**Next**: Create bridge script and configure Cursor  
**Documentation**: This guide

