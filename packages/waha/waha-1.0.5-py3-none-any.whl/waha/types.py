"""
Type definitions and Pydantic models for WAHA

Contains all request/response models based on the OpenAPI specification.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Base Models
class BaseRequest(BaseModel):
    """Base class for all API requests."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class BaseResponse(BaseModel):
    """Base class for all API responses."""

    model_config = ConfigDict(extra="ignore", use_enum_values=True)


# Enums
class SessionStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    SCAN_QR_CODE = "SCAN_QR_CODE"
    WORKING = "WORKING"
    FAILED = "FAILED"


class MessageAck(str, Enum):
    ERROR = "ERROR"
    PENDING = "PENDING"
    SERVER = "SERVER"
    DEVICE = "DEVICE"
    READ = "READ"
    PLAYED = "PLAYED"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    POLL = "poll"
    REACTION = "reaction"


class QRFormat(str, Enum):
    IMAGE = "image"
    RAW = "raw"


class EngineType(str, Enum):
    WEBJS = "WEBJS"
    NOWEB = "NOWEB"
    VENOM = "VENOM"


# File/Media Models
class Base64File(BaseModel):
    """Base64 encoded file representation."""

    mimetype: str
    filename: Optional[str] = None
    data: str  # Base64 encoded data


class URLFile(BaseModel):
    """URL-based file representation."""

    url: str
    filename: Optional[str] = None


class MediaFile(BaseModel):
    """Media file that can be either base64 or URL."""

    file: Optional[Union[Base64File, URLFile]] = None
    caption: Optional[str] = None


# Session Models
class SessionConfig(BaseModel):
    """Session configuration."""

    webhooks: Optional[List[Dict[str, Any]]] = None
    debug: Optional[bool] = False
    noweb: Optional[Dict[str, Any]] = None
    webjs: Optional[Dict[str, Any]] = None


class SessionCreateRequest(BaseRequest):
    """Request to create a new session."""

    name: str
    config: Optional[SessionConfig] = None
    start: Optional[bool] = True


class SessionUpdateRequest(BaseRequest):
    """Request to update a session."""

    config: Optional[SessionConfig] = None
    stop: Optional[bool] = False
    start: Optional[bool] = False


class SessionDTO(BaseResponse):
    """Session data transfer object."""

    name: str
    status: SessionStatus
    config: Optional[SessionConfig] = None


class SessionInfo(BaseResponse):
    """Session information."""

    name: str
    status: SessionStatus
    config: Optional[SessionConfig] = None
    me: Optional[Dict[str, Any]] = None
    engine: Optional[EngineType] = None
    engine_raw: Optional[Any] = None

    def __init__(self, **data):
        engine = data.get("engine")
        data["engine_raw"] = engine
        if isinstance(engine, dict):
            data["engine"] = None
        elif isinstance(engine, str):
            try:
                data["engine"] = EngineType(engine)
            except ValueError:
                data["engine"] = None
        super().__init__(**data)


class MeInfo(BaseResponse):
    """Information about the authenticated account."""

    id: str
    pushName: Optional[str] = None
    name: Optional[str] = None


# Auth Models
class QRCodeValue(BaseResponse):
    """QR code value response."""

    qr: str


class RequestCodeRequest(BaseRequest):
    """Request for authentication code."""

    phoneNumber: str


# Profile Models
class MyProfile(BaseResponse):
    """User profile information."""

    id: str
    name: Optional[str] = None
    pushName: Optional[str] = None
    status: Optional[str] = None


class ProfileNameRequest(BaseRequest):
    """Request to update profile name."""

    name: str


class ProfileStatusRequest(BaseRequest):
    """Request to update profile status."""

    status: str


class ProfilePictureRequest(BaseRequest):
    """Request to update profile picture."""

    file: Union[Base64File, URLFile]


# Message Models
class MessageTextRequest(BaseRequest):
    """Request to send text message."""

    chatId: str
    text: str
    session: str = "default"
    replyTo: Optional[str] = None
    linkPreview: Optional[bool] = True
    mentionsIds: Optional[List[str]] = None


class MessageImageRequest(BaseRequest):
    """Request to send image message."""

    chatId: str
    file: Union[Base64File, URLFile]
    session: str = "default"
    caption: Optional[str] = None
    replyTo: Optional[str] = None
    mentionsIds: Optional[List[str]] = None


class MessageFileRequest(BaseRequest):
    """Request to send file message."""

    chatId: str
    file: Union[Base64File, URLFile]
    session: str = "default"
    caption: Optional[str] = None
    replyTo: Optional[str] = None
    mentionsIds: Optional[List[str]] = None


class MessageVideoRequest(BaseRequest):
    """Request to send video message."""

    chatId: str
    file: Union[Base64File, URLFile]
    session: str = "default"
    caption: Optional[str] = None
    replyTo: Optional[str] = None
    mentionsIds: Optional[List[str]] = None


class MessageVoiceRequest(BaseRequest):
    """Request to send voice message."""

    chatId: str
    file: Union[Base64File, URLFile]
    session: str = "default"
    replyTo: Optional[str] = None


class MessageLocationRequest(BaseRequest):
    """Request to send location message."""

    chatId: str
    latitude: float
    longitude: float
    session: str = "default"
    title: Optional[str] = None
    replyTo: Optional[str] = None


class ContactVcard(BaseModel):
    """Contact vCard information."""

    fullName: str
    displayName: Optional[str] = None
    phoneNumber: str
    email: Optional[str] = None
    organization: Optional[str] = None
    url: Optional[str] = None


class MessageContactVcardRequest(BaseRequest):
    """Request to send contact vCard."""

    chatId: str
    contacts: List[ContactVcard]
    session: str = "default"
    replyTo: Optional[str] = None


class MessageReactionRequest(BaseRequest):
    """Request to react to a message."""

    messageId: str
    reaction: str
    session: str = "default"


class MessageStarRequest(BaseRequest):
    """Request to star/unstar a message."""

    messageId: str
    star: bool
    session: str = "default"


class PollOption(BaseModel):
    """Poll option."""

    name: str
    localId: Optional[int] = None


class MessagePollRequest(BaseRequest):
    """Request to send poll message."""

    chatId: str
    poll: str
    options: List[PollOption]
    session: str = "default"
    multipleAnswers: Optional[bool] = False


class MessageForwardRequest(BaseRequest):
    """Request to forward a message."""

    messageId: str
    chatId: str
    session: str = "default"


class ChatRequest(BaseRequest):
    """Basic chat request."""

    chatId: str
    session: str = "default"


class SendSeenRequest(ChatRequest):
    """Request to mark messages as seen."""

    messageId: Optional[str] = None


# Button Models
class Button(BaseModel):
    """Interactive button."""

    id: str
    title: str


class SendButtonsRequest(BaseRequest):
    """Request to send buttons."""

    chatId: str
    text: str
    buttons: List[Button]
    session: str = "default"
    footer: Optional[str] = None


class MessageButtonReply(BaseRequest):
    """Reply to a button message."""

    messageId: str
    text: str
    session: str = "default"


# Link Preview Models
class LinkPreview(BaseModel):
    """Link preview information."""

    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[Union[Base64File, URLFile]] = None


class MessageLinkCustomPreviewRequest(BaseRequest):
    """Request to send message with custom link preview."""

    chatId: str
    text: str
    linkPreview: LinkPreview
    session: str = "default"


# Message Response Models
class WAMessageFrom(BaseModel):
    """Message sender information."""

    id: str
    name: Optional[str] = None
    pushName: Optional[str] = None


class WAMessageBody(BaseModel):
    """Message body content."""

    text: Optional[str] = None
    caption: Optional[str] = None


class WAMessage(BaseResponse):
    """WhatsApp message."""

    id: str
    timestamp: int
    from_: Optional[Union[WAMessageFrom, str]] = Field(alias="from", default=None)
    fromMe: bool
    body: Optional[str] = None
    type: Optional[MessageType] = None
    ack: Optional[Union[MessageAck, int]] = None
    chatId: Optional[str] = None
    hasMedia: Optional[bool] = False
    mediaUrl: Optional[str] = None
    
    @field_validator('from_', mode='before')
    @classmethod
    def validate_from(cls, v):
        if isinstance(v, str):
            return WAMessageFrom(id=v)
        return v
    
    @field_validator('ack', mode='before')
    @classmethod
    def validate_ack(cls, v):
        if isinstance(v, int):
            # Map integer values to MessageAck enum
            mapping = {
                0: MessageAck.ERROR,
                1: MessageAck.PENDING, 
                2: MessageAck.SERVER,
                3: MessageAck.DEVICE,
                4: MessageAck.READ,
                5: MessageAck.PLAYED
            }
            return mapping.get(v, MessageAck.ERROR)
        return v


# Contact Models
class WANumberExistResult(BaseResponse):
    """Result of number existence check."""

    numberExists: bool
    chatId: Optional[str] = None


class ContactCheckRequest(BaseRequest):
    """Request to check if contact exists."""

    phone: str
    session: str = "default"


# Chat Models
class WAChat(BaseResponse):
    """WhatsApp chat."""

    id: str
    name: Optional[str] = None
    isGroup: bool
    timestamp: Optional[int] = None
    unreadCount: Optional[int] = 0
    archived: Optional[bool] = False
    pinned: Optional[bool] = False
    isMuted: Optional[bool] = False


class ChatListRequest(BaseRequest):
    """Request to list chats."""

    session: str = "default"
    limit: Optional[int] = 100
    offset: Optional[int] = 0


class MessagesFilter(BaseModel):
    """Message filtering options."""

    timestamp: Optional[Dict[str, int]] = None  # gte, lte
    fromMe: Optional[bool] = None
    ack: Optional[MessageAck] = None


class GetMessagesRequest(BaseRequest):
    """Request to get messages."""

    chatId: str
    session: str = "default"
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    downloadMedia: Optional[bool] = True
    filter: Optional[MessagesFilter] = None


# Group Models
class GroupParticipant(BaseModel):
    """Group participant information."""

    id: str
    isAdmin: Optional[bool] = False
    isSuperAdmin: Optional[bool] = False


class GroupCreateRequest(BaseRequest):
    """Request to create a group."""

    name: str
    participants: List[str]
    session: str = "default"


class GroupUpdateRequest(BaseRequest):
    """Request to update group."""

    groupId: str
    name: Optional[str] = None
    description: Optional[str] = None
    session: str = "default"


class GroupParticipantRequest(BaseRequest):
    """Request to manage group participants."""

    groupId: str
    participants: List[str]
    session: str = "default"


# Result Models
class Result(BaseResponse):
    """Generic result response."""

    success: bool
    message: Optional[str] = None


class WAPresence(BaseResponse):
    """WhatsApp presence information."""

    participant: str
    lastKnownPresence: Optional[str] = None
    lastSeen: Optional[int] = None


# Deprecated Models (for backward compatibility)
class SessionStartDeprecatedRequest(BaseRequest):
    """Deprecated session start request."""

    name: str = "default"
    config: Optional[SessionConfig] = None


class SessionStopDeprecatedRequest(BaseRequest):
    """Deprecated session stop request."""

    name: str = "default"
    logout: Optional[bool] = True


class SessionLogoutDeprecatedRequest(BaseRequest):
    """Deprecated session logout request."""

    name: str = "default"


class MessageReplyRequest(BaseRequest):
    """Deprecated message reply request."""

    chatId: str
    text: str
    reply_to: str
    session: str = "default"


class MessageLinkPreviewRequest(BaseRequest):
    """Deprecated link preview request."""

    chatId: str
    url: str
    title: str
    session: str = "default"


# Export all models
__all__ = [
    # Base
    "BaseRequest",
    "BaseResponse",
    # Enums
    "SessionStatus",
    "MessageAck",
    "MessageType",
    "QRFormat",
    "EngineType",
    # Session
    "SessionConfig",
    "SessionCreateRequest",
    "SessionUpdateRequest",
    "SessionDTO",
    "SessionInfo",
    "MeInfo",
    # Auth
    "QRCodeValue",
    "RequestCodeRequest",
    # Profile
    "MyProfile",
    "ProfileNameRequest",
    "ProfileStatusRequest",
    "ProfilePictureRequest",
    # Files/Media
    "Base64File",
    "URLFile",
    "MediaFile",
    # Messages
    "MessageTextRequest",
    "MessageImageRequest",
    "MessageFileRequest",
    "MessageVideoRequest",
    "MessageVoiceRequest",
    "MessageLocationRequest",
    "MessageContactVcardRequest",
    "MessageReactionRequest",
    "MessageStarRequest",
    "MessagePollRequest",
    "MessageForwardRequest",
    "WAMessage",
    "WAMessageFrom",
    "WAMessageBody",
    # Chat
    "ChatRequest",
    "SendSeenRequest",
    "WAChat",
    "ChatListRequest",
    "GetMessagesRequest",
    "MessagesFilter",
    # Buttons
    "Button",
    "SendButtonsRequest",
    "MessageButtonReply",
    # Link Preview
    "LinkPreview",
    "MessageLinkCustomPreviewRequest",
    # Contacts
    "ContactVcard",
    "WANumberExistResult",
    "ContactCheckRequest",
    # Groups
    "GroupParticipant",
    "GroupCreateRequest",
    "GroupUpdateRequest",
    "GroupParticipantRequest",
    # Polls
    "PollOption",
    # Results
    "Result",
    "WAPresence",
]
