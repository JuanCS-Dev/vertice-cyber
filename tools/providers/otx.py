"""
AlienVault OTX Provider - Threat Intelligence API.

API Docs: https://otx.alienvault.com/api
"""

import os
import logging
from typing import Dict, List, Optional, Any

import httpx
from pydantic import BaseModel

from core.feature_flags import get_feature_flags
from core.circuit_breaker import api_circuit_breaker
from core.rate_limiter import rate_limit
from tools.providers.base import BaseProvider, ProviderNotConfiguredError

logger = logging.getLogger(__name__)


class OTXIndicator(BaseModel):
    """Informação de um indicador do OTX."""

    indicator: str
    type: str
    pulse_count: int
    last_external_analysis: Optional[str] = None
    tags: List[str] = []


class OTXProvider(BaseProvider[Dict[str, Any]]):
    """Provider real para AlienVault OTX API."""

    name = "otx_real"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.api_key = os.getenv("OTX_API_KEY")
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.fallback = fallback

    def is_available(self) -> bool:
        """Verifica se API key está configurada E feature flag ativa."""
        flags = get_feature_flags()
        return bool(self.api_key) and flags.threat_use_real_otx

    @rate_limit("otx", rps=5.0)
    @api_circuit_breaker(failure_threshold=5, recovery_timeout=60, name="otx")
    async def execute(
        self, indicator: str, type: str = "ip", **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Consulta reputação de um indicador (IP, Domain, MD5, etc).

        Args:
            indicator: O indicador a consultar
            type: Tipo (IPv4, domain, FileHash-MD5, etc)

        Returns:
            Dict com informações de reputação e pulsos
        """
        if not self.api_key:
            raise ProviderNotConfiguredError("OTX_API_KEY not set")

        # Mapeamento simples de tipos para OTX paths
        type_map = {
            "ip": f"IPv4/{indicator}",
            "domain": f"domain/{indicator}",
            "md5": f"filehash/{indicator}",
            "sha256": f"filehash/{indicator}",
        }

        path = type_map.get(type.lower(), f"IPv4/{indicator}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/indicators/{path}/general",
                headers={"X-OTX-API-KEY": self.api_key},
            )

            if response.status_code == 404:
                return {"status": "clean", "pulse_count": 0}

            response.raise_for_status()
            data = response.json()

            # Caching do sucesso
            try:
                from tools.providers.cache import get_cache

                get_cache().set(f"otx:{type}:{indicator}", data)
            except Exception as e:
                logger.error(f"Failed to cache OTX result: {e}")

            return data


class OTXCacheProvider(BaseProvider[Dict[str, Any]]):
    """Provider que usa cache local para OTX."""

    name = "otx_cache"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.fallback = fallback
        from tools.providers.cache import get_cache

        self.cache = get_cache()

    def is_available(self) -> bool:
        return True

    async def execute(
        self, indicator: str, type: str = "ip", **kwargs: Any
    ) -> Dict[str, Any]:
        cached_data = self.cache.get(f"otx:{type}:{indicator}")
        if cached_data:
            logger.debug(f"Cache hit for OTX:{indicator}")
            return cached_data

        if self.fallback:
            return await self.fallback.execute_with_fallback(
                indicator, type=type, **kwargs
            )

        return {"status": "unknown", "source": "cache_miss"}


def get_otx_provider() -> BaseProvider[Dict[str, Any]]:
    """Chain: Real → Cache"""
    cache = OTXCacheProvider()
    real = OTXProvider(fallback=cache)
    return real
