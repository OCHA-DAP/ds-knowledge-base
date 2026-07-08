#!/usr/bin/env python3
"""Smoke-test a deployed KB MCP server over Streamable HTTP.

    python mcp_server/deploy/check_remote.py https://<host>/mcp

Connects exactly like a claude.ai custom connector does: opens the streamable-HTTP
transport, runs the MCP handshake, lists tools, and calls search_kb. If the endpoint
is behind auth, set MCP_BEARER to a valid token; without one you should get rejected
(which is the point — confirm unauth is blocked, then confirm auth works).
"""
from __future__ import annotations

import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(url: str) -> None:
    headers = {}
    token = os.environ.get("MCP_BEARER")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with streamablehttp_client(url, headers=headers or None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("connected:", url)
            print("tools:", [t.name for t in tools.tools])
            r = await session.call_tool("search_kb", {"query": "drought", "max_results": 2})
            print("search_kb('drought') ->", r.content[0].text.splitlines()[0])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check_remote.py https://<host>/mcp   (set MCP_BEARER for auth)")
    asyncio.run(main(sys.argv[1]))
