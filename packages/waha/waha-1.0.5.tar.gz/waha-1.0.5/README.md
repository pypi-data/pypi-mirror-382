# WAHA - Python

[![PyPI version](https://badge.fury.io/py/waha.svg)](https://badge.fury.io/py/waha)
[![Python versions](https://img.shields.io/pypi/pyversions/waha.svg)](https://pypi.org/project/waha/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/devlikeapro/waha-python/workflows/tests/badge.svg)](https://github.com/devlikeapro/waha-python/actions)

A comprehensive Python package for the **WAHA (WhatsApp HTTP API)** service. This package provides a clean, type-safe, and easy-to-use interface for interacting with WhatsApp through the WAHA API.

## 🌟 Features

- **🔄 Full API Coverage**: Complete implementation of all WAHA API endpoints
- **⚡ Async & Sync Support**: Both synchronous and asynchronous operation modes
- **🛡️ Type Safety**: Full typing with Pydantic models for request/response validation
- **🎯 Organized Namespaces**: Intuitive organization by functionality (auth, sessions, messages, etc.)
- **📝 Rich Documentation**: Comprehensive docstrings and examples
- **🧪 Well Tested**: Extensive test coverage with pytest
- **🐍 Modern Python**: Support for Python 3.8+ with modern async/await patterns

## 🚀 Quick Start

### Installation

```bash
pip install waha
```

### Basic Usage

```python
from waha import WahaClient

# Initialize the client
client = WahaClient(
    base_url="http://localhost:3000",
    api_key="your-api-key"  # Optional, can use WAHA_API_KEY env var
)

# Start a session
session = client.sessions.start("default")

# Send a text message
message = client.messages.send_text(
    session="default",
    chat_id="1234567890@c.us",
    text="Hello from WAHA! 👋"
)

print(f"Message sent: {message.id}")
```

### Async Usage

```python
import asyncio
from waha import AsyncWahaClient

async def main():
    async with AsyncWahaClient(
        base_url="http://localhost:3000",
        api_key="your-api-key"
    ) as client:
        # Start a session
        session = await client.sessions.start("default")
        
        # Send a message
        message = await client.messages.send_text(
            session="default",
            chat_id="1234567890@c.us",
            text="Hello from async WAHA! 🚀"
        )
        
        print(f"Message sent: {message.id}")

asyncio.run(main())
```

## 📚 Documentation

### Core Components

The SDK is organized into several namespaces, each handling a specific area of functionality:

#### 🔑 Authentication (`client.auth`)

Handle QR code authentication and phone verification:

```python
# Get QR code for authentication
qr_code = client.auth.get_qr_code("default", format="raw")
print(f"QR Code: {qr_code.qr}")

# Request authentication code
client.auth.request_code("default", phone_number="+1234567890")
```

#### 🖥️ Sessions (`client.sessions`)

Manage WhatsApp sessions:

```python
# Create and start a session
session = client.sessions.create("my-session", start=True)

# List all sessions
sessions = client.sessions.list()

# Get session info
info = client.sessions.get("default")

# Stop a session
client.sessions.stop("default")

# Get authenticated account info
me = client.sessions.get_me("default")
print(f"Logged in as: {me.pushName} ({me.id})")
```

#### 📤 Messages (`client.messages`)

Send various types of messages:

```python
# Send text message
client.messages.send_text(
    chat_id="1234567890@c.us",
    text="Hello! 👋",
    reply_to="message_id_to_reply_to"  # Optional
)

# Send image
client.messages.send_image(
    chat_id="1234567890@c.us",
    file="https://example.com/image.jpg",
    caption="Check this out!"
)

# Send document
client.messages.send_file(
    chat_id="1234567890@c.us",
    file="https://example.com/document.pdf",
    caption="Important document"
)

# Send location
client.messages.send_location(
    chat_id="1234567890@c.us",
    latitude=40.7128,
    longitude=-74.0060,
    title="New York City"
)

# Send contact
from waha.types import ContactVcard

contact = ContactVcard(
    fullName="John Doe",
    phoneNumber="+1234567890",
    email="john@example.com"
)
client.messages.send_contact_vcard(
    chat_id="1234567890@c.us",
    contacts=[contact]
)

# Send poll
client.messages.send_poll(
    chat_id="1234567890@c.us",
    poll_text="What's your favorite color?",
    options=["Red", "Green", "Blue", "Yellow"]
)

# Send buttons
buttons = [
    {"id": "btn1", "title": "Option 1"},
    {"id": "btn2", "title": "Option 2"},
]
client.messages.send_buttons(
    chat_id="1234567890@c.us",
    text="Choose an option:",
    buttons=buttons
)

# React to a message
client.messages.react(
    message_id="some_message_id",
    reaction="👍"
)

# Forward a message
client.messages.forward_message(
    message_id="source_message_id",
    chat_id="target_chat_id"
)
```

#### 💬 Chats (`client.chats`)

Manage chats and retrieve messages:

```python
# List chats
chats = client.chats.list(limit=50)

# Get messages from a chat
messages = client.chats.get_messages(
    chat_id="1234567890@c.us",
    limit=100
)
```

#### 👤 Contacts (`client.contacts`)

Manage contacts:

```python
# Check if a number exists on WhatsApp
result = client.contacts.check_exists("+1234567890")
if result.numberExists:
    print(f"Number exists! Chat ID: {result.chatId}")
```

#### 🆔 Profile (`client.profile`)

Manage your WhatsApp profile:

```python
# Get profile info
profile = client.profile.get()
print(f"Name: {profile.name}, Status: {profile.status}")

# Update profile name
client.profile.set_name("New Name")

# Update profile status
client.profile.set_status("Available")

# Set profile picture
client.profile.set_picture("https://example.com/avatar.jpg")
```

#### 👥 Groups (`client.groups`)

Manage WhatsApp groups:

```python
# Create a group
group = client.groups.create(
    name="My Group",
    participants=["1234567890@c.us", "0987654321@c.us"]
)

# Add participants
client.groups.add_participants(
    group_id="group_id@g.us",
    participants=["newuser@c.us"]
)
```

### 🔧 Configuration

#### Environment Variables

You can configure the SDK using environment variables:

```bash
export WAHA_URL="http://localhost:3000"
export WAHA_API_KEY="your-api-key"
```

#### Client Configuration

```python
client = WahaClient(
    base_url="http://localhost:3000",
    api_key="your-api-key",
    timeout=30.0,  # Request timeout in seconds
    headers={"Custom-Header": "value"}  # Additional headers
)
```

### 📁 File Handling

The SDK supports multiple ways to handle files:

#### Using URLs

```python
client.messages.send_image(
    chat_id="1234567890@c.us",
    file="https://example.com/image.jpg"
)
```

#### Using Base64

```python
from waha.types import Base64File

file = Base64File(
    mimetype="image/jpeg",
    filename="image.jpg",
    data="base64_encoded_data_here"
)

client.messages.send_image(
    chat_id="1234567890@c.us",
    file=file
)
```

#### Using URLFile Objects

```python
from waha.types import URLFile

file = URLFile(
    url="https://example.com/image.jpg",
    filename="custom_name.jpg"
)

client.messages.send_image(
    chat_id="1234567890@c.us",
    file=file
)
```

### 🚨 Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from waha.exceptions import (
    WahaException,
    WahaAPIError,
    WahaTimeoutError,
    WahaAuthenticationError,
    WahaSessionError
)

try:
    message = client.messages.send_text(
        chat_id="invalid_chat_id",
        text="Hello"
    )
except WahaAuthenticationError:
    print("Authentication failed - check your API key")
except WahaAPIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
except WahaTimeoutError:
    print("Request timed out")
except WahaException as e:
    print(f"General WAHA error: {e}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=waha_sdk

# Run specific test file
pytest tests/test_client.py
```

## 🔄 Development

### Setting up for development:

```bash
# Clone the repository
git clone https://github.com/devlikeapro/waha-python.git
cd waha-python

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black waha tests examples

# Type checking
mypy waha
```

### Project Structure

```
waha-python/
├── waha/
│   ├── __init__.py
│   ├── client.py              # Main client classes
│   ├── exceptions.py          # Custom exceptions
│   ├── types.py              # Pydantic models
│   ├── http_client.py        # HTTP client implementation
│   └── namespaces/           # API namespaces
│       ├── auth.py
│       ├── sessions.py
│       ├── messages.py
│       └── ...
├── tests/                    # Test suite
├── examples/                 # Usage examples
├── pyproject.toml           # Package configuration
└── README.md
```

## 📋 Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **WAHA Documentation**: [https://waha.devlike.pro](https://waha.devlike.pro)
- **WAHA GitHub**: [https://github.com/devlikeapro/waha](https://github.com/devlikeapro/waha)
- **PyPI Package**: [https://pypi.org/project/waha/](https://pypi.org/project/waha/)
- **Issues**: [https://github.com/devlikeapro/waha-python/issues](https://github.com/devlikeapro/waha-python/issues)

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [documentation](https://waha.devlike.pro)
2. Search existing [issues](https://github.com/devlikeapro/waha-python/issues)
3. Create a new issue with detailed information about your problem

## 🎯 Roadmap

- [ ] Add webhook handling utilities
- [ ] Implement retry logic with exponential backoff
- [ ] Add rate limiting support
- [ ] Create CLI tool for common operations
- [ ] Add more comprehensive examples
- [ ] Support for WhatsApp Business API features

## 🙏 Acknowledgments

- Thanks to the [WAHA](https://github.com/devlikeapro/waha) project for providing the WhatsApp HTTP API
- Built with [httpx](https://www.python-httpx.org/) for HTTP client functionality
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation and serialization