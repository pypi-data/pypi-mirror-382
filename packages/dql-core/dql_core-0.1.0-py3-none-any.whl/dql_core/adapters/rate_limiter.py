"""Rate limiting utilities for API adapters."""

import time
from typing import Optional


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second: float):
        """Initialize rate limiter.

        Args:
            calls_per_second: Maximum number of calls allowed per second
        """
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time: Optional[float] = None

    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.last_call_time is not None:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()

    def reset(self) -> None:
        """Reset rate limiter state."""
        self.last_call_time = None
