# Kirim.Email SMTP Python SDK

Python SDK for Kirim.Email SMTP API - A modern, type-safe Python client for sending emails and managing SMTP services.

## Features

- 🚀 Modern Python with full type hints
- ⚡ Async/await support with httpx
- 📝 Pydantic models for data validation
- 🔄 Comprehensive error handling
- 📎 File attachment support
- 📊 Email log streaming
- 🧪 Full test coverage
- 📦 Minimal dependencies

## Installation

```bash
pip install kirimemail-smtp-sdk
```

## Quick Start

```python
import asyncio
from kirimemail_smtp import SmtpClient, MessagesApi

async def send_email():
    # Initialize client
    client = SmtpClient(username="your-username", token="your-token")
    messages_api = MessagesApi(client)
    
    # Send email
    result = await messages_api.send_message(
        domain="example.com",
        message={
            "from": "sender@example.com",
            "from_name": "Company Name",
            "to": "recipient@example.com",
            "subject": "Hello from Python SDK",
            "text": "This is a test email sent using the Kirim.Email Python SDK."
        }
    )
    
    print(f"Email sent: {result}")

# Run the async function
asyncio.run(send_email())
```

## API Reference

### Client

The `SmtpClient` is the core HTTP client with authentication and error handling.

```python
from kirimemail_smtp import SmtpClient

client = SmtpClient(
    username="your-username",
    token="your-token",
    base_url="https://smtp-app.kirim.email"  # Optional, defaults to production
)
```

### Messages API

Send emails and templates:

```python
from kirimemail_smtp import MessagesApi

messages_api = MessagesApi(client)

# Send simple email
await messages_api.send_message(domain="example.com", message={
    "from": "sender@example.com",
    "from_name": "Company Name",
    "to": "recipient@example.com",
    "subject": "Test Email",
    "text": "Email content"
})

# Send with attachments
await messages_api.send_message_with_attachments(
    domain="example.com",
    message={
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Email with attachments",
        "text": "Please find attached files"
    },
    files=[
        {"field": "attachment", "filename": "document.pdf", "content": b"PDF content"}
    ]
)

# Send template email
await messages_api.send_template_message(
    domain="example.com",
    template={
        "template_guid": "template-uuid",
        "from": "sender@example.com",
        "from_name": "Company Name",
        "to": "recipient@example.com",
        "variables": {"name": "John", "product": "Premium Plan"}
    }
)
```

### Domains API

Manage domains:

```python
from kirimemail_smtp import DomainsApi

domains_api = DomainsApi(client)

# List domains
domains = await domains_api.list_domains()

# Create domain
domain = await domains_api.create_domain(
    domain="newdomain.com",
    dkim_key_length=2048
)

# Get domain details
domain = await domains_api.get_domain("example.com")

# Update domain
await domains_api.update_domain("example.com", {
    "open_track": True,
    "click_track": True
})
```

### Credentials API

Manage SMTP credentials:

```python
from kirimemail_smtp import CredentialsApi

credentials_api = CredentialsApi(client)

# List credentials
credentials = await credentials_api.list_credentials("example.com")

# Create credential
credential = await credentials_api.create_credential(
    domain="example.com",
    username="new-credential"
)

# Delete credential
await credentials_api.delete_credential("example.com", "credential-username")
```

### Logs API

Retrieve and stream email logs:

```python
from kirimemail_smtp import LogsApi

logs_api = LogsApi(client)

# Get logs
logs = await logs_api.get_logs("example.com", {
    "limit": 50,
    "page": 1
})

# Stream logs (async generator)
async for log_entry in logs_api.stream_logs("example.com"):
    print(f"Log: {log_entry}")
```

### Suppressions API

Manage email suppressions:

```python
from kirimemail_smtp import SuppressionsApi

suppressions_api = SuppressionsApi(client)

# Get suppressions
suppressions = await suppressions_api.get_suppressions("example.com")

# Get suppressions by type
bounce_suppressions = await suppressions_api.get_suppressions_by_type(
    "example.com", "bounce"
)
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from kirimemail_smtp.exceptions import (
    ApiException,
    AuthenticationException,
    ValidationException,
    NotFoundException,
    ServerException
)

try:
    await messages_api.send_message(domain="example.com", message=message_data)
except AuthenticationException:
    print("Authentication failed - check your credentials")
except ValidationException as e:
    print(f"Validation error: {e.message}")
    print(f"Field errors: {e.errors}")
except NotFoundException:
    print("Domain not found")
except ServerException:
    print("Server error - please try again later")
except ApiException as e:
    print(f"API error: {e.message}")
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/kirimemail/kirimemail-smtp-python-sdk.git
cd kirimemail-smtp-python-sdk

# Install with uv
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/kirimemail_smtp --cov-report=html
```

### Code Quality

```bash
# Lint code
uv run ruff check src/

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@kirim.email
- 🐛 Issues: [GitHub Issues](https://github.com/kirimemail/kirimemail-smtp-python-sdk/issues)
- 📖 Documentation: [GitHub Repository](https://github.com/kirimemail/kirimemail-smtp-python-sdk)