"""HTTP client abstraction for raven-py.

Wraps synchronous HTTP requests with headers and base URL handling.
"""

from typing import Any, Dict, Optional
import requests


class HttpClient:
    """Thin HTTP client for performing JSON requests with base URL and headers."""

    def __init__(self, base_url: str, api_key: str, timeout: Optional[float] = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"X-API-Key": api_key}

    def _join(self, path: str) -> str:
        """Joins the base URL and a relative path."""

        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a POST request and returns a decoded JSON body."""

        url = self._join(path)
        resp = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
        return resp.json()

    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs a GET request and returns a decoded JSON body."""

        url = self._join(path)
        resp = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        return resp.json()