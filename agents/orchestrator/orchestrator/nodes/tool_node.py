from langchain_mcp_adapters.client import MultiServerMCPClient
import os
from .auth import Auth
import asyncio

async def get_tools_function():
    mcp_server_url = os.getenv("MCP_SERVER_URL")
    auth = Auth()
    client = MultiServerMCPClient({
        "my-server": {
            "transport": "http",
            "url": mcp_server_url,
            "auth": auth
        }

    })

    tools = await client.get_tools()
    return tools

