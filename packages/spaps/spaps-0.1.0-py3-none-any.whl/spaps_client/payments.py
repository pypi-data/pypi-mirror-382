"""
Payments helpers for the Sweet Potato Authentication & Payment Service.

This module wraps payment-related endpoints including Stripe checkout sessions
and balance tracking.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel, ConfigDict

from .crypto import CryptoPaymentsClient

__all__ = [
    "PaymentsClient",
    "PaymentsError",
    "CheckoutSession",
    "PaymentIntent",
    "WalletDeposit",
    "WalletTransaction",
    "SubscriptionPlan",
    "SubscriptionDetail",
    "SubscriptionCancellation",
    "BalanceAmounts",
    "UsageSummary",
    "BalanceOverview",
    "PaymentMethodUpdateResult",
]


class PaymentsError(Exception):
    """Raised when a payments endpoint returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_code: Optional[str] = None,
        response: Optional[httpx.Response] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response = response
        self.request_id = request_id


class CheckoutSession(BaseModel):
    """Stripe checkout session metadata."""

    model_config = ConfigDict(extra="ignore")

    session_id: str
    checkout_url: str
    expires_at: Optional[dt.datetime] = None


class PaymentIntent(BaseModel):
    """Stripe payment intent response."""

    model_config = ConfigDict(extra="ignore")

    payment_intent_id: str
    client_secret: Optional[str] = None
    status: Optional[str] = None


class WalletDeposit(BaseModel):
    """Wallet deposit submission status."""

    model_config = ConfigDict(extra="ignore")

    deposit_id: str
    status: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    confirmation_required: Optional[int] = None
    confirmation_current: Optional[int] = None


class WalletTransaction(BaseModel):
    """Wallet transaction confirmation status."""

    model_config = ConfigDict(extra="ignore")

    transaction_id: str
    status: Optional[str] = None
    confirmations: Optional[int] = None
    chain_type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    balance_added: Optional[float] = None
    completed_at: Optional[dt.datetime] = None


class SubscriptionPlan(BaseModel):
    """Subscription plan/price details."""

    model_config = ConfigDict(extra="ignore")

    price_id: Optional[str] = None
    interval: Optional[str] = None


class SubscriptionDetail(BaseModel):
    """Active subscription information."""

    model_config = ConfigDict(extra="ignore")

    subscription_id: str
    status: Optional[str] = None
    plan: SubscriptionPlan
    current_period_end: Optional[dt.datetime] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionCancellation(BaseModel):
    """Cancellation request result."""

    model_config = ConfigDict(extra="ignore")

    subscription_id: str
    status: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None


class BalanceAmounts(BaseModel):
    """Breakdown of available/pending balances."""

    model_config = ConfigDict(extra="ignore")

    available: float
    pending: float
    currency: str


class UsageSummary(BaseModel):
    """Usage metrics for the current billing period."""

    model_config = ConfigDict(extra="ignore")

    current_period_start: Optional[dt.datetime] = None
    current_period_end: Optional[dt.datetime] = None
    credits_used: Optional[int] = None
    credits_remaining: Optional[int] = None


class BalanceOverview(BaseModel):
    """Composite balance information."""

    model_config = ConfigDict(extra="ignore")

    balance: BalanceAmounts
    tier: Optional[str] = None
    tier_expires_at: Optional[dt.datetime] = None
    usage: UsageSummary


class PaymentMethodUpdateResult(BaseModel):
    """Result of updating the default payment method."""

    model_config = ConfigDict(extra="ignore")

    message: Optional[str] = None
    customer_id: Optional[str] = None
    payment_method_id: str
    is_default: bool = False


class PaymentsClient:
    """Client wrapper for payment endpoints."""

    PAYMENTS_PREFIX = "/api/payments"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        access_token: str,
        client: Optional[httpx.Client] = None,
        request_timeout: float | httpx.Timeout = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self._client = client or httpx.Client(base_url=self.base_url, timeout=request_timeout)
        self._owns_client = client is None
        self.crypto: CryptoPaymentsClient = CryptoPaymentsClient(
            client=self._client,
            header_builder=self._build_headers,
        )

    def __enter__(self) -> "PaymentsClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore[override]
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    # Public API

    def create_checkout_session(
        self,
        *,
        price_id: str,
        mode: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, Any]] = None,
        access_token_override: Optional[str] = None,
    ) -> CheckoutSession:
        payload: Dict[str, Any] = {
            "price_id": price_id,
            "mode": mode,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        if metadata:
            payload["metadata"] = metadata

        data = self._post(
            "/create-checkout-session",
            json=payload,
            access_token_override=access_token_override,
        )
        return CheckoutSession.model_validate(data)

    def get_balance(
        self,
        *,
        access_token_override: Optional[str] = None,
    ) -> BalanceOverview:
        data = self._get("/balance", access_token_override=access_token_override)
        return BalanceOverview.model_validate(data)

    def create_payment_intent(
        self,
        *,
        amount: int,
        currency: str,
        payment_method_types: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        access_token_override: Optional[str] = None,
    ) -> PaymentIntent:
        payload: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
        }
        if payment_method_types is not None:
            payload["payment_method_types"] = payment_method_types
        if metadata:
            payload["metadata"] = metadata

        data = self._post(
            "/create-payment-intent",
            json=payload,
            access_token_override=access_token_override,
        )
        return PaymentIntent.model_validate(data)

    def update_payment_method(
        self,
        *,
        payment_method_id: str,
        set_default: Optional[bool] = None,
        access_token_override: Optional[str] = None,
    ) -> PaymentMethodUpdateResult:
        if not payment_method_id:
            raise ValueError("payment_method_id is required")
        payload: Dict[str, Any] = {"payment_method_id": payment_method_id}
        if set_default is not None:
            payload["set_default"] = set_default
        data = self._post(
            "/update-payment-method",
            json=payload,
            access_token_override=access_token_override,
        )
        return PaymentMethodUpdateResult.model_validate(data)

    def wallet_deposit(
        self,
        *,
        wallet_address: str,
        chain_type: str,
        transaction_id: str,
        amount: float,
        currency: str,
        tier: Optional[str] = None,
        access_token_override: Optional[str] = None,
    ) -> WalletDeposit:
        payload: Dict[str, Any] = {
            "wallet_address": wallet_address,
            "chain_type": chain_type,
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
        }
        if tier:
            payload["tier"] = tier

        data = self._post(
            "/wallet-deposit",
            json=payload,
            access_token_override=access_token_override,
        )
        return WalletDeposit.model_validate(data)

    def get_wallet_transaction(
        self,
        *,
        transaction_id: str,
        access_token_override: Optional[str] = None,
    ) -> WalletTransaction:
        data = self._get(
            f"/wallet-transaction/{transaction_id}",
            access_token_override=access_token_override,
        )
        return WalletTransaction.model_validate(data)

    def get_subscription(
        self,
        *,
        subscription_id: str,
        access_token_override: Optional[str] = None,
    ) -> SubscriptionDetail:
        data = self._get(
            f"/subscription/{subscription_id}",
            access_token_override=access_token_override,
        )
        return SubscriptionDetail.model_validate(data)

    def cancel_subscription(
        self,
        *,
        subscription_id: str,
        cancel_at_period_end: Optional[bool] = None,
        access_token_override: Optional[str] = None,
    ) -> SubscriptionCancellation:
        payload: Dict[str, Any] = {"subscription_id": subscription_id}
        if cancel_at_period_end is not None:
            payload["cancel_at_period_end"] = cancel_at_period_end

        data = self._post(
            "/cancel-subscription",
            json=payload,
            access_token_override=access_token_override,
        )
        return SubscriptionCancellation.model_validate(data)

    # Internal helpers

    def _get(self, path: str, *, access_token_override: Optional[str]) -> Dict[str, Any]:
        response = self._client.get(
            f"{self.PAYMENTS_PREFIX}{path}",
            headers=self._build_headers(access_token_override),
        )
        return self._parse_response(response)

    def _post(self, path: str, *, json: Dict[str, Any], access_token_override: Optional[str]) -> Dict[str, Any]:
        response = self._client.post(
            f"{self.PAYMENTS_PREFIX}{path}",
            json=json,
            headers=self._build_headers(access_token_override),
        )
        return self._parse_response(response)

    def _build_headers(self, access_token_override: Optional[str]) -> Dict[str, str]:
        token = access_token_override or self.access_token
        if not token:
            raise ValueError("Access token is required for payment operations")
        return {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}",
        }

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            raise self._build_error(response)
        payload = response.json()
        return payload.get("data", payload)

    @staticmethod
    def _build_error(response: httpx.Response) -> PaymentsError:
        try:
            payload = response.json()
        except ValueError:  # pragma: no cover
            payload = {}
        error_info = payload.get("error", {})
        message = error_info.get("message") or response.text or "Payments request failed"
        request_id = (
            response.headers.get("x-request-id")
            or payload.get("metadata", {}).get("request_id")
        )
        return PaymentsError(
            message,
            status_code=response.status_code,
            error_code=error_info.get("code"),
            response=response,
            request_id=request_id,
        )
