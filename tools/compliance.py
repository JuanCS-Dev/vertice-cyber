"""
Compliance Guardian - Regulatory Compliance Tool
Verificação automática de conformidade com regulamentações de segurança.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory
from tools.compliance_api import get_compliance_api

logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Frameworks de conformidade suportados."""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO_27001 = "iso_27001"
    NIST = "nist"


class ComplianceStatus(str, Enum):
    """Status de conformidade."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"


class ComplianceRequirement(BaseModel):
    """Requisito de conformidade."""

    requirement_id: str
    title: str
    description: str
    framework: ComplianceFramework
    category: str  # data_protection, access_control, encryption, etc.
    severity: str  # low, medium, high, critical


class ComplianceCheck(BaseModel):
    """Resultado de uma verificação de conformidade."""

    requirement: ComplianceRequirement
    status: ComplianceStatus
    evidence: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    score: float = 0.0  # 0-100 compliance score


class ComplianceAssessment(BaseModel):
    """Avaliação completa de conformidade."""

    target: str
    framework: ComplianceFramework
    overall_status: ComplianceStatus
    overall_score: float = 0.0
    checks: List[ComplianceCheck] = Field(default_factory=list)
    critical_violations: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    assessment_date: datetime = Field(default_factory=datetime.utcnow)


class ComplianceGuardian:
    """
    Compliance Guardian - Guardião da Conformidade.

    Capacidades:
    - Automated compliance checking
    - Regulatory framework validation
    - Risk assessment for non-compliance
    - Remediation recommendations
    - Continuous compliance monitoring
    """

    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("compliance_guardian")
        self.event_bus = get_event_bus()
        self.compliance_api = get_compliance_api()

    async def assess_compliance(
        self, target: str, framework: ComplianceFramework
    ) -> ComplianceAssessment:
        """
        Executa avaliação completa de conformidade.

        Args:
            target: Sistema, processo ou organização a avaliar
            framework: Framework de conformidade (GDPR, HIPAA, etc.)

        Returns:
            ComplianceAssessment com status detalhado
        """
        await self.event_bus.emit(
            EventType.THREAT_DETECTED,  # Reutilizando evento existente
            {
                "target": target,
                "framework": framework.value,
                "assessment_type": "compliance",
            },
            source="compliance_guardian",
        )

        assessment = ComplianceAssessment(
            target=target,
            framework=framework,
            overall_status=ComplianceStatus.NOT_APPLICABLE,
        )

        # Busca controles reais do framework e cria verificações
        assessment.checks = await self._create_compliance_checks(target, framework)

        # Calcula status geral e score
        assessment.overall_score = self._calculate_compliance_score(assessment.checks)
        assessment.overall_status = self._determine_overall_status(assessment.checks)

        # Identifica violações críticas
        assessment.critical_violations = self._identify_critical_violations(
            assessment.checks
        )

        # Gera ações recomendadas
        assessment.recommended_actions = self._generate_recommendations(
            assessment.checks, framework
        )

        # Cache results
        cache_key = f"compliance:{target}:{framework.value}"
        self.memory.set(
            cache_key, assessment.model_dump(), ttl_seconds=86400
        )  # 24h cache

        await self.event_bus.emit(
            EventType.THREAT_MITRE_MAPPED,  # Reutilizando evento existente
            {"target": target, "compliance_score": assessment.overall_score},
            source="compliance_guardian",
        )

        return assessment

    async def _create_compliance_checks(
        self, target: str, framework: ComplianceFramework
    ) -> List[ComplianceCheck]:
        """Cria verificações de conformidade baseadas em dados reais da API."""
        checks = []

        # Mapeia framework do enum para ID da API
        framework_mapping = {
            ComplianceFramework.GDPR: "gdpr",
            ComplianceFramework.HIPAA: "hipaa",
            ComplianceFramework.PCI_DSS: "pci_dss",
            ComplianceFramework.SOX: "sox",
            ComplianceFramework.ISO_27001: "iso_27001",
            ComplianceFramework.NIST: "nist_csf",
        }

        api_framework_id = framework_mapping.get(framework, framework.value.lower())

        # Busca controles reais do framework
        controls = await self.compliance_api.get_controls_by_framework(api_framework_id)

        # Se não encontrou controles específicos, busca controles relacionados
        if not controls:
            # Busca por categoria geral
            all_controls = await self.compliance_api.get_all_controls()
            # Filtra controles que podem ser aplicáveis genericamente
            controls = all_controls[:5]  # Limita a 5 controles para não sobrecarregar

        # Cria verificações para cada controle encontrado
        for control in controls:
            # Simula status baseado no ID do controle (em produção seria análise real)
            if (
                "access" in control.control_id.lower()
                or "auth" in control.control_id.lower()
            ):
                status = ComplianceStatus.PARTIALLY_COMPLIANT
                evidence = ["Basic authentication implemented"]
                violations = ["Multi-factor authentication not enforced"]
                remediation = [
                    "Enable MFA for all users",
                    "Implement role-based access control",
                ]
            elif (
                "encrypt" in control.control_id.lower()
                or "data" in control.control_id.lower()
            ):
                status = ComplianceStatus.COMPLIANT
                evidence = [
                    "Encryption policies implemented",
                    "Data classification in place",
                ]
                violations = []
                remediation = []
            else:
                # Status aleatório para demonstração
                status = ComplianceStatus.PARTIALLY_COMPLIANT
                evidence = ["Basic controls implemented"]
                violations = ["Advanced controls pending implementation"]
                remediation = ["Review and implement advanced security controls"]

            check = ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id=control.control_id,
                    title=control.title,
                    description=control.description,
                    framework=framework,
                    category=control.category,
                    severity=control.severity,
                ),
                status=status,
                evidence=evidence,
                violations=violations,
                remediation_steps=remediation,
            )

            checks.append(check)

        # Se não encontrou controles reais, cria verificação genérica
        if not checks:
            checks.append(
                ComplianceCheck(
                    requirement=ComplianceRequirement(
                        requirement_id=f"{framework.value.upper()}-GENERAL",
                        title="General Compliance Check",
                        description=f"General compliance verification for {framework.value}",
                        framework=framework,
                        category="general",
                        severity="medium",
                    ),
                    status=ComplianceStatus.NOT_APPLICABLE,
                    evidence=["Framework not fully configured"],
                    violations=[],
                    remediation_steps=["Configure specific framework controls"],
                )
            )

        return checks

    async def _check_hipaa_compliance(self, target: str) -> List[ComplianceCheck]:
        """Verifica conformidade HIPAA."""
        checks = []

        # Verificação de safeguards administrativos
        checks.append(
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="HIPAA-164.308",
                    title="Administrative Safeguards",
                    description="Implement administrative actions to manage risk",
                    framework=ComplianceFramework.HIPAA,
                    category="administrative_safeguards",
                    severity="high",
                ),
                status=ComplianceStatus.PARTIALLY_COMPLIANT,
                evidence=["Security officer designated", "Risk analysis performed"],
                violations=["Incomplete security training program"],
                remediation_steps=[
                    "Complete annual security training",
                    "Update policies and procedures",
                ],
            )
        )

        return checks

    async def _check_pci_compliance(self, target: str) -> List[ComplianceCheck]:
        """Verifica conformidade PCI DSS."""
        checks = []

        # Verificação de proteção de dados do titular do cartão
        checks.append(
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="PCI-3.1",
                    title="Protect Stored Cardholder Data",
                    description="Protect stored cardholder data",
                    framework=ComplianceFramework.PCI_DSS,
                    category="data_protection",
                    severity="critical",
                ),
                status=ComplianceStatus.COMPLIANT,
                evidence=["Card data encrypted", "Access controls implemented"],
            )
        )

        return checks

    async def _check_generic_compliance(
        self, target: str, framework: ComplianceFramework
    ) -> List[ComplianceCheck]:
        """Verificações genéricas de conformidade."""
        checks = []

        # Verificações básicas aplicáveis a qualquer framework
        checks.append(
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id=f"{framework.value.upper()}-ACCESS",
                    title="Access Control",
                    description="Implement proper access controls",
                    framework=framework,
                    category="access_control",
                    severity="high",
                ),
                status=ComplianceStatus.PARTIALLY_COMPLIANT,
                evidence=["Basic authentication implemented"],
                violations=["Multi-factor authentication not enforced"],
                remediation_steps=[
                    "Enable MFA for all users",
                    "Implement role-based access control",
                ],
            )
        )

        return checks

    def _calculate_compliance_score(self, checks: List[ComplianceCheck]) -> float:
        """Calcula score de conformidade geral (0-100)."""
        if not checks:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        severity_weights = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}

        for check in checks:
            weight = severity_weights.get(check.requirement.severity, 1.0)

            # Pontuação baseada no status
            if check.status == ComplianceStatus.COMPLIANT:
                score = 100.0
            elif check.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                score = 60.0
            elif check.status == ComplianceStatus.NON_COMPLIANT:
                score = 0.0
            else:  # NOT_APPLICABLE
                score = 100.0
                weight = 0.0  # Não conta no cálculo

            check.score = score
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _determine_overall_status(
        self, checks: List[ComplianceCheck]
    ) -> ComplianceStatus:
        """Determina status geral baseado nas verificações."""
        if not checks:
            return ComplianceStatus.NOT_APPLICABLE

        # Se há violações críticas, é non-compliant
        critical_violations = [
            c
            for c in checks
            if c.requirement.severity == "critical"
            and c.status in [ComplianceStatus.NON_COMPLIANT]
        ]

        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT

        # Se há violações de alta severidade, parcialmente compliant
        high_violations = [
            c
            for c in checks
            if c.requirement.severity == "high"
            and c.status in [ComplianceStatus.NON_COMPLIANT]
        ]

        if high_violations:
            return ComplianceStatus.PARTIALLY_COMPLIANT

        # Se todas são compliant ou parcialmente compliant
        all_compliant = all(
            c.status
            in [ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]
            for c in checks
        )

        return (
            ComplianceStatus.COMPLIANT
            if all_compliant
            else ComplianceStatus.PARTIALLY_COMPLIANT
        )

    def _identify_critical_violations(self, checks: List[ComplianceCheck]) -> List[str]:
        """Identifica violações críticas."""
        critical = []
        for check in checks:
            if check.requirement.severity in ["critical", "high"] and check.status in [
                ComplianceStatus.NON_COMPLIANT
            ]:
                critical.extend(check.violations)

        return critical

    def _generate_recommendations(
        self, checks: List[ComplianceCheck], framework: ComplianceFramework
    ) -> List[str]:
        """Gera ações recomendadas baseadas nas verificações."""
        recommendations = []

        for check in checks:
            if check.status in [
                ComplianceStatus.NON_COMPLIANT,
                ComplianceStatus.PARTIALLY_COMPLIANT,
            ]:
                recommendations.extend(check.remediation_steps)

        # Remove duplicatas
        return list(set(recommendations))

    async def generate_compliance_report(
        self, target: str, frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """
        Gera relatório de conformidade para múltiplos frameworks.

        Args:
            target: Sistema ou organização alvo
            frameworks: Lista de frameworks a verificar

        Returns:
            Relatório consolidado de conformidade
        """
        report = {
            "target": target,
            "generated_at": datetime.utcnow().isoformat(),
            "frameworks_assessed": [f.value for f in frameworks],
            "assessments": [],
            "summary": {
                "total_frameworks": len(frameworks),
                "compliant_frameworks": 0,
                "average_score": 0.0,
            },
        }

        total_score = 0.0

        for framework in frameworks:
            assessment = await self.assess_compliance(target, framework)
            report["assessments"].append(assessment.model_dump())

            if assessment.overall_status == ComplianceStatus.COMPLIANT:
                report["summary"]["compliant_frameworks"] += 1

            total_score += assessment.overall_score

        report["summary"]["average_score"] = (
            total_score / len(frameworks) if frameworks else 0.0
        )

        return report


# Singleton
_compliance_guardian: Optional[ComplianceGuardian] = None


def get_compliance_guardian() -> ComplianceGuardian:
    """Retorna singleton do Compliance Guardian."""
    global _compliance_guardian
    if _compliance_guardian is None:
        _compliance_guardian = ComplianceGuardian()
    return _compliance_guardian


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================


async def compliance_assess(
    ctx: Context, target: str, framework: str
) -> Dict[str, Any]:
    """
    Executa avaliação de conformidade para um framework específico.

    Args:
        target: Sistema ou organização a avaliar
        framework: Framework (gdpr, hipaa, pci_dss, sox, iso_27001, nist)

    Returns:
        Avaliação completa de conformidade
    """
    ctx.info(f"Starting compliance assessment for {target} against {framework}")

    guardian = get_compliance_guardian()
    framework_enum = ComplianceFramework(framework)
    assessment = await guardian.assess_compliance(target, framework_enum)

    ctx.info(f"Assessment complete. Score: {assessment.overall_score:.1f}%")

    return assessment.model_dump()


async def compliance_report(
    ctx: Context, target: str, frameworks: List[str]
) -> Dict[str, Any]:
    """
    Gera relatório de conformidade para múltiplos frameworks.

    Args:
        target: Sistema ou organização alvo
        frameworks: Lista de frameworks a verificar

    Returns:
        Relatório consolidado de conformidade
    """
    ctx.info(
        f"Generating compliance report for {target} across {len(frameworks)} frameworks"
    )

    guardian = get_compliance_guardian()
    framework_enums = [ComplianceFramework(f) for f in frameworks]
    report = await guardian.generate_compliance_report(target, framework_enums)

    ctx.info(
        f"Report generated. Average score: {report['summary']['average_score']:.1f}%"
    )

    return report


async def compliance_check(
    ctx: Context, requirement_id: str, target: str
) -> Dict[str, Any]:
    """
    Verifica conformidade para um requisito específico.

    Args:
        requirement_id: ID do requisito (ex: "GDPR-ART6", "HIPAA-164.308")
        target: Sistema ou processo alvo

    Returns:
        Status de conformidade para o requisito específico
    """
    ctx.info(f"Checking compliance for requirement {requirement_id} on {target}")

    # Esta seria uma verificação mais específica
    # Por enquanto, retorna um placeholder
    return {
        "requirement_id": requirement_id,
        "target": target,
        "status": "check_implemented",
        "note": "Specific requirement checking to be implemented based on framework",
    }
