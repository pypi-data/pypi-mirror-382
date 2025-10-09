"""
Tests for HTTP client functionality.
"""

import pytest
from unittest.mock import Mock, patch
import httpx
from waha.http_client import SyncHTTPClient, AsyncHTTPClient
from waha.exceptions import WahaAPIError, WahaTimeoutError, WahaAuthenticationError
from waha.types import BaseRequest


class TestSyncHTTPClient:
    """Tests for the synchronous HTTP client."""

    def test_client_initialization(self):
        """Test HTTP client initialization."""
        client = SyncHTTPClient(
            base_url="http://localhost:3000",
            api_key="test-key",
            timeout=30.0,
            headers={"Custom": "header"},
        )

        assert client.base_url == "http://localhost:3000"
        assert client.api_key == "test-key"
        assert client.timeout == 30.0
        assert "Authorization" in client.default_headers
        assert "Custom" in client.default_headers

    def test_build_url(self):
        """Test URL building."""
        client = SyncHTTPClient(base_url="http://localhost:3000")

        assert client._build_url("/api/test") == "http://localhost:3000/api/test"
        assert client._build_url("api/test") == "http://localhost:3000/api/test"

    def test_prepare_request_data(self):
        """Test request data preparation."""
        client = SyncHTTPClient(base_url="http://localhost:3000")

        # Test dict
        data = {"key": "value"}
        result = client._prepare_request_data(data)
        assert result == '{"key": "value"}'

        # Test None
        result = client._prepare_request_data(None)
        assert result is None

        # Test string
        result = client._prepare_request_data("raw string")
        assert result == "raw string"

    def test_handle_response_error_401(self):
        """Test handling 401 authentication errors."""
        client = SyncHTTPClient(base_url="http://localhost:3000")

        mock_response = Mock()
        mock_response.status_code = 401

        with pytest.raises(WahaAuthenticationError):
            client._handle_response_error(mock_response)

    def test_handle_response_error_404(self):
        """Test handling 404 not found errors."""
        client = SyncHTTPClient(base_url="http://localhost:3000")

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "http://localhost:3000/api/missing"

        with pytest.raises(WahaAPIError, match="Endpoint not found"):
            client._handle_response_error(mock_response)

    def test_handle_response_error_with_json(self):
        """Test handling errors with JSON response."""
        client = SyncHTTPClient(base_url="http://localhost:3000")

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Bad request",
            "details": "Invalid parameter",
        }

        with pytest.raises(WahaAPIError, match="Bad request"):
            client._handle_response_error(mock_response)

    @patch("httpx.Client")
    def test_successful_request(self, mock_httpx_client):
        """Test successful HTTP request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}

        # Setup mock client
        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        # Create HTTP client and make request
        client = SyncHTTPClient(base_url="http://localhost:3000")
        result = client.get("/api/test")

        assert result == {"success": True}
        mock_client_instance.request.assert_called_once()

    @patch("httpx.Client")
    def test_timeout_error(self, mock_httpx_client):
        """Test timeout error handling."""
        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = httpx.TimeoutException(
            "Request timed out"
        )
        mock_httpx_client.return_value = mock_client_instance

        client = SyncHTTPClient(base_url="http://localhost:3000", timeout=5.0)

        with pytest.raises(WahaTimeoutError):
            client.get("/api/test")


class TestAsyncHTTPClient:
    """Tests for the asynchronous HTTP client."""

    def test_async_client_initialization(self):
        """Test async HTTP client initialization."""
        client = AsyncHTTPClient(
            base_url="http://localhost:3000", api_key="test-key", timeout=30.0
        )

        assert client.base_url == "http://localhost:3000"
        assert client.api_key == "test-key"
        assert client.timeout == 30.0
        assert "Authorization" in client.default_headers

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_async_successful_request(self, mock_httpx_client):
        """Test successful async HTTP request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}

        # Setup mock client
        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        # Create HTTP client and make request
        client = AsyncHTTPClient(base_url="http://localhost:3000")
        result = await client.get("/api/test")

        assert result == {"success": True}
        mock_client_instance.request.assert_called_once()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_async_timeout_error(self, mock_httpx_client):
        """Test async timeout error handling."""
        mock_client_instance = Mock()
        mock_client_instance.request.side_effect = httpx.TimeoutException(
            "Request timed out"
        )
        mock_httpx_client.return_value = mock_client_instance

        client = AsyncHTTPClient(base_url="http://localhost:3000", timeout=5.0)

        with pytest.raises(WahaTimeoutError):
            await client.get("/api/test")
