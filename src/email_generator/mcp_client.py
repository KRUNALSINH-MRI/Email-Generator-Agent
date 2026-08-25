import os

from dotenv import load_dotenv
from fastmcp import Client


load_dotenv()

MCP_SERVER_PATH = "mcp_server/server.py"


def get_mcp_client():
    """
    Create an MCP client.

    If MCP_SERVER_URL is configured, connect to the
    remote FastMCP HTTP server.

    Otherwise, use the local FastMCP server over stdio.
    """

    mcp_server_url = os.getenv("MCP_SERVER_URL")

    if mcp_server_url:
        # FastMCP HTTP transport serves at /mcp/ by default
        url = mcp_server_url.rstrip("/")
        if not url.endswith("/mcp"):
            url += "/mcp/"
        return Client(url)

    return Client(
        {
            "mcpServers": {
                "email_guidelines": {
                    "command": "uv",
                    "args": [
                        "run",
                        "python",
                        MCP_SERVER_PATH,
                    ],
                }
            }
        }
    )