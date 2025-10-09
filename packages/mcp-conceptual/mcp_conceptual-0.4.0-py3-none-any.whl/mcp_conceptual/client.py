"""API client for Conceptual Keywords & Creative Performance API."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from .key_manager import APIKeyManager


class ConceptualAPIError(Exception):
    """Base exception for Conceptual API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_type: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(message)


class ConceptualAPIClient:
    """Client for the Conceptual Keywords & Creative Performance API."""

    def __init__(self, base_url: Optional[str] = None):
        # Get current active key from global key manager
        self.key_manager = APIKeyManager()
        self.api_key = self.key_manager.get_current_key()

        self.base_url = base_url or os.getenv(
            "CONCEPTUAL_BASE_URL", "https://api.conceptualhq.com/api"
        )
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                600.0, connect=300.0
            )  # 10 minutes total, 5 minutes connect
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an API endpoint."""
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"

    def _add_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API key to request parameters."""
        params = params.copy()
        params["api_key"] = self.api_key
        return params

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request and handle errors."""
        url = self._build_url(endpoint)
        params = self._add_api_key(params or {})

        try:
            response = await self.client.request(method, url, params=params, json=json)
            response_data = response.json()

            if response.status_code >= 400:
                error_msg = response_data.get("message", f"HTTP {response.status_code}")
                error_type = response_data.get("error", "Unknown Error")
                raise ConceptualAPIError(error_msg, response.status_code, error_type)

            return response_data

        except httpx.RequestError as e:
            raise ConceptualAPIError(f"Request failed: {e}")
        except (KeyError, ValueError) as e:
            raise ConceptualAPIError(f"Invalid response format: {e}")

    async def get_keyword_performance_raw(
        self,
        start_date: str,
        end_date: str,
        view_type: str = "keywords",
        advanced_mode: bool = False,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get keyword performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "view_type": view_type,
            "advanced_mode": advanced_mode,
            "limit": limit,
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/keywords/performance", params)

    async def get_search_terms_performance_raw(
        self,
        start_date: str,
        end_date: str,
        advanced_mode: bool = False,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get search terms performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "advanced_mode": advanced_mode,
            "limit": limit,
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/keywords/search-terms", params)

    async def get_manual_keywords_info_raw(
        self, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Get manual keywords information as raw JSON."""
        params = {"start_date": start_date, "end_date": end_date}
        return await self._make_request("GET", "/keywords/manual", params)

    async def get_campaign_content_info_raw(
        self, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """Get campaign content information as raw JSON."""
        params = {"start_date": start_date, "end_date": end_date}
        return await self._make_request("GET", "/keywords/campaign-content", params)

    async def get_meta_creative_performance_raw(
        self,
        start_date: str,
        end_date: str,
        platform: str = "all",
        status: str = "all",
        limit: int = 100,
        offset: int = 0,
        include_images: bool = True,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get Meta creative performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "platform": platform,
            "status": status,
            "limit": min(limit, 500),  # API max is 500 for creatives
            "offset": offset,
            "include_images": include_images,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/creatives/meta", params)

    async def get_google_creative_performance_raw(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get Google Ads creative performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": min(limit, 500),  # API max is 500 for creatives
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/creatives/google", params)

    async def get_bing_creative_performance_raw(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get Bing Ads creative performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": min(limit, 10000),  # API max is 10000 for Bing creatives
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/creatives/bing", params)

    async def get_linkedin_creative_performance_raw(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get LinkedIn Display Ads creative performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": min(limit, 10000),  # API max is 10000 for LinkedIn creatives
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/creatives/linkedin", params)

    async def get_linkedin_message_creative_performance_raw(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get LinkedIn Message Ads creative performance data as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": min(limit, 10000),  # API max is 10000 for LinkedIn creatives
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/creatives/linkedin/message", params)

    async def get_creative_status_raw(self, creative_id: str) -> Dict[str, Any]:
        """Get creative status as raw JSON."""
        return await self._make_request("GET", f"/creatives/{creative_id}/status")

    async def update_creative_status_raw(
        self, creative_id: str, status: str
    ) -> Dict[str, Any]:
        """Update creative status and return raw JSON."""
        json_data = {"status": status}
        return await self._make_request(
            "PUT", f"/creatives/{creative_id}/status", json=json_data
        )

    async def get_account_metrics_raw(
        self,
        start_date: str,
        end_date: str,
        advanced_mode: bool = False,
    ) -> Dict[str, Any]:
        """Get account-level performance metrics as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "advanced_mode": advanced_mode,
        }
        return await self._make_request("GET", "/metrics/account", params)

    async def get_campaign_metrics_raw(
        self,
        start_date: str,
        end_date: str,
        platform: str = "all",
        advanced_mode: bool = False,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Get campaign-level performance metrics as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "platform": platform,
            "advanced_mode": advanced_mode,
            "limit": limit,
            "offset": offset,
            "sort_direction": sort_direction,
        }
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/metrics/campaigns", params)

    async def get_budget_efficiency_metrics_raw(
        self,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """Get budget and efficiency checks as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return await self._make_request("GET", "/metrics/budget-efficiency", params)

    async def get_crm_contacts_raw(
        self,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """Get CRM contacts list as raw JSON."""
        params = {"per_page": min(per_page, 500)}
        if search:
            params["search"] = search
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/crm/contacts", params)

    async def get_crm_contact_raw(self, contact_id: int) -> Dict[str, Any]:
        """Get single CRM contact with attribution history as raw JSON."""
        return await self._make_request("GET", f"/crm/contacts/{contact_id}")

    async def get_crm_attribution_logs_raw(
        self,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        per_page: int = 200,
    ) -> Dict[str, Any]:
        """Get CRM attribution logs as raw JSON."""
        params = {"per_page": min(per_page, 500)}
        if search:
            params["search"] = search
        if sort_by:
            params["sort_by"] = sort_by

        return await self._make_request("GET", "/crm/attribution", params)

    async def get_crm_analytics_raw(self) -> Dict[str, Any]:
        """Get comprehensive CRM analytics as raw JSON."""
        return await self._make_request("GET", "/crm/analytics")

    async def export_crm_contacts_raw(
        self, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export CRM contacts as CSV (returns response info, not actual CSV)."""
        params = {}
        if search:
            params["search"] = search

        return await self._make_request("GET", "/crm/export", params)

    async def get_weekly_metrics_raw(
        self,
        start_date: str,
        end_date: str,
        comparison_start_date: Optional[str] = None,
        comparison_end_date: Optional[str] = None,
        comparison_label: str = "vs. previous period",
        platform: str = "all",
        include_insights: bool = True,
        include_budget_pacing: bool = True,
    ) -> Dict[str, Any]:
        """Get weekly metrics report as raw JSON."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "comparison_label": comparison_label,
            "platform": platform,
            "include_insights": include_insights,
            "include_budget_pacing": include_budget_pacing,
        }
        if comparison_start_date:
            params["comparison_start_date"] = comparison_start_date
        if comparison_end_date:
            params["comparison_end_date"] = comparison_end_date

        return await self._make_request("GET", "/weekly-metrics", params)

    async def list_client_api_keys_raw(
        self,
        username: str,
        password: str,
    ) -> Dict[str, Any]:
        """List all client API keys using admin credentials."""
        # For admin endpoint, we don't use the standard API key
        # Instead, we pass username and password
        params = {
            "username": username,
            "password": password,
        }

        # Make request without adding the standard API key
        url = self._build_url("/list_client_api_keys")

        try:
            response = await self.client.request("GET", url, params=params)
            response_data = response.json()

            if response.status_code >= 400:
                error_msg = response_data.get("message", f"HTTP {response.status_code}")
                error_type = response_data.get("error", "Unknown Error")
                raise ConceptualAPIError(error_msg, response.status_code, error_type)

            return response_data

        except httpx.RequestError as e:
            raise ConceptualAPIError(f"Request failed: {e}")
        except (KeyError, ValueError) as e:
            raise ConceptualAPIError(f"Invalid response format: {e}")
