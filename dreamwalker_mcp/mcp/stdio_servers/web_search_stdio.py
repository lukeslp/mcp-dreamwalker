#!/usr/bin/env python3
"""
Web Search MCP Server (Stdio)

Exposes web search capabilities via MCP stdio protocol.

Author: Luke Steuber
"""

import sys
import json
import logging
from typing import Dict, Any

sys.path.insert(0, '/home/coolhand/dreamwalker-mcp')

from dreamwalker_mcp.mcp.web_search_server import WebSearchServer
from dreamwalker_mcp.config import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_mcp_request(server: WebSearchServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol request."""
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
            if hasattr(server, f'tool_{tool_name}'):
                result = getattr(server, f'tool_{tool_name}')(arguments)
                return {"jsonrpc": "2.0", "id": request.get('id'), "result": result}
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }
    except Exception as e:
        logger.exception(f"Error: {e}")
        return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -32603, "message": str(e)}}


def main():
    logger.info("Starting Web Search MCP Server (stdio)")
    config = ConfigManager(app_name='dreamwalker_web_search_mcp')
    server = WebSearchServer(config_manager=config)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            response = handle_mcp_request(server, request)
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.exception(f"Error in main loop: {e}")


if __name__ == '__main__':
    main()
