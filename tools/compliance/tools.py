"""
Compliance Guardian - MCP Tool Functions
Funções MCP para integração com o servidor FastMCP.
"""

from typing import Dict, Any, List

from .guardian import get_compliance_guardian
from .models import ComplianceFramework


async def compliance_assess(ctx, target: str, framework: str) -> Dict[str, Any]:
    """
    Executa avaliação de conformidade para um framework específico.

    Args:
        target: Sistema ou organização a avaliar
        framework: Framework (gdpr, hipaa, pci_dss, sox, iso_27001, nist)

    Returns:
        Avaliação completa de conformidade
    """
    ctx.info(f"Starting compliance assessment for {target} against {framework}")

    # Map string to enum
    framework_enum = ComplianceFramework(framework.lower())

    guardian = get_compliance_guardian()
    assessment = await guardian.assess_compliance(target, framework_enum)

    ctx.info(f"Assessment complete. Score: {assessment.overall_score:.1f}")

    return assessment.model_dump()


async def compliance_report(ctx, target: str, frameworks: List[str]) -> Dict[str, Any]:
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
    assessments = []

    for framework_name in frameworks:
        try:
            framework_enum = ComplianceFramework(framework_name.lower())
            assessment = await guardian.assess_compliance(target, framework_enum)
            assessments.append(assessment)
        except ValueError:
            ctx.warning(f"Unknown framework: {framework_name}")
            continue

    # Calculate consolidated metrics
    if assessments:
        total_score = sum(a.overall_score for a in assessments) / len(assessments)
        overall_status = max(
            (a.overall_status for a in assessments),
            key=lambda x: [
                "compliant",
                "partially_compliant",
                "non_compliant",
                "not_applicable",
            ].index(x.value),
        )
    else:
        total_score = 0.0
        overall_status = "not_applicable"

    report = {
        "target": target,
        "frameworks_assessed": len(assessments),
        "overall_score": total_score,
        "overall_status": overall_status,
        "assessments": [a.model_dump() for a in assessments],
        "generated_at": assessments[0].assessment_date.isoformat()
        if assessments
        else None,
    }

    ctx.info(f"Report generated. Overall score: {total_score:.1f}")

    return report


async def compliance_check(ctx, requirement_id: str, target: str) -> Dict[str, Any]:
    """
    Verifica conformidade para um requisito específico.

    Args:
        requirement_id: ID do requisito (ex: "GDPR-ART6", "HIPAA-164.308")
        target: Sistema ou processo alvo

    Returns:
        Status de conformidade para o requisito específico
    """
    ctx.info(f"Checking compliance for requirement {requirement_id} on {target}")

    # Extract framework from requirement ID
    if requirement_id.startswith("GDPR"):
        framework = ComplianceFramework.GDPR
    elif requirement_id.startswith("HIPAA"):
        framework = ComplianceFramework.HIPAA
    elif requirement_id.startswith("PCI"):
        framework = ComplianceFramework.PCI_DSS
    elif requirement_id.startswith("SOX"):
        framework = ComplianceFramework.SOX
    elif requirement_id.startswith("A."):
        framework = ComplianceFramework.ISO_27001
    elif requirement_id.startswith(("ID.", "PR.", "DE.", "RS.", "RC.")):
        framework = ComplianceFramework.NIST
    else:
        # Fallback - try to infer from target assessment
        framework = ComplianceFramework.GDPR  # Default fallback

    guardian = get_compliance_guardian()
    assessment = await guardian.assess_compliance(target, framework)

    # Find specific requirement
    specific_check = None
    for check in assessment.checks:
        if check.requirement.requirement_id == requirement_id:
            specific_check = check
            break

    if specific_check:
        result = {
            "requirement_id": requirement_id,
            "found": True,
            "status": specific_check.status.value,
            "score": specific_check.score,
            "evidence": specific_check.evidence,
            "violations": specific_check.violations,
            "remediation_steps": specific_check.remediation_steps,
            "checked_at": specific_check.checked_at.isoformat(),
        }
    else:
        result = {
            "requirement_id": requirement_id,
            "found": False,
            "status": "not_found",
            "message": f"Requirement {requirement_id} not found in {framework.value} framework",
        }

    ctx.info(f"Compliance check result: {result['status']}")

    return result
