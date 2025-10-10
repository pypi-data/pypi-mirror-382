"""External API adapter framework."""

from dql_core.adapters.base import ExternalAPIAdapter
from dql_core.adapters.factory import APIAdapterFactory, default_adapter_factory
from dql_core.adapters.rate_limiter import RateLimiter
from dql_core.adapters.retry import retry_with_backoff

__all__ = [
    "ExternalAPIAdapter",
    "APIAdapterFactory",
    "default_adapter_factory",
    "RateLimiter",
    "retry_with_backoff",
]
