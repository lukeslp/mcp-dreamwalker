#!/bin/bash
# Script to properly restart Claude Code with dreamwalker MCP

echo "🛑 Stopping all Claude instances..."
pkill -f claude
sleep 2

echo "✅ Loading environment from ~/.env..."
set -a
source ~/.env
set +a

echo "🔍 Verifying environment..."
if [ -z "$XAI_API_KEY" ]; then
    echo "❌ ERROR: XAI_API_KEY not loaded from ~/.env"
    echo "Please check your ~/.env file"
    exit 1
fi

echo "✅ Environment loaded successfully"
echo "   XAI_API_KEY: ${XAI_API_KEY:0:10}..."

echo ""
echo "🚀 Starting Claude Code with dreamwalker MCP..."
echo "   When Claude opens, try typing: @mcp__dreamwalker"
echo ""

# Start Claude with the loaded environment
claude