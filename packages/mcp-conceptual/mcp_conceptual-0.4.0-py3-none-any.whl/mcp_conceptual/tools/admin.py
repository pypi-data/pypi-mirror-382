"""MCP tools for admin endpoints."""

import json
from typing import List, Optional

from mcp.types import TextContent, Tool

from ..client import ConceptualAPIClient, ConceptualAPIError


async def list_client_api_keys(
    username: str,
    password: str,
) -> List[TextContent]:
    """List all client API keys from admin endpoint.
    
    Rate limit: 5 requests per minute
    Requires admin authentication
    """
    try:
        async with ConceptualAPIClient() as client:
            response = await client.list_client_api_keys_raw(
                username=username,
                password=password,
            )
            
            # Return raw JSON response for processing
            return [TextContent(type="text", text=json.dumps(response, indent=2))]
            
    except ConceptualAPIError as e:
        error_msg = f"Admin API Error: {e.message}"
        if e.status_code == 429:
            error_msg += "\nRate limit exceeded. Admin endpoint allows 5 requests per minute."
        elif e.status_code == 401:
            error_msg += "\nAuthentication failed. Check admin credentials or privileges."
        elif e.status_code == 400:
            error_msg += "\nInvalid request parameters."
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool definitions
ADMIN_TOOLS = [
    Tool(
        name="list_client_api_keys",
        description="""List all client API keys (admin only).
        
        Rate limit: 5 requests per minute
        Retrieves all active client API keys for admin users. Returns comprehensive client information 
        including all API keys (secret, CRM, attribution) and platform integration details.
        
        Security Requirements:
        - Valid admin user credentials (username/password)
        - User must have is_admin = true privilege
        - All access attempts are logged
        
        Parameters:
        - username: Admin user email address
        - password: Admin user password""",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "format": "email",
                    "minLength": 5,
                    "maxLength": 255,
                    "description": "Admin user email address"
                },
                "password": {
                    "type": "string",
                    "minLength": 8,
                    "maxLength": 255,
                    "description": "Admin user password"
                }
            },
            "required": ["username", "password"]
        }
    )
]