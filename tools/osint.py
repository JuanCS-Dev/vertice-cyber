"""
OSINT Hunter - Intelligence Gathering Tool
Investigação autônoma de inteligência open-source.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

logger = logging.getLogger(__name__)


class InvestigationDepth(str, Enum):
    """Profundidade da investigação."""

    BASIC = "basic"
    DEEP = "deep"
    EXHAUSTIVE = "exhaustive"


class BreachInfo(BaseModel):
    """Informação de um breach."""

    name: str
    date: str
    data_classes: List[str]
    is_verified: bool


class OSINTFinding(BaseModel):
    """Um achado da investigação."""

    source: str
    finding_type: str
    severity: str  # low, medium, high, critical
    data: Dict[str, Any]
    confidence: float


class OSINTResult(BaseModel):
    """Resultado de investigação OSINT."""

    target: str
    depth: InvestigationDepth
    findings: List[OSINTFinding] = Field(default_factory=list)
    breaches: List[BreachInfo] = Field(default_factory=list)
    risk_score: float = 0.0
    sources_checked: List[str] = Field(default_factory=list)


class OSINTHunter:
    """
    OSINT Hunter - Investigador Digital.

    Capacidades:
    - Breach data analysis (HaveIBeenPwned)
    - Google dorking patterns
    - Domain reconnaissance
    - Email intelligence
    """

    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("osint_hunter")
        self.event_bus = get_event_bus()
        self.hibp_api_key = None

        if self.settings.api_keys.hibp_api_key:
            self.hibp_api_key = self.settings.api_keys.hibp_api_key.get_secret_value()

    async def investigate(
        self, target: str, depth: InvestigationDepth = InvestigationDepth.BASIC
    ) -> OSINTResult:
        """
        Executa investigação OSINT completa.

        Args:
            target: Email, domínio, ou IP
            depth: Profundidade da investigação

        Returns:
            OSINTResult com todos os achados
        """
        await self.event_bus.emit(
            EventType.OSINT_INVESTIGATION_STARTED,
            {"target": target, "depth": depth.value},
            source="osint_hunter",
        )

        result = OSINTResult(target=target, depth=depth)

        # Detecta tipo de target
        if "@" in target:
            await self._investigate_email(target, result)
        elif "." in target and not target.replace(".", "").isdigit():
            await self._investigate_domain(target, result)
        else:
            await self._investigate_ip(target, result)

        # Calcula risk score
        result.risk_score = self._calculate_risk(result)

        # Cache result
        cache_key = f"investigation:{target}:{depth.value}"
        self.memory.set(cache_key, result.model_dump(), ttl_seconds=3600)

        await self.event_bus.emit(
            EventType.OSINT_INVESTIGATION_COMPLETED,
            {"target": target, "risk_score": result.risk_score},
            source="osint_hunter",
        )

        return result

    async def check_breach(self, email: str) -> List[BreachInfo]:
        """
        Verifica se email aparece em breaches conhecidos.

        Args:
            email: Email a verificar

        Returns:
            Lista de breaches
        """
        if not self.hibp_api_key:
            logger.warning("HIBP API key not configured")
            return []

        breaches = []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={
                        "hibp-api-key": self.hibp_api_key,
                        "User-Agent": "Vertice-Cyber-OSINT/2.0",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    for breach in data:
                        breaches.append(
                            BreachInfo(
                                name=breach.get("Name", "Unknown"),
                                date=breach.get("BreachDate", "Unknown"),
                                data_classes=breach.get("DataClasses", []),
                                is_verified=breach.get("IsVerified", False),
                            )
                        )

                    if breaches:
                        await self.event_bus.emit(
                            EventType.OSINT_BREACH_DETECTED,
                            {"email": email, "count": len(breaches)},
                            source="osint_hunter",
                        )

                elif response.status_code == 404:
                    pass  # No breaches found
                else:
                    logger.warning(f"HIBP API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Breach check failed: {e}")

        return breaches

    def get_google_dorks(self, domain: str) -> List[Dict[str, str]]:
        """
        Gera lista de Google dorks para um domínio.

        Args:
            domain: Domínio alvo

        Returns:
            Lista de dorks categorizados
        """
        dorks = [
            {
                "category": "sensitive_files",
                "dork": f"site:{domain} filetype:pdf OR filetype:doc OR filetype:xls",
                "description": "Documentos potencialmente sensíveis",
            },
            {
                "category": "exposed_dirs",
                "dork": f'site:{domain} intitle:"index of"',
                "description": "Diretórios expostos",
            },
            {
                "category": "login_pages",
                "dork": f"site:{domain} inurl:login OR inurl:admin",
                "description": "Páginas de login",
            },
            {
                "category": "config_files",
                "dork": f"site:{domain} filetype:env OR filetype:config",
                "description": "Arquivos de configuração",
            },
            {
                "category": "error_messages",
                "dork": f'site:{domain} "error" OR "exception" OR "warning"',
                "description": "Mensagens de erro expostas",
            },
            {
                "category": "backup_files",
                "dork": f"site:{domain} filetype:bak OR filetype:old OR filetype:backup",
                "description": "Arquivos de backup",
            },
        ]
        return dorks

    async def _investigate_email(self, email: str, result: OSINTResult) -> None:
        """Investiga um email."""
        result.sources_checked.append("hibp_breaches")
        result.breaches = await self.check_breach(email)

        # Extrai domínio
        domain = email.split("@")[1]
        result.sources_checked.append("domain_from_email")

        result.findings.append(
            OSINTFinding(
                source="email_analysis",
                finding_type="domain_extracted",
                severity="info",
                data={"domain": domain},
                confidence=1.0,
            )
        )

    async def _investigate_domain(self, domain: str, result: OSINTResult) -> None:
        """Investiga um domínio."""
        result.sources_checked.append("google_dorks")

        dorks = self.get_google_dorks(domain)
        result.findings.append(
            OSINTFinding(
                source="google_dorking",
                finding_type="dorks_generated",
                severity="info",
                data={"dorks": dorks, "count": len(dorks)},
                confidence=1.0,
            )
        )

    async def _investigate_ip(self, ip: str, result: OSINTResult) -> None:
        """Investiga um IP."""
        result.sources_checked.append("ip_analysis")
        result.findings.append(
            OSINTFinding(
                source="ip_analysis",
                finding_type="ip_info",
                severity="info",
                data={"ip": ip},
                confidence=1.0,
            )
        )

    def _calculate_risk(self, result: OSINTResult) -> float:
        """Calcula score de risco (0-100)."""
        score = 0.0

        # Breaches aumentam risco
        score += len(result.breaches) * 15

        # Findings de alta severidade
        for finding in result.findings:
            if finding.severity == "critical":
                score += 25
            elif finding.severity == "high":
                score += 15
            elif finding.severity == "medium":
                score += 5

        return min(score, 100.0)


# Singleton
_osint_hunter: Optional[OSINTHunter] = None


def get_osint_hunter() -> OSINTHunter:
    """Retorna singleton do OSINT Hunter."""
    global _osint_hunter
    if _osint_hunter is None:
        _osint_hunter = OSINTHunter()
    return _osint_hunter


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================


async def osint_investigate(ctx, target: str, depth: str = "basic") -> Dict[str, Any]:
    """
    Executa investigação OSINT sobre um alvo.

    Args:
        target: Email, domínio ou IP a investigar
        depth: Profundidade (basic, deep, exhaustive)

    Returns:
        Resultado com findings, breaches e risk_score
    """
    ctx.info(f"Starting OSINT investigation on {target}")

    hunter = get_osint_hunter()
    depth_enum = InvestigationDepth(depth)
    result = await hunter.investigate(target, depth_enum)

    ctx.info(f"Investigation complete. Risk score: {result.risk_score}")

    return result.model_dump()


async def osint_breach_check(ctx, email: str) -> Dict[str, Any]:
    """
    Verifica se email aparece em breaches conhecidos.

    Args:
        email: Email a verificar

    Returns:
        Lista de breaches onde o email aparece
    """
    ctx.info(f"Checking breaches for {email}")

    hunter = get_osint_hunter()
    breaches = await hunter.check_breach(email)

    return {
        "email": email,
        "breached": len(breaches) > 0,
        "breach_count": len(breaches),
        "breaches": [b.model_dump() for b in breaches],
    }


async def osint_google_dork(ctx, target_domain: str) -> Dict[str, Any]:
    """
    Gera Google dorks para reconhecimento de domínio.

    Args:
        target_domain: Domínio alvo

    Returns:
        Lista de dorks categorizados
    """
    hunter = get_osint_hunter()
    dorks = hunter.get_google_dorks(target_domain)

    return {"domain": target_domain, "dork_count": len(dorks), "dorks": dorks}
