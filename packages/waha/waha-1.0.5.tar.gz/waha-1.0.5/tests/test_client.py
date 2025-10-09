"""
Tests for the main WAHA client classes.
"""

import pytest
from unittest.mock import Mock, patch
from waha import WahaClient, AsyncWahaClient
from waha.namespaces.auth import AuthNamespace, AsyncAuthNamespace
from waha.namespaces.sessions import SessionsNamespace, AsyncSessionsNamespace
from waha.namespaces.messages import MessagesNamespace, AsyncMessagesNamespace


class TestWahaClient:
    """Tests for the synchronous WahaClient."""

    def test_client_initialization(self):
        """Test client initialization with different parameters."""
        client = WahaClient(
            base_url="http://localhost:3000",
            api_key="test-key",
            timeout=60.0,
            headers={"Custom-Header": "value"},
        )

        assert client._http_client.base_url == "http://localhost:3000"
        assert client._http_client.api_key == "test-key"
        assert client._http_client.timeout == 60.0
        assert "Custom-Header" in client._http_client.default_headers

    def test_client_initialization_with_env_var(self):
        """Test client initialization using environment variables."""
        with patch.dict("os.environ", {"WAHA_API_KEY": "env-key"}):
            client = WahaClient(base_url="http://localhost:3000")
            assert client._http_client.api_key == "env-key"

    def test_client_namespaces(self):
        """Test that all namespaces are properly initialized."""
        client = WahaClient(base_url="http://localhost:3000")

        assert isinstance(client.auth, AuthNamespace)
        assert isinstance(client.sessions, SessionsNamespace)
        assert isinstance(client.messages, MessagesNamespace)
        assert hasattr(client, "chats")
        assert hasattr(client, "contacts")
        assert hasattr(client, "profile")
        assert hasattr(client, "groups")
        assert hasattr(client, "labels")
        assert hasattr(client, "status")
        assert hasattr(client, "channels")
        assert hasattr(client, "media")
        assert hasattr(client, "presence")

    def test_client_close(self):
        """Test client cleanup."""
        client = WahaClient(base_url="http://localhost:3000")
        client._http_client.close = Mock()

        client.close()
        client._http_client.close.assert_called_once()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with patch.object(WahaClient, "close") as mock_close:
            with WahaClient(base_url="http://localhost:3000") as client:
                assert isinstance(client, WahaClient)
            mock_close.assert_called_once()


class TestAsyncWahaClient:
    """Tests for the asynchronous AsyncWahaClient."""

    def test_async_client_initialization(self):
        """Test async client initialization."""
        client = AsyncWahaClient(base_url="http://localhost:3000", api_key="test-key")

        assert client._http_client.base_url == "http://localhost:3000"
        assert client._http_client.api_key == "test-key"

    def test_async_client_namespaces(self):
        """Test that all async namespaces are properly initialized."""
        client = AsyncWahaClient(base_url="http://localhost:3000")

        assert isinstance(client.auth, AsyncAuthNamespace)
        assert isinstance(client.sessions, AsyncSessionsNamespace)
        assert isinstance(client.messages, AsyncMessagesNamespace)
        assert hasattr(client, "chats")
        assert hasattr(client, "contacts")
        assert hasattr(client, "profile")

    @pytest.mark.asyncio
    async def test_async_client_close(self):
        """Test async client cleanup."""
        client = AsyncWahaClient(base_url="http://localhost:3000")
        client._http_client.close = Mock()

        await client.close()
        client._http_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test async client as context manager."""
        with patch.object(AsyncWahaClient, "close") as mock_close:
            async with AsyncWahaClient(base_url="http://localhost:3000") as client:
                assert isinstance(client, AsyncWahaClient)
            mock_close.assert_called_once()
