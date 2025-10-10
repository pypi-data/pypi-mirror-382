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
Determine hardware compatibility and interoperability using the Juniper Networks
Hardware Compatiblity Tool. You can retrieve detailed hardware information for
Juniper products from the HCT.

These tools allow you to access the Hardware Compatibility Tool (HCT) API. A typical workflow is:

- Get the list of all categories
- Get the list of components in the categories your interested in.
- Confirm that the component name exists.
- Get the component details.
- Get the supported models and platforms.

Juniper groups things in the following way:

- Family (Routing, Switching, Security, etc.)
  - Series (MX Series, ACX Series, EX Series, etc.)
    - Platform (EX4000)
      - Models [components compatible with the parent platform] (i.e EX-SFP-... transcievers)

- Categories are horizontal groupings of models.  For example, some transcievers
(common optics) can be used across different product families.
"""

mcp = FastMCP(name="Juniper Hardware Compatibility Tool", instructions=INSTRUCTIONS)

URLS = {
    "categories": "https://apps.juniper.net/hct/allCategories",
    "category_components": "https://apps.juniper.net/hct/model/{category_key}",
    "component_details": "https://apps.juniper.net/hct/details?component={component_name}",
    "component_supported_platforms": "https://apps.juniper.net/hct/supportedPlatforms/{component_name}",
    "component_supported_models": "https://apps.juniper.net/hct/supportedModels/{component_name}",
    "platforms_grouped_by_family": "https://apps.juniper.net/hct/allPlatformsGroupByFamily",
    "platform_components": "https://apps.juniper.net/hct/modelsForProduct/{platform}",
    "platform_hardware_specification_detail": "https://apps.juniper.net/hardwaresrv/hct/specification-detail",
    "platform_information": "https://apps.juniper.net/hct/productInfo/{platform}",
}

VERIFY_SSL = False


class HctResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    response: Optional[dict[str, Any] | list[dict[str, Any]]] = None


@mcp.tool
def categories() -> HctResponse:
    """Get the list of all component categories."""
    response = requests.get(URLS["categories"], verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def category_components(category_key: int) -> HctResponse:
    """Get the list of all components in a category."""
    url = URLS["category_components"].format(category_key=category_key)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def component_details(component_name: str) -> HctResponse:
    """Get the details of a specific component."""
    url = URLS["component_details"].format(component_name=component_name)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def component_supported_platforms(component_name: str) -> HctResponse:
    """Get list of platforms on which a component is supported."""
    url = URLS["component_supported_platforms"].format(component_name=component_name)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def component_supported_models(component_name: str) -> HctResponse:
    """Get the list of models that support the component."""
    url = URLS["component_supported_models"].format(component_name=component_name)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def platforms_by_family() -> HctResponse:
    """Get the list of all platforms grouped by family."""
    url = URLS["platforms_grouped_by_family"].format()
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def components_for_platform(platform: str) -> HctResponse:
    """Get the list of models that support the component."""
    url = URLS["platform_components"].format(platform=platform)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def platform_hardware_details(platform: str) -> HctResponse:
    """Get the list of platforms that support the component."""
    url = URLS["platform_hardware_specification_detail"]
    payload = {"productName": platform}
    response = requests.post(url, json=payload, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )


@mcp.tool
def platform_information(platform: str) -> HctResponse:
    """Get the list of platforms that support the component."""
    url = URLS["platform_information"].format(platform=platform)
    response = requests.get(url, verify=VERIFY_SSL)
    if response.ok and len(response.content):
        return HctResponse(success=True, response=response.json())
    return HctResponse(
        success=False,
        error=response.text
        or "Empty response from API. Check that component names and category ids are correct.",
    )
