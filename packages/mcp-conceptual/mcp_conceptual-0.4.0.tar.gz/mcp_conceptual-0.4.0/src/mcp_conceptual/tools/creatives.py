"""MCP tools for creatives endpoints."""

import json
from typing import List, Optional

from mcp.types import TextContent, Tool

from ..client import ConceptualAPIClient, ConceptualAPIError
from ..key_manager import APIKeyManager


async def get_meta_creative_performance(
    start_date: str,
    end_date: str,
    platform: str = "all",
    status: str = "all",
    limit: int = 100,
    offset: int = 0,
    include_images: bool = True,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get Meta creative performance data from Conceptual API.

    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_meta_creative_performance_raw(
                start_date=start_date,
                end_date=end_date,
                platform=platform,
                status=status,
                limit=limit,
                offset=offset,
                include_images=include_images,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "Meta" in e.message:
            error_msg += "\nCustomer may not have Meta advertising configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_google_creative_performance(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get Google Ads creative performance data from Conceptual API.

    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_google_creative_performance_raw(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "Google" in e.message:
            error_msg += "\nCustomer may not have Google Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_bing_creative_performance(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get Bing Ads creative performance data from Conceptual API.

    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_bing_creative_performance_raw(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "Bing" in e.message:
            error_msg += "\nCustomer may not have Bing Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_linkedin_creative_performance(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get LinkedIn Display Ads creative performance data from Conceptual API.

    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_linkedin_creative_performance_raw(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "LinkedIn" in e.message:
            error_msg += "\nCustomer may not have LinkedIn Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_linkedin_message_creative_performance(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get LinkedIn Message Ads creative performance data from Conceptual API.

    Rate limit: 30 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_linkedin_message_creative_performance_raw(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_direction=sort_direction,
            )

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Creatives endpoint allows 30 requests per minute."
        elif e.status_code == 400 and "LinkedIn" in e.message:
            error_msg += "\nCustomer may not have LinkedIn Message Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_creative_status(creative_id: str) -> List[TextContent]:
    """Get creative status from Conceptual API."""
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_creative_status_raw(creative_id)

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 404:
            error_msg = (
                f"Creative with ID '{creative_id}' not found (using {active_client})."
            )
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def update_creative_status(creative_id: str, status: str) -> List[TextContent]:
    """Update creative status in Conceptual API.

    Rate limit: 10 requests per minute
    Requires Meta OAuth permissions for the customer account.
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.update_creative_status_raw(creative_id, status)

            # Return raw JSON response for LLM processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

    except ConceptualAPIError as e:
        # Enhanced error handling with active client info
        key_manager = APIKeyManager()
        client_info = key_manager.get_current_client_info()
        active_client = client_info.get("active_client") or "default"

        error_msg = f"API Error ({active_client}): {e.message}"
        if e.status_code == 429:
            error_msg += (
                "\nRate limit exceeded. Status updates allow 10 requests per minute."
            )
        elif e.status_code == 400:
            error_msg += "\nCheck that the status value is valid (ACTIVE/PAUSED) and customer has proper configuration."
        elif e.status_code == 503:
            error_msg += "\nMeta API issues. Please try again later."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool definitions
CREATIVE_TOOLS = [
    Tool(
        name="get_meta_creative_performance",
        description="""Get Meta (Facebook/Instagram) creative performance data.
        
        Rate limit: 30 requests per minute
        Includes creative assets, performance metrics, and optimization insights.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - platform: meta, google, or all (default: all)
        - status: active, paused, or all (default: all)
        - limit: Max records to return (1-500, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - include_images: Include creative image URLs (default: true)
        - sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format",
                },
                "platform": {
                    "type": "string",
                    "enum": ["meta", "google", "all"],
                    "default": "all",
                    "description": "Platform filter",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "paused", "all"],
                    "default": "all",
                    "description": "Filter by creative status",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 100,
                    "description": "Maximum number of records to return",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination",
                },
                "include_images": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include creative image URLs in response",
                },
                "sort_by": {
                    "type": "string",
                    "enum": [
                        "spend",
                        "impressions",
                        "clicks",
                        "conversions",
                        "cpm",
                        "cpc",
                        "ctr",
                        "conversion_rate",
                    ],
                    "description": "Field to sort results by",
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction",
                },
            },
            "required": ["start_date", "end_date"],
        },
    ),
    Tool(
        name="get_google_creative_performance",
        description="""Get Google Ads creative (ad assets) performance data.
        
        Rate limit: 30 requests per minute
        Includes asset-level performance metrics and optimization insights.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - limit: Max records to return (1-500, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 100,
                    "description": "Maximum number of records to return",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination",
                },
                "sort_by": {
                    "type": "string",
                    "enum": [
                        "spend",
                        "impressions",
                        "clicks",
                        "conversions",
                        "cpm",
                        "cpc",
                        "ctr",
                        "conversion_rate",
                    ],
                    "description": "Field to sort results by",
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction",
                },
            },
            "required": ["start_date", "end_date"],
        },
    ),
    Tool(
        name="get_creative_status",
        description="""Get the current status of a specific creative/ad.
        
        Parameters:
        - creative_id: Creative/Ad ID""",
        inputSchema={
            "type": "object",
            "properties": {
                "creative_id": {
                    "type": "string",
                    "description": "Creative/Ad ID to check status for",
                }
            },
            "required": ["creative_id"],
        },
    ),
    Tool(
        name="update_creative_status",
        description="""Update the status of a creative/ad (pause or activate).
        
        Rate limit: 10 requests per minute
        Requires Meta OAuth permissions for the customer account.
        
        Parameters:
        - creative_id: Creative/Ad ID
        - status: New status (ACTIVE, PAUSED, active, or paused - case insensitive)""",
        inputSchema={
            "type": "object",
            "properties": {
                "creative_id": {
                    "type": "string",
                    "description": "Creative/Ad ID to update",
                },
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED", "active", "paused"],
                    "description": "New status for the creative (case insensitive)",
                },
            },
            "required": ["creative_id", "status"],
        },
    ),
]
