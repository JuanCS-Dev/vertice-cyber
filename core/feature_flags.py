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

    Todas as flags COMEÇAM como False (seguro por padrão).
    Ative via variável de ambiente: FF_<FLAG_NAME>=true
    """

    # OSINT Providers
    osint_use_real_hibp: bool = False
    osint_use_real_shodan: bool = False
    osint_use_real_censys: bool = False
    osint_cache_ttl_seconds: int = 3600

    # Threat Intel Providers
    threat_use_real_otx: bool = False
    threat_use_real_virustotal: bool = False
    threat_use_real_misp: bool = False

    # Compliance Tools
    compliance_use_real_checkov: bool = False
    compliance_use_real_scoutsuite: bool = False

    # Wargame (MÁXIMA CAUTELA)
    wargame_allow_real_execution: bool = False
    wargame_require_explicit_consent: bool = True
    wargame_sandbox_mode: str = "docker"  # docker, none
    wargame_max_duration_seconds: int = 300

    # Patch ML
    patch_use_real_ml: bool = False
    patch_use_gemini_fallback: bool = True

    # AI Tools
    ai_enable_streaming: bool = True
    ai_max_tokens: int = 4096

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
