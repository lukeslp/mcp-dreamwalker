#!/usr/bin/env python3
"""Test MCP servers initialization"""

import subprocess
import json
import sys

servers = [
    ("unified_stdio", "dreamwalker-unified"),
    ("providers_stdio", "dreamwalker-providers"), 
    ("data_stdio", "dreamwalker-data"),
    ("cache_stdio", "dreamwalker-cache"),
    ("utility_stdio", "dreamwalker-utility"),
    ("web_search_stdio", "dreamwalker-websearch")
]

print("Testing MCP servers protocol handshake...\n")

for module, expected_name in servers:
    print(f"Testing {module}...")
    
    # Send initialize request
    cmd = f'echo \'{{"jsonrpc":"2.0","id":1,"method":"initialize","params":{{}}}}\' | python3 -m dreamwalker_mcp.mcp.stdio_servers.{module} 2>/dev/null'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        
        if result.stdout:
            response = json.loads(result.stdout.strip())
            
            if 'result' in response:
                protocol_version = response['result'].get('protocolVersion', 'Unknown')
                server_name = response['result'].get('serverInfo', {}).get('name', 'Unknown')
                
                if protocol_version == "2024-11-05":
                    print(f"  ✅ Protocol version: {protocol_version}")
                else:
                    print(f"  ❌ Wrong protocol version: {protocol_version}")
                
                print(f"     Server name: {server_name}")
            else:
                print(f"  ❌ No result in response: {response}")
        else:
            print(f"  ❌ No output received")
            if result.stderr:
                print(f"     Error: {result.stderr[:100]}")
                
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout - server didn't respond")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()

print("Test complete!")