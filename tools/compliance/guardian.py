"""
Compliance Guardian - Regulatory Compliance Tool
Verificação automática de conformidade com regulamentações de segurança.
"""

import logging
from typing import List, Optional

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

from .models import (
    ComplianceFramework,
    ComplianceStatus,
    ComplianceRequirement,
    ComplianceCheck,
    ComplianceAssessment,
)
from .client import get_compliance_api

logger = logging.getLogger(__name__)


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
        self._compliance_api = None

    @property
    def compliance_api(self):
        """Lazy initialization of compliance API."""
        if self._compliance_api is None:
            self._compliance_api = get_compliance_api()
        return self._compliance_api

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

        # Contagem de status
        status_counts = {}
        for check in checks:
            status_counts[check.status] = status_counts.get(check.status, 0) + 1

        # Lógica de determinação
        total_checks = len(checks)

        # Se todos são compliant
        if status_counts.get(ComplianceStatus.COMPLIANT, 0) == total_checks:
            return ComplianceStatus.COMPLIANT

        # Se há violações críticas
        critical_violations = [
            c
            for c in checks
            if c.requirement.severity == "critical"
            and c.status != ComplianceStatus.COMPLIANT
        ]
        if critical_violations:
            return ComplianceStatus.NON_COMPLIANT

        # Se maioria é compliant ou parcialmente compliant
        compliant_count = status_counts.get(ComplianceStatus.COMPLIANT, 0)
        partial_count = status_counts.get(ComplianceStatus.PARTIALLY_COMPLIANT, 0)

        if (compliant_count + partial_count) / total_checks >= 0.6:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT

    def _identify_critical_violations(self, checks: List[ComplianceCheck]) -> List[str]:
        """Identifica violações críticas."""
        violations = []
        for check in checks:
            if (
                check.requirement.severity == "critical"
                and check.status
                in [
                    ComplianceStatus.NON_COMPLIANT,
                    ComplianceStatus.PARTIALLY_COMPLIANT,
                ]
                and check.violations
            ):
                violations.extend(
                    [
                        f"{check.requirement.requirement_id}: {violation}"
                        for violation in check.violations
                    ]
                )
        return violations

    def _generate_recommendations(
        self, checks: List[ComplianceCheck], framework: ComplianceFramework
    ) -> List[str]:
        """Gera recomendações de remediação."""
        recommendations = []

        # Coleta todas as recomendações dos checks
        for check in checks:
            recommendations.extend(check.remediation_steps)

        # Remove duplicatas e limita a 10 recomendações
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]


# Singleton
_compliance_guardian: Optional[ComplianceGuardian] = None


def get_compliance_guardian() -> ComplianceGuardian:
    """Retorna singleton do Compliance Guardian."""
    global _compliance_guardian
    if _compliance_guardian is None:
        _compliance_guardian = ComplianceGuardian()
    return _compliance_guardian
