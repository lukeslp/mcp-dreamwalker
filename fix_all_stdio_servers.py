#!/usr/bin/env python3
"""Fix all stdio servers to add initialize method"""

import os
import re

STDIO_DIR = "/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/mcp/stdio_servers"

INITIALIZE_CODE = '''    try:
        if method == 'initialize':
            # Handle MCP initialization handshake
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "dreamwalker-SERVER_NAME",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == 'initialized':
            # Client confirms initialization complete
            return {
                "jsonrpc": "2.0", 
                "id": request.get('id'),
                "result": {}
            }
        
        elif method == 'tools/list':'''

servers = [
    ("cache_stdio.py", "cache"),
    ("data_stdio.py", "data"),
    ("providers_stdio.py", "providers"),
    ("utility_stdio.py", "utility"),
    ("web_search_stdio.py", "websearch")
]

for filename, server_name in servers:
    filepath = os.path.join(STDIO_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already fixed
    if 'method == \'initialize\'' in content:
        print(f"✓ {filename} already has initialize method")
        continue
    
    # Replace the pattern
    pattern = r'(\s+try:\s*\n\s+if method == \'tools/list\':)'
    replacement = INITIALIZE_CODE.replace('SERVER_NAME', server_name)
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"✅ Fixed {filename}")
    else:
        print(f"⚠️  Could not fix {filename} - pattern not found")

print("\nDone! Testing servers...")

# Test each server
import subprocess
for filename, server_name in servers:
    module = filename.replace('.py', '')
    cmd = f"echo '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{{}}}}' | timeout 2 python3 -m dreamwalker_mcp.mcp.stdio_servers.{module} 2>&1 | grep -q '\"result\"'"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ {server_name} server works!")
    else:
        print(f"❌ {server_name} server failed")