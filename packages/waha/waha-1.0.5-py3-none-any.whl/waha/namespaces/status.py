"""
Status namespace for WAHA

Handles WhatsApp status (stories) operations.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient


class StatusNamespace:
    """Synchronous status operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_stories(self, session: str = "default") -> Dict[str, Any]:
        """Get WhatsApp stories/status updates."""
        return self._http_client.get(f"/api/{session}/status/stories")

    def send_text_status(
        self,
        text: str,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Send text status update."""
        data = {"text": text}
        return self._http_client.post(f"/api/{session}/status/text", data=data)


class AsyncStatusNamespace:
    """Asynchronous status operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get_stories(self, session: str = "default") -> Dict[str, Any]:
        """Get WhatsApp stories/status updates (async version)."""
        return await self._http_client.get(f"/api/{session}/status/stories")
