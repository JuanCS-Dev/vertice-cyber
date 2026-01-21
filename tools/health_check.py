"""
Health Check para todos os providers.

Retorna status de cada provider configurado.
"""

import os
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderHealth(BaseModel):
    """Status de saúde de um provider."""

    name: str
    status: str  # healthy, degraded, unavailable
    latency_ms: float
    last_check: str
    error: Optional[str] = None


class HealthCheckResult(BaseModel):
    """Resultado completo do health check."""

    overall_status: str
    providers: List[ProviderHealth]
    timestamp: str


async def provider_health_check(ctx) -> Dict[str, Any]:
    """
    MCP Tool: Verifica saúde de todos os providers.

    Returns:
        Status de cada provider com latência e erros
    """
    await ctx.info("Executando health check de providers...")

    providers_status = []

    # 1. HIBP Provider
    providers_status.append(await _check_hibp())

    # 2. OTX Provider
    providers_status.append(await _check_otx())

    # 3. VirusTotal Provider
    providers_status.append(await _check_vt())

    # 4. Redis Cache
    providers_status.append(await _check_redis())

    # Calcular status geral
    statuses = [p.status for p in providers_status]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unavailable" for s in statuses):
        overall = "degraded"
    else:
        overall = "partial"

    result = HealthCheckResult(
        overall_status=overall,
        providers=providers_status,
        timestamp=datetime.utcnow().isoformat(),
    )

    await ctx.info(f"Health check completo: {overall}")

    return result.model_dump()


async def _check_hibp() -> ProviderHealth:
    """Verifica HIBP provider."""
    start = time.perf_counter()

    api_key = os.getenv("HIBP_API_KEY")
    if not api_key:
        return ProviderHealth(
            name="hibp",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error="HIBP_API_KEY not configured",
        )

    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Apenas verifica se API responde (endpoint público ou teste simples)
            resp = await client.get(
                "https://haveibeenpwned.com/api/v3/breaches",
                headers={"hibp-api-key": api_key},
            )
            latency = (time.perf_counter() - start) * 1000

            return ProviderHealth(
                name="hibp",
                status="healthy" if resp.status_code == 200 else "degraded",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat(),
                error=None if resp.status_code == 200 else f"HTTP {resp.status_code}",
            )
    except Exception as e:
        return ProviderHealth(
            name="hibp",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e),
        )


async def _check_otx() -> ProviderHealth:
    """Verifica OTX provider."""
    start = time.perf_counter()
    api_key = os.getenv("OTX_API_KEY")
    if not api_key:
        return ProviderHealth(
            name="otx",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error="OTX_API_KEY not set",
        )
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://otx.alienvault.com/api/v1/indicators/IPv4/8.8.8.8/general",
                headers={"X-OTX-API-KEY": api_key},
            )
            latency = (time.perf_counter() - start) * 1000
            return ProviderHealth(
                name="otx",
                status="healthy" if resp.status_code == 200 else "degraded",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat(),
            )
    except Exception as e:
        return ProviderHealth(
            name="otx",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e),
        )


async def _check_vt() -> ProviderHealth:
    """Verifica VirusTotal provider."""
    start = time.perf_counter()
    api_key = os.getenv("VT_API_KEY")
    if not api_key:
        return ProviderHealth(
            name="virustotal",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error="VT_API_KEY not set",
        )
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
                headers={"x-apikey": api_key},
            )
            latency = (time.perf_counter() - start) * 1000
            return ProviderHealth(
                name="virustotal",
                status="healthy" if resp.status_code == 200 else "degraded",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat(),
            )
    except Exception as e:
        return ProviderHealth(
            name="virustotal",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e),
        )


async def _check_redis() -> ProviderHealth:
    """Verifica Redis cache."""
    start = time.perf_counter()

    try:
        from tools.providers.cache import get_cache

        cache = get_cache()
        backend_name = cache._backend.__class__.__name__

        if "Redis" in backend_name:
            latency = (time.perf_counter() - start) * 1000
            return ProviderHealth(
                name="redis",
                status="healthy",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat(),
            )
        else:
            return ProviderHealth(
                name="redis",
                status="unavailable",
                latency_ms=0,
                last_check=datetime.utcnow().isoformat(),
                error="Using JSON fallback instead of Redis",
            )
    except Exception as e:
        return ProviderHealth(
            name="redis",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:50],
        )
