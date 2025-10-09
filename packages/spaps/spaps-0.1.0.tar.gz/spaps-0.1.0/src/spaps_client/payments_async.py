"""
Async payments client mirroring the synchronous PaymentsClient API.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .payments import (
    PaymentsError,
    CheckoutSession,
    PaymentIntent,
    WalletDeposit,
    WalletTransaction,
    SubscriptionDetail,
    SubscriptionCancellation,
    BalanceOverview,
    PaymentMethodUpdateResult,
)
from .crypto_async import AsyncCryptoPaymentsClient


class AsyncPaymentsClient:
    PAYMENTS_PREFIX = "/api/payments"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        access_token: str,
        client: Optional[httpx.AsyncClient] = None,
        request_timeout: float | httpx.Timeout = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=request_timeout)
        self._owns_client = client is None
        self.crypto = AsyncCryptoPaymentsClient(client=self._client, header_builder=self._build_headers)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def create_checkout_session(
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
        data = await self._post(
            "/create-checkout-session",
            json=payload,
            access_token_override=access_token_override,
        )
        return CheckoutSession.model_validate(data)

    async def get_balance(self, *, access_token_override: Optional[str] = None) -> BalanceOverview:
        data = await self._get("/balance", access_token_override=access_token_override)
        return BalanceOverview.model_validate(data)

    async def create_payment_intent(
        self,
        *,
        amount: int,
        currency: str,
        payment_method_types: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        access_token_override: Optional[str] = None,
    ) -> PaymentIntent:
        payload: Dict[str, Any] = {"amount": amount, "currency": currency}
        if payment_method_types is not None:
            payload["payment_method_types"] = payment_method_types
        if metadata:
            payload["metadata"] = metadata
        data = await self._post(
            "/create-payment-intent",
            json=payload,
            access_token_override=access_token_override,
        )
        return PaymentIntent.model_validate(data)

    async def update_payment_method(
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
        data = await self._post(
            "/update-payment-method",
            json=payload,
            access_token_override=access_token_override,
        )
        return PaymentMethodUpdateResult.model_validate(data)

    async def wallet_deposit(
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
        data = await self._post(
            "/wallet-deposit",
            json=payload,
            access_token_override=access_token_override,
        )
        return WalletDeposit.model_validate(data)

    async def get_wallet_transaction(
        self,
        *,
        transaction_id: str,
        access_token_override: Optional[str] = None,
    ) -> WalletTransaction:
        data = await self._get(
            f"/wallet-transaction/{transaction_id}",
            access_token_override=access_token_override,
        )
        return WalletTransaction.model_validate(data)

    async def get_subscription(
        self,
        *,
        subscription_id: str,
        access_token_override: Optional[str] = None,
    ) -> SubscriptionDetail:
        data = await self._get(
            f"/subscription/{subscription_id}",
            access_token_override=access_token_override,
        )
        return SubscriptionDetail.model_validate(data)

    async def cancel_subscription(
        self,
        *,
        subscription_id: str,
        cancel_at_period_end: Optional[bool] = None,
        access_token_override: Optional[str] = None,
    ) -> SubscriptionCancellation:
        payload: Dict[str, Any] = {"subscription_id": subscription_id}
        if cancel_at_period_end is not None:
            payload["cancel_at_period_end"] = cancel_at_period_end
        data = await self._post(
            "/cancel-subscription",
            json=payload,
            access_token_override=access_token_override,
        )
        return SubscriptionCancellation.model_validate(data)

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        access_token_override: Optional[str],
    ) -> Dict[str, Any]:
        response = await self._client.get(
            f"{self.PAYMENTS_PREFIX}{path}",
            headers=self._build_headers(access_token_override),
            params=params,
        )
        return await self._parse_response(response)

    async def _post(
        self,
        path: str,
        *,
        json: Dict[str, Any],
        access_token_override: Optional[str],
    ) -> Dict[str, Any]:
        response = await self._client.post(
            f"{self.PAYMENTS_PREFIX}{path}",
            json=json,
            headers=self._build_headers(access_token_override),
        )
        return await self._parse_response(response)

    def _build_headers(self, access_token_override: Optional[str]) -> Dict[str, str]:
        token = access_token_override or self.access_token
        if not token:
            raise ValueError("Access token is required for payment operations")
        return {"X-API-Key": self.api_key, "Authorization": f"Bearer {token}"}

    async def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        if response.status_code >= 400:
            raise await self._build_error(response)
        payload = response.json()
        return payload.get("data", payload)

    @staticmethod
    async def _build_error(response: httpx.Response) -> PaymentsError:
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


__all__ = ["AsyncPaymentsClient"]
