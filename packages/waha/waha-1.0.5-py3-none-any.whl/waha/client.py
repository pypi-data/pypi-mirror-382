"""
Main client for WAHA

Provides the primary interface for interacting with the WAHA API.
"""

import os
from typing import Optional, Dict, Any

from .http_client import SyncHTTPClient, AsyncHTTPClient
from .namespaces.auth import AuthNamespace, AsyncAuthNamespace
from .namespaces.sessions import SessionsNamespace, AsyncSessionsNamespace
from .namespaces.messages import MessagesNamespace, AsyncMessagesNamespace
from .namespaces.chats import ChatsNamespace, AsyncChatsNamespace
from .namespaces.contacts import ContactsNamespace, AsyncContactsNamespace
from .namespaces.profile import ProfileNamespace, AsyncProfileNamespace
from .namespaces.groups import GroupsNamespace, AsyncGroupsNamespace
from .namespaces.labels import LabelsNamespace, AsyncLabelsNamespace
from .namespaces.status import StatusNamespace, AsyncStatusNamespace
from .namespaces.channels import ChannelsNamespace, AsyncChannelsNamespace
from .namespaces.media import MediaNamespace, AsyncMediaNamespace
from .namespaces.presence import PresenceNamespace, AsyncPresenceNamespace


class WahaClient:
    """
    Synchronous WAHA API client.

    This client provides access to all WAHA API functionality through
    organized namespaces for different types of operations.

    Args:
        base_url: The base URL of the WAHA API server
        api_key: API key for authentication (can also be set via WAHA_API_KEY env var)
        timeout: Request timeout in seconds (default: 30.0)
        headers: Additional headers to send with requests

    Example:
        client = WahaClient(
            base_url="http://localhost:3000",
            api_key="your-api-key"
        )

        # Start a session
        client.sessions.start("default")

        # Send a message
        client.messages.send_text(
            session="default",
            chat_id="1234567890@c.us",
            text="Hello, World!"
        )
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        # Use environment variable if api_key not provided
        if api_key is None:
            api_key = os.getenv("WAHA_API_KEY")

        self._http_client = SyncHTTPClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            headers=headers,
        )

        # Initialize namespaces
        self.auth = AuthNamespace(self._http_client)
        self.sessions = SessionsNamespace(self._http_client)
        self.messages = MessagesNamespace(self._http_client)
        self.chats = ChatsNamespace(self._http_client)
        self.contacts = ContactsNamespace(self._http_client)
        self.profile = ProfileNamespace(self._http_client)
        self.groups = GroupsNamespace(self._http_client)
        self.labels = LabelsNamespace(self._http_client)
        self.status = StatusNamespace(self._http_client)
        self.channels = ChannelsNamespace(self._http_client)
        self.media = MediaNamespace(self._http_client)
        self.presence = PresenceNamespace(self._http_client)

    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncWahaClient:
    """
    Asynchronous WAHA API client.

    This client provides async access to all WAHA API functionality through
    organized namespaces for different types of operations.

    Args:
        base_url: The base URL of the WAHA API server
        api_key: API key for authentication (can also be set via WAHA_API_KEY env var)
        timeout: Request timeout in seconds (default: 30.0)
        headers: Additional headers to send with requests

    Example:
        async with AsyncWahaClient(
            base_url="http://localhost:3000",
            api_key="your-api-key"
        ) as client:
            # Start a session
            await client.sessions.start("default")

            # Send a message
            await client.messages.send_text(
                session="default",
                chat_id="1234567890@c.us",
                text="Hello, World!"
            )
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        # Use environment variable if api_key not provided
        if api_key is None:
            api_key = os.getenv("WAHA_API_KEY")

        self._http_client = AsyncHTTPClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            headers=headers,
        )

        # Initialize async namespaces
        self.auth = AsyncAuthNamespace(self._http_client)
        self.sessions = AsyncSessionsNamespace(self._http_client)
        self.messages = AsyncMessagesNamespace(self._http_client)
        self.chats = AsyncChatsNamespace(self._http_client)
        self.contacts = AsyncContactsNamespace(self._http_client)
        self.profile = AsyncProfileNamespace(self._http_client)
        self.groups = AsyncGroupsNamespace(self._http_client)
        self.labels = AsyncLabelsNamespace(self._http_client)
        self.status = AsyncStatusNamespace(self._http_client)
        self.channels = AsyncChannelsNamespace(self._http_client)
        self.media = AsyncMediaNamespace(self._http_client)
        self.presence = AsyncPresenceNamespace(self._http_client)

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        await self._http_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
