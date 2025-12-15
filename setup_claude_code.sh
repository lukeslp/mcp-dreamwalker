#!/bin/bash
# Quick setup script for dreamwalker MCP in Claude Code

echo "🚀 Dreamwalker MCP Setup for Claude Code"
echo "========================================"

# Check if API keys are set
echo -e "\n📋 Checking API keys..."
missing_keys=false

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    missing_keys=true
else
    echo "✅ ANTHROPIC_API_KEY is set"
fi

if [ -z "$XAI_API_KEY" ]; then
    echo "⚠️  XAI_API_KEY not set (optional but recommended)"
fi

if [ "$missing_keys" = true ]; then
    echo -e "\n⚠️  Missing required API keys!"
    echo "Add to your ~/.bashrc:"
    echo 'export ANTHROPIC_API_KEY="your-key-here"'
    echo 'export XAI_API_KEY="your-key-here"'
    echo ""
    echo "Then run: source ~/.bashrc"
    exit 1
fi

# Test MCP servers
echo -e "\n🧪 Testing MCP servers..."
servers=(unified providers data utility web_search cache)
failed=false

for server in "${servers[@]}"; do
    printf "  Testing dreamwalker-$server... "
    if timeout 5s echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
       python3 -m dreamwalker_mcp.mcp.stdio_servers.${server}_stdio 2>/dev/null | \
       grep -q "result"; then
        echo "✅"
    else
        echo "❌"
        failed=true
    fi
done

# Check Claude Code
echo -e "\n🔍 Checking Claude Code..."
if pgrep -f "claude" > /dev/null; then
    echo "⚠️  Claude Code is running. You need to:"
    echo "   1. Save all your work"
    echo "   2. Fully quit Claude Code (Cmd/Ctrl+Q)"
    echo "   3. Start Claude Code again"
    echo ""
    echo "MCP servers are only loaded at startup!"
else
    echo "✅ Claude Code is not running. Good to start fresh!"
fi

# Summary
echo -e "\n📊 Summary"
echo "========="
if [ "$failed" = false ]; then
    echo "✅ All MCP servers are working correctly!"
    echo ""
    echo "Next steps:"
    echo "1. Start Claude Code"
    echo "2. Try typing: @mcp__dreamwalker"
    echo "3. You should see tools like:"
    echo "   - @mcp__dreamwalker-unified__dreamwalker.orchestrate.cascade"
    echo "   - @mcp__dreamwalker-data__dreamwalker.tool.arxiv"
else
    echo "❌ Some MCP servers failed to start"
    echo "Check the troubleshooting guide: CLAUDE_CODE_TROUBLESHOOTING.md"
fi