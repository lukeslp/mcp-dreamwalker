# Claude Code MCP Connection Troubleshooting

## Current Status
- ✅ MCP servers configured in `~/.config/Claude/claude_desktop_config.json`
- ❌ API keys not set in environment
- ❌ MCP tools not appearing in Claude Code

## Steps to Fix

### 1. Set Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Essential API keys for dreamwalker
export ANTHROPIC_API_KEY="sk-ant-..."
export XAI_API_KEY="xai-..."
export OPENAI_API_KEY="sk-..."

# Optional data source keys
export GITHUB_TOKEN="ghp_..."
export NEWS_API_KEY="..."
export OPENWEATHER_API_KEY="..."

# Redis configuration (if using cache server)
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

Then reload:
```bash
source ~/.bashrc
```

### 2. Test MCP Servers Manually

Before restarting Claude Code, verify the servers work:

```bash
# Test unified server
echo $ANTHROPIC_API_KEY  # Should show your key
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 -m dreamwalker_mcp.mcp.stdio_servers.unified_stdio

# If you get module errors, ensure dreamwalker-mcp is installed:
cd /home/coolhand/dreamwalker-mcp
pip install -e .
```

### 3. Restart Claude Code Completely

**IMPORTANT**: You must fully quit and restart Claude Code for MCP changes to take effect.

1. **Quit all Claude Code instances**:
   ```bash
   # Check running instances
   ps aux | grep claude
   
   # Kill all Claude processes (save your work first!)
   pkill -f claude
   ```

2. **Clear any cache** (optional):
   ```bash
   rm -rf ~/.cache/claude-code/
   ```

3. **Start Claude Code fresh**

### 4. Verify MCP Tools Are Available

After restart, in Claude Code you should see tools like:
- `@mcp__dreamwalker-unified__dreamwalker.orchestrate.cascade`
- `@mcp__dreamwalker-unified__dreamwalker.utility.status`

Try typing `@mcp__dreamwalker` to see if autocomplete shows the tools.

### 5. Debug MCP Connection

If tools still don't appear, check Claude Code logs:

```bash
# Find Claude Code log location (usually in ~/.config/Claude/logs/)
ls -la ~/.config/Claude/logs/

# Check for MCP errors
grep -i "mcp\|dreamwalker" ~/.config/Claude/logs/*.log
```

### Common Issues

1. **"Module not found" errors**:
   - Ensure `dreamwalker-mcp` is installed: `pip show dreamwalker-mcp`
   - Check Python path: `python3 -c "import dreamwalker_mcp; print(dreamwalker_mcp.__file__)"`

2. **"Permission denied" errors**:
   - Check file permissions: `ls -la ~/.config/Claude/claude_desktop_config.json`
   - Should be readable by your user

3. **API key errors**:
   - MCP servers need at least one LLM provider key
   - Set `ANTHROPIC_API_KEY` or `XAI_API_KEY` at minimum

4. **Redis connection errors**:
   - The cache server requires Redis running
   - Either start Redis: `sudo systemctl start redis-server`
   - Or remove the dreamwalker-cache server from config

### Quick Test Script

Save this as `test_mcp.sh`:

```bash
#!/bin/bash
echo "Testing dreamwalker MCP servers..."

# Check environment
echo -e "\n1. Checking API keys:"
[ -n "$ANTHROPIC_API_KEY" ] && echo "✅ ANTHROPIC_API_KEY set" || echo "❌ ANTHROPIC_API_KEY missing"
[ -n "$XAI_API_KEY" ] && echo "✅ XAI_API_KEY set" || echo "❌ XAI_API_KEY missing"

# Test servers
echo -e "\n2. Testing MCP servers:"
for server in unified providers data utility web_search; do
  echo -n "Testing $server... "
  if echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
     python3 -m dreamwalker_mcp.mcp.stdio_servers.${server}_stdio 2>/dev/null | \
     jq -e '.result.tools' >/dev/null; then
    echo "✅ OK"
  else
    echo "❌ FAILED"
  fi
done

echo -e "\n3. Claude Code status:"
pgrep -f claude >/dev/null && echo "✅ Claude Code is running" || echo "❌ Claude Code not running"
```

Make it executable: `chmod +x test_mcp.sh`
Run it: `./test_mcp.sh`