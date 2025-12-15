# MCP Tool Naming Fix Summary

## Issue
The MCP tools were being exposed with invalid names containing dots (e.g., `dreamwalker.orchestrate.cascade`), which violates the MCP protocol naming rules. MCP tool names must match the pattern `^[a-zA-Z0-9_-]{1,128}$`, meaning only alphanumeric characters, underscores, and dashes are allowed.

## Root Cause
The `get_mcp_tool_name()` function in `/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/naming/mcp_naming.py` was generating tool names with dots as separators.

## Fix Applied
1. **Updated `get_mcp_tool_name()` function**: Changed from generating names like `dreamwalker.type.name` to `dreamwalker_type_name`, replacing dots with underscores.

2. **Updated `parse_mcp_tool_name()` function**: Modified to parse the new underscore-based format correctly.

3. **Updated `resolve_legacy_tool_name()` function**: Changed the check for new format names from `startswith("dreamwalker.")` to `startswith("dreamwalker_")`.

4. **Updated stdio server mappings**: In `unified_stdio.py`, updated the tool name mappings to use the new underscore format.

5. **Fixed comments in unified_server.py**: The header comments were updated by the fix script to reflect the actual tool names (though these are just comments and don't affect functionality).

## Affected Files
- `/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/naming/mcp_naming.py`
- `/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/mcp/stdio_servers/unified_stdio.py`
- `/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/mcp/unified_server.py` (comments only)

## Valid Tool Names Now Exposed
All tools now have valid names:
- `dreamwalker_orchestrate_cascade`
- `dreamwalker_orchestrate_swarm`
- `dreamwalker_utility_status`
- `dreamwalker_utility_cancel`
- `dreamwalker_utility_patterns`
- `dreamwalker_utility_registry_list`
- `dreamwalker_utility_registry_execute`

## Note on "info" Tool
The investigation did not find any explicit "info" tool being registered. If this is still appearing in your MCP client, it may be:
1. Coming from a different MCP server
2. Being dynamically registered by the tool registry at runtime
3. A client-side issue

All the standard MCP servers in the dreamwalker-mcp package are now using valid tool names.