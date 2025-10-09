"""
Sweet Potato Authentication & Payment Service Python client.

This package exposes modules for authentication, session management,
payments, and supporting utilities as implementation progresses.
"""

from .auth import AuthClient, AuthError, NonceResponse, TokenPair, TokenUser
from .sessions import (
    SessionError,
    SessionSummary,
    SessionValidationResult,
    SessionListResult,
    SessionRecord,
    SessionTouchResult,
    SessionRevokeResult,
    SessionsClient,
)
from .payments import (
    PaymentsClient,
    PaymentsError,
    CheckoutSession,
    PaymentIntent,
    WalletDeposit,
    WalletTransaction,
    SubscriptionPlan,
    SubscriptionDetail,
    SubscriptionCancellation,
    BalanceOverview,
    BalanceAmounts,
    UsageSummary,
    PaymentMethodUpdateResult,
)
from .whitelist import (
    WhitelistClient,
    WhitelistError,
    WhitelistEntry,
    WhitelistCheckResult,
    WhitelistListResult,
    WhitelistMessage,
)
from .config import Settings, create_http_client
from .crypto import (
    CryptoPaymentsClient,
    CryptoPaymentsError,
    CryptoInvoice,
    CryptoInvoiceStatus,
    CryptoReconcileJob,
    verify_crypto_webhook_signature,
)
from .usage import (
    UsageClient,
    UsageError,
    UsagePeriod,
    UsageFeature,
    UsageFeaturesResponse,
    UsageRecordUsage,
    UsageRecordResult,
    UsageHistoryEntry,
    UsageHistoryResponse,
)
from .secure_messages import (
    SecureMessagesClient,
    SecureMessagesError,
    SecureMessage,
)
from .metrics import MetricsClient
from .auth_async import AsyncAuthClient
from .sessions_async import AsyncSessionsClient
from .payments_async import AsyncPaymentsClient
from .usage_async import AsyncUsageClient
from .whitelist_async import AsyncWhitelistClient
from .secure_messages_async import AsyncSecureMessagesClient
from .metrics_async import AsyncMetricsClient
from .crypto_async import AsyncCryptoPaymentsClient
from .async_client import AsyncSpapsClient
from .http_async import RetryAsyncClient
from .client import SpapsClient
from .storage import (
    StoredTokens,
    TokenStorage,
    InMemoryTokenStorage,
    FileTokenStorage,
)
from .http import RetryConfig, LoggingHooks, default_logging_hooks

__all__ = [
    "__version__",
    "AuthClient",
    "AuthError",
    "NonceResponse",
    "TokenPair",
    "TokenUser",
    "SessionsClient",
    "SessionListResult",
    "SessionRecord",
    "SessionTouchResult",
    "SessionRevokeResult",
    "PaymentsClient",
    "PaymentsError",
    "CheckoutSession",
    "PaymentIntent",
    "WalletDeposit",
    "WalletTransaction",
    "SubscriptionPlan",
    "SubscriptionDetail",
    "SubscriptionCancellation",
    "BalanceOverview",
    "BalanceAmounts",
    "UsageSummary",
    "PaymentMethodUpdateResult",
    "WhitelistClient",
    "WhitelistError",
    "WhitelistEntry",
    "WhitelistCheckResult",
    "WhitelistListResult",
    "WhitelistMessage",
    "Settings",
    "create_http_client",
    "SessionError",
    "SessionSummary",
    "SessionValidationResult",
    "CryptoPaymentsClient",
    "CryptoPaymentsError",
    "CryptoInvoice",
    "CryptoInvoiceStatus",
    "CryptoReconcileJob",
    "verify_crypto_webhook_signature",
    "UsageClient",
    "UsageError",
    "UsagePeriod",
    "UsageFeature",
    "UsageFeaturesResponse",
    "UsageRecordUsage",
    "UsageRecordResult",
    "UsageHistoryEntry",
    "UsageHistoryResponse",
    "SecureMessagesClient",
    "SecureMessagesError",
    "SecureMessage",
    "MetricsClient",
    "SpapsClient",
    "AsyncSpapsClient",
    "AsyncAuthClient",
    "AsyncSessionsClient",
    "AsyncPaymentsClient",
    "AsyncUsageClient",
    "AsyncWhitelistClient",
    "AsyncSecureMessagesClient",
    "AsyncMetricsClient",
    "AsyncCryptoPaymentsClient",
    "RetryAsyncClient",
    "StoredTokens",
    "TokenStorage",
    "InMemoryTokenStorage",
    "FileTokenStorage",
    "RetryConfig",
    "LoggingHooks",
    "default_logging_hooks",
]

# Temporary development version; replaced during release automation.
__version__ = "0.1.0"
