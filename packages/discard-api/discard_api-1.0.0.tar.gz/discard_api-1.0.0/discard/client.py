"""
discard/client.py - Core client for Discard API
"""

import requests
from typing import Dict, Any, Optional, Union
import json


class APIResponse:
    """Standard API response structure"""

    def __init__(self, data: Dict[str, Any]):
        self.creator = data.get("creator")
        self.result = data.get("result")
        self.status = data.get("status")
        self._raw = data

    def __repr__(self):
        return f"APIResponse(status={self.status}, creator={self.creator})"


class DiscardClient:
    """Main client for Discard API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://discardapi.dpdns.org",
        full_response: bool = False,
        timeout: int = 30,
    ):
        """
        Initialize Discard API client

        Args:
            api_key: Your API key
            base_url: Base URL for API (default: https://discardapi.dpdns.org)
            full_response: Return full response or just result (default: False)
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.full_response = full_response
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Discard-Python-SDK/1.0.0"})

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build full URL with query parameters"""
        url = f"{self.base_url}{endpoint}"
        return url

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict, APIResponse]:
        """
        Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            files: Files to upload
            json_data: JSON data

        Returns:
            API response (dict or APIResponse object)
        """
        if params is None:
            params = {}

        # Add API key to params
        params["apikey"] = self.api_key

        url = self._build_url(endpoint, params)

        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method == "POST":
                if files:
                    if data is None:
                        data = {}
                    data["apikey"] = self.api_key
                    response = self.session.post(
                        url, data=data, files=files, timeout=self.timeout
                    )
                elif json_data:
                    response = self.session.post(
                        url, json=json_data, params=params, timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url, data=data, params=params, timeout=self.timeout
                    )
            elif method == "PUT":
                if json_data:
                    response = self.session.put(
                        url, json=json_data, params=params, timeout=self.timeout
                    )
                else:
                    response = self.session.put(
                        url, data=data, params=params, timeout=self.timeout
                    )
            elif method == "DELETE":
                if json_data:
                    response = self.session.delete(
                        url, json=json_data, params=params, timeout=self.timeout
                    )
                else:
                    response = self.session.delete(
                        url, data=data, params=params, timeout=self.timeout
                    )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Try to parse JSON response
            try:
                api_resp = response.json()

                if self.full_response:
                    return APIResponse(api_resp)

                # Return just the result if available
                if isinstance(api_resp, dict) and "result" in api_resp:
                    return api_resp["result"]

                return api_resp

            except ValueError:
                # Return raw text if not JSON
                return response.text

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def set_full_response(self, value: bool):
        """Set full response mode"""
        self.full_response = value

    def get_full_response(self) -> bool:
        """Get current full response mode"""
        return self.full_response

    def set_api_key(self, api_key: str):
        """Update API key"""
        self.api_key = api_key

    def set_timeout(self, timeout: int):
        """Update request timeout"""
        self.timeout = timeout

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
