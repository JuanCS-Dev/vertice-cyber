"""
VirusTotal Provider - File and URL Reputation API.

API Docs: https://docs.virustotal.com/reference/overview
"""

import os
import logging
from typing import Dict, Optional, Any

import httpx

from core.feature_flags import get_feature_flags
from core.circuit_breaker import api_circuit_breaker
from core.rate_limiter import rate_limit
from tools.providers.base import BaseProvider, ProviderNotConfiguredError

logger = logging.getLogger(__name__)


class VTProvider(BaseProvider[Dict[str, Any]]):
    """
    Provider real para VirusTotal API v3.

    LIMITAÇÕES FREE TIER: 4 requests/min, 500/dia.
    """

    name = "virustotal_real"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.api_key = os.getenv("VT_API_KEY")
        self.base_url = "https://www.virustotal.com/api/v3"
        self.fallback = fallback

    def is_available(self) -> bool:
        flags = get_feature_flags()
        return bool(self.api_key) and flags.threat_use_real_virustotal

    @rate_limit(
        "virustotal", rps=0.05
    )  # ~1 request a cada 20s para respeitar free tier
    @api_circuit_breaker(
        failure_threshold=2,
        recovery_timeout=300,  # 5 minutos se bloquear
        name="virustotal",
    )
    async def execute(
        self, resource: str, type: str = "file", **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Consulta reputação no VirusTotal.

        Args:
            resource: Hash (file) ou URL/IP/Domain
            type: file, url, ip_address, domain
        """
        if not self.api_key:
            raise ProviderNotConfiguredError("VT_API_KEY not set")

        endpoint_map = {
            "file": f"files/{resource}",
            "url": f"urls/{resource}",
            "ip": f"ip_addresses/{resource}",
            "domain": f"domains/{resource}",
        }

        endpoint = endpoint_map.get(type.lower(), f"files/{resource}")

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}", headers={"x-apikey": self.api_key}
            )

            if response.status_code == 404:
                return {"status": "not_found", "last_analysis_stats": {}}

            if response.status_code == 429:
                logger.warning("VirusTotal Rate Limit Exceeded (429)")
                raise httpx.HTTPError("Rate limited")

            response.raise_for_status()
            data = response.json()

            # Caching
            try:
                from tools.providers.cache import get_cache

                get_cache().set(f"vt:{type}:{resource}", data)
            except Exception as e:
                logger.error(f"Failed to cache VT result: {e}")

            return data


class VTCacheProvider(BaseProvider[Dict[str, Any]]):
    """Provider que usa cache local para VirusTotal."""

    name = "virustotal_cache"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.fallback = fallback
        from tools.providers.cache import get_cache

        self.cache = get_cache()

    def is_available(self) -> bool:
        return True

    async def execute(
        self, resource: str, type: str = "file", **kwargs: Any
    ) -> Dict[str, Any]:
        cached_data = self.cache.get(f"vt:{type}:{resource}")
        if cached_data:
            logger.debug(f"Cache hit for VT:{resource}")
            return cached_data

        if self.fallback:
            return await self.fallback.execute_with_fallback(
                resource, type=type, **kwargs
            )

        return {"status": "unknown", "source": "cache_miss"}


def get_vt_provider() -> BaseProvider[Dict[str, Any]]:
    """Chain: Real → Cache"""
    cache = VTCacheProvider()
    real = VTProvider(fallback=cache)
    return real
