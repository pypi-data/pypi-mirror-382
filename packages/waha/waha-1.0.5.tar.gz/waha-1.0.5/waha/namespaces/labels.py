"""
Labels namespace for WAHA

Handles chat labeling operations.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient


class LabelsNamespace:
    """Synchronous label operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list(self, session: str = "default") -> Dict[str, Any]:
        """List all labels."""
        return self._http_client.get(f"/api/{session}/labels")

    def create(
        self,
        name: str,
        color: int = 0,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Create a new label."""
        data = {"name": name, "color": color}
        return self._http_client.post(f"/api/{session}/labels", data=data)


class AsyncLabelsNamespace:
    """Asynchronous label operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list(self, session: str = "default") -> Dict[str, Any]:
        """List all labels (async version)."""
        return await self._http_client.get(f"/api/{session}/labels")
