# Changelog

All notable changes to the WAHA Python project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of WAHA for Python
- Complete implementation of WAHA API endpoints
- Synchronous and asynchronous client support
- Full type safety with Pydantic models
- Organized namespace structure for different API areas:
  - Authentication (QR codes, phone verification)
  - Session management (create, start, stop, restart)
  - Message sending (text, media, location, contacts, polls, buttons)
  - Chat management and message retrieval
  - Contact operations
  - Profile management
  - Group operations
  - Labels, status, channels, media, and presence features
- Comprehensive error handling with custom exception classes
- HTTP client with timeout configuration and retry logic
- Support for both Base64 and URL-based file uploads
- Examples and comprehensive documentation
- Test suite with pytest
- Python 3.8+ support

### Features
- **WahaClient**: Main synchronous client class
- **AsyncWahaClient**: Asynchronous client with async/await support
- **Type Safety**: Full typing with Pydantic models for all requests/responses
- **Error Handling**: Custom exceptions for different error scenarios
- **File Support**: Handle media files via URLs or Base64 encoding
- **Environment Variables**: Support for configuration via env vars
- **Context Managers**: Proper resource cleanup with context manager support

### Dependencies
- httpx >= 0.24.0 (HTTP client)
- pydantic >= 2.0.0 (Data validation and serialization)

### Documentation
- Complete README with usage examples
- Inline documentation with docstrings
- Example scripts demonstrating common use cases
- Type hints for all public APIs

### Testing
- Unit tests for all major components
- Integration test structure
- Mock-based testing for HTTP operations
- Coverage reporting with pytest-cov

## [Unreleased]

### Planned
- Webhook handling utilities
- Rate limiting support  
- Retry logic with exponential backoff
- CLI tool for common operations
- Additional examples and use cases
- Performance optimizations
- Enhanced error messages and debugging