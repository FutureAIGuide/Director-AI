"""
security_manager.py

Provides Basic Auth support for Director-AI, with a note to scale to OAuth for advanced security needs.
"""

import requests
from typing import Optional, Dict, Any

class SecurityManager:
    def __init__(self, username: str, password: str):
        self.auth = (username, password)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.get(url, params=params, auth=self.auth, timeout=10)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.post(url, data=data, auth=self.auth, timeout=10)

# NOTE: For advanced security and access to third-party APIs, scale to OAuth using libraries like 'requests-oauthlib' or 'oauthlib'.
# Example usage:
# sec = SecurityManager('user', 'pass')
# response = sec.get('https://protected.example.com/api')
# print(response.json())
