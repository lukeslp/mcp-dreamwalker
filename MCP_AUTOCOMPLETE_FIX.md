# MCP Tools @ Autocomplete Fix Guide

## Problem
MCP tools are not appearing in @ predictions/autocomplete in Claude and Codex, even though they are properly registered and working when invoked manually.

## Root Causes

1. **Tool Naming Convention**: MCP tools must follow strict naming rules - only alphanumeric characters, underscores, and hyphens are allowed. The tools have been updated from dot notation (e.g., `dreamwalker.orchestrate.cascade`) to underscore notation (e.g., `dreamwalker_orchestrate_cascade`).

2. **MCP Tool Prefix in Claude Code**: In Claude Code, MCP tools appear with the prefix pattern `mcp__<server-name>__<tool-name>`. This is different from the simple `@toolname` pattern.

3. **Claude Desktop Restart Required**: Claude Desktop/Code must be fully restarted (not just closed) after MCP configuration changes for tools to appear in autocomplete.

4. **Environment Variables**: API keys must be properly exported in your shell environment before starting Claude.

## Solution Steps

### 1. Verify Environment Variables
```bash
# Check if API keys are set
echo $ANTHROPIC_API_KEY
echo $XAI_API_KEY
echo $OPENAI_API_KEY

# If not set, add to ~/.bashrc or ~/.zshrc:
export ANTHROPIC_API_KEY="your-key"
export XAI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Reload shell
source ~/.bashrc
```

### 2. Test MCP Servers
```bash
# Test each server to ensure they're working
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 -m dreamwalker_mcp.mcp.stdio_servers.unified_stdio | jq .

# Should return a list of tools with valid names like:
# - dreamwalker_orchestrate_cascade
# - dreamwalker_orchestrate_swarm
# - dreamwalker_utility_status
```

### 3. Fully Restart Claude Desktop/Code
```bash
# Kill all Claude processes
pkill -f claude

# Clear any cache (optional)
rm -rf ~/.cache/claude-code/

# Start Claude fresh
```

### 4. Using Tools in Claude Code

After restart, tools should appear with the full MCP prefix pattern:

**Correct Tool Names in Claude Code:**
- `@mcp__dreamwalker-unified__dreamwalker_orchestrate_cascade`
- `@mcp__dreamwalker-unified__dreamwalker_orchestrate_swarm`
- `@mcp__dreamwalker-unified__dreamwalker_utility_status`
- `@mcp__dreamwalker-providers__chat_completion`
- `@mcp__dreamwalker-data__dream_of_arxiv`

**Autocomplete Tips:**
1. Start typing `@mcp__` to see all MCP servers
2. Then type the server name: `@mcp__dreamwalker-unified__`
3. The autocomplete should show available tools for that server

### 5. Using Tools in Standard Claude Desktop

In the standard Claude Desktop app (not Code), tools may appear differently or may not support @ mentions at all. The MCP integration is primarily designed for Claude Code.

## Troubleshooting

### Tools Still Not Appearing in Autocomplete

1. **Check Claude Logs**:
```bash
# Find log files
ls -la ~/.config/Claude/logs/

# Look for MCP errors
grep -i "mcp\|dreamwalker" ~/.config/Claude/logs/*.log
```

2. **Verify Server Registration**:
```bash
# Check config file
cat ~/.config/Claude/claude_desktop_config.json | jq .mcpServers
```

3. **Test Individual Servers**:
```bash
# Create test script
cat > test_mcp_tools.py << 'EOF'
import json
import subprocess
import sys

servers = [
    "unified_stdio",
    "providers_stdio", 
    "data_stdio",
    "utility_stdio",
    "web_search_stdio",
    "cache_stdio"
]

for server in servers:
    print(f"\nTesting {server}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", f"dreamwalker_mcp.mcp.stdio_servers.{server}"],
            input='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n',
            capture_output=True,
            text=True
        )
        if result.stdout:
            data = json.loads(result.stdout.strip())
            if "result" in data and "tools" in data["result"]:
                print(f"✅ Found {len(data['result']['tools'])} tools")
                for tool in data['result']['tools'][:3]:
                    print(f"   - {tool['name']}")
            else:
                print(f"❌ No tools found")
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Failed: {e}")
EOF

python3 test_mcp_tools.py
```

### Alternative: Direct Tool Invocation

If autocomplete isn't working, you can still use tools by typing the full name:
1. Type `/mcp` to see available MCP commands
2. Use the full tool name without autocomplete

## Expected Behavior

After following these steps, when you type `@` in Claude Code, you should see:
1. A dropdown menu with various options
2. MCP servers listed with the `mcp__` prefix
3. Typing `@mcp__dreamwalker` should show all dreamwalker servers
4. Selecting a server should show its available tools

## Note on Tool Names

The current valid tool names use underscores, not dots:
- ✅ `dreamwalker_orchestrate_cascade`
- ❌ `dreamwalker.orchestrate.cascade`

This change was made to comply with MCP protocol requirements.