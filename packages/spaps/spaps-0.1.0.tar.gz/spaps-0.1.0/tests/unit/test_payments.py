import json
from typing import Any, Dict

import pytest
import respx
from httpx import Response

from spaps_client import payments
from spaps_client.crypto import verify_crypto_webhook_signature


@pytest.fixture()
def base_url() -> str:
    return "https://api.sweetpotato.dev"


@pytest.fixture()
def api_key() -> str:
    return "test_key_local_dev_only"


@pytest.fixture()
def access_token() -> str:
    return "access-token"


@pytest.fixture()
def payments_client(base_url: str, api_key: str, access_token: str) -> payments.PaymentsClient:
    return payments.PaymentsClient(base_url=base_url, api_key=api_key, access_token=access_token)


@pytest.fixture()
def checkout_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "session_id": "cs_test_abc123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_abc123",
            "expires_at": "2025-01-09T11:30:00Z",
        },
    }


@pytest.fixture()
def balance_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "balance": {
                "available": 250.0,
                "pending": 100.0,
                "currency": "USD",
            },
            "tier": "premium",
            "tier_expires_at": "2025-02-09T00:00:00Z",
            "usage": {
                "current_period_start": "2025-01-01T00:00:00Z",
                "current_period_end": "2025-01-31T23:59:59Z",
                "credits_used": 150,
                "credits_remaining": 850,
            },
        },
    }


@respx.mock
def test_create_checkout_session_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, checkout_payload: Dict[str, Any]) -> None:
    route = respx.post(f"{base_url}/api/payments/create-checkout-session").mock(return_value=Response(200, json=checkout_payload))

    result = payments_client.create_checkout_session(
        price_id="price_1234567890",
        mode="subscription",
        success_url="https://yourapp.com/success",
        cancel_url="https://yourapp.com/cancel",
        metadata={"user_id": "user_123"},
    )

    assert route.called, "Checkout session endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body == {
        "price_id": "price_1234567890",
        "mode": "subscription",
        "success_url": "https://yourapp.com/success",
        "cancel_url": "https://yourapp.com/cancel",
        "metadata": {"user_id": "user_123"},
    }

    assert result.session_id == checkout_payload["data"]["session_id"]
    assert result.checkout_url == checkout_payload["data"]["checkout_url"]


@respx.mock
def test_create_checkout_session_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.post(f"{base_url}/api/payments/create-checkout-session").mock(
        return_value=Response(400, json={"success": False, "error": {"code": "INVALID_PRICE", "message": "Price not found"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.create_checkout_session(
            price_id="price_missing",
            mode="subscription",
            success_url="https://yourapp.com/success",
            cancel_url="https://yourapp.com/cancel",
        )

    assert exc.value.status_code == 400
    assert exc.value.error_code == "INVALID_PRICE"


@respx.mock
def test_get_balance_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, balance_payload: Dict[str, Any]) -> None:
    route = respx.get(f"{base_url}/api/payments/balance").mock(return_value=Response(200, json=balance_payload))

    result = payments_client.get_balance()

    assert route.called, "Balance endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"

    assert result.balance.available == 250.0
    assert result.balance.currency == "USD"
    assert result.usage.credits_remaining == 850


@respx.mock
def test_get_balance_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.get(f"{base_url}/api/payments/balance").mock(
        return_value=Response(401, json={"success": False, "error": {"code": "UNAUTHORIZED", "message": "Missing token"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.get_balance()

    assert exc.value.status_code == 401
    assert exc.value.error_code == "UNAUTHORIZED"


@pytest.fixture()
def payment_intent_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "payment_intent_id": "pi_12345",
            "client_secret": "pi_12345_secret_67890",
            "status": "requires_confirmation",
        },
    }


@pytest.fixture()
def wallet_deposit_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "deposit_id": "dep_abc123",
            "status": "pending",
            "amount": 100.0,
            "currency": "USDC",
            "confirmation_required": 12,
            "confirmation_current": 0,
        },
    }


@pytest.fixture()
def transaction_status_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "transaction_id": "0x123abc",
            "status": "confirmed",
            "confirmations": 12,
            "chain_type": "ethereum",
            "amount": 100.0,
            "currency": "USDC",
            "balance_added": 100.0,
            "completed_at": "2025-01-09T10:45:00Z",
        },
    }


@pytest.fixture()
def subscription_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "subscription_id": "sub_1234567890",
            "status": "active",
            "plan": {
                "price_id": "price_basic",
                "interval": "month",
            },
            "current_period_end": "2025-01-31T23:59:59Z",
            "cancel_at_period_end": False,
        },
    }


@pytest.fixture()
def cancel_subscription_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "subscription_id": "sub_1234567890",
            "status": "cancelling",
            "cancel_at_period_end": True,
        },
    }


@pytest.fixture()
def update_payment_method_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "message": "Default payment method updated",
            "customer_id": "cus_123",
            "payment_method_id": "pm_abc123",
            "is_default": True,
        },
    }


@pytest.fixture()
def crypto_invoice_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "invoice": {
                "invoice_id": "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE",
                "asset": "USDC",
                "network": "base",
                "amount": "42.75",
                "status": "pending",
                "expires_at": "2025-01-09T10:45:00Z",
                "metadata": {
                    "order_id": "ord_123",
                    "application_id": "app_789"
                },
            }
        },
    }


@pytest.fixture()
def crypto_invoice_status_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "invoice_id": "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE",
            "status": "confirmed",
            "finalized_at": "2025-01-09T11:00:00Z",
            "normalized_amount": "42.75",
            "settlement_ids": ["ledg_01J1CK5K3QPKM783X2TSZGSQEG"],
        },
    }


@pytest.fixture()
def crypto_reconcile_payload() -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "job_id": "job_123",
            "scheduled_at": "2025-01-09T11:05:00Z",
            "cursor": {
                "last_invoice_id": "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE"
            },
        },
    }


@respx.mock
def test_create_payment_intent_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, payment_intent_payload: Dict[str, Any]) -> None:
    route = respx.post(f"{base_url}/api/payments/create-payment-intent").mock(return_value=Response(200, json=payment_intent_payload))

    result = payments_client.create_payment_intent(
        amount=5000,
        currency="usd",
        payment_method_types=["card"],
        metadata={"order_id": "order_123"},
    )

    assert route.called, "Create payment intent endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body == {
        "amount": 5000,
        "currency": "usd",
        "payment_method_types": ["card"],
        "metadata": {"order_id": "order_123"},
    }

    assert result.payment_intent_id == "pi_12345"
    assert result.status == "requires_confirmation"


@respx.mock
def test_create_payment_intent_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.post(f"{base_url}/api/payments/create-payment-intent").mock(
        return_value=Response(402, json={"success": False, "error": {"code": "CARD_DECLINED", "message": "Card declined"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.create_payment_intent(amount=5000, currency="usd", payment_method_types=["card"])

    assert exc.value.status_code == 402
    assert exc.value.error_code == "CARD_DECLINED"


@respx.mock
def test_wallet_deposit_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, wallet_deposit_payload: Dict[str, Any]) -> None:
    route = respx.post(f"{base_url}/api/payments/wallet-deposit").mock(return_value=Response(200, json=wallet_deposit_payload))

    result = payments_client.wallet_deposit(
        wallet_address="0x742d35Cc6637C0532925a3b844Bc454e2b3edb19",
        chain_type="ethereum",
        transaction_id="0x123abc",
        amount=100.0,
        currency="USDC",
        tier="premium",
    )

    assert route.called, "Wallet deposit endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body == {
        "wallet_address": "0x742d35Cc6637C0532925a3b844Bc454e2b3edb19",
        "chain_type": "ethereum",
        "transaction_id": "0x123abc",
        "amount": 100.0,
        "currency": "USDC",
        "tier": "premium",
    }

    assert result.deposit_id == "dep_abc123"
    assert result.status == "pending"


@respx.mock
def test_wallet_deposit_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.post(f"{base_url}/api/payments/wallet-deposit").mock(
        return_value=Response(422, json={"success": False, "error": {"code": "INVALID_TRANSACTION", "message": "Transaction already processed"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.wallet_deposit(
            wallet_address="0x742d35Cc6637C0532925a3b844Bc454e2b3edb19",
            chain_type="ethereum",
            transaction_id="0x123abc",
            amount=100.0,
            currency="USDC",
        )

    assert exc.value.status_code == 422
    assert exc.value.error_code == "INVALID_TRANSACTION"


@respx.mock
def test_update_payment_method_success(
    payments_client: payments.PaymentsClient,
    base_url: str,
    api_key: str,
    access_token: str,
    update_payment_method_payload: Dict[str, Any],
) -> None:
    route = respx.post(f"{base_url}/api/payments/update-payment-method").mock(
        return_value=Response(200, json=update_payment_method_payload)
    )

    result = payments_client.update_payment_method(payment_method_id="pm_abc123", set_default=True)

    assert route.called, "Update payment method endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body == {"payment_method_id": "pm_abc123", "set_default": True}

    assert result.payment_method_id == "pm_abc123"
    assert result.is_default is True
    assert "updated" in result.message


@respx.mock
def test_update_payment_method_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.post(f"{base_url}/api/payments/update-payment-method").mock(
        return_value=Response(404, json={"success": False, "error": {"code": "PAYMENT_METHOD_NOT_FOUND", "message": "Payment method not found"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.update_payment_method(payment_method_id="pm_missing")

    assert exc.value.status_code == 404
    assert exc.value.error_code == "PAYMENT_METHOD_NOT_FOUND"


@respx.mock
def test_crypto_create_invoice_success(
    payments_client: payments.PaymentsClient,
    base_url: str,
    api_key: str,
    access_token: str,
    crypto_invoice_payload: Dict[str, Any],
) -> None:
    route = respx.post(f"{base_url}/api/payments/crypto/invoices").mock(return_value=Response(200, json=crypto_invoice_payload))

    invoice = payments_client.crypto.create_invoice(
        asset="USDC",
        network="base",
        amount="42.75",
        expires_in_seconds=900,
        metadata={"order_id": "ord_123"},
    )

    assert route.called, "Create crypto invoice endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body["asset"] == "USDC"
    assert body["network"] == "base"
    assert body["amount"] == "42.75"
    assert body["expires_in_seconds"] == 900
    assert body["metadata"] == {"order_id": "ord_123"}

    assert invoice.invoice_id == "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE"
    assert invoice.status == "pending"


@respx.mock
def test_crypto_get_invoice_success(
    payments_client: payments.PaymentsClient,
    base_url: str,
    crypto_invoice_payload: Dict[str, Any],
) -> None:
    respx.get(f"{base_url}/api/payments/crypto/invoices/inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE").mock(return_value=Response(200, json=crypto_invoice_payload))

    invoice = payments_client.crypto.get_invoice("inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE")

    assert invoice.invoice_id == "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE"
    assert invoice.amount == "42.75"


@respx.mock
def test_crypto_get_invoice_status(
    payments_client: payments.PaymentsClient,
    base_url: str,
    crypto_invoice_status_payload: Dict[str, Any],
) -> None:
    respx.get(f"{base_url}/api/payments/crypto/invoices/inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE/status").mock(return_value=Response(200, json=crypto_invoice_status_payload))

    status = payments_client.crypto.get_invoice_status("inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE")

    assert status.invoice_id == "inv_01J1CJZ3H6TQ1FA6HJX2Y5M3VE"
    assert status.status == "confirmed"
    assert status.normalized_amount == "42.75"


@respx.mock
def test_crypto_reconcile(
    payments_client: payments.PaymentsClient,
    base_url: str,
    api_key: str,
    access_token: str,
    crypto_reconcile_payload: Dict[str, Any],
) -> None:
    route = respx.post(f"{base_url}/api/payments/crypto/reconcile").mock(return_value=Response(200, json=crypto_reconcile_payload))

    job = payments_client.crypto.reconcile(recon_token="recon_123", cursor={"last_invoice_id": "inv_123"})

    assert route.called, "Crypto reconcile endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    assert request.headers["X-Recon-Token"] == "recon_123"
    assert json.loads(request.content.decode()) == {"cursor": {"last_invoice_id": "inv_123"}}

    assert job.job_id == "job_123"
    assert "scheduled_at" in job.model_dump()


def test_verify_crypto_webhook_signature_success() -> None:
    import hmac
    import hashlib
    import time

    body = {"data": {"invoice_id": "inv_123", "amount": "10.0"}}
    secret = "super-secret"
    timestamp = str(int(time.time()))
    raw_body = json.dumps(body, separators=(",", ":"))
    expected = hmac.new(secret.encode(), f"{timestamp}.{raw_body}".encode(), hashlib.sha256).hexdigest()
    signature = f"t={timestamp},v1={expected}"

    assert verify_crypto_webhook_signature(body=body, signature=signature, secret=secret) is True


def test_verify_crypto_webhook_signature_invalid() -> None:
    import time

    body = {"data": {"invoice_id": "inv_123"}}
    secret = "super-secret"
    timestamp = str(int(time.time()))
    signature = f"t={timestamp},v1=deadbeef"

    with pytest.raises(ValueError):
        verify_crypto_webhook_signature(body=body, signature=signature, secret=secret)

@respx.mock
def test_get_wallet_transaction_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, transaction_status_payload: Dict[str, Any]) -> None:
    route = respx.get(f"{base_url}/api/payments/wallet-transaction/0x123abc").mock(return_value=Response(200, json=transaction_status_payload))

    result = payments_client.get_wallet_transaction(transaction_id="0x123abc")

    assert route.called, "Wallet transaction endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"

    assert result.transaction_id == "0x123abc"
    assert result.status == "confirmed"
    assert result.balance_added == 100.0


@respx.mock
def test_get_wallet_transaction_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.get(f"{base_url}/api/payments/wallet-transaction/0xmissing").mock(
        return_value=Response(404, json={"success": False, "error": {"code": "TRANSACTION_NOT_FOUND", "message": "Not found"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.get_wallet_transaction(transaction_id="0xmissing")

    assert exc.value.status_code == 404
    assert exc.value.error_code == "TRANSACTION_NOT_FOUND"


@respx.mock
def test_get_subscription_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, subscription_payload: Dict[str, Any]) -> None:
    route = respx.get(f"{base_url}/api/payments/subscription/sub_1234567890").mock(return_value=Response(200, json=subscription_payload))

    result = payments_client.get_subscription(subscription_id="sub_1234567890")

    assert route.called, "Subscription endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"

    assert result.subscription_id == "sub_1234567890"
    assert result.status == "active"
    assert result.plan.interval == "month"


@respx.mock
def test_get_subscription_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.get(f"{base_url}/api/payments/subscription/sub_missing").mock(
        return_value=Response(404, json={"success": False, "error": {"code": "SUBSCRIPTION_NOT_FOUND", "message": "Not found"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.get_subscription(subscription_id="sub_missing")

    assert exc.value.status_code == 404
    assert exc.value.error_code == "SUBSCRIPTION_NOT_FOUND"


@respx.mock
def test_cancel_subscription_success(payments_client: payments.PaymentsClient, base_url: str, api_key: str, access_token: str, cancel_subscription_payload: Dict[str, Any]) -> None:
    route = respx.post(f"{base_url}/api/payments/cancel-subscription").mock(return_value=Response(200, json=cancel_subscription_payload))

    result = payments_client.cancel_subscription(
        subscription_id="sub_1234567890",
        cancel_at_period_end=True,
    )

    assert route.called, "Cancel subscription endpoint not called"
    request = route.calls.last.request
    assert request.headers["X-API-Key"] == api_key
    assert request.headers["Authorization"] == f"Bearer {access_token}"
    body = json.loads(request.content.decode())
    assert body == {
        "subscription_id": "sub_1234567890",
        "cancel_at_period_end": True,
    }

    assert result.status == "cancelling"
    assert result.cancel_at_period_end is True


@respx.mock
def test_cancel_subscription_error(payments_client: payments.PaymentsClient, base_url: str) -> None:
    respx.post(f"{base_url}/api/payments/cancel-subscription").mock(
        return_value=Response(400, json={"success": False, "error": {"code": "INVALID_SUBSCRIPTION", "message": "Already cancelled"}}),
    )

    with pytest.raises(payments.PaymentsError) as exc:
        payments_client.cancel_subscription(subscription_id="sub_1234567890")

    assert exc.value.status_code == 400
    assert exc.value.error_code == "INVALID_SUBSCRIPTION"
