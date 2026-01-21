"""
Rate Limiter client-side usando asyncio.

HIBP limita 1 request a cada 1.5 segundos.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """Rate limiter baseado em token bucket."""

    def __init__(self, requests_per_second: float = 0.67):  # 1/1.5s
        self.min_interval = 1.0 / requests_per_second
        self._last_request = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Aguarda até poder fazer próximo request."""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_request

            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            self._last_request = time.time()


# Rate limiters por serviço
_limiters: dict[str, RateLimiter] = {}


def get_rate_limiter(service: str, rps: float = 0.67) -> RateLimiter:
    """Retorna rate limiter para serviço."""
    if service not in _limiters:
        _limiters[service] = RateLimiter(rps)
    return _limiters[service]


def rate_limit(service: str, rps: float = 0.67) -> Callable:
    """
    Decorator para aplicar rate limiting.

    Usage:
        @rate_limit("hibp", rps=0.67)
        async def call_hibp(email: str):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            limiter = get_rate_limiter(service, rps)
            await limiter.acquire()
            import asyncio

            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
