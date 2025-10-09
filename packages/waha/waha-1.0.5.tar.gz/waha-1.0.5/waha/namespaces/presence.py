"""
Presence namespace for WAHA

Handles online presence and typing indicators.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import WAPresence


class PresenceNamespace:
    """Synchronous presence operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get(
        self,
        chat_id: str,
        session: str = "default",
    ) -> WAPresence:
        """Get presence information for a chat."""
        params = {"chatId": chat_id, "session": session}
        response = self._http_client.get("/api/presence", params=params)
        return WAPresence(**response)

    def set_online(self, session: str = "default") -> Dict[str, Any]:
        """Set presence to online."""
        data = {"presence": "available"}
        return self._http_client.post(f"/api/{session}/presence", data=data)

    def set_offline(self, session: str = "default") -> Dict[str, Any]:
        """Set presence to offline."""
        data = {"presence": "unavailable"}
        return self._http_client.post(f"/api/{session}/presence", data=data)


class AsyncPresenceNamespace:
    """Asynchronous presence operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get(
        self,
        chat_id: str,
        session: str = "default",
    ) -> WAPresence:
        """Get presence information for a chat (async version)."""
        params = {"chatId": chat_id, "session": session}
        response = await self._http_client.get("/api/presence", params=params)
        return WAPresence(**response)
