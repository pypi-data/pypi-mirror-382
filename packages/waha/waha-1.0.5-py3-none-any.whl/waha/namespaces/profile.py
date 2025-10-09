"""
Profile namespace for WAHA

Handles user profile management operations.
"""

from typing import Union
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import (
    MyProfile,
    ProfileNameRequest,
    ProfileStatusRequest,
    ProfilePictureRequest,
    Result,
    Base64File,
    URLFile,
)


class ProfileNamespace:
    """Synchronous profile operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get(self, session: str = "default") -> MyProfile:
        """
        Get my profile information.

        Args:
            session: Session name

        Returns:
            Profile information

        Example:
            profile = client.profile.get()
            print(f"My name: {profile.name}")
        """
        response = self._http_client.get(f"/api/{session}/profile")
        return MyProfile(**response)

    def set_name(
        self,
        name: str,
        session: str = "default",
    ) -> Result:
        """
        Set profile name.

        Args:
            name: New profile name
            session: Session name

        Returns:
            Operation result

        Example:
            result = client.profile.set_name("John Doe")
        """
        request_data = ProfileNameRequest(name=name)
        response = self._http_client.put(
            f"/api/{session}/profile/name", data=request_data
        )
        return Result(**response)

    def set_status(
        self,
        status: str,
        session: str = "default",
    ) -> Result:
        """
        Set profile status (About).

        Args:
            status: New profile status
            session: Session name

        Returns:
            Operation result

        Example:
            result = client.profile.set_status("Available")
        """
        request_data = ProfileStatusRequest(status=status)
        response = self._http_client.put(
            f"/api/{session}/profile/status", data=request_data
        )
        return Result(**response)

    def set_picture(
        self,
        file: Union[Base64File, URLFile, str],
        session: str = "default",
    ) -> Result:
        """
        Set profile picture.

        Args:
            file: Profile picture file
            session: Session name

        Returns:
            Operation result

        Example:
            result = client.profile.set_picture("https://example.com/avatar.jpg")
        """
        if isinstance(file, str):
            file = URLFile(url=file)

        request_data = ProfilePictureRequest(file=file)
        response = self._http_client.put(
            f"/api/{session}/profile/picture", data=request_data
        )
        return Result(**response)

    def delete_picture(self, session: str = "default") -> Result:
        """
        Delete profile picture.

        Args:
            session: Session name

        Returns:
            Operation result

        Example:
            result = client.profile.delete_picture()
        """
        response = self._http_client.delete(f"/api/{session}/profile/picture")
        return Result(**response)


class AsyncProfileNamespace:
    """Asynchronous profile operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get(self, session: str = "default") -> MyProfile:
        """Get my profile information (async version)."""
        response = await self._http_client.get(f"/api/{session}/profile")
        return MyProfile(**response)

    async def set_name(
        self,
        name: str,
        session: str = "default",
    ) -> Result:
        """Set profile name (async version)."""
        request_data = ProfileNameRequest(name=name)
        response = await self._http_client.put(
            f"/api/{session}/profile/name", data=request_data
        )
        return Result(**response)

    async def set_status(
        self,
        status: str,
        session: str = "default",
    ) -> Result:
        """Set profile status (async version)."""
        request_data = ProfileStatusRequest(status=status)
        response = await self._http_client.put(
            f"/api/{session}/profile/status", data=request_data
        )
        return Result(**response)

    async def set_picture(
        self,
        file: Union[Base64File, URLFile, str],
        session: str = "default",
    ) -> Result:
        """Set profile picture (async version)."""
        if isinstance(file, str):
            file = URLFile(url=file)

        request_data = ProfilePictureRequest(file=file)
        response = await self._http_client.put(
            f"/api/{session}/profile/picture", data=request_data
        )
        return Result(**response)

    async def delete_picture(self, session: str = "default") -> Result:
        """Delete profile picture (async version)."""
        response = await self._http_client.delete(f"/api/{session}/profile/picture")
        return Result(**response)
