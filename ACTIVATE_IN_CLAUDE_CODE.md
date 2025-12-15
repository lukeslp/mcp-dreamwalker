# 🚀 Activating Dreamwalker in Claude Code

Your setup is correct! The issue is that Claude Code needs the environment variables when it starts.

## Quick Steps:

### 1. Open a NEW terminal and load the environment:
```bash
source ~/.bashrc
# OR manually:
set -a; source ~/.env; set +a
```

### 2. Verify keys are loaded:
```bash
echo $XAI_API_KEY  # Should show your key
```

### 3. Kill ALL Claude Code instances:
```bash
pkill -f claude
```

### 4. Start Claude Code FROM THAT TERMINAL:
```bash
claude
```

**Important**: You must start Claude Code from a terminal where the environment variables are already loaded!

## Alternative: Create a launcher script

Save this as `~/bin/claude-with-env`:

```bash
#!/bin/bash
# Load environment and start Claude Code
set -a
source ~/.env
set +a
exec claude "$@"
```

Then:
```bash
chmod +x ~/bin/claude-with-env
```

Now you can always start Claude with: `claude-with-env`

## Verify It's Working

Once Claude Code starts with the environment loaded, you should see:
- Type `@mcp` and you'll see dreamwalker servers
- Tools like `@mcp__dreamwalker-unified__dreamwalker.orchestrate.cascade`

## Troubleshooting

If tools still don't appear:
1. Check Claude Code logs: `~/.config/Claude/logs/`
2. Look for MCP startup messages
3. Any errors will show which API key is missing

The key insight: Claude Code must inherit the environment variables from the shell that launches it!