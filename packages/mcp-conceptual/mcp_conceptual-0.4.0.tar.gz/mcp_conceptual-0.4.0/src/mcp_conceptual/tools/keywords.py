"""MCP tools for keywords endpoints."""

import json
from typing import Any, Dict, List, Optional

from mcp.types import TextContent, Tool

from ..client import ConceptualAPIClient, ConceptualAPIError
from ..key_manager import APIKeyManager


async def get_keyword_performance(
    start_date: str,
    end_date: str,
    view_type: str = "keywords",
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get keyword performance data from Conceptual API.
    
    Rate limit: 60 requests per minute
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_keyword_performance_raw(
                start_date=start_date,
                end_date=end_date,
                view_type=view_type,
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
            error_msg += "\nRate limit exceeded. Keywords endpoint allows 60 requests per minute."
        elif e.status_code == 401:
            error_msg += f"\nCheck the API key configuration for client: {active_client}"
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_search_terms_performance(
    start_date: str,
    end_date: str,
    advanced_mode: bool = False,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
) -> List[TextContent]:
    """Get search terms performance data from Conceptual API.
    
    Rate limit: 60 requests per minute
    Note: This endpoint may be slower due to large volume of search terms data.
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_search_terms_performance_raw(
                start_date=start_date,
                end_date=end_date,
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
            error_msg += "\nRate limit exceeded. Keywords endpoint allows 60 requests per minute."
        elif e.status_code == 504:
            error_msg += "\nQuery timeout - try reducing the date range or using pagination."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_manual_keywords_info(
    start_date: str,
    end_date: str,
) -> List[TextContent]:
    """Get manual keywords information from Conceptual API."""
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_manual_keywords_info_raw(
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
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_campaign_content_info(
    start_date: str,
    end_date: str,
) -> List[TextContent]:
    """Get campaign content information from Conceptual API."""
    try:
        async with ConceptualAPIClient() as client:
            response = await client.get_campaign_content_info_raw(
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
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool definitions
KEYWORD_TOOLS = [
    Tool(
        name="get_keyword_performance",
        description="""Get keyword performance data including cost, clicks, conversions, and CAC analysis.
        
        Rate limit: 60 requests per minute
        Data is cached for 120 minutes
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD) 
        - view_type: keywords, search_terms, manual, or campaign_content (default: keywords)
        - advanced_mode: Include advanced metrics (default: false)
        - limit: Max records to return (1-1000, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - sort_by: Field to sort by (cost, clicks, impressions, conversions, cac, ctr, cpc, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string", 
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format"
                },
                "view_type": {
                    "type": "string",
                    "enum": ["keywords", "search_terms", "manual", "campaign_content"],
                    "default": "keywords",
                    "description": "Type of keyword data to retrieve"
                },
                "advanced_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include advanced metrics and analysis"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 100,
                    "description": "Maximum number of records to return"
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["cost", "clicks", "impressions", "conversions", "cac", "ctr", "cpc", "conversion_rate"],
                    "description": "Field to sort results by"
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction"
                }
            },
            "required": ["start_date", "end_date"]
        }
    ),
    Tool(
        name="get_search_terms_performance",
        description="""Get search terms that triggered your ads with performance metrics.
        
        Rate limit: 60 requests per minute
        Note: May be slower due to large volume of search terms data
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - advanced_mode: Include advanced metrics (default: false)
        - limit: Max records to return (1-1000, default: 100)
        - offset: Records to skip for pagination (default: 0)
        - sort_by: Field to sort by (cost, clicks, impressions, conversions, cac, ctr, cpc, conversion_rate)
        - sort_direction: asc or desc (default: desc)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$", 
                    "description": "End date in YYYY-MM-DD format"
                },
                "advanced_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include advanced metrics and analysis"
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 100,
                    "description": "Maximum number of records to return"
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Number of records to skip for pagination"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["cost", "clicks", "impressions", "conversions", "cac", "ctr", "cpc", "conversion_rate"],
                    "description": "Field to sort results by"
                },
                "sort_direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                    "description": "Sort direction"
                }
            },
            "required": ["start_date", "end_date"]
        }
    ),
    Tool(
        name="get_manual_keywords_info",
        description="""Get information about manual keywords functionality.
        
        Manual keywords are used for campaign generation, not performance analysis.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["start_date", "end_date"]
        }
    ),
    Tool(
        name="get_campaign_content_info",
        description="""Get information about campaign content functionality.
        
        Campaign content is used for managing campaign templates and content.
        
        Parameters:
        - start_date: Start date (YYYY-MM-DD)  
        - end_date: End date (YYYY-MM-DD)""",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["start_date", "end_date"]
        }
    )
]