# Cursor Manual Setup - Step by Step

**For connecting Cursor (on your local machine) to Dreamwalker MCP (on dr.eamer.dev)**

---

## Quick Overview

Since Cursor runs on your **LOCAL machine** but Dreamwalker MCP runs on your **REMOTE server**, you need:
1. Bridge script on your local machine
2. Cursor configuration pointing to the bridge
3. Restart Cursor

---

## Option 1: Automated Setup (Recommended)

### On Your LOCAL Machine:

```bash
# Download and run the installer
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/install_cursor_mcp.sh ~/
chmod +x ~/install_cursor_mcp.sh
~/install_cursor_mcp.sh
```

This will:
- Download the bridge script to `~/.dreamwalker/`
- Configure Cursor automatically (or show you what to add)
- Test the connection

Then restart Cursor!

---

## Option 2: Manual Setup

### Step 1: Copy Bridge Script to Local Machine

**On your LOCAL machine** (in terminal):

```bash
# Create directory
mkdir -p ~/.dreamwalker

# Download bridge from server
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/mcp_http_bridge.py ~/.dreamwalker/

# Make executable
chmod +x ~/.dreamwalker/mcp_http_bridge.py
```

### Step 2: Configure Cursor

**Find your Cursor settings file**:

- **Linux**: `~/.config/Cursor/User/settings.json`
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`  
- **Windows**: `%APPDATA%\Cursor\User\settings.json`

**Open settings.json** and add the `mcpServers` section:

```json
{
  // ... your existing settings ...
  
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/Users/YOUR_USERNAME/.dreamwalker/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ],
      "description": "Dreamwalker - 26 tools for orchestration, data, cache, utilities"
    }
  }
}
```

**Important**: Replace `/Users/YOUR_USERNAME/` with your actual home directory path:
- Linux: `/home/yourusername/.dreamwalker/mcp_http_bridge.py`
- macOS: `/Users/yourusername/.dreamwalker/mcp_http_bridge.py`
- Windows: `C:\Users\yourusername\.dreamwalker\mcp_http_bridge.py`

### Step 3: Test the Bridge (Before Restarting Cursor)

**On your LOCAL machine**:

```bash
# Test the bridge works
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 ~/.dreamwalker/mcp_http_bridge.py --url https://dr.eamer.dev/mcp 2>&1 | grep -o '"tools"'

# Should output: "tools"
```

If that works, you're ready!

### Step 4: Restart Cursor

1. Close Cursor completely (quit, don't just close window)
2. Reopen Cursor
3. Look for MCP status (usually in status bar or settings)

### Step 5: Verify in Cursor

Check Cursor's MCP settings/panel:
- Should show "dreamwalker" server
- Status: Connected
- Tools: 26 available

---

## Option 3: SSH Tunnel (If Bridge Doesn't Work)

If the bridge approach doesn't work, use SSH port forwarding:

### Step 1: Create SSH Tunnel

**On your LOCAL machine**, open a terminal and run:

```bash
ssh -L 5060:localhost:5060 coolhand@dr.eamer.dev -N
```

Keep this terminal open (the tunnel stays active while connected).

### Step 2: Configure Cursor for Local Port

Update Cursor settings to use localhost:

```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/Users/YOUR_USERNAME/.dreamwalker/mcp_http_bridge.py",
        "--url",
        "http://localhost:5060"
      ]
    }
  }
}
```

Note: URL changed to `http://localhost:5060` (forwarded port)

### Step 3: Restart Cursor

With the SSH tunnel still running, restart Cursor.

---

## Testing After Setup

### In Cursor, Try These Commands:

**1. List available tools:**
```
"What MCP tools do you have available?"
```

Should show 26 tools including search_arxiv, cache_set, orchestrate_research, etc.

**2. Search arXiv:**
```
"Use the search_arxiv tool to find 3 papers about neural networks"
```

Should return paper titles, authors, and summaries.

**3. Cache something:**
```
"Use cache_set to store {'name': 'test'} with key 'test_key' for 60 seconds"
```

Then:
```
"Use cache_get to retrieve key 'test_key'"
```

Should return the cached value.

**4. Orchestrate research:**
```
"Use orchestrate_research to analyze AI safety approaches with 5 agents"
```

Should start a research workflow and return a task_id.

---

## Troubleshooting

### "MCP Server Failed to Start"

**Problem**: Cursor can't execute the bridge script

**Solutions**:
1. Check Python3 is available: `which python3` (on local machine)
2. Verify script path is correct in settings.json
3. Make sure script is executable: `chmod +x ~/.dreamwalker/mcp_http_bridge.py`
4. Test manually: `python3 ~/.dreamwalker/mcp_http_bridge.py --verbose`

### "No Tools Available"

**Problem**: Bridge running but not finding tools

**Solutions**:
1. Verify remote server is up: `curl https://dr.eamer.dev/mcp/health`
2. Test bridge manually:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
     python3 ~/.dreamwalker/mcp_http_bridge.py
   ```
3. Check Cursor MCP logs (usually in Cursor settings/output panel)

### "Connection Timeout"

**Problem**: Can't reach remote server

**Solutions**:
1. Check server is running: `curl https://dr.eamer.dev/mcp/health`
2. Verify firewall/network allows HTTPS
3. Try SSH tunnel method (Option 3 above)

---

## Alternative: Copy/Paste Config

If you prefer not to run the install script, here's the complete config:

### Linux/macOS

**1. Download bridge:**
```bash
mkdir -p ~/.dreamwalker
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/mcp_http_bridge.py ~/.dreamwalker/
chmod +x ~/.dreamwalker/mcp_http_bridge.py
```

**2. Add to Cursor settings** (`~/.config/Cursor/User/settings.json`):
```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": [
        "/home/YOURUSERNAME/.dreamwalker/mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ]
    }
  }
}
```

**3. Restart Cursor**

### Windows

**1. Download bridge** (in PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.dreamwalker"
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/mcp_http_bridge.py "$env:USERPROFILE\.dreamwalker\"
```

**2. Add to Cursor settings** (`%APPDATA%\Cursor\User\settings.json`):
```json
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python",
      "args": [
        "C:\\Users\\YOURUSERNAME\\.dreamwalker\\mcp_http_bridge.py",
        "--url",
        "https://dr.eamer.dev/mcp"
      ]
    }
  }
}
```

**3. Restart Cursor**

---

## Verification

### After Restart, Check Cursor:

1. **Open Cursor Settings** → Search for "MCP"
2. **Look for "dreamwalker" server** in MCP servers list
3. **Status should be**: Connected / Running
4. **Tool count should be**: 26

### Test in Cursor Chat:

```
You: "What MCP tools do you have access to?"

Expected: Lists 26 tools including search_arxiv, cache_set, 
orchestrate_research, parse_document, etc.
```

```
You: "Use search_arxiv to find 2 papers about transformers"

Expected: Makes API call and returns 2 paper results with 
titles, authors, abstracts
```

---

## What You Get

Once connected, you can use Cursor to:

✅ **Orchestrate multi-agent research** - "Research [topic] with 9 agents"  
✅ **Search academic papers** - "Find arXiv papers about [topic]"  
✅ **Fetch Census data** - "Get poverty data for California counties"  
✅ **Cache data** - "Cache this value for 1 hour"  
✅ **Parse documents** - "Extract text from this PDF"  
✅ **Multi-source search** - "Search across multiple providers"

All without writing any API client code!

---

## Next Steps After Setup

1. **Test basic tools** (search_arxiv, cache_set/get)
2. **Try an orchestration** (orchestrate_research)
3. **Read migration plan** for Phase 2 (eliminate ~5,000 lines of duplicate code)

---

**Need Help?**

- Bridge script: `/home/coolhand/shared/mcp/mcp_http_bridge.py`
- Full guide: `/home/coolhand/shared/mcp/CURSOR_REMOTE_SETUP.md`
- What's next: `/home/coolhand/shared/mcp/WHATS_NEXT.md`

**Ready to migrate services?** See `/home/coolhand/shared/mcp/MIGRATION_ROADMAP.md`

---

🌊 **Dreamwalker awaits your connection!**

