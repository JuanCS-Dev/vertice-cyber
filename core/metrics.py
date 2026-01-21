"""
Sistema de Métricas para Providers.

Rastreia uso de providers e fallbacks.
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from collections import defaultdict
from functools import wraps

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderMetrics(BaseModel):
    """Métricas de um provider."""

    name: str
    calls_total: int = 0
    calls_success: int = 0
    calls_failed: int = 0
    fallback_triggered: int = 0
    last_used: Optional[str] = None


class MetricsCollector:
    """Coletor de métricas de providers."""

    def __init__(self):
        self._metrics: Dict[str, ProviderMetrics] = defaultdict(
            lambda: ProviderMetrics(name="unknown")
        )

    def record_call(self, provider: str, success: bool) -> None:
        """Registra chamada a provider."""
        if provider not in self._metrics:
            self._metrics[provider] = ProviderMetrics(name=provider)

        m = self._metrics[provider]
        m.calls_total += 1
        if success:
            m.calls_success += 1
        else:
            m.calls_failed += 1
        m.last_used = datetime.utcnow().isoformat()

    def record_fallback(self, from_provider: str, to_provider: str) -> None:
        """Registra fallback entre providers."""
        if from_provider not in self._metrics:
            self._metrics[from_provider] = ProviderMetrics(name=from_provider)

        self._metrics[from_provider].fallback_triggered += 1
        logger.info(f"Fallback: {from_provider} -> {to_provider}")

    def get_all_metrics(self) -> Dict[str, ProviderMetrics]:
        """Retorna todas as métricas."""
        return dict(self._metrics)

    def get_summary(self) -> Dict[str, Any]:
        """Retorna sumário das métricas."""
        total_calls = sum(m.calls_total for m in self._metrics.values())
        total_fallbacks = sum(m.fallback_triggered for m in self._metrics.values())

        return {
            "total_calls": total_calls,
            "total_fallbacks": total_fallbacks,
            "fallback_rate": round(total_fallbacks / max(total_calls, 1), 4),
            "providers": {k: v.model_dump() for k, v in self._metrics.items()},
        }


# Singleton
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Retorna singleton do coletor."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def track_provider_usage(provider_name: str):
    """
    Decorator para rastrear uso de provider.

    Usage:
        @track_provider_usage("hibp")
        async def call_hibp():
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            try:
                import asyncio

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                collector.record_call(provider_name, success=True)
                return result
            except Exception:
                collector.record_call(provider_name, success=False)
                raise

        return wrapper

    return decorator


async def provider_metrics_tool(ctx) -> Dict[str, Any]:
    """MCP Tool: Retorna métricas de providers."""
    await ctx.info("Coletando métricas de providers...")

    collector = get_metrics_collector()
    summary = collector.get_summary()

    await ctx.info(
        f"Total calls: {summary['total_calls']}, Fallbacks: {summary['total_fallbacks']}"
    )

    return summary
