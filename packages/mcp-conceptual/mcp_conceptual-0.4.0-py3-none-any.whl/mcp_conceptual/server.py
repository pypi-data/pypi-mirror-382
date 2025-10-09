"""MCP Server for Conceptual Keywords & Creative Performance API."""

import json
import os
import sys
from typing import Sequence

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .key_manager import APIKeyManager
from .tools.admin import list_client_api_keys
from .tools.creatives import (
    get_bing_creative_performance,
    get_creative_status,
    get_google_creative_performance,
    get_linkedin_creative_performance,
    get_linkedin_message_creative_performance,
    get_meta_creative_performance,
    update_creative_status,
)
from .tools.crm import (
    export_crm_contacts,
    get_crm_analytics,
    get_crm_attribution_logs,
    get_crm_contact,
    get_crm_contacts,
)
from .tools.keywords import (
    get_campaign_content_info,
    get_keyword_performance,
    get_manual_keywords_info,
    get_search_terms_performance,
)
from .tools.metrics import (
    get_account_metrics,
    get_budget_efficiency_metrics,
    get_campaign_metrics,
    get_weekly_metrics,
)

# Load environment variables
load_dotenv()

# Initialize and validate key manager
try:
    key_manager = APIKeyManager()
    print("✓ API key configuration loaded", file=sys.stderr)

    # Check if using admin API for keys
    if key_manager.admin_username and key_manager.admin_password:
        print(
            f"✓ Using admin API for client keys (username: {key_manager.admin_username})",
            file=sys.stderr,
        )

    if key_manager.has_multi_client_support():
        clients = key_manager.list_available_clients()
        print(
            f"✓ Multi-client support enabled for: {', '.join(clients)}", file=sys.stderr
        )
    if key_manager.has_default_key():
        print("✓ Default API key available", file=sys.stderr)
except ValueError as e:
    print(f"Error: {e}", file=sys.stderr)
    print("Please set one of the following:", file=sys.stderr)
    print("  - CONCEPTUAL_API_KEY (single client)", file=sys.stderr)
    print("  - CONCEPTUAL_CLIENT_API_KEYS (multi-client)", file=sys.stderr)
    print(
        "  - CONCEPTUAL_ADMIN_USERNAME and CONCEPTUAL_ADMIN_PASSWORD (fetch from API)",
        file=sys.stderr,
    )
    sys.exit(1)

# Create server instance
mcp = FastMCP("Conceptual API Server")


@mcp.tool()
async def get_keyword_performance_tool(
    start_date: str,
    end_date: str,
    view_type: str = "keywords",
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get keyword performance data including cost, clicks, conversions, and CAC analysis.

    Rate limit: 60 requests per minute
    Data is cached for 120 minutes

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        view_type: keywords, search_terms, manual, or campaign_content (default: keywords)
        advanced_mode: Include advanced metrics (default: false)
        limit: Max records to return (1-1000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (cost, clicks, impressions, conversions, cac, ctr, cpc, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_keyword_performance(
        start_date,
        end_date,
        view_type,
        advanced_mode,
        limit,
        offset,
        sort_by,
        sort_direction,
    )
    return result[0].text


@mcp.tool()
async def get_search_terms_performance_tool(
    start_date: str,
    end_date: str,
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get search terms that triggered your ads with performance metrics.

    Rate limit: 60 requests per minute
    Note: May be slower due to large volume of search terms data

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        advanced_mode: Include advanced metrics (default: false)
        limit: Max records to return (1-1000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (cost, clicks, impressions, conversions, cac, ctr, cpc, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_search_terms_performance(
        start_date, end_date, advanced_mode, limit, offset, sort_by, sort_direction
    )
    return result[0].text


@mcp.tool()
async def get_manual_keywords_info_tool(start_date: str, end_date: str) -> str:
    """Get information about manual keywords functionality.

    Manual keywords are used for campaign generation, not performance analysis.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    result = await get_manual_keywords_info(start_date, end_date)
    return result[0].text


@mcp.tool()
async def get_campaign_content_info_tool(start_date: str, end_date: str) -> str:
    """Get information about campaign content functionality.

    Campaign content is used for managing campaign templates and content.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    result = await get_campaign_content_info(start_date, end_date)
    return result[0].text


@mcp.tool()
async def get_meta_creative_performance_tool(
    start_date: str,
    end_date: str,
    platform: str = "all",
    status: str = "all",
    limit: int = 100,
    offset: int = 0,
    include_images: bool = True,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get Meta (Facebook/Instagram) creative performance data.

    Rate limit: 30 requests per minute
    Includes creative assets, performance metrics, and optimization insights.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        platform: meta, google, or all (default: all)
        status: active, paused, or all (default: all)
        limit: Max records to return (1-500, default: 100)
        offset: Records to skip for pagination (default: 0)
        include_images: Include creative image URLs (default: true)
        sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_meta_creative_performance(
        start_date,
        end_date,
        platform,
        status,
        limit,
        offset,
        include_images,
        sort_by,
        sort_direction,
    )
    return result[0].text


@mcp.tool()
async def get_google_creative_performance_tool(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get Google Ads creative performance data.

    Rate limit: 30 requests per minute
    Includes asset-level performance metrics and optimization insights.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Max records to return (1-500, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_google_creative_performance(
        start_date, end_date, limit, offset, sort_by, sort_direction
    )
    return result[0].text


@mcp.tool()
async def get_bing_creative_performance_tool(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get Bing Ads creative performance data.

    Rate limit: 30 requests per minute
    Includes campaign-level performance metrics with conversions and cost data.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Max records to return (1-10000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_bing_creative_performance(
        start_date, end_date, limit, offset, sort_by, sort_direction
    )
    return result[0].text


@mcp.tool()
async def get_linkedin_creative_performance_tool(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get LinkedIn Display Ads creative performance data.

    Rate limit: 30 requests per minute
    Includes LinkedIn Display Ads (Sponsored Content) performance metrics.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Max records to return (1-10000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_linkedin_creative_performance(
        start_date, end_date, limit, offset, sort_by, sort_direction
    )
    return result[0].text


@mcp.tool()
async def get_linkedin_message_creative_performance_tool(
    start_date: str,
    end_date: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get LinkedIn Message Ads creative performance data.

    Rate limit: 30 requests per minute
    Includes LinkedIn Message Ads (Sponsored InMail) performance metrics.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Max records to return (1-10000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (spend, impressions, clicks, conversions, cpm, cpc, ctr, conversion_rate)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_linkedin_message_creative_performance(
        start_date, end_date, limit, offset, sort_by, sort_direction
    )
    return result[0].text


@mcp.tool()
async def get_creative_status_tool(creative_id: str) -> str:
    """Get the current status of a specific creative/ad.

    Args:
        creative_id: Creative/Ad ID to check status for
    """
    result = await get_creative_status(creative_id)
    return result[0].text


@mcp.tool()
async def update_creative_status_tool(creative_id: str, status: str) -> str:
    """Update the status of a creative/ad (pause or activate).

    Rate limit: 10 requests per minute
    Requires Meta OAuth permissions for the customer account.

    Args:
        creative_id: Creative/Ad ID to update
        status: New status (ACTIVE, PAUSED, active, or paused - case insensitive)
    """
    result = await update_creative_status(creative_id, status)
    return result[0].text


@mcp.tool()
async def get_account_metrics_tool(
    start_date: str,
    end_date: str,
    advanced_mode: bool = False,
) -> str:
    """Get account-level performance metrics by campaign type (Google Ads only).

    Rate limit: 60 requests per minute
    Includes campaign type performance, cost analysis, conversion metrics, and comparison with previous period.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        advanced_mode: Include advanced metrics and analysis (default: false)
    """
    result = await get_account_metrics(start_date, end_date, advanced_mode)
    return result[0].text


@mcp.tool()
async def get_campaign_metrics_tool(
    start_date: str,
    end_date: str,
    platform: str = "all",
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = None,
    sort_direction: str = "desc",
) -> str:
    """Get campaign-level performance metrics for Google Ads, Meta, Bing Ads, and/or LinkedIn Ads platforms.

    Rate limit: 60 requests per minute
    Includes individual campaign performance, cost analysis, and conversion metrics with sorting and pagination support.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        platform: google, meta, bing, linkedin, or all (default: all)
        advanced_mode: Include advanced metrics and analysis (default: false)
        limit: Max records to return (1-1000, default: 100)
        offset: Records to skip for pagination (default: 0)
        sort_by: Field to sort by (cost, campaign_name, conversions, cac, roas)
        sort_direction: asc or desc (default: desc)
    """
    result = await get_campaign_metrics(
        start_date,
        end_date,
        platform,
        advanced_mode,
        limit,
        offset,
        sort_by,
        sort_direction,
    )
    return result[0].text


@mcp.tool()
async def get_budget_efficiency_metrics_tool(
    start_date: str,
    end_date: str,
) -> str:
    """Get automated budget and efficiency checks.

    Rate limit: 60 requests per minute
    Includes budget pacing analysis, efficiency metrics, and actionable recommendations.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    result = await get_budget_efficiency_metrics(start_date, end_date)
    return result[0].text


@mcp.tool()
async def get_weekly_metrics_tool(
    start_date: str,
    end_date: str,
    comparison_start_date: str = None,
    comparison_end_date: str = None,
    comparison_label: str = "vs. previous period",
    platform: str = "all",
    include_insights: bool = True,
    include_budget_pacing: bool = True,
) -> str:
    """Get comprehensive weekly marketing performance report.

    Rate limit: 60 requests per minute
    Identical to the /slack endpoint data - includes Google Ads and Meta performance metrics,
    AI-generated insights, budget pacing analysis, and dashboard links.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        comparison_start_date: Comparison period start date (YYYY-MM-DD). Auto-generated if not provided.
        comparison_end_date: Comparison period end date (YYYY-MM-DD). Auto-generated if not provided.
        comparison_label: Label for the comparison period (default: "vs. previous period")
        platform: Platform filter - google, meta, or all (default: all)
        include_insights: Include performance insights and analysis (default: true)
        include_budget_pacing: Include budget pacing analysis (default: true)
    """
    result = await get_weekly_metrics(
        start_date,
        end_date,
        comparison_start_date,
        comparison_end_date,
        comparison_label,
        platform,
        include_insights,
        include_budget_pacing,
    )
    return result[0].text


@mcp.tool()
async def set_active_client(client_name: str) -> str:
    """Set the active client for all subsequent API calls.

    After setting an active client, all other tools will use that client's API key
    until changed or cleared.

    Args:
        client_name: Name of the client to activate (from CONCEPTUAL_CLIENT_API_KEYS)
    """
    try:
        key_manager = APIKeyManager()
        result = key_manager.set_active_client(client_name)
        return result
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def clear_active_client() -> str:
    """Clear the active client and revert to using the default API key.

    After clearing, all tools will use the CONCEPTUAL_API_KEY.
    """
    try:
        key_manager = APIKeyManager()
        result = key_manager.clear_active_client()
        return result
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def get_current_client_info() -> str:
    """Get information about the currently active client and available options."""
    try:
        key_manager = APIKeyManager()
        info = key_manager.get_current_client_info()
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_available_clients() -> str:
    """List all available client configurations."""
    try:
        key_manager = APIKeyManager()

        response = {
            "available_clients": key_manager.list_available_clients(),
            "has_default_key": key_manager.has_default_key(),
            "current_active_client": key_manager._active_client,
            "usage": {
                "set_client": "Use set_active_client tool to switch to a specific client",
                "clear_client": "Use clear_active_client tool to revert to default key",
                "check_status": "Use get_current_client_info tool to see current state",
            },
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_crm_contacts_tool(
    search: str = None,
    sort_by: str = None,
    per_page: int = 50,
) -> str:
    """Get CRM contacts list with search and sort functionality.

    Rate limit: 60 requests per minute
    Uses raw data pass-through from CrmContactsComponent.

    Args:
        search: Search term to filter contacts (email, name, company)
        sort_by: Field to sort contacts by (handled by component)
        per_page: Records per page (1-500, default 50)
    """
    result = await get_crm_contacts(search, sort_by, per_page)
    return result[0].text


@mcp.tool()
async def get_crm_contact_tool(contact_id: int) -> str:
    """Get single contact with attribution history.

    Uses raw data pass-through from CrmContactsComponent and AttributionComponent.

    Args:
        contact_id: Contact ID to retrieve
    """
    result = await get_crm_contact(contact_id)
    return result[0].text


@mcp.tool()
async def get_crm_attribution_logs_tool(
    search: str = None,
    sort_by: str = None,
    per_page: int = 200,
) -> str:
    """Get attribution logs with search and sort functionality.

    Rate limit: 60 requests per minute
    Uses raw data pass-through from AttributionComponent.

    Args:
        search: Search term to filter attribution logs
        sort_by: Field to sort attribution logs by
        per_page: Records per page (1-500, default 200)
    """
    result = await get_crm_attribution_logs(search, sort_by, per_page)
    return result[0].text


@mcp.tool()
async def get_crm_analytics_tool() -> str:
    """Get comprehensive CRM analytics.

    Rate limit: 60 requests per minute
    Uses raw data pass-through from both CrmContactsComponent and AttributionComponent.
    Provides a complete CRM overview with contacts summary and attribution analysis.
    """
    result = await get_crm_analytics()
    return result[0].text


@mcp.tool()
async def export_crm_contacts_tool(search: str = None) -> str:
    """Export contacts as CSV.

    Rate limit: 10 requests per minute (lower due to resource intensity)
    Exports contacts data as CSV using CrmContactsComponent data.
    Applies search filters if provided and includes all contact fields.

    Args:
        search: Search term to filter exported contacts
    """
    result = await export_crm_contacts(search)
    return result[0].text


@mcp.tool()
async def list_client_api_keys_tool(username: str, password: str) -> str:
    """List all client API keys (admin only).

    Rate limit: 5 requests per minute
    Retrieves all active client API keys for admin users. Returns comprehensive client information
    including all API keys (secret, CRM, attribution) and platform integration details.

    Security Requirements:
    - Valid admin user credentials (username/password)
    - User must have is_admin = true privilege
    - All access attempts are logged

    Args:
        username: Admin user email address
        password: Admin user password
    """
    result = await list_client_api_keys(username, password)
    return result[0].text


def cli_main():
    """CLI entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    cli_main()
