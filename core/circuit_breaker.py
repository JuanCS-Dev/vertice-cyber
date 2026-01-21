"""
Circuit Breaker para APIs externas.

Padrão: 5 falhas → abre circuito por 60s → tenta novamente
"""

import logging
from functools import wraps
from typing import Callable, TypeVar, Any
from circuitbreaker import circuit, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def api_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    fallback: Callable[..., T] | None = None,
    name: str = "api",
) -> Callable:
    """
    Decorator para proteger chamadas de API com circuit breaker.

    Args:
        failure_threshold: Número de falhas antes de abrir
        recovery_timeout: Segundos até tentar novamente
        fallback: Função a chamar quando circuito aberto
        name: Nome para logging

    Example:
        @api_circuit_breaker(fallback=lambda x: [], name="hibp")
        async def check_breaches(email: str) -> List[dict]:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Aplica circuit breaker da lib
        breaker = circuit(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            name=name,
        )
        wrapped = breaker(func)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                # Se for uma função corotina, precisa de await
                import asyncio

                if asyncio.iscoroutinefunction(func):
                    return await wrapped(*args, **kwargs)
                return wrapped(*args, **kwargs)
            except CircuitBreakerError:
                logger.warning(
                    f"Circuit breaker OPEN for {name}. "
                    f"Using fallback. Recovery in {recovery_timeout}s"
                )
                if fallback:
                    if asyncio.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    return fallback(*args, **kwargs)
                raise
            except Exception as e:
                logger.error(f"{name} API error: {e}")
                raise

        return async_wrapper

    return decorator
