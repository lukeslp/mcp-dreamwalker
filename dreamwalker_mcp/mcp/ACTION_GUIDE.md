# 🎯 Action Guide - What To Do Right Now

---

## You Are Here

✅ **Dreamwalker MCP v2.0.0** is deployed and running  
✅ **26 tools** are available at https://dr.eamer.dev/mcp/  
⏸️ **Cursor can't connect** (you're SSH'd in, Cursor runs locally)

---

## Do This Now (2 Options)

### Option A: Quick Setup (5 minutes)

**ON YOUR LOCAL MACHINE** (where Cursor runs):

1. **Download the bridge script:**
```bash
mkdir -p ~/.dreamwalker
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/mcp_http_bridge.py ~/.dreamwalker/
chmod +x ~/.dreamwalker/mcp_http_bridge.py
```

2. **Add to Cursor settings:**

Find and edit: `~/.config/Cursor/User/settings.json` (Linux/Mac) or `%APPDATA%\Cursor\User\settings.json` (Windows)

Add this JSON (adjust path for your home directory):
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

3. **Restart Cursor**

4. **Test:** Ask Cursor "What MCP tools do you have?"

### Option B: Automated Setup (Use the Script)

**ON YOUR LOCAL MACHINE**:

```bash
# Download the installer
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/install_cursor_mcp.sh ~/

# Run it
bash ~/install_cursor_mcp.sh
```

Then restart Cursor.

---

## How to Know It Worked

### In Cursor:

1. **Check MCP Status:**
   - Open Cursor Settings
   - Look for "MCP" or "Model Context Protocol"
   - Should show "dreamwalker" server as Connected

2. **Test a Tool:**
   Ask Cursor:
   ```
   "Use the search_arxiv tool to find 3 papers about large language models"
   ```

   Should get actual paper results!

3. **List All Tools:**
   Ask Cursor:
   ```
   "What MCP tools do you have access to?"
   ```

   Should list 26 tools.

---

## Troubleshooting

### "Can't find python3"

**Fix**: Use full path to python in Cursor config:
```json
"command": "/usr/bin/python3"
```

### "Bridge script not found"

**Fix**: Verify the path in settings.json matches where you copied the script:
```bash
ls -la ~/.dreamwalker/mcp_http_bridge.py
```

### "Connection refused"

**Fix**: Verify remote server is running:
```bash
curl https://dr.eamer.dev/mcp/health
```

Should return: `{"status": "healthy", ...}`

---

## What You Can Do Once Connected

### Academic Research
```
"Search arXiv for the 5 most cited papers about transformers"
"Find Semantic Scholar papers about AI safety"
```

### Data Analysis
```
"Get Census poverty data for California counties"
"Fetch population statistics for all US states"
```

### Caching
```
"Cache this configuration: {'theme': 'dark', 'lang': 'en'} with key 'user_prefs' for 1 hour"
"Get the cached value for key 'user_prefs'"
```

### Orchestration
```
"Use orchestrate_research to analyze quantum computing applications with 9 agents"
"Use orchestrate_search to gather information about climate change policies"
```

### Document Processing
```
"Parse the PDF at /path/to/document.pdf"
"Extract text from this DOCX file"
```

---

## After Cursor is Connected

### Next: Phase 2 Migrations

**Goal**: Eliminate ~3,400 lines of duplicated code

**Services to migrate**:
1. **studio** - Use shared SwarmOrchestrator (3 days)
2. **swarm** - Use shared ToolRegistry (2 days)
3. **planner** - Extend BaseOrchestrator (3 days)

**See**: `/home/coolhand/shared/mcp/MIGRATION_ROADMAP.md`

---

## TL;DR

**Right now, on your LOCAL machine:**

```bash
# 1. Get the bridge
mkdir -p ~/.dreamwalker
scp coolhand@dr.eamer.dev:/home/coolhand/shared/mcp/mcp_http_bridge.py ~/.dreamwalker/

# 2. Add to Cursor settings.json:
{
  "mcpServers": {
    "dreamwalker": {
      "command": "python3",
      "args": ["~/.dreamwalker/mcp_http_bridge.py", "--url", "https://dr.eamer.dev/mcp"]
    }
  }
}

# 3. Restart Cursor

# 4. Test: "Use search_arxiv to find papers about AI"
```

---

🌊 **That's it! You'll have 26 Dreamwalker tools available in Cursor!**

