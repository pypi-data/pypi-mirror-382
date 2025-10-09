"""Middleware components for FraiseQL."""

# Import non-Redis classes first
from .rate_limiter import (
    InMemoryRateLimiter,
    RateLimitConfig,
    RateLimiterMiddleware,
    RateLimitExceeded,
    RateLimitInfo,
    SlidingWindowRateLimiter,
)

# Lazy import Redis-dependent classes
try:
    from .rate_limiter import RedisRateLimiter

    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False

    class RedisRateLimiter:
        """Placeholder class when Redis is not available."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Redis is required for RedisRateLimiter. "
                "Install it with: pip install fraiseql[redis]",
            )


# Import APQ middleware components
from .apq import (
    create_apq_error_response,
    get_apq_hash,
    handle_apq_request,
    is_apq_request,
    is_apq_with_query_request,
)

__all__ = [
    "InMemoryRateLimiter",
    "RateLimitConfig",
    "RateLimitExceeded",
    "RateLimitInfo",
    "RateLimiterMiddleware",
    "RedisRateLimiter",
    "SlidingWindowRateLimiter",
    # APQ middleware
    "create_apq_error_response",
    "get_apq_hash",
    "handle_apq_request",
    "is_apq_request",
    "is_apq_with_query_request",
]
