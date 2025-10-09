import json

import pytest
import pytest_asyncio
import respx
from httpx import Response

from spaps_client import AsyncSpapsClient, InMemoryTokenStorage


@pytest_asyncio.fixture()
async def async_client() -> AsyncSpapsClient:
    storage = InMemoryTokenStorage()
    client = AsyncSpapsClient(
        base_url="https://api.sweetpotato.dev",
        api_key="test_key_local_dev_only",
        token_storage=storage,
    )
    yield client
    await client.aclose()


"""Return token storage for tests."""

@pytest.fixture()
def storage(async_client: AsyncSpapsClient) -> InMemoryTokenStorage:
    return async_client.token_storage  # type: ignore[return-value]


@pytest.fixture()
def login_payload() -> dict:
    return {
        "success": True,
        "data": {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "expires_in": 900,
            "token_type": "Bearer",
            "user": {"id": "user_123", "email": "user@example.com"},
        },
    }


@pytest.mark.asyncio
@respx.mock
async def test_async_sign_in_persists_tokens(async_client: AsyncSpapsClient, storage: InMemoryTokenStorage, login_payload: dict) -> None:
    base_url = "https://api.sweetpotato.dev"
    respx.post(f"{base_url}/api/auth/login").mock(return_value=Response(200, json=login_payload))
    respx.get(f"{base_url}/api/sessions").mock(return_value=Response(200, json={"data": {"sessions": [], "total": 0}}))

    tokens = await async_client.auth.sign_in_with_password(email="user@example.com", password="Secret123!")
    assert tokens.access_token == "access-token"
    stored = storage.load()
    assert stored is not None
    assert stored.access_token == "access-token"

    await async_client.sessions.list_sessions()


@pytest.mark.asyncio
@respx.mock
async def test_async_payments_uses_stored_token(async_client: AsyncSpapsClient) -> None:
    base_url = "https://api.sweetpotato.dev"
    async_client.set_tokens(access_token="stored-access")

    payload = {
        "success": True,
        "data": {
            "session_id": "cs_test",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test",
        },
    }
    route = respx.post(f"{base_url}/api/payments/create-checkout-session").mock(return_value=Response(200, json=payload))

    await async_client.payments.create_checkout_session(
        price_id="price_123",
        mode="subscription",
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
    )

    sent_request = route.calls.last.request
    assert json.loads(sent_request.content.decode())["price_id"] == "price_123"
    assert sent_request.headers["Authorization"] == "Bearer stored-access"


@pytest.mark.asyncio
@respx.mock
async def test_async_payments_crypto(async_client: AsyncSpapsClient) -> None:
    base_url = "https://api.sweetpotato.dev"
    async_client.set_tokens(access_token="stored-access")

    payload = {
        "success": True,
        "data": {
            "invoice": {
                "id": "inv_123",
                "asset": "USDC",
                "network": "base",
                "amount": "10",
                "status": "pending",
            }
        },
    }
    route = respx.post(f"{base_url}/api/payments/crypto/invoices").mock(return_value=Response(200, json=payload))

    invoice = await async_client.payments.crypto.create_invoice(asset="USDC", network="base", amount="10")
    assert invoice.invoice_id == "inv_123"
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_async_metrics(async_client: AsyncSpapsClient) -> None:
    base_url = "https://api.sweetpotato.dev"
    respx.get(f"{base_url}/health").mock(return_value=Response(200, json={"status": "ok"}))
    payload = await async_client.metrics.health()
    assert payload["status"] == "ok"
