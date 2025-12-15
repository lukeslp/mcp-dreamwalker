#!/bin/bash

echo "🔍 Dreamwalker MCP Diagnostic"
echo "============================="

# Check environment
echo -e "\n1️⃣ Environment Variables:"
echo -n "Current shell has XAI_API_KEY: "
[ -n "$XAI_API_KEY" ] && echo "✅ SET" || echo "❌ NOT SET"

echo -n "Loading from ~/.env: "
set -a; source ~/.env 2>/dev/null; set +a
[ -n "$XAI_API_KEY" ] && echo "✅ Works" || echo "❌ Failed"

# Check Claude processes
echo -e "\n2️⃣ Claude Code Status:"
claude_pids=$(pgrep -f "claude" | grep -v grep)
if [ -n "$claude_pids" ]; then
    echo "✅ Claude is running (PIDs: $(echo $claude_pids | tr '\n' ' '))"
    
    # Check if Claude has environment
    for pid in $claude_pids; do
        if [ -r "/proc/$pid/environ" ]; then
            echo -n "   PID $pid has XAI_API_KEY: "
            grep -q "XAI_API_KEY" /proc/$pid/environ 2>/dev/null && echo "✅ YES" || echo "❌ NO"
        fi
    done
else
    echo "❌ Claude is not running"
fi

# Check MCP processes
echo -e "\n3️⃣ MCP Servers Running:"
dreamwalker_mcps=$(ps aux | grep -E "dreamwalker.*stdio" | grep -v grep)
if [ -n "$dreamwalker_mcps" ]; then
    echo "✅ Found dreamwalker MCP processes:"
    echo "$dreamwalker_mcps"
else
    echo "❌ No dreamwalker MCP servers running"
fi

# Test MCP servers directly
echo -e "\n4️⃣ Testing MCP Servers Directly:"
set -a; source ~/.env 2>/dev/null; set +a
for server in unified providers data utility web_search; do
    echo -n "   dreamwalker-$server: "
    if timeout 2s echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
       python3 -m dreamwalker_mcp.mcp.stdio_servers.${server}_stdio 2>/dev/null | \
       grep -q "result"; then
        echo "✅ OK"
    else
        echo "❌ Failed"
    fi
done

# Check logs
echo -e "\n5️⃣ Claude Logs (last MCP errors):"
log_dir="$HOME/.config/Claude/logs"
if [ -d "$log_dir" ]; then
    latest_log=$(ls -t "$log_dir"/*.log 2>/dev/null | head -1)
    if [ -f "$latest_log" ]; then
        echo "   Checking: $latest_log"
        grep -i "dreamwalker\|mcp.*error" "$latest_log" | tail -5
    else
        echo "   No log files found"
    fi
else
    echo "   Log directory not found at $log_dir"
fi

echo -e "\n📋 Summary:"
echo "If Claude was started without environment variables, you need to:"
echo "1. Kill all Claude: pkill -f claude"
echo "2. Load environment: set -a; source ~/.env; set +a"
echo "3. Start Claude from that shell: claude"
echo ""
echo "Or use the launcher: ~/bin/claude-with-env"