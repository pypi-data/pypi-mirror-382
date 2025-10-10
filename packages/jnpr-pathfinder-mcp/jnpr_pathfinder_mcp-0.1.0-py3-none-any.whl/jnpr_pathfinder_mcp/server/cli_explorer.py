import logging
from typing import Any, Optional

import requests
from fastmcp import FastMCP  # type: ignore
from pydantic import BaseModel

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/tmp/workspace.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

INSTRUCTIONS = """
Search for JUNOS CLI instructions, hierarchy, and commands.

Typical usage might be to search for a command and then retrieve
the topic page if found.

If unsure of specific topic name, get either topic reference or
hierarchy and browse.
"""

mcp = FastMCP(name="Juniper JUNOS Command Line Interface Explorer", instructions=INSTRUCTIONS)

URLS = {
    "search": "https://apps.juniper.net/softwaresrv/cli/search",
    "topic_reference": "https://apps.juniper.net/cli-explorer/_next/data/kIKlKSc6gfynXek-2p9Pm/reference.json",
    "topic_hierarchy": "https://apps.juniper.net/softwaresrv/cli/hierarchy",
}

VERIFY_SSL = False


class CliExplorerResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    response: Optional[dict[str, Any] | list[dict[str, Any]]] = None


@mcp.tool
def search(query: str, page_number: int = 1, page_size: int = 100) -> CliExplorerResponse:
    """Search for JUNOS CLI commands by keywords."""
    # POST {pageNumber: 1, pageSize: 20, searchQuery: "bgp show peers"}
    payload = {"searchQuery": query, "pageNumber": page_number, "pageSize": page_size}
    response = requests.post(URLS["search"], json=payload, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return CliExplorerResponse(success=True, response=response.json())
    return CliExplorerResponse(success=False, error=response.text or "Empty response from API.")


@mcp.tool
def topic_reference() -> CliExplorerResponse:
    """Get the full list of topics (top level cli commands)."""
    response = requests.get(URLS["topic_reference"], verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return CliExplorerResponse(success=True, response=response.json())
    return CliExplorerResponse(success=False, error=response.text or "Empty response from API.")


@mcp.tool
def topic_hierarchy() -> CliExplorerResponse:
    """Get the full topic (top level cli commands) hierarchy."""
    response = requests.post(URLS["topic_hierarchy"], json={}, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return CliExplorerResponse(success=True, response=response.json())
    return CliExplorerResponse(success=False, error=response.text or "Empty response from API.")
