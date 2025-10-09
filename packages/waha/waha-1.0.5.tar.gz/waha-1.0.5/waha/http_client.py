"""
HTTP Client implementation for WAHA

Provides both synchronous and asynchronous HTTP clients using httpx.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .exceptions import WahaAPIError, WahaTimeoutError, WahaAuthenticationError

logger = logging.getLogger(__name__)


class HTTPClient:
    """Base HTTP client for WAHA API requests."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            self.default_headers["X-Api-Key"] = f"{api_key}"

        if headers:
            self.default_headers.update(headers)

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return urljoin(self.base_url, endpoint)

    def _prepare_request_data(self, data: Any) -> Optional[str]:
        """Prepare request data for HTTP request."""
        if data is None:
            return None

        if isinstance(data, BaseModel):
            return data.model_dump_json(exclude_none=True)
        elif isinstance(data, dict):
            return json.dumps(data)
        elif isinstance(data, str):
            return data
        else:
            return json.dumps(data)

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP response errors."""
        if response.status_code == 401:
            raise WahaAuthenticationError("Authentication failed. Check your API key.")
        elif response.status_code == 404:
            raise WahaAPIError(
                f"Endpoint not found: {response.url}", response.status_code
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", f"HTTP {response.status_code}")
                details = error_data.get("details")
            except (json.JSONDecodeError, ValueError):
                message = f"HTTP {response.status_code}: {response.text}"
                details = None

            raise WahaAPIError(message, response.status_code, details)


class SyncHTTPClient(HTTPClient):
    """Synchronous HTTP client for WAHA API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.timeout),
                headers=self.default_headers,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request."""
        url = self._build_url(endpoint)
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        json_data = None
        content = None

        if data is not None:
            if isinstance(data, (dict, BaseModel)):
                json_data = (
                    data.model_dump(exclude_none=True)
                    if isinstance(data, BaseModel)
                    else data
                )
            else:
                content = self._prepare_request_data(data)
                request_headers["Content-Type"] = "application/json"

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                content=content,
                headers=request_headers,
            )

            self._handle_response_error(response)

            # Handle different response types
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                return response.json()
            elif "image/" in content_type:
                return {"content": response.content, "content_type": content_type}
            else:
                return {"text": response.text, "content_type": content_type}

        except httpx.TimeoutException:
            raise WahaTimeoutError(f"Request to {url} timed out after {self.timeout}s")
        except httpx.RequestError as e:
            raise WahaAPIError(f"Request failed: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make GET request."""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return self.request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)


class AsyncHTTPClient(HTTPClient):
    """Asynchronous HTTP client for WAHA API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=self.default_headers,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make async HTTP request."""
        url = self._build_url(endpoint)
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        json_data = None
        content = None

        if data is not None:
            if isinstance(data, (dict, BaseModel)):
                json_data = (
                    data.model_dump(exclude_none=True)
                    if isinstance(data, BaseModel)
                    else data
                )
            else:
                content = self._prepare_request_data(data)
                request_headers["Content-Type"] = "application/json"

        try:
            logger.debug(f"Making async {method} request to {url}")
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                content=content,
                headers=request_headers,
            )

            self._handle_response_error(response)

            # Handle different response types
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                return response.json()
            elif "image/" in content_type:
                return {"content": response.content, "content_type": content_type}
            else:
                return {"text": response.text, "content_type": content_type}

        except httpx.TimeoutException:
            raise WahaTimeoutError(f"Request to {url} timed out after {self.timeout}s")
        except httpx.RequestError as e:
            raise WahaAPIError(f"Request failed: {str(e)}")

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make async GET request."""
        return await self.request("GET", endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make async POST request."""
        return await self.request("POST", endpoint, data=data, **kwargs)

    async def put(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make async PUT request."""
        return await self.request("PUT", endpoint, data=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make async DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)
