"""
Authentication namespace for WAHA

Handles QR code authentication and phone verification.
"""

from typing import Union, Dict, Any
from ..http_client import SyncHTTPClient, AsyncHTTPClient
from ..types import QRCodeValue, Base64File, RequestCodeRequest, QRFormat


class AuthNamespace:
    """Synchronous authentication operations."""

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_qr_code(
        self,
        session: str = "default",
        format: QRFormat = QRFormat.IMAGE,
    ) -> Union[bytes, QRCodeValue]:
        """
        Get QR code for pairing WhatsApp API.

        Args:
            session: Session name
            format: QR code format ('image' for PNG binary or 'raw' for text)

        Returns:
            Binary image data if format='image', or QRCodeValue if format='raw'

        Example:
            # Get QR code as image
            qr_image = client.auth.get_qr_code("default", format="image")

            # Get QR code as raw text
            qr_text = client.auth.get_qr_code("default", format="raw")
        """
        response = self._http_client.get(
            f"/api/{session}/auth/qr", params={"format": format.value}
        )

        if format == QRFormat.IMAGE:
            return response["content"]  # Binary image data
        else:
            return QRCodeValue(**response)

    def request_code(
        self,
        session: str = "default",
        phone_number: str = None,
    ) -> Dict[str, Any]:
        """
        Request authentication code for phone number verification.

        Args:
            session: Session name
            phone_number: Phone number in international format

        Returns:
            Response from the API

        Example:
            client.auth.request_code("default", "+1234567890")
        """
        request_data = RequestCodeRequest(phoneNumber=phone_number)
        return self._http_client.post(
            f"/api/{session}/auth/request-code", data=request_data
        )


class AsyncAuthNamespace:
    """Asynchronous authentication operations."""

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get_qr_code(
        self,
        session: str = "default",
        format: QRFormat = QRFormat.IMAGE,
    ) -> Union[bytes, QRCodeValue]:
        """
        Get QR code for pairing WhatsApp API.

        Args:
            session: Session name
            format: QR code format ('image' for PNG binary or 'raw' for text)

        Returns:
            Binary image data if format='image', or QRCodeValue if format='raw'

        Example:
            # Get QR code as image
            qr_image = await client.auth.get_qr_code("default", format="image")

            # Get QR code as raw text
            qr_text = await client.auth.get_qr_code("default", format="raw")
        """
        response = await self._http_client.get(
            f"/api/{session}/auth/qr", params={"format": format.value}
        )

        if format == QRFormat.IMAGE:
            return response["content"]  # Binary image data
        else:
            return QRCodeValue(**response)

    async def request_code(
        self,
        session: str = "default",
        phone_number: str = None,
    ) -> Dict[str, Any]:
        """
        Request authentication code for phone number verification.

        Args:
            session: Session name
            phone_number: Phone number in international format

        Returns:
            Response from the API

        Example:
            await client.auth.request_code("default", "+1234567890")
        """
        request_data = RequestCodeRequest(phoneNumber=phone_number)
        return await self._http_client.post(
            f"/api/{session}/auth/request-code", data=request_data
        )
