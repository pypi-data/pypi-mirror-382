"""MCP tools for metrics endpoints."""

import json
from typing import List, Optional

from mcp.types import TextContent, Tool

from ..client import ConceptualAPIClient, ConceptualAPIError
from ..key_manager import APIKeyManager


async def get_account_metrics(
    start_date: str,
    end_date: str,
    advanced_mode: bool = False,
) -> List[TextContent]:
    """Get account-level performance metrics from Conceptual API.

    Rate limit: 60 requests per minute
    Google Ads only - provides campaign type breakdown
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_account_metrics_raw(
                start_date=start_date,
                end_date=end_date,
                advanced_mode=advanced_mode,
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
            error_msg += (
                "\nRate limit exceeded. Metrics endpoint allows 60 requests per minute."
            )
        elif e.status_code == 401:
            error_msg += (
                f"\nCheck the API key configuration for client: {active_client}"
            )
        elif e.status_code == 400 and "Google Ads" in e.message:
            error_msg += "\nCustomer may not have Google Ads configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_campaign_metrics(
    start_date: str,
    end_date: str,
    platform: str = "all",
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get campaign-level performance metrics from Conceptual API.

    Rate limit: 60 requests per minute
    Supports Google Ads, Meta, Bing Ads, and LinkedIn Ads platforms
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_campaign_metrics_raw(
                start_date=start_date,
                end_date=end_date,
                platform=platform,
                advanced_mode=advanced_mode,
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
            error_msg += (
                "\nRate limit exceeded. Metrics endpoint allows 60 requests per minute."
            )
        elif e.status_code == 401:
            error_msg += (
                f"\nCheck the API key configuration for client: {active_client}"
            )
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_budget_efficiency_metrics(
    start_date: str,
    end_date: str,
) -> List[TextContent]:
    """Get budget and efficiency checks from Conceptual API.

    Rate limit: 60 requests per minute
    Provides automated budget pacing and efficiency analysis
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_budget_efficiency_metrics_raw(
                start_date=start_date,
                end_date=end_date,
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
            error_msg += (
                "\nRate limit exceeded. Metrics endpoint allows 60 requests per minute."
            )
        elif e.status_code == 401:
            error_msg += (
                f"\nCheck the API key configuration for client: {active_client}"
            )
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_weekly_metrics(
    start_date: str,
    end_date: str,
    comparison_start_date: Optional[str] = None,
    comparison_end_date: Optional[str] = None,
    comparison_label: str = "vs. previous period",
    platform: str = "all",
    include_insights: bool = True,
    include_budget_pacing: bool = True,
) -> List[TextContent]:
    """Get weekly metrics report from Conceptual API.

    Rate limit: 60 requests per minute
    Comprehensive weekly marketing performance report identical to /slack endpoint
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_weekly_metrics_raw(
                start_date=start_date,
                end_date=end_date,
                comparison_start_date=comparison_start_date,
                comparison_end_date=comparison_end_date,
                comparison_label=comparison_label,
                platform=platform,
                include_insights=include_insights,
                include_budget_pacing=include_budget_pacing,
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
            error_msg += "\nRate limit exceeded. Weekly metrics endpoint allows 60 requests per minute."
        elif e.status_code == 401:
            error_msg += (
                f"\nCheck the API key configuration for client: {active_client}"
            )
        elif e.status_code == 400 and "platform" in e.message:
            error_msg += "\nCustomer may not have the required platform configured."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool definitions
METRICS_TOOLS = [
    Tool(
        name="get_account_metrics",
        description="""Get account-level performance metrics by campaign type (Google Ads only).
        
        Rate limit: 60 requests per minute
        Includes campaign type performance, cost analysis, conversion metrics, and comparison with previous period.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - advanced_mode: Include advanced metrics and analysis (default: false)""",
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
                "advanced_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include advanced metrics and analysis",
                },
            },
            "required": ["start_date", "end_date"],
        },
    ),
    Tool(
        name="get_campaign_metrics",
        description="""Get campaign-level performance metrics for Google Ads, Meta, Bing Ads, and/or LinkedIn Ads platforms.

        Rate limit: 60 requests per minute
        Includes individual campaign performance, cost analysis, and conversion metrics with sorting and pagination support.

        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - platform: google, meta, bing, linkedin, or all (default: all)
        - advanced_mode: Include advanced metrics and analysis (default: false)
        - limit: Max records to return (1-1000, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - sort_by: Field to sort by (cost, campaign_name, conversions, cac, roas)
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
                    "enum": ["google", "meta", "bing", "linkedin", "all"],
                    "default": "all",
                    "description": "Platform filter",
                },
                "advanced_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include advanced metrics and analysis",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
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
                    "enum": ["cost", "campaign_name", "conversions", "cac", "roas"],
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
        name="get_budget_efficiency_metrics",
        description="""Get automated budget and efficiency checks.
        
        Rate limit: 60 requests per minute
        Includes budget pacing analysis, efficiency metrics, and actionable recommendations.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)""",
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
            },
            "required": ["start_date", "end_date"],
        },
    ),
]
