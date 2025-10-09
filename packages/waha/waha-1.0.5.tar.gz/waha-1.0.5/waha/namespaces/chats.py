"""
Chats namespace for WAHA

Handles chat management operations.
"""

from typing import List, Optional, Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import WAChat, WAMessage, GetMessagesRequest, MessagesFilter


class ChatsNamespace:
    """Synchronous chat operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list(
        self,
        session: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[WAChat]:
        """
        List all chats.

        Args:
            session: Session name
            limit: Maximum number of chats to return
            offset: Offset for pagination

        Returns:
            List of chats

        Example:
            chats = client.chats.list(limit=50)
        """
        params = {
            "session": session,
            "limit": limit,
            "offset": offset,
        }
        response = self._http_client.get("/api/chats", params=params)
        return [WAChat(**chat) for chat in response]

    def get_messages(
        self,
        chat_id: str,
        session: str = "default",
        limit: int = 100,
        offset: int = 0,
        download_media: bool = True,
        filter: Optional[MessagesFilter] = None,
    ) -> List[WAMessage]:
        """
        Get messages in a chat.

        Args:
            chat_id: Chat ID
            session: Session name
            limit: Maximum number of messages to return
            offset: Offset for pagination
            download_media: Whether to download media
            filter: Message filter options

        Returns:
            List of messages

        Example:
            messages = client.chats.get_messages(
                chat_id="1234567890@c.us",
                limit=50
            )
        """
        params = {
            "chatId": chat_id,
            "session": session,
            "limit": limit,
            "offset": offset,
            "downloadMedia": download_media,
        }

        if filter:
            if filter.timestamp:
                for key, value in filter.timestamp.items():
                    params[f"filter.timestamp.{key}"] = value
            if filter.fromMe is not None:
                params["filter.fromMe"] = filter.fromMe
            if filter.ack:
                params["filter.ack"] = filter.ack.value

        response = self._http_client.get("/api/messages", params=params)
        return [WAMessage(**message) for message in response]


class AsyncChatsNamespace:
    """Asynchronous chat operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list(
        self,
        session: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[WAChat]:
        """List all chats (async version)."""
        params = {
            "session": session,
            "limit": limit,
            "offset": offset,
        }
        response = await self._http_client.get("/api/chats", params=params)
        return [WAChat(**chat) for chat in response]

    async def get_messages(
        self,
        chat_id: str,
        session: str = "default",
        limit: int = 100,
        offset: int = 0,
        download_media: bool = True,
        filter: Optional[MessagesFilter] = None,
    ) -> List[WAMessage]:
        """Get messages in a chat (async version)."""
        params = {
            "chatId": chat_id,
            "session": session,
            "limit": limit,
            "offset": offset,
            "downloadMedia": download_media,
        }

        if filter:
            if filter.timestamp:
                for key, value in filter.timestamp.items():
                    params[f"filter.timestamp.{key}"] = value
            if filter.fromMe is not None:
                params["filter.fromMe"] = filter.fromMe
            if filter.ack:
                params["filter.ack"] = filter.ack.value

        response = await self._http_client.get("/api/messages", params=params)
        return [WAMessage(**message) for message in response]
