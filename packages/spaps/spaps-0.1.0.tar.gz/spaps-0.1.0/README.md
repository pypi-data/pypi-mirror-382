---
id: spaps-python-sdk
title: Sweet Potato Python Client
category: sdk
tags:
  - sdk
  - python
  - client
ai_summary: |
  Explains installation, configuration, and usage patterns for the spaps Python
  SDK, including environment setup, async support, and integration guidance for
  backend services.
last_updated: 2025-02-14
---

# Sweet Potato Python Client

> Python SDK for the Sweet Potato Authentication & Payment Service (SPAPS).

This package is under active development. Follow the TDD plan in `TDD_PLAN.md`
to track progress and upcoming milestones.

## Installation

Install from PyPI:

```bash
pip install spaps
```

For local development inside this repository:

```bash
pip install -e .[dev]
```

## Development

```bash
pytest
```

### Available clients

- `AuthClient` – wallet, email/password, and magic link flows
- `SessionsClient` – current session, validation, listing, revocation
- `PaymentsClient` – checkout sessions, wallet deposits, crypto invoices
- `UsageClient` – feature usage snapshots, recording, aggregated history
- `SecureMessagesClient` – encrypted message creation and retrieval
- `MetricsClient` – health and metrics convenience helpers

### Quickstart

```python
from spaps_client import SpapsClient

spaps = SpapsClient(base_url="http://localhost:3300", api_key="test_key_local_dev_only")

# Authenticate (tokens are persisted automatically)
spaps.auth.sign_in_with_password(email="user@example.com", password="Secret123!")

# Call downstream services using the stored access token
current = spaps.sessions.get_current_session()
print(current.session_id)

checkout = spaps.payments.create_checkout_session(
    price_id="price_123",
    mode="subscription",
    success_url="https://example.com/success",
    cancel_url="https://example.com/cancel",
)
print(checkout.checkout_url)

spaps.close()
```

Configure retry/backoff and structured logging when constructing the client:

```python
from spaps_client import SpapsClient, RetryConfig, default_logging_hooks

spaps = SpapsClient(
    base_url="http://localhost:3300",
    api_key="test_key_local_dev_only",
    retry_config=RetryConfig(max_attempts=4, backoff_factor=0.2),
    logging_hooks=default_logging_hooks(),
)
```

### Async Quickstart

```python
import asyncio
from spaps_client import AsyncSpapsClient

async def main():
    client = AsyncSpapsClient(base_url="http://localhost:3300", api_key="test_key_local_dev_only")
    try:
        await client.auth.sign_in_with_password(email="user@example.com", password="Secret123!")
        current = await client.sessions.list_sessions()
        print(len(current.sessions))
    finally:
        await client.aclose()

asyncio.run(main())
```

### Useful Scripts

```bash
npm run test:python-client   # run pytest from repo root
npm run lint:python-client   # ruff linting
npm run typecheck:python-client # mypy type checking
npm run build:python-client  # build wheel/sdist and run twine check
npm run publish:python-client # build and upload via twine (requires PYPI_TOKEN)
```

Refer to `docs/RELEASE_CHECKLIST.md` for the full release process.

Refer to the repository root documentation for integration details.

## Documentation

- [Quickstart (Python section)](../../docs/getting-started/quickstart.md#python-example---using-spaps)
- [Python Backend Integration Guide](../../docs/guides/python-backend.md)
- API references under `docs/api/` include Python usage snippets for sessions, payments, usage, whitelist, and secure messages.
