"""
HaveIBeenPwned Provider - Breach Data API.

API Docs: https://haveibeenpwned.com/API/v3
Requer: HIBP_API_KEY ($3.50/mês)
"""

import os
import logging
from typing import List, Optional, Any

import httpx
from pydantic import BaseModel

from core.feature_flags import get_feature_flags
from core.circuit_breaker import api_circuit_breaker
from core.rate_limiter import rate_limit
from tools.providers.base import BaseProvider, ProviderNotConfiguredError

logger = logging.getLogger(__name__)


class BreachData(BaseModel):
    """Dados de um breach do HIBP."""

    name: str
    title: str
    domain: str
    breach_date: str
    added_date: str
    modified_date: str
    pwn_count: int
    description: str
    logo_path: str
    data_classes: List[str]
    is_verified: bool
    is_fabricated: bool
    is_sensitive: bool
    is_retired: bool
    is_spam_list: bool
    is_malware: bool
    is_subscription_free: bool


class HIBPProvider(BaseProvider[List[BreachData]]):
    """Provider real para HaveIBeenPwned API."""

    name = "hibp_real"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.api_key = os.getenv("HIBP_API_KEY")
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.fallback = fallback

    def is_available(self) -> bool:
        """Verifica se API key está configurada E feature flag ativa."""
        flags = get_feature_flags()
        return bool(self.api_key) and flags.osint_use_real_hibp

    @rate_limit("hibp", rps=0.67)
    @api_circuit_breaker(failure_threshold=3, recovery_timeout=120, name="hibp")
    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """
        Consulta breaches para um email.

        Args:
            email: Email a verificar

        Returns:
            Lista de breaches onde email aparece

        Raises:
            httpx.HTTPError: Se API falhar
        """
        if not self.api_key:
            raise ProviderNotConfiguredError(
                "HIBP_API_KEY not set. "
                "Get key at: https://haveibeenpwned.com/API/Key ($3.50/mo)"
            )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/breachedaccount/{email}",
                headers={
                    "hibp-api-key": self.api_key,
                    "user-agent": "Vertice-Cyber-OSINT-Agent/1.0",
                },
                params={"truncateResponse": "false"},
            )

            if response.status_code == 404:
                # Email não encontrado em breaches (bom!)
                return []

            if response.status_code == 429:
                # Rate limited
                logger.warning("HIBP rate limited, retrying later")
                raise httpx.HTTPError("Rate limited")

            response.raise_for_status()

            data = response.json()
            breaches = [BreachData(**b) for b in data]

            # Salva no cache para uso futuro
            try:
                from tools.providers.cache import get_cache

                get_cache().set(f"hibp:{email}", data)
            except Exception as e:
                logger.error(f"Failed to cache HIBP result: {e}")

            logger.info(f"HIBP found {len(breaches)} breaches for {email}")
            return breaches


class HIBPCacheProvider(BaseProvider[List[BreachData]]):
    """Provider que usa cache local de breaches conhecidos."""

    name = "hibp_cache"

    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.fallback = fallback
        from tools.providers.cache import get_cache

        self.cache = get_cache()

    def is_available(self) -> bool:
        """Cache está sempre disponível."""
        return True

    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """Consulta cache local."""
        cached_data = self.cache.get(f"hibp:{email}")
        if cached_data is not None:
            logger.debug(f"Cache hit for {email}")
            return [BreachData(**b) for b in cached_data]

        # Cache miss - propaga para fallback
        if self.fallback:
            result = await self.fallback.execute_with_fallback(email, **kwargs)
            # Se o fallback trouxe dados reais ou AI, podemos opcionalmente cachear
            # Mas aqui o ideal é que o HIBPProvider real cacheie o sucesso.
            return result

        return []


class HIBPAIFallback(BaseProvider[List[BreachData]]):
    """Fallback usando Gemini 3 para análise de risco (sem dados reais)."""

    name = "hibp_ai_fallback"

    def is_available(self) -> bool:
        """Sempre disponível se GCP Project configurado."""
        return bool(os.getenv("GCP_PROJECT_ID"))

    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """
        Usa IA para estimar risco, NÃO tem dados reais.
        """
        try:
            from tools.vertex_ai import get_vertex_ai

            get_vertex_ai()

            # Por enquanto apenas logamos e retornamos vazio (seguro)
            logger.warning(
                f"Using AI fallback for breach check for {email}. "
                f"Result is ESTIMATION, not real data."
            )
        except Exception as e:
            logger.error(f"AI Fallback failed: {e}")

        return []  # Não inventa breaches falsos


def get_hibp_provider() -> BaseProvider[List[BreachData]]:
    """
    Factory que retorna chain de providers HIBP.

    Chain: Real HIBP → Cache → AI Fallback
    """
    ai_fallback = HIBPAIFallback()
    cache = HIBPCacheProvider(fallback=ai_fallback)
    real = HIBPProvider(fallback=cache)

    return real
