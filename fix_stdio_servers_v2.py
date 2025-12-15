#!/usr/bin/env python3
"""Fix all stdio servers properly"""

import os

STDIO_DIR = "/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/mcp/stdio_servers"

def fix_server(filepath, server_name):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the try: block
    for i, line in enumerate(lines):
        if line.strip() == "try:" and i > 0:
            # Check if params line exists
            if "params = request.get('params', {})" in lines[i-1]:
                # Check if there's already an initialize method
                if i + 1 < len(lines) and "method == 'initialize'" in lines[i+1]:
                    print(f"✓ {filepath} already fixed")
                    return
                
                # Insert the initialize handling after try:
                indent = "        "  # 8 spaces
                initialize_block = f'''{indent}if method == 'initialize':
{indent}    # Handle MCP initialization handshake
{indent}    return {{
{indent}        "jsonrpc": "2.0",
{indent}        "id": request.get('id'),
{indent}        "result": {{
{indent}            "protocolVersion": "0.1.0",
{indent}            "capabilities": {{
{indent}                "tools": {{}},
{indent}                "resources": {{}}
{indent}            }},
{indent}            "serverInfo": {{
{indent}                "name": "dreamwalker-{server_name}",
{indent}                "version": "1.0.0"
{indent}            }}
{indent}        }}
{indent}    }}
{indent}
{indent}elif method == 'initialized':
{indent}    # Client confirms initialization complete
{indent}    return {{
{indent}        "jsonrpc": "2.0", 
{indent}        "id": request.get('id'),
{indent}        "result": {{}}
{indent}    }}
{indent}
{indent}el'''
                
                # Find the next if statement after try:
                next_line = lines[i+1]
                if "if method ==" in next_line:
                    # Replace 'if' with 'elif' in the existing line
                    lines[i+1] = next_line.replace("if method ==", "elif method ==", 1)
                    # Insert our block
                    lines.insert(i+1, initialize_block)
                    
                    # Write back
                    with open(filepath, 'w') as f:
                        f.writelines(lines)
                    print(f"✅ Fixed {filepath}")
                    return
    
    print(f"⚠️  Could not fix {filepath} - pattern not found")

# Fix each server
servers = [
    ("cache_stdio.py", "cache"),
    ("data_stdio.py", "data"), 
    ("providers_stdio.py", "providers"),
    ("utility_stdio.py", "utility"),
    ("web_search_stdio.py", "websearch")
]

# First pass - check syntax errors
for filename, server_name in servers:
    filepath = os.path.join(STDIO_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        # Fix the specific syntax error
        if "params = request.get('params', {})    try:" in content:
            content = content.replace(
                "params = request.get('params', {})    try:",
                "params = request.get('params', {})\n\n    try:"
            )
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"🔧 Fixed syntax error in {filename}")

# Second pass - add initialize method
for filename, server_name in servers:
    filepath = os.path.join(STDIO_DIR, filename)
    if os.path.exists(filepath):
        fix_server(filepath, server_name)

print("\n🧪 Testing servers...")
import subprocess
for filename, server_name in servers:
    module = filename.replace('.py', '')
    cmd = f"echo '{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{{}}}}' | timeout 2 python3 -m dreamwalker_mcp.mcp.stdio_servers.{module} 2>&1"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if '"result"' in result.stdout and '"error"' not in result.stdout:
        print(f"✅ {server_name} server works!")
    else:
        print(f"❌ {server_name} server failed")
        if result.stderr:
            print(f"   Error: {result.stderr.strip()[:100]}...")