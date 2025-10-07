# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Updated minimum Python version from 3.8 to 3.9+
- Modernized type hints to use built-in `dict` and `list` instead of `typing.Dict` and `typing.List`
- Updated ruff configuration to use modern `lint` section format
- Improved exception chaining with proper `from` syntax

### Added
- Publishing documentation and version management guide

## [1.0.0] - 2024-10-07

### Added
- Initial release of Kirim.Email SMTP Python SDK
- Full API compatibility with Node.js SDK
- Support for Credentials, Domains, Logs, Messages, and Suppressions APIs
- Async/await support throughout
- Comprehensive test suite (100% pass rate - 53/53 tests)
- Full documentation and examples
- Pydantic models for data validation
- Type hints throughout the codebase
- Async generator support for streaming logs
- Comprehensive exception handling

### Fixed
- All API endpoint mismatches with Node.js SDK
- Credentials API password reset endpoint: `POST /reset` → `PUT /reset-password`
- Domains API auth setup endpoint: `POST /auth` → `POST /setup-auth-domain`
- Domains API mandatory verification: `GET /verify/mandatory` → `POST /verify-mandatory`
- Domains API auth verification: `GET /verify/auth` → `POST /verify-auth-domain`
- Domains API tracklink setup: `POST /tracklink` → `POST /setup-tracklink`
- Domains API tracklink verification: `GET /verify/tracklink` → `POST /verify-tracklink`
- Logs API endpoint paths: `/logs` → `/log` for consistency

### Changed
- Removed 3 extra Python methods that didn't exist in Node.js SDK
- Added missing `get_logs_by_date_range()` method to match Node.js SDK
- Updated all tests to match corrected API endpoints
- Improved error messages and exception handling

### Features
- HTTP client with proper authentication and error handling
- Support for all Kirim.Email SMTP API endpoints
- Streaming support for log retrieval
- Pagination support for list endpoints
- Comprehensive filtering options for logs
- Domain verification and setup workflows
- Credential management with password reset
- Message sending with attachments and templates
- Suppression list management

### Security
- Secure API key handling
- Proper HTTP header management
- Input validation with Pydantic models
- Safe async/await patterns

### Documentation
- Complete API documentation
- Usage examples
- Installation guide
- Publishing and version management guide
- Troubleshooting section

### Testing
- 100% test pass rate (53/53 tests)
- 67% code coverage
- Unit tests for all API classes
- Integration tests for client functionality
- Mock-based testing for external API calls

### Dependencies
- httpx>=0.25.0 for HTTP client functionality
- pydantic>=2.0.0 for data validation
- pytest>=7.0.0 for testing framework
- pytest-asyncio>=0.21.0 for async test support

### Python Support
- Python 3.8+
- Type hints throughout
- Async/await patterns
- Modern Python features

## [Previous Versions]

No previous versions - this is the initial release.