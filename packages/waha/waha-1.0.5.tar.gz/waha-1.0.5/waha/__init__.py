"""
WAHA - WhatsApp HTTP API Python SDK

A comprehensive Python SDK for the WAHA (WhatsApp HTTP API) service.
"""

from .client import WahaClient, AsyncWahaClient
from .exceptions import (
    WahaException,
    WahaAPIError,
    WahaTimeoutError,
    WahaAuthenticationError,
    WahaValidationError,
    WahaSessionError,
)
from .types import *

__version__ = "1.0.5"
__author__ = "WAHA"
__email__ = "support@waha.dev"

__all__ = [
    "WahaClient",
    "AsyncWahaClient",
    "WahaException",
    "WahaAPIError",
    "WahaTimeoutError",
    "WahaAuthenticationError",
    "WahaValidationError",
    "WahaSessionError",
]
