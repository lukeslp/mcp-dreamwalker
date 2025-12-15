#!/bin/bash
# Test script to diagnose MCP autocomplete issues

echo "=== MCP Tools Autocomplete Diagnostic ==="
echo ""

# 1. Check environment variables
echo "1. Checking API Keys:"
echo "-------------------"
[ -n "$ANTHROPIC_API_KEY" ] && echo "✅ ANTHROPIC_API_KEY is set" || echo "❌ ANTHROPIC_API_KEY is NOT set"
[ -n "$XAI_API_KEY" ] && echo "✅ XAI_API_KEY is set" || echo "❌ XAI_API_KEY is NOT set"
[ -n "$OPENAI_API_KEY" ] && echo "✅ OPENAI_API_KEY is set" || echo "❌ OPENAI_API_KEY is NOT set"
echo ""

# 2. Check Claude config
echo "2. Checking Claude Config:"
echo "-------------------------"
if [ -f ~/.config/Claude/claude_desktop_config.json ]; then
    echo "✅ Claude config exists"
    echo "Configured MCP servers:"
    jq -r '.mcpServers | keys[]' ~/.config/Claude/claude_desktop_config.json 2>/dev/null | while read server; do
        echo "   - $server"
    done
else
    echo "❌ Claude config NOT found at ~/.config/Claude/claude_desktop_config.json"
fi
echo ""

# 3. Check if dreamwalker-mcp is installed
echo "3. Checking Dreamwalker MCP Installation:"
echo "----------------------------------------"
if python3 -c "import dreamwalker_mcp" 2>/dev/null; then
    echo "✅ dreamwalker_mcp module is installed"
    location=$(python3 -c "import dreamwalker_mcp; print(dreamwalker_mcp.__file__)")
    echo "   Location: $location"
else
    echo "❌ dreamwalker_mcp module NOT installed"
fi
echo ""

# 4. Test MCP servers and show exact tool names
echo "4. Testing MCP Servers and Tool Names:"
echo "-------------------------------------"

test_server() {
    local server=$1
    local module=$2
    
    echo -n "Testing $server... "
    
    # Send initialize and tools/list requests
    response=$(echo -e '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | \
        python3 -m dreamwalker_mcp.mcp.stdio_servers.$module 2>/dev/null | \
        grep '"id":2' | \
        jq -r '.result.tools[]?.name' 2>/dev/null)
    
    if [ -n "$response" ]; then
        tool_count=$(echo "$response" | wc -l)
        echo "✅ OK ($tool_count tools)"
        echo "$response" | head -5 | while read tool; do
            echo "   → mcp__${server}__${tool}"
        done
        if [ $tool_count -gt 5 ]; then
            echo "   ... and $((tool_count - 5)) more"
        fi
    else
        echo "❌ FAILED"
    fi
    echo ""
}

test_server "dreamwalker-unified" "unified_stdio"
test_server "dreamwalker-providers" "providers_stdio"
test_server "dreamwalker-data" "data_stdio"
test_server "dreamwalker-utility" "utility_stdio"

# 5. Check Claude processes
echo "5. Claude Process Status:"
echo "------------------------"
if pgrep -f claude > /dev/null; then
    echo "⚠️  Claude is currently running"
    echo "   You need to fully quit and restart Claude for MCP changes to take effect"
    echo "   Run: pkill -f claude"
else
    echo "✅ Claude is not running (good - you can start it fresh)"
fi
echo ""

# 6. Summary and recommendations
echo "6. Summary and Next Steps:"
echo "-------------------------"
echo "To make MCP tools appear in @ autocomplete:"
echo ""
echo "1. Set required environment variables in ~/.bashrc:"
echo "   export ANTHROPIC_API_KEY='your-key'"
echo "   export XAI_API_KEY='your-key'"
echo "   source ~/.bashrc"
echo ""
echo "2. Fully restart Claude Code:"
echo "   pkill -f claude"
echo "   # Then start Claude Code again"
echo ""
echo "3. In Claude Code, type @ and look for entries like:"
echo "   @mcp__dreamwalker-unified__dreamwalker_orchestrate_cascade"
echo ""
echo "4. If still not working, check Claude logs:"
echo "   grep -i mcp ~/.config/Claude/logs/*.log"