# unsent Python SDK

## Prerequisites

- [unsent API key](https://app.unsent.dev/dev-settings/api-keys)
- [Verified domain](https://app.unsent.dev/domains)

## Installation

### pip

```bash
pip install unsent
```

### poetry

```bash
poetry add unsent
```

## Usage

### Basic Setup

```python
from unsent import unsent

client = unsent("us_12345")
```

### Environment Variables

You can also set your API key using environment variables:

```python
# Set UNSENT_API_KEY or UNSENT_API_KEY in your environment
# Then initialize without passing the key
client = unsent()
```

### Sending Emails

#### Simple Email

```python
data, error = client.emails.send({
    "to": "hello@acme.com",
    "from": "hello@company.com",
    "subject": "unsent email",
    "html": "<p>unsent is the best open source product to send emails</p>",
    "text": "unsent is the best open source product to send emails",
})

if error:
    print(f"Error: {error}")
else:
    print(f"Email sent! ID: {data['id']}")
```

#### Email with Attachments

```python
data, error = client.emails.send({
    "to": "hello@acme.com",
    "from": "hello@company.com",
    "subject": "Email with attachment",
    "html": "<p>Please find the attachment below</p>",
    "attachments": [
        {
            "filename": "document.pdf",
            "content": "base64-encoded-content-here",
        }
    ],
})
```

#### Scheduled Email

```python
from datetime import datetime, timedelta

# Schedule email for 1 hour from now
scheduled_time = datetime.now() + timedelta(hours=1)

data, error = client.emails.send({
    "to": "hello@acme.com",
    "from": "hello@company.com",
    "subject": "Scheduled email",
    "html": "<p>This email was scheduled</p>",
    "scheduledAt": scheduled_time,
})
```

#### Batch Emails

```python
emails = [
    {
        "to": "user1@example.com",
        "from": "hello@company.com",
        "subject": "Hello User 1",
        "html": "<p>Welcome User 1</p>",
    },
    {
        "to": "user2@example.com",
        "from": "hello@company.com",
        "subject": "Hello User 2",
        "html": "<p>Welcome User 2</p>",
    },
]

data, error = client.emails.batch(emails)

if error:
    print(f"Error: {error}")
else:
    print(f"Sent {len(data['emails'])} emails")
```

### Managing Emails

#### Get Email Details

```python
data, error = client.emails.get("email_id")

if error:
    print(f"Error: {error}")
else:
    print(f"Email status: {data['status']}")
```

#### Update Email

```python
data, error = client.emails.update("email_id", {
    "subject": "Updated subject",
    "html": "<p>Updated content</p>",
})
```

#### Cancel Scheduled Email

```python
data, error = client.emails.cancel("email_id")

if error:
    print(f"Error: {error}")
else:
    print("Email cancelled successfully")
```

### Managing Contacts

#### Create Contact

```python
data, error = client.contacts.create("contact_book_id", {
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "metadata": {
        "company": "Acme Inc",
        "role": "Developer"
    }
})
```

#### Get Contact

```python
data, error = client.contacts.get("contact_book_id", "contact_id")
```

#### Update Contact

```python
data, error = client.contacts.update("contact_book_id", "contact_id", {
    "firstName": "Jane",
    "metadata": {
        "role": "Senior Developer"
    }
})
```

#### Upsert Contact

```python
# Creates if doesn't exist, updates if exists
data, error = client.contacts.upsert("contact_book_id", "contact_id", {
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
})
```

#### Delete Contact

```python
data, error = client.contacts.delete(
    book_id="contact_book_id",
    contact_id="contact_id"
)
```

### Managing Domains

#### List Domains

```python
data, error = client.domains.list()

if error:
    print(f"Error: {error}")
else:
    for domain in data:
        print(f"Domain: {domain['domain']}, Status: {domain['status']}")
```

#### Create Domain

```python
data, error = client.domains.create({
    "domain": "example.com"
})
```

#### Verify Domain

```python
data, error = client.domains.verify(domain_id=123)

if error:
    print(f"Error: {error}")
else:
    print(f"Verification status: {data['status']}")
```

#### Get Domain

```python
data, error = client.domains.get(domain_id=123)
```

### Error Handling

By default, the SDK raises exceptions on HTTP errors:

```python
from unsent import unsent, unsentHTTPError

client = unsent("us_12345")

try:
    data, error = client.emails.send({
        "to": "invalid-email",
        "from": "hello@company.com",
        "subject": "Test",
        "html": "<p>Test</p>",
    })
except unsentHTTPError as e:
    print(f"HTTP {e.status_code}: {e.error['message']}")
```

To disable automatic error raising:

```python
client = unsent("us_12345", raise_on_error=False)

data, error = client.emails.send({
    "to": "hello@acme.com",
    "from": "hello@company.com",
    "subject": "Test",
    "html": "<p>Test</p>",
})

if error:
    print(f"Error: {error['message']}")
else:
    print("Success!")
```

### Custom Session

For advanced use cases, you can provide your own `requests.Session`:

```python
import requests
from unsent import unsent

session = requests.Session()
session.verify = False  # Not recommended for production!

client = unsent("us_12345", session=session)
```

## API Reference

### Client Methods

- `unsent(key, url, raise_on_error=True, session=None)` - Initialize the client

### Email Methods

- `client.emails.send(payload)` - Send an email (alias for `create`)
- `client.emails.create(payload)` - Create and send an email
- `client.emails.batch(emails)` - Send multiple emails in batch
- `client.emails.get(email_id)` - Get email details
- `client.emails.update(email_id, payload)` - Update a scheduled email
- `client.emails.cancel(email_id)` - Cancel a scheduled email

### Contact Methods

- `client.contacts.create(book_id, payload)` - Create a contact
- `client.contacts.get(book_id, contact_id)` - Get contact details
- `client.contacts.update(book_id, contact_id, payload)` - Update a contact
- `client.contacts.upsert(book_id, contact_id, payload)` - Upsert a contact
- `client.contacts.delete(book_id, contact_id)` - Delete a contact

### Domain Methods

- `client.domains.list()` - List all domains
- `client.domains.create(payload)` - Create a domain
- `client.domains.verify(domain_id)` - Verify a domain
- `client.domains.get(domain_id)` - Get domain details

## Requirements

- Python 3.8+
- requests >= 2.32.0
- typing_extensions >= 4.7

## License

MIT
