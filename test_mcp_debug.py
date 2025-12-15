#!/usr/bin/env python3
"""Debug MCP stdio communication"""

import subprocess
import json
import sys

print("Testing unified_stdio with debug output...\n")

# Create a combined request
requests = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}},
    {"jsonrpc":"2.0","id":2,"method":"initialized","params":{}},
    {"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}}
]

# Write requests to temp file
with open('/tmp/mcp_test_requests.json', 'w') as f:
    for req in requests:
        f.write(json.dumps(req) + '\n')

# Run the server
cmd = 'python3 -m dreamwalker_mcp.mcp.stdio_servers.unified_stdio < /tmp/mcp_test_requests.json 2>/tmp/mcp_stderr.log'

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nNumber of lines:", len(result.stdout.strip().split('\n')) if result.stdout else 0)
    
    # Parse each response
    if result.stdout:
        for i, line in enumerate(result.stdout.strip().split('\n')):
            print(f"\nLine {i+1}:")
            try:
                response = json.loads(line)
                print(json.dumps(response, indent=2))
            except:
                print("  Failed to parse:", line)
    
    # Check stderr
    with open('/tmp/mcp_stderr.log', 'r') as f:
        stderr = f.read()
        if stderr:
            print("\nSTDERR:")
            print(stderr[:500])
            
except Exception as e:
    print(f"Error: {e}")

print("\nTest complete!")