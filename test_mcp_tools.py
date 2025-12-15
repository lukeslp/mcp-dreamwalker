#!/usr/bin/env python3
"""Test MCP servers tools/list method"""

import json
import subprocess

servers = [
    ("unified_stdio", "dreamwalker-unified"),
    ("providers_stdio", "dreamwalker-providers"),
]

initialize_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
tools_list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

print("Testing MCP servers tools/list...\n")

for module, expected_name in servers:
    print(f"Testing {module}...")

    payload = "\n".join(
        json.dumps(request) for request in (initialize_request, tools_list_request)
    ) + "\n"

    try:
        result = subprocess.run(
            [
                "python3",
                "-m",
                f"dreamwalker_mcp.mcp.stdio_servers.{module}",
            ],
            input=payload,
            text=True,
            capture_output=True,
            timeout=5,
        )

        if not result.stdout.strip():
            print("  ❌ No output received")
            if result.stderr:
                print(f"     Error: {result.stderr[:200]}")
            print()
            continue

        json_responses = []
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                json_responses.append(json.loads(stripped))
            except json.JSONDecodeError:
                continue

        init_response = next((resp for resp in json_responses if resp.get("id") == 1), None)
        tools_response = next(
            (
                resp
                for resp in json_responses
                if resp.get("id") == 2
                and resp.get("result")
                and "tools" in resp["result"]
            ),
            None,
        )

        if init_response:
            server_name = (
                init_response.get("result", {})
                .get("serverInfo", {})
                .get("name", "Unknown")
            )
            if server_name == expected_name:
                print(f"  ✅ Server name: {server_name}")
            else:
                print(
                    "  ❌ Unexpected server name: "
                    f"{server_name} (expected {expected_name})"
                )
        else:
            print("  ⚠️ Initialize response missing")

        if tools_response:
            tools = tools_response["result"]["tools"]
            print(f"  ✅ Found {len(tools)} tools")
            for tool in tools[:3]:
                print(f"     - {tool['name']}")
            remaining = len(tools) - 3
            if remaining > 0:
                print(f"     ... and {remaining} more")
        else:
            print("  ❌ tools/list response not found")

    except subprocess.TimeoutExpired:
        print("  ❌ Timeout - server didn't respond")
    except Exception as exc:  # noqa: BLE001
        print(f"  ❌ Error: {exc}")

    print()

print("Test complete!")
