#!/bin/bash
# Script to export .env variables to current shell

if [ -f ~/.env ]; then
    echo "Loading environment variables from ~/.env..."
    set -a  # automatically export all variables
    source ~/.env
    set +a  # turn off automatic export
    echo "✅ Environment variables loaded"
    
    # Check key variables
    [ -n "$ANTHROPIC_API_KEY" ] && echo "✅ ANTHROPIC_API_KEY is set" || echo "❌ ANTHROPIC_API_KEY not found"
    [ -n "$XAI_API_KEY" ] && echo "✅ XAI_API_KEY is set" || echo "❌ XAI_API_KEY not found"
    [ -n "$OPENAI_API_KEY" ] && echo "✅ OPENAI_API_KEY is set" || echo "❌ OPENAI_API_KEY not found"
else
    echo "❌ ~/.env file not found"
fi