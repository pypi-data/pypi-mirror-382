"""
Contacts namespace for WAHA

Handles contact operations.
"""

from typing import Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import WANumberExistResult, ContactCheckRequest


class ContactsNamespace:
    """Synchronous contact operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def check_exists(
        self,
        phone: str,
        session: str = "default",
    ) -> WANumberExistResult:
        """
        Check if a phone number exists on WhatsApp.

        Args:
            phone: Phone number to check
            session: Session name

        Returns:
            Result of the existence check

        Example:
            result = client.contacts.check_exists("+1234567890")
            if result.numberExists:
                print(f"Number exists! Chat ID: {result.chatId}")
        """
        params = {"phone": phone, "session": session}
        response = self._http_client.get(
            "/api/contacts/check-exists", params=params
        )
        return WANumberExistResult(**response)


class AsyncContactsNamespace:
    """Asynchronous contact operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def check_exists(
        self,
        phone: str,
        session: str = "default",
    ) -> WANumberExistResult:
        """
        Check if a phone number exists on WhatsApp (async version).

        Args:
            phone: Phone number to check
            session: Session name

        Returns:
            Result of the existence check

        Example:
            result = await client.contacts.check_exists("+1234567890")
            if result.numberExists:
                print(f"Number exists! Chat ID: {result.chatId}")
        """
        params = {"phone": phone, "session": session}
        response = await self._http_client.get(
            "/api/contacts/check-exists", params=params
        )
        return WANumberExistResult(**response)
