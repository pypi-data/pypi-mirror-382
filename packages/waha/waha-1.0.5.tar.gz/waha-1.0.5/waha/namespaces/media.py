"""
Media namespace for WAHA

Handles media operations.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient


class MediaNamespace:
    """Synchronous media operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def download(
        self,
        message_id: str,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Download media from a message."""
        params = {"messageId": message_id, "session": session}
        return self._http_client.get("/api/media/download", params=params)

    def upload(
        self,
        file_data: bytes,
        filename: str,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Upload media file."""
        data = {
            "file": file_data,
            "filename": filename,
            "session": session,
        }
        return self._http_client.post("/api/media/upload", data=data)


class AsyncMediaNamespace:
    """Asynchronous media operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def download(
        self,
        message_id: str,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Download media from a message (async version)."""
        params = {"messageId": message_id, "session": session}
        return await self._http_client.get("/api/media/download", params=params)
