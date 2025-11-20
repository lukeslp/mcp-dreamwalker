#!/usr/bin/env python3
"""
Unified Orchestrator MCP Server (Stdio)

Exposes Beltalowda and Swarm orchestrators via MCP stdio protocol.

Author: Luke Steuber
"""

import sys
import json
import asyncio
import logging
from typing import Dict, Any

# Add parent to path for imports
sys.path.insert(0, '/home/coolhand/dreamwalker-mcp')

from dreamwalker_mcp.mcp.unified_server import UnifiedMCPServer
from dreamwalker_mcp.config import ConfigManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def handle_mcp_request(server: UnifiedMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle MCP protocol request.

    Args:
        server: UnifiedMCPServer instance
        request: MCP request dict

    Returns:
        MCP response dict
    """
    method = request.get('method')
    params = request.get('params', {})

    try:
        if method == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {"tools": server.get_tools_manifest()}
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            # Map tool calls to server methods
            tool_method_map = {
                'orchestrate_research': server.tool_orchestrate_research,
                'orchestrate_search': server.tool_orchestrate_search,
                'get_orchestration_status': server.tool_get_orchestration_status,
                'cancel_orchestration': server.tool_cancel_orchestration,
                'list_orchestrator_patterns': server.tool_list_orchestrator_patterns,
                'list_registered_tools': server.tool_list_registered_tools,
                'execute_registered_tool': server.tool_execute_registered_tool,
            }

            if tool_name in tool_method_map:
                result = await tool_method_map[tool_name](arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

        elif method == 'resources/list':
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {"resources": server.get_resources_manifest()}
            }

        elif method == 'resources/read':
            uri = params.get('uri')

            # Route to appropriate resource handler
            if uri.startswith('orchestrator://') and uri.endswith('/info'):
                result = await server.resource_orchestrator_info(uri)
            elif uri.startswith('orchestrator://') and '/status' in uri:
                result = await server.resource_workflow_status(uri)
            elif uri.startswith('orchestrator://') and '/results' in uri:
                result = await server.resource_workflow_results(uri)
            else:
                result = {"uri": uri, "error": "Unknown resource"}

            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": result
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }

    except Exception as e:
        logger.exception(f"Error handling request: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "error": {"code": -32603, "message": str(e)}
        }


async def main():
    """Main stdio loop for MCP server."""
    logger.info("Starting Unified Orchestrator MCP Server (stdio)")

    # Initialize server
    config = ConfigManager(app_name='dreamwalker_unified_mcp')
    server = UnifiedMCPServer(config_manager=config)

    # Read requests from stdin, write responses to stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            response = await handle_mcp_request(server, request)

            # Write response to stdout
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")


if __name__ == '__main__':
    asyncio.run(main())
