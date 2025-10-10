from typing import Optional

from fastmcp import FastMCP  # type: ignore

from jnpr_pathfinder_mcp.server.cli_explorer import mcp as cli_explorer_mcp
from jnpr_pathfinder_mcp.server.feature_explorer import mcp as feature_explorer_mcp
from jnpr_pathfinder_mcp.server.hct import mcp as hct_mcp

# Create the MCP instance and expose tools
mcp = FastMCP("jnpr_pathfinder_mcp")


def run(transport: str = "stdio", host: Optional[str] = None, port: Optional[int] = None) -> None:
    """
    Run the FastMCP server.

    Allowed transports: 'stdio', 'http'
    When transport == 'stdio', host and port MUST NOT be provided.
    When transport == 'http', host and/or port may be provided (port should be int).
    """
    transport = transport.lower()
    if transport not in ("stdio", "http"):
        raise ValueError("transport must be 'stdio' or 'http'")

    if transport == "stdio":
        if host is not None or port is not None:
            raise ValueError("host/port cannot be used with stdio transport")
        mcp.run(transport="stdio")
        return

    # http transport
    kwargs = {"transport": "http"}
    if host:
        kwargs["host"] = host
    if port is not None:
        kwargs["port"] = int(port)

    mcp.mount(hct_mcp, prefix="juniper_hardware_compatibility_tool")
    mcp.mount(cli_explorer_mcp, prefix="juniper_cli_explorer")
    mcp.mount(feature_explorer_mcp, prefix="juniper_feature_explorer")

    mcp.run(**kwargs)
