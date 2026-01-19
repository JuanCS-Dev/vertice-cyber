"""
Threat Prophet - Threat Intelligence & Prediction Tool
Análise avançada de ameaças usando MITRE ATT&CK e machine learning.

Nota: Esta implementação usa dados mockados devido a conflitos de dependências
com pyattck (requer pydantic <2.0, mas projeto usa pydantic >=2.0).
Em produção, seria integrado com pyattck ou API oficial do MITRE ATT&CK.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from .fastmcp_compat import get_fastmcp_context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory
from tools.mitre_api import get_mitre_client, MITRETechnique

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    """Níveis de ameaça."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackVector(str, Enum):
    """Vetores de ataque."""

    NETWORK = "network"
    PHYSICAL = "physical"
    SOCIAL_ENGINEERING = "social_engineering"
    SUPPLY_CHAIN = "supply_chain"
    CREDENTIALS = "credentials"


class ThreatIndicator(BaseModel):
    """Indicador de ameaça."""

    indicator_type: str  # IP, domain, hash, etc.
    value: str
    confidence: float
    first_seen: str
    last_seen: str
    tags: List[str] = Field(default_factory=list)


class ThreatPrediction(BaseModel):
    """Predição de ameaça."""

    target: str
    predicted_threats: List[str]
    confidence_score: float
    risk_level: ThreatLevel
    recommended_actions: List[str]
    time_horizon: str  # short_term, medium_term, long_term


class ThreatAnalysis(BaseModel):
    """Resultado de análise de ameaça."""

    target: str
    indicators: List[ThreatIndicator] = Field(default_factory=list)
    techniques: List[MITRETechnique] = Field(default_factory=list)
    predictions: List[ThreatPrediction] = Field(default_factory=list)
    overall_risk_score: float = 0.0
    attack_vectors: List[AttackVector] = Field(default_factory=list)


class ThreatProphet:
    """
    Threat Prophet - Profeta das Ameaças.

    Capacidades:
    - MITRE ATT&CK framework integration
    - Threat intelligence correlation
    - Predictive threat modeling
    - Risk assessment and scoring
    - Attack vector analysis
    """

    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("threat_prophet")
        self.event_bus = get_event_bus()
        self.mitre_client = get_mitre_client("enterprise")

    async def analyze_threats(
        self, target: str, include_predictions: bool = True
    ) -> ThreatAnalysis:
        """
        Executa análise completa de ameaças.

        Args:
            target: Sistema, rede ou organização a analisar
            include_predictions: Incluir predições de ameaças

        Returns:
            ThreatAnalysis com indicadores, técnicas e predições
        """
        await self.event_bus.emit(
            EventType.THREAT_DETECTED,
            {"target": target, "analysis_type": "comprehensive"},
            source="threat_prophet",
        )

        analysis = ThreatAnalysis(target=target)

        # Analisa indicadores de ameaça
        analysis.indicators = await self._gather_indicators(target)

        # Mapeia para técnicas MITRE ATT&CK
        analysis.techniques = await self._map_to_mitre_techniques(target)

        # Predições se solicitadas
        if include_predictions:
            analysis.predictions = await self._generate_predictions(target)

        # Calcula risco geral
        analysis.overall_risk_score = self._calculate_overall_risk(analysis)

        # Identifica vetores de ataque
        analysis.attack_vectors = self._identify_attack_vectors(analysis)

        # Cache results
        cache_key = f"threat_analysis:{target}:{include_predictions}"
        self.memory.set(cache_key, analysis.model_dump(), ttl_seconds=1800)

        await self.event_bus.emit(
            EventType.THREAT_PREDICTED,
            {"target": target, "risk_score": analysis.overall_risk_score},
            source="threat_prophet",
        )

        return analysis

    async def _gather_indicators(self, target: str) -> List[ThreatIndicator]:
        """Coleta indicadores de ameaça para o alvo."""
        indicators = []

        # Simulação de indicadores baseados no target
        # Em produção, isso seria integrado com feeds reais de threat intel

        if "@" in target:  # Email target
            indicators.extend(
                [
                    ThreatIndicator(
                        indicator_type="email",
                        value=target,
                        confidence=0.8,
                        first_seen="2024-01-15",
                        last_seen="2024-01-20",
                        tags=["phishing", "credential_stuffing"],
                    )
                ]
            )

        elif "." in target and not target.replace(".", "").isdigit():  # Domain
            indicators.extend(
                [
                    ThreatIndicator(
                        indicator_type="domain",
                        value=target,
                        confidence=0.6,
                        first_seen="2024-01-10",
                        last_seen="2024-01-18",
                        tags=["suspicious_registration", "malware_distribution"],
                    )
                ]
            )

        return indicators

    async def _map_to_mitre_techniques(self, target: str) -> List:
        """Mapeia ameaças para técnicas MITRE ATT&CK usando dados reais."""
        # Buscar técnicas relevantes baseadas no target
        if "@" in target:  # Email target - phishing related
            techniques = await self.mitre_client.search_techniques("phishing")
            # Adicionar mais técnicas relacionadas se não encontrar phishing
            if not techniques:
                techniques = await self.mitre_client.get_techniques_by_tactic(
                    "Initial Access"
                )
        elif "." in target and not target.replace(".", "").isdigit():  # Domain
            techniques = await self.mitre_client.search_techniques("phishing")
            if not techniques:
                techniques = await self.mitre_client.get_techniques_by_tactic(
                    "Initial Access"
                )
        else:  # Generic target
            techniques = await self.mitre_client.get_techniques_by_tactic(
                "Credential Access"
            )

        # Limitar a 5 técnicas mais relevantes para não sobrecarregar
        return techniques[:5] if techniques else []

    async def _generate_predictions(self, target: str) -> List[ThreatPrediction]:
        """Gera predições de ameaças futuras."""
        predictions = []

        # Predição baseada em padrões históricos
        predictions.append(
            ThreatPrediction(
                target=target,
                predicted_threats=["Credential Stuffing", "Phishing Campaign"],
                confidence_score=0.75,
                risk_level=ThreatLevel.HIGH,
                recommended_actions=[
                    "Implement multi-factor authentication",
                    "Conduct security awareness training",
                    "Deploy advanced email filtering",
                ],
                time_horizon="medium_term",
            )
        )

        return predictions

    def _calculate_overall_risk(self, analysis: ThreatAnalysis) -> float:
        """Calcula score de risco geral (0-100)."""
        score = 0.0

        # Indicadores aumentam risco
        score += len(analysis.indicators) * 10

        # Técnicas MITRE aumentam risco
        score += len(analysis.techniques) * 5

        # Predições de alta confiança aumentam risco
        for prediction in analysis.predictions:
            if prediction.confidence_score > 0.7:
                score += 20

        return min(score, 100.0)

    def _identify_attack_vectors(self, analysis: ThreatAnalysis) -> List[AttackVector]:
        """Identifica vetores de ataque possíveis."""
        vectors = []

        # Análise baseada nos indicadores encontrados
        for indicator in analysis.indicators:
            if "phishing" in indicator.tags:
                vectors.append(AttackVector.SOCIAL_ENGINEERING)
            if "credential" in indicator.tags:
                vectors.append(AttackVector.CREDENTIALS)

        # Remove duplicatas
        return list(set(vectors))

    async def get_threat_intelligence(self, query: str) -> Dict[str, Any]:
        """
        Busca inteligência de ameaças por query.

        Args:
            query: Termo de busca (ex: "ransomware", "APT41")

        Returns:
            Informações de inteligência de ameaças
        """
        # Mock data - em produção seria integrado com pyattck
        mock_techniques = [
            {
                "id": "T1486",
                "name": "Data Encrypted for Impact",
                "description": "Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources.",
                "tactics": ["Impact"],
            },
            {
                "id": "T1490",
                "name": "Inhibit System Recovery",
                "description": "Adversaries may delete or remove built-in operating system tools or native operating system commands that are installed as part of a network device.",
                "tactics": ["Impact"],
            },
        ]

        # Busca mock baseada na query
        matching_techniques = []
        for technique in mock_techniques:
            if query.lower() in technique["name"].lower():
                matching_techniques.append(technique)

        return {
            "query": query,
            "matching_techniques": matching_techniques,
            "total_matches": len(matching_techniques),
        }


# Singleton
_threat_prophet: Optional[ThreatProphet] = None


def get_threat_prophet() -> ThreatProphet:
    """Retorna singleton do Threat Prophet."""
    global _threat_prophet
    if _threat_prophet is None:
        _threat_prophet = ThreatProphet()
    return _threat_prophet


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================


async def threat_analyze(
    ctx, target: str, include_predictions: bool = True
) -> Dict[str, Any]:
    """
    Executa análise completa de ameaças para um alvo.

    Args:
        target: Sistema, rede ou organização a analisar
        include_predictions: Incluir predições de ameaças futuras

    Returns:
        Análise completa com indicadores, técnicas MITRE e predições
    """
    ctx.info(f"Starting threat analysis for {target}")

    prophet = get_threat_prophet()
    analysis = await prophet.analyze_threats(target, include_predictions)

    ctx.info(f"Analysis complete. Risk score: {analysis.overall_risk_score}")

    return analysis.model_dump()


async def threat_intelligence(ctx, query: str) -> Dict[str, Any]:
    """
    Busca inteligência de ameaças usando MITRE ATT&CK.

    Args:
        query: Termo de busca (ex: "ransomware", "APT41")

    Returns:
        Técnicas MITRE ATT&CK relacionadas à query
    """
    ctx.info(f"Searching threat intelligence for: {query}")

    prophet = get_threat_prophet()
    results = await prophet.get_threat_intelligence(query)

    ctx.info(f"Found {results['total_matches']} matching techniques")

    return results


async def threat_predict(ctx, target: str) -> Dict[str, Any]:
    """
    Gera predições de ameaças futuras para um alvo.

    Args:
        target: Sistema ou organização alvo

    Returns:
        Predições de ameaças com ações recomendadas
    """
    ctx.info(f"Generating threat predictions for {target}")

    prophet = get_threat_prophet()
    analysis = await prophet.analyze_threats(target, include_predictions=True)

    # Retorna apenas as predições
    return {
        "target": target,
        "predictions": [p.model_dump() for p in analysis.predictions],
        "overall_risk_score": analysis.overall_risk_score,
    }
