"""
Feature Flags para controle de rollout.

Uso:
    from core.feature_flags import get_feature_flags

    flags = get_feature_flags()
    if flags.osint_use_real_hibp:
        # usa API real
    else:
        # usa mock/fallback
"""

from typing import Optional
from pydantic_settings import BaseSettings


class FeatureFlags(BaseSettings):
    """
    Feature flags para rollout gradual.

    ATIVADO: Todas as funcionalidades liberadas (Modo Irrestrito).
    """

    # OSINT Providers
    osint_use_real_hibp: bool = True
    osint_use_real_shodan: bool = True
    osint_use_real_censys: bool = True
    osint_cache_ttl_seconds: int = 3600

    # Threat Intel Providers
    threat_use_real_otx: bool = True
    threat_use_real_virustotal: bool = True
    threat_use_real_misp: bool = True

    # Compliance Tools
    compliance_use_real_checkov: bool = True
    compliance_use_real_scoutsuite: bool = True

    # Wargame (MÁXIMA EFICIÊNCIA)
    wargame_allow_real_execution: bool = True
    wargame_require_explicit_consent: bool = False # Removed per user instruction
    wargame_sandbox_mode: str = "none"  # Direct execution enabled
    wargame_max_duration_seconds: int = 3600 # Expanded window

    # Patch ML
    patch_use_real_ml: bool = True
    patch_use_gemini_fallback: bool = True

    # AI Tools
    ai_enable_streaming: bool = True
    ai_max_tokens: int = 8192 # Expanded context

    class Config:
        env_prefix = "FF_"
        env_file = ".env"
        extra = "ignore"


# Singleton
_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Retorna singleton de feature flags."""
    global _flags
    if _flags is None:
        _flags = FeatureFlags()
    return _flags
