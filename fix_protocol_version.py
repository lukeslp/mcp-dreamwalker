#!/usr/bin/env python3
"""Fix protocol version in all stdio servers to use 2024-11-05"""

import os
import re
import glob

# Find all stdio server files
stdio_files = glob.glob("/home/coolhand/dreamwalker-mcp/dreamwalker_mcp/mcp/stdio_servers/*_stdio.py")

print(f"Found {len(stdio_files)} stdio server files")

for filepath in stdio_files:
    filename = os.path.basename(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check current protocol version
    old_version_match = re.search(r'"protocolVersion"\s*:\s*"([^"]+)"', content)
    if old_version_match:
        old_version = old_version_match.group(1)
        print(f"\n{filename}: Current protocol version: {old_version}")
        
        if old_version == "2024-11-05":
            print(f"  ✓ Already using correct protocol version")
            continue
        
        # Replace protocol version
        new_content = re.sub(
            r'"protocolVersion"\s*:\s*"[^"]+"',
            '"protocolVersion": "2024-11-05"',
            content
        )
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"  ✅ Updated to protocol version 2024-11-05")
        else:
            print(f"  ⚠️  Failed to update protocol version")
    else:
        print(f"\n{filename}: No protocol version found")

print("\nDone!")