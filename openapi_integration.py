"""
openapi_integration.py

Provides OpenAPI client functionality for Director-AI.
Allows dynamic retrieval of URLs and metadata from OpenAPI endpoints.
"""

import requests
from typing import Any, Dict, Optional

class OpenAPIClient:
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_urls(self, endpoint: str, params: Optional[Dict[str, Any]] = None, url_key: str = "url") -> list:
        data = self.get(endpoint, params)
        # Assumes the response is a list of dicts with a key containing the URL
        return [item[url_key] for item in data if url_key in item]

# Example usage:
# client = OpenAPIClient("https://api.example.com/v1/", auth_token="your_token")
# urls = client.fetch_urls("/websites", url_key="website_url")
