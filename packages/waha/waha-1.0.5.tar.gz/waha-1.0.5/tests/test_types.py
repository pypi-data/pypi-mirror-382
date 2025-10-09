"""
Tests for Pydantic models and type definitions.
"""

import pytest
from pydantic import ValidationError
from waha.types import (
    MessageTextRequest,
    MessageImageRequest,
    SessionCreateRequest,
    SessionInfo,
    WAMessage,
    Base64File,
    URLFile,
    ContactVcard,
    SessionStatus,
    MessageAck,
    QRFormat,
)


class TestBaseModels:
    """Tests for base Pydantic models."""

    def test_base64_file_model(self):
        """Test Base64File model validation."""
        file = Base64File(
            mimetype="image/jpeg", filename="test.jpg", data="base64_data_here"
        )

        assert file.mimetype == "image/jpeg"
        assert file.filename == "test.jpg"
        assert file.data == "base64_data_here"

    def test_url_file_model(self):
        """Test URLFile model validation."""
        file = URLFile(url="https://example.com/image.jpg", filename="image.jpg")

        assert file.url == "https://example.com/image.jpg"
        assert file.filename == "image.jpg"

    def test_contact_vcard_model(self):
        """Test ContactVcard model validation."""
        contact = ContactVcard(
            fullName="John Doe",
            displayName="Johnny",
            phoneNumber="+1234567890",
            email="john@example.com",
        )

        assert contact.fullName == "John Doe"
        assert contact.phoneNumber == "+1234567890"
        assert contact.email == "john@example.com"

    def test_contact_vcard_required_fields(self):
        """Test ContactVcard model with missing required fields."""
        with pytest.raises(ValidationError):
            ContactVcard(displayName="Johnny")  # Missing fullName and phoneNumber


class TestMessageModels:
    """Tests for message-related models."""

    def test_message_text_request(self):
        """Test MessageTextRequest model validation."""
        request = MessageTextRequest(
            chatId="1234567890@c.us",
            text="Hello, World!",
            session="default",
            replyTo="message_id",
            linkPreview=True,
        )

        assert request.chatId == "1234567890@c.us"
        assert request.text == "Hello, World!"
        assert request.session == "default"
        assert request.replyTo == "message_id"
        assert request.linkPreview is True

    def test_message_text_request_defaults(self):
        """Test MessageTextRequest with default values."""
        request = MessageTextRequest(chatId="1234567890@c.us", text="Hello, World!")

        assert request.session == "default"
        assert request.linkPreview is True
        assert request.replyTo is None

    def test_message_image_request_with_url(self):
        """Test MessageImageRequest with URL file."""
        url_file = URLFile(url="https://example.com/image.jpg")
        request = MessageImageRequest(
            chatId="1234567890@c.us", file=url_file, caption="Test image"
        )

        assert isinstance(request.file, URLFile)
        assert request.caption == "Test image"

    def test_message_image_request_with_base64(self):
        """Test MessageImageRequest with Base64 file."""
        base64_file = Base64File(mimetype="image/jpeg", data="base64_data_here")
        request = MessageImageRequest(chatId="1234567890@c.us", file=base64_file)

        assert isinstance(request.file, Base64File)
        assert request.file.mimetype == "image/jpeg"

    def test_wa_message_model(self):
        """Test WAMessage model validation."""
        message_data = {
            "id": "message_123",
            "timestamp": 1640995200,
            "from": {"id": "1234567890@c.us", "name": "Test User"},
            "fromMe": False,
            "body": "Hello, World!",
            "type": "text",
            "ack": "READ",
            "chatId": "1234567890@c.us",
            "hasMedia": False,
        }

        message = WAMessage(**message_data)

        assert message.id == "message_123"
        assert message.timestamp == 1640995200
        assert message.from_.id == "1234567890@c.us"
        assert message.body == "Hello, World!"
        assert message.type == "text"
        assert message.ack == MessageAck.READ


class TestSessionModels:
    """Tests for session-related models."""

    def test_session_create_request(self):
        """Test SessionCreateRequest model validation."""
        request = SessionCreateRequest(name="test-session", start=True)

        assert request.name == "test-session"
        assert request.start is True
        assert request.config is None

    def test_session_info_model(self):
        """Test SessionInfo model validation."""
        session_data = {
            "name": "default",
            "status": "WORKING",
            "config": {"debug": False},
            "engine": "WEBJS",
        }

        session = SessionInfo(**session_data)

        assert session.name == "default"
        assert session.status == SessionStatus.WORKING
        assert session.config == {"debug": False}


class TestEnums:
    """Tests for enum values."""

    def test_session_status_enum(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.STOPPED == "STOPPED"
        assert SessionStatus.WORKING == "WORKING"
        assert SessionStatus.SCAN_QR_CODE == "SCAN_QR_CODE"

    def test_message_ack_enum(self):
        """Test MessageAck enum values."""
        assert MessageAck.READ == "READ"
        assert MessageAck.DEVICE == "DEVICE"
        assert MessageAck.SERVER == "SERVER"

    def test_qr_format_enum(self):
        """Test QRFormat enum values."""
        assert QRFormat.IMAGE == "image"
        assert QRFormat.RAW == "raw"


class TestModelSerialization:
    """Tests for model serialization and deserialization."""

    def test_model_json_serialization(self):
        """Test model serialization to JSON."""
        request = MessageTextRequest(
            chatId="1234567890@c.us",
            text="Hello, World!",
            mentionsIds=["user1", "user2"],
        )

        json_data = request.model_dump_json(exclude_none=True)
        assert "chatId" in json_data
        assert "text" in json_data
        assert "mentionsIds" in json_data
        # replyTo should be excluded since it's None
        assert "replyTo" not in json_data

    def test_model_dict_conversion(self):
        """Test model conversion to dictionary."""
        contact = ContactVcard(fullName="John Doe", phoneNumber="+1234567890")

        data = contact.model_dump(exclude_none=True)

        assert data["fullName"] == "John Doe"
        assert data["phoneNumber"] == "+1234567890"
        # Optional fields should be excluded
        assert "email" not in data
        assert "organization" not in data
