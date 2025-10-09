"""API Key Manager for single and multi-client configurations."""

import os
import sys
from typing import Dict, List, Optional


class APIKeyManager:
    """Manages API keys and active client state."""

    _instance = None
    _active_client: Optional[str] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIKeyManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Admin credentials for fetching client keys
        self.admin_username = os.getenv("CONCEPTUAL_ADMIN_USERNAME")
        self.admin_password = os.getenv("CONCEPTUAL_ADMIN_PASSWORD")

        # Primary single key (backward compatibility)
        self.default_key = os.getenv("CONCEPTUAL_API_KEY")

        # Multi-client keys from environment (backward compatibility)
        client_keys_string = os.getenv("CONCEPTUAL_CLIENT_API_KEYS")
        self.client_keys = {}

        # If admin credentials are provided, fetch keys from API
        if self.admin_username and self.admin_password:
            # Fetch keys from admin API
            self.client_keys = self._fetch_client_keys_from_api()
        elif client_keys_string:
            # Fall back to environment variable approach
            self.client_keys = self._parse_client_keys(client_keys_string)

        # Validation
        if not self.default_key and not self.client_keys:
            raise ValueError(
                "Either CONCEPTUAL_API_KEY, CONCEPTUAL_CLIENT_API_KEYS, or admin credentials must be set"
            )

        self._initialized = True

    def _parse_client_keys(self, keys_string: str) -> Dict[str, str]:
        """Parse client API keys string into client->key mapping."""
        keys = {}
        pairs = keys_string.split(",")

        for pair in pairs:
            pair = pair.strip()
            if ":" not in pair:
                raise ValueError(
                    f"Invalid client key format: '{pair}'. Expected 'ClientName:key'"
                )

            client_name, api_key = pair.split(":", 1)
            client_name = client_name.strip()
            api_key = api_key.strip()

            if not client_name or not api_key:
                raise ValueError(
                    f"Invalid client key format: '{pair}'. Both client name and key required"
                )

            keys[client_name] = api_key

        return keys

    def set_active_client(self, client_name: str) -> str:
        """Set the active client for subsequent API calls."""
        if client_name not in self.client_keys:
            available = (
                ", ".join(self.client_keys.keys()) if self.client_keys else "None"
            )
            raise ValueError(
                f"Client '{client_name}' not found. Available clients: {available}"
            )

        self._active_client = client_name
        return f"Active client set to: {client_name}"

    def clear_active_client(self) -> str:
        """Clear active client, reverting to default key."""
        if not self.default_key:
            raise ValueError(
                "Cannot clear active client: CONCEPTUAL_API_KEY not configured"
            )

        previous = self._active_client
        self._active_client = None
        return f"Cleared active client (was: {previous}). Using default key."

    def get_current_key(self) -> str:
        """Get the currently active API key."""
        if self._active_client:
            return self.client_keys[self._active_client]
        elif self.default_key:
            return self.default_key
        else:
            raise ValueError(
                "No active client set and CONCEPTUAL_API_KEY not configured"
            )

    def get_current_client_info(self) -> Dict[str, any]:
        """Get information about current active client."""
        return {
            "active_client": self._active_client,
            "using_default_key": self._active_client is None
            and self.default_key is not None,
            "available_clients": list(self.client_keys.keys()),
            "has_default_key": self.default_key is not None,
        }

    def list_available_clients(self) -> List[str]:
        """Return list of available client names."""
        return list(self.client_keys.keys())

    def has_multi_client_support(self) -> bool:
        """Check if multi-client keys are configured."""
        return len(self.client_keys) > 0

    def has_default_key(self) -> bool:
        """Check if default key is configured."""
        return self.default_key is not None

    def _fetch_client_keys_from_api(self) -> Dict[str, str]:
        """Fetch client API keys from admin API."""
        import httpx

        try:
            # Make direct HTTP request to avoid circular dependency
            base_url = os.getenv(
                "CONCEPTUAL_BASE_URL", "https://api.conceptualhq.com/api"
            )
            url = f"{base_url.rstrip('/')}/list_client_api_keys"

            # Create a synchronous client for this one-time request
            with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
                response = client.get(
                    url,
                    params={
                        "username": self.admin_username,
                        "password": self.admin_password,
                    },
                )

                if response.status_code >= 400:
                    print(
                        f"Failed to fetch client keys: HTTP {response.status_code}",
                        file=sys.stderr,
                    )
                    return {}

                response_data = response.json()

                # Parse response and extract client keys
                keys = {}
                if "data" in response_data and "clients" in response_data["data"]:
                    for client in response_data["data"]["clients"]:
                        client_name = client.get("name")
                        api_key = client.get("api_keys", {}).get("secret")

                        if client_name and api_key:
                            keys[client_name] = api_key

                if keys:
                    print(
                        f"Successfully fetched keys for {len(keys)} clients from admin API",
                        file=sys.stderr,
                    )

                return keys

        except Exception as e:
            print(
                f"Error fetching client keys from admin API: {str(e)}", file=sys.stderr
            )
            return {}
