"""
Channels namespace for WAHA

Handles WhatsApp channels operations.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient


class ChannelsNamespace:
    """Synchronous channel operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list(self, session: str = "default") -> Dict[str, Any]:
        """List WhatsApp channels."""
        return self._http_client.get(f"/api/{session}/channels")

    def follow(
        self,
        channel_id: str,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Follow a WhatsApp channel."""
        data = {"channelId": channel_id}
        return self._http_client.post(f"/api/{session}/channels/follow", data=data)


class AsyncChannelsNamespace:
    """Asynchronous channel operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list(self, session: str = "default") -> Dict[str, Any]:
        """List WhatsApp channels (async version)."""
        return await self._http_client.get(f"/api/{session}/channels")
