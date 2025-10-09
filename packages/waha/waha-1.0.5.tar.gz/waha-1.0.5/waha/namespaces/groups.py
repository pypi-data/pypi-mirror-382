"""
Groups namespace for WAHA

Handles group management operations.
"""

from typing import List, Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import GroupCreateRequest, GroupUpdateRequest, GroupParticipantRequest


class GroupsNamespace:
    """Synchronous group operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create(
        self,
        name: str,
        participants: List[str],
        session: str = "default",
    ) -> Dict[str, Any]:
        """Create a new group."""
        request_data = GroupCreateRequest(
            name=name,
            participants=participants,
            session=session,
        )
        return self._http_client.post("/api/groups", data=request_data)

    def update(
        self,
        group_id: str,
        name: str = None,
        description: str = None,
        session: str = "default",
    ) -> Dict[str, Any]:
        """Update group information."""
        request_data = GroupUpdateRequest(
            groupId=group_id,
            name=name,
            description=description,
            session=session,
        )
        return self._http_client.put(f"/api/groups/{group_id}", data=request_data)

    def add_participants(
        self,
        group_id: str,
        participants: List[str],
        session: str = "default",
    ) -> Dict[str, Any]:
        """Add participants to group."""
        request_data = GroupParticipantRequest(
            groupId=group_id,
            participants=participants,
            session=session,
        )
        return self._http_client.post(
            f"/api/groups/{group_id}/participants", data=request_data
        )

    def remove_participants(
        self,
        group_id: str,
        participants: List[str],
        session: str = "default",
    ) -> Dict[str, Any]:
        """Remove participants from group."""
        request_data = GroupParticipantRequest(
            groupId=group_id,
            participants=participants,
            session=session,
        )
        return self._http_client.delete(
            f"/api/groups/{group_id}/participants", data=request_data
        )


class AsyncGroupsNamespace:
    """Asynchronous group operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def create(
        self,
        name: str,
        participants: List[str],
        session: str = "default",
    ) -> Dict[str, Any]:
        """Create a new group (async version)."""
        request_data = GroupCreateRequest(
            name=name,
            participants=participants,
            session=session,
        )
        return await self._http_client.post("/api/groups", data=request_data)
