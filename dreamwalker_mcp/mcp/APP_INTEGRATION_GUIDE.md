# MCP App.py Integration Guide

**Date**: November 18, 2025  
**Status**: Ready for Integration

---

## Overview

This guide provides step-by-step instructions for integrating the new MCP servers (data_server, cache_server, utility_server) into the existing `app.py` Flask application.

---

## New Servers Implemented

### 1. DataServer (`data_server.py`)

**Tools (8):**
- `fetch_census_acs` - Fetch ACS demographic data
- `fetch_census_saipe` - Fetch poverty estimates  
- `list_census_variables` - Search variable catalog
- `search_arxiv` - Search arXiv papers
- `search_semantic_scholar` - Search research papers
- `get_semantic_scholar_paper` - Get paper details
- `wayback_search` - Search Wayback Machine
- `wayback_available_snapshots` - List snapshots

**Resources (3):**
- `census://variables/{table}`
- `arxiv://category/{category}`
- `archive://snapshot/{url}/{timestamp}`

### 2. CacheServer (`cache_server.py`)

**Tools (7):**
- `cache_get` - Retrieve value
- `cache_set` - Store value with TTL
- `cache_delete` - Delete key
- `cache_increment` - Increment counter
- `cache_exists` - Check existence
- `cache_expire` - Set TTL
- `cache_list_keys` - List keys by pattern

**Resources (2):**
- `cache://stats` - Cache statistics
- `cache://keys/{namespace}` - List namespace keys

### 3. UtilityServer (`utility_server.py`)

**Tools (4):**
- `parse_document` - Parse 50+ file formats
- `multi_provider_search` - Multi-query research
- `extract_citations` - Extract citations
- `format_citation_bibtex` - Format as BibTeX

**Resources (2):**
- `utils://supported_formats` - Supported file types
- `utils://citation_styles` - Citation styles

---

## Integration Steps

### Step 1: Import New Servers

Add imports at the top of `app.py`:

```python
from data_server import DataServer
from cache_server import CacheServer
from utility_server import UtilityServer
```

### Step 2: Initialize Servers

In the server initialization section (likely near `ProvidersServer` and `UnifiedMCPServer` initialization):

```python
# Initialize all MCP servers
config = ConfigManager(app_name='mcp_orchestrator')

providers_server = ProvidersServer(config_manager=config)
unified_server = UnifiedMCPServer(config_manager=config)

# NEW: Initialize additional servers
data_server = DataServer(config_manager=config)
cache_server = CacheServer(config_manager=config)
utility_server = UtilityServer(config_manager=config)
```

### Step 3: Update /tools Endpoint

Modify the `/tools` endpoint to include tools from all servers:

```python
@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools."""
    tools = []
    
    # Existing servers
    tools.extend(providers_server.get_tools_manifest())
    tools.extend(unified_server.get_tools_manifest())
    
    # NEW: Add new server tools
    tools.extend(data_server.get_tools_manifest())
    tools.extend(cache_server.get_tools_manifest())
    tools.extend(utility_server.get_tools_manifest())
    
    return jsonify(tools)
```

### Step 4: Update /resources Endpoint

Modify the `/resources` endpoint to include resources from all servers:

```python
@app.route('/resources', methods=['GET'])
def list_resources():
    """List all available MCP resources."""
    resources = []
    
    # Existing servers
    resources.extend(providers_server.get_resources_manifest())
    resources.extend(unified_server.get_resources_manifest())
    
    # NEW: Add new server resources
    resources.extend(data_server.get_resources_manifest())
    resources.extend(cache_server.get_resources_manifest())
    resources.extend(utility_server.get_resources_manifest())
    
    return jsonify(resources)
```

### Step 5: Add Tool Endpoints for DataServer

Add routes for each data_server tool:

```python
# Census tools
@app.route('/tools/fetch_census_acs', methods=['POST'])
def tool_fetch_census_acs():
    arguments = request.get_json()
    result = data_server.tool_fetch_census_acs(arguments)
    return jsonify(result)

@app.route('/tools/fetch_census_saipe', methods=['POST'])
def tool_fetch_census_saipe():
    arguments = request.get_json()
    result = data_server.tool_fetch_census_saipe(arguments)
    return jsonify(result)

@app.route('/tools/list_census_variables', methods=['POST'])
def tool_list_census_variables():
    arguments = request.get_json()
    result = data_server.tool_list_census_variables(arguments)
    return jsonify(result)

# arXiv tools
@app.route('/tools/search_arxiv', methods=['POST'])
def tool_search_arxiv():
    arguments = request.get_json()
    result = data_server.tool_search_arxiv(arguments)
    return jsonify(result)

# Semantic Scholar tools
@app.route('/tools/search_semantic_scholar', methods=['POST'])
def tool_search_semantic_scholar():
    arguments = request.get_json()
    result = data_server.tool_search_semantic_scholar(arguments)
    return jsonify(result)

@app.route('/tools/get_semantic_scholar_paper', methods=['POST'])
def tool_get_semantic_scholar_paper():
    arguments = request.get_json()
    result = data_server.tool_get_semantic_scholar_paper(arguments)
    return jsonify(result)

# Wayback Machine tools
@app.route('/tools/wayback_search', methods=['POST'])
def tool_wayback_search():
    arguments = request.get_json()
    result = data_server.tool_wayback_search(arguments)
    return jsonify(result)

@app.route('/tools/wayback_available_snapshots', methods=['POST'])
def tool_wayback_available_snapshots():
    arguments = request.get_json()
    result = data_server.tool_wayback_available_snapshots(arguments)
    return jsonify(result)
```

### Step 6: Add Tool Endpoints for CacheServer

```python
@app.route('/tools/cache_get', methods=['POST'])
def tool_cache_get():
    arguments = request.get_json()
    result = cache_server.tool_cache_get(arguments)
    return jsonify(result)

@app.route('/tools/cache_set', methods=['POST'])
def tool_cache_set():
    arguments = request.get_json()
    result = cache_server.tool_cache_set(arguments)
    return jsonify(result)

@app.route('/tools/cache_delete', methods=['POST'])
def tool_cache_delete():
    arguments = request.get_json()
    result = cache_server.tool_cache_delete(arguments)
    return jsonify(result)

@app.route('/tools/cache_increment', methods=['POST'])
def tool_cache_increment():
    arguments = request.get_json()
    result = cache_server.tool_cache_increment(arguments)
    return jsonify(result)

@app.route('/tools/cache_exists', methods=['POST'])
def tool_cache_exists():
    arguments = request.get_json()
    result = cache_server.tool_cache_exists(arguments)
    return jsonify(result)

@app.route('/tools/cache_expire', methods=['POST'])
def tool_cache_expire():
    arguments = request.get_json()
    result = cache_server.tool_cache_expire(arguments)
    return jsonify(result)

@app.route('/tools/cache_list_keys', methods=['POST'])
def tool_cache_list_keys():
    arguments = request.get_json()
    result = cache_server.tool_cache_list_keys(arguments)
    return jsonify(result)
```

### Step 7: Add Tool Endpoints for UtilityServer

```python
@app.route('/tools/parse_document', methods=['POST'])
def tool_parse_document():
    arguments = request.get_json()
    result = utility_server.tool_parse_document(arguments)
    return jsonify(result)

@app.route('/tools/multi_provider_search', methods=['POST'])
def tool_multi_provider_search():
    arguments = request.get_json()
    result = utility_server.tool_multi_provider_search(arguments)
    return jsonify(result)

@app.route('/tools/extract_citations', methods=['POST'])
def tool_extract_citations():
    arguments = request.get_json()
    result = utility_server.tool_extract_citations(arguments)
    return jsonify(result)

@app.route('/tools/format_citation_bibtex', methods=['POST'])
def tool_format_citation_bibtex():
    arguments = request.get_json()
    result = utility_server.tool_format_citation_bibtex(arguments)
    return jsonify(result)
```

### Step 8: Add Resource Endpoints

Add resource handlers for new URIs:

```python
@app.route('/resources/<path:uri>', methods=['GET'])
def get_resource(uri):
    """Get MCP resource by URI."""
    try:
        # Parse URI scheme
        if uri.startswith('provider://'):
            # Existing provider resources
            # ...
            
        elif uri.startswith('orchestrator://'):
            # Existing orchestrator resources
            # ...
            
        # NEW: Census resources
        elif uri.startswith('census://'):
            if '/variables/' in uri:
                return jsonify(data_server.resource_census_variables(uri))
                
        # NEW: arXiv resources
        elif uri.startswith('arxiv://'):
            if '/category/' in uri:
                return jsonify(data_server.resource_arxiv_category(uri))
                
        # NEW: Archive.org resources
        elif uri.startswith('archive://'):
            if '/snapshot/' in uri:
                return jsonify(data_server.resource_archive_snapshot(uri))
                
        # NEW: Cache resources
        elif uri.startswith('cache://'):
            if uri == 'cache://stats':
                return jsonify(cache_server.resource_cache_stats(uri))
            elif uri.startswith('cache://keys/'):
                return jsonify(cache_server.resource_cache_keys(uri))
                
        # NEW: Utility resources
        elif uri.startswith('utils://'):
            if uri == 'utils://supported_formats':
                return jsonify(utility_server.resource_supported_formats(uri))
            elif uri == 'utils://citation_styles':
                return jsonify(utility_server.resource_citation_styles(uri))
                
        else:
            return jsonify({"error": f"Unknown resource URI scheme: {uri}"}), 404
            
    except Exception as e:
        logger.exception(f"Error getting resource {uri}: {e}")
        return jsonify({"error": str(e)}), 500
```

### Step 9: Update Health Endpoint

Update the health check to report on new servers:

```python
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'mcp-orchestrator',
        'servers': {
            'providers': 'active',
            'orchestration': 'active',
            'data_fetching': 'active',  # NEW
            'cache': 'active',           # NEW
            'utilities': 'active'        # NEW
        },
        'tool_count': len(
            providers_server.get_tools_manifest() +
            unified_server.get_tools_manifest() +
            data_server.get_tools_manifest() +      # NEW
            cache_server.get_tools_manifest() +     # NEW
            utility_server.get_tools_manifest()     # NEW
        )
    })
```

---

## Verification Steps

### 1. Test Server Startup

```bash
cd /home/coolhand/shared/mcp
python app.py
```

Should start without errors.

### 2. Verify Tools List

```bash
curl http://localhost:5060/mcp/tools | jq '. | length'
```

Should show 30+ tools (was 12, now should be 31+).

### 3. Test Individual Tools

**Census:**
```bash
curl -X POST http://localhost:5060/mcp/tools/fetch_census_acs \
  -H "Content-Type: application/json" \
  -d '{"year": 2022, "variables": {"B01003_001E": "population"}, "geography": "state:*"}'
```

**Cache:**
```bash
curl -X POST http://localhost:5060/mcp/tools/cache_set \
  -H "Content-Type: application/json" \
  -d '{"key": "test", "value": "hello", "ttl": 60}'
  
curl -X POST http://localhost:5060/mcp/tools/cache_get \
  -H "Content-Type: application/json" \
  -d '{"key": "test"}'
```

**Utilities:**
```bash
curl -X POST http://localhost:5060/mcp/tools/parse_document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf"}'
```

### 4. Verify Resources

```bash
curl http://localhost:5060/mcp/resources | jq '.[] | .uri'
```

Should show all resource URIs including new ones.

---

## Dependencies

Update `requirements.txt` if needed:

```txt
# Existing dependencies
flask
flask-cors
gunicorn
...

# NEW: Data fetching dependencies
arxiv          # arXiv API
aiohttp        # Semantic Scholar async client
requests       # General HTTP

# NEW: Cache dependencies
redis          # Redis client (already present)

# NEW: Utility dependencies
pdfminer.six   # PDF parsing
python-docx    # DOCX parsing
openpyxl       # Excel parsing
beautifulsoup4 # HTML parsing
bibtexparser   # BibTeX formatting
```

---

## Rollback Plan

If integration fails:

1. Comment out new server imports
2. Remove new route additions
3. Restart service
4. Fix issues, then re-integrate

```python
# ROLLBACK: Comment out new servers
# from data_server import DataServer
# from cache_server import CacheServer
# from utility_server import UtilityServer

# # Comment out initializations
# # data_server = DataServer(config_manager=config)
# # cache_server = CacheServer(config_manager=config)
# # utility_server = UtilityServer(config_manager=config)
```

---

## Performance Considerations

1. **Lazy Client Initialization**: All servers use lazy loading for expensive clients (Census, Redis, etc.)

2. **Caching**: Data server results should be cached to avoid repeated API calls

3. **Rate Limiting**: Consider adding rate limiting for expensive operations:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/tools/fetch_census_acs', methods=['POST'])
@limiter.limit("10 per minute")  # Limit Census API calls
def tool_fetch_census_acs():
    # ...
```

4. **Error Handling**: All tools return `{success: bool, error: str}` format for consistent error handling

---

## Next Steps

After integration:

1. Update MCP README.md with new tools
2. Add integration tests
3. Update Caddy configuration if needed
4. Restart MCP service: `sm restart mcp-server`
5. Monitor logs for errors
6. Test via Codex/Claude Code

---

**Status**: Ready for implementation  
**Estimated Time**: 2-3 hours  
**Risk Level**: Low (additive changes, no breaking modifications)

