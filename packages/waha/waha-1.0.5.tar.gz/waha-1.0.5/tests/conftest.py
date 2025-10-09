"""
Pytest configuration and fixtures for WAHA tests.
"""

import pytest
from unittest.mock import Mock
from waha import WahaClient, AsyncWahaClient
from waha.http_client import SyncHTTPClient, AsyncHTTPClient


@pytest.fixture
def mock_sync_http_client():
    """Mock synchronous HTTP client for testing."""
    return Mock(spec=SyncHTTPClient)


@pytest.fixture
def mock_async_http_client():
    """Mock asynchronous HTTP client for testing."""
    return Mock(spec=AsyncHTTPClient)


@pytest.fixture
def sync_client(mock_sync_http_client):
    """Create a WahaClient instance with mocked HTTP client."""
    client = WahaClient(base_url="http://localhost:3000", api_key="test-key")
    client._http_client = mock_sync_http_client
    return client


@pytest.fixture
def async_client(mock_async_http_client):
    """Create an AsyncWahaClient instance with mocked HTTP client."""
    client = AsyncWahaClient(base_url="http://localhost:3000", api_key="test-key")
    client._http_client = mock_async_http_client
    return client


@pytest.fixture
def sample_session_info():
    """Sample session information for testing."""
    return {
        "name": "default",
        "status": "WORKING",
        "config": {"debug": False},
        "me": {"id": "1234567890@c.us", "pushName": "Test User"},
        "engine": "WEBJS",
    }


@pytest.fixture
def sample_message():
    """Sample WhatsApp message for testing."""
    return {
        "id": "message_123",
        "timestamp": 1640995200,
        "from": {"id": "1234567890@c.us", "name": "Test User"},
        "fromMe": False,
        "body": "Hello, World!",
        "type": "text",
        "ack": "READ",
        "chatId": "1234567890@c.us",
        "hasMedia": False,
    }


@pytest.fixture
def sample_chat():
    """Sample WhatsApp chat for testing."""
    return {
        "id": "1234567890@c.us",
        "name": "Test Chat",
        "isGroup": False,
        "timestamp": 1640995200,
        "unreadCount": 0,
        "archived": False,
        "pinned": False,
        "isMuted": False,
    }
