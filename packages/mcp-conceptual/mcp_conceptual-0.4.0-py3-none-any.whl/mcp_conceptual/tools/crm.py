"""CRM tools for Conceptual API."""

import json
from typing import List

from mcp.types import TextContent

from ..client import ConceptualAPIClient, ConceptualAPIError


async def get_crm_contacts(
    search: str = None,
    sort_by: str = None, 
    per_page: int = 50,
) -> List[TextContent]:
    """Get CRM contacts list with search/sort functionality.
    
    Uses raw data pass-through from CrmContactsComponent.
    
    Args:
        search: Search term to filter contacts (email, name, company)
        sort_by: Field to sort contacts by
        per_page: Records per page (1-500, default 50)
    
    Returns:
        List containing formatted response text
    """
    try:
        async with ConceptualAPIClient() as client:
            data = await client.get_crm_contacts_raw(
                search=search,
                sort_by=sort_by,
                per_page=per_page,
            )
            
            # Format the response for better readability
            formatted_response = {
                "message": data.get("message", "CRM contacts retrieved successfully"),
                "contacts": data.get("data", []),
                "component_state": data.get("component_state", {}),
                "metadata": data.get("meta", {}),
                "total_contacts": data.get("meta", {}).get("total_contacts", 0)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_response, indent=2, ensure_ascii=False)
            )]
            
    except ConceptualAPIError as e:
        error_response = {
            "error": str(e),
            "status_code": e.status_code,
            "error_type": e.error_type
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]


async def get_crm_contact(contact_id: int) -> List[TextContent]:
    """Get single contact with attribution history.
    
    Uses raw data pass-through from CrmContactsComponent and AttributionComponent.
    
    Args:
        contact_id: Contact ID to retrieve
    
    Returns:
        List containing formatted response text
    """
    try:
        async with ConceptualAPIClient() as client:
            data = await client.get_crm_contact_raw(contact_id)
            
            # Format the response for better readability
            formatted_response = {
                "message": data.get("message", "Contact retrieved successfully"),
                "contact": data.get("data", {}),
                "attribution_history": data.get("attribution_history", {}),
                "metadata": data.get("meta", {})
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_response, indent=2, ensure_ascii=False)
            )]
            
    except ConceptualAPIError as e:
        error_response = {
            "error": str(e),
            "status_code": e.status_code,
            "error_type": e.error_type
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]


async def get_crm_attribution_logs(
    search: str = None,
    sort_by: str = None,
    per_page: int = 200,
) -> List[TextContent]:
    """Get attribution logs with search/sort functionality.
    
    Uses raw data pass-through from AttributionComponent.
    
    Args:
        search: Search term to filter attribution logs
        sort_by: Field to sort attribution logs by
        per_page: Records per page (1-500, default 200)
    
    Returns:
        List containing formatted response text
    """
    try:
        async with ConceptualAPIClient() as client:
            data = await client.get_crm_attribution_logs_raw(
                search=search,
                sort_by=sort_by,
                per_page=per_page,
            )
            
            # Format the response for better readability
            formatted_response = {
                "message": data.get("message", "Attribution logs retrieved successfully"),
                "attribution_logs": data.get("data", {}),
                "component_state": data.get("component_state", {}),
                "metadata": data.get("meta", {})
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_response, indent=2, ensure_ascii=False)
            )]
            
    except ConceptualAPIError as e:
        error_response = {
            "error": str(e),
            "status_code": e.status_code,
            "error_type": e.error_type
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]


async def get_crm_analytics() -> List[TextContent]:
    """Get comprehensive CRM analytics.
    
    Uses raw data pass-through from both CrmContactsComponent and AttributionComponent.
    
    Returns:
        List containing formatted response text
    """
    try:
        async with ConceptualAPIClient() as client:
            data = await client.get_crm_analytics_raw()
            
            # Format the response for better readability
            formatted_response = {
                "message": data.get("message", "CRM analytics retrieved successfully"),
                "analytics_data": data.get("data", {}),
                "component_states": data.get("component_states", {}),
                "metadata": data.get("meta", {})
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_response, indent=2, ensure_ascii=False)
            )]
            
    except ConceptualAPIError as e:
        error_response = {
            "error": str(e),
            "status_code": e.status_code,
            "error_type": e.error_type
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]


async def export_crm_contacts(search: str = None) -> List[TextContent]:
    """Export contacts as CSV.
    
    Args:
        search: Search term to filter exported contacts
    
    Returns:
        List containing export information and CSV download details
    """
    try:
        async with ConceptualAPIClient() as client:
            data = await client.export_crm_contacts_raw(search=search)
            
            # Format the response for CSV export information
            formatted_response = {
                "message": data.get("message", "CSV export initiated successfully"),
                "export_info": data.get("data", {}),
                "metadata": data.get("meta", {}),
                "note": "This endpoint provides export information. The actual CSV download would be handled by the browser or HTTP client."
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(formatted_response, indent=2, ensure_ascii=False)
            )]
            
    except ConceptualAPIError as e:
        error_response = {
            "error": str(e),
            "status_code": e.status_code,
            "error_type": e.error_type
        }
        return [TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]