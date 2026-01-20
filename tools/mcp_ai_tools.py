"""
Vertex AI MCP Tools
Ferramentas MCP específicas para integração com Vertex AI.
"""

from typing import Any, Dict, List
from fastmcp import Context

from tools.vertex_ai import get_vertex_ai

async def ai_threat_analysis(
    ctx: Context,
    target: str,
    context_data: Dict[str, Any],
    analysis_type: str = "comprehensive",
) -> Dict[str, Any]:
    """
    Análise inteligente de ameaças usando Vertex AI.

    Args:
        target: Alvo da análise (IP, domínio, email)
        context_data: Dados contextuais (threat indicators, OSINT findings, etc.)
        analysis_type: Tipo de análise ("comprehensive", "quick", "detailed")

    Returns:
        Análise completa com insights de IA
    """
    vertex_ai = get_vertex_ai()

    # Add analysis type to context
    context_data["analysis_type"] = analysis_type
    context_data["target_type"] = _infer_target_type(target)

    result = await vertex_ai.analyze_threat_intelligence(
        f"Analyze {target} for {analysis_type} threat intelligence", context_data
    )

    await ctx.info(
        f"AI Threat Analysis completed for {target}: Risk {result.get('risk_level', 'unknown')}"
    )
    return result


async def ai_compliance_assessment(
    ctx: Context, target: str, framework: str, current_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Avaliação de conformidade inteligente usando Vertex AI.

    Args:
        target: Sistema/alvo da avaliação
        framework: Framework de conformidade (gdpr, hipaa, pci_dss)
        current_state: Estado atual (controles implementados, violações, etc.)

    Returns:
        Relatório executivo de conformidade com recomendações de IA
    """
    vertex_ai = get_vertex_ai()

    result = await vertex_ai.generate_compliance_report(
        target, framework, current_state
    )

    await ctx.info(
        f"AI Compliance Report generated for {target} ({framework}): Score {result.get('overall_compliance_score', 0)}"
    )
    return result


async def ai_osint_analysis(
    ctx: Context,
    target: str,
    findings: List[Dict[str, Any]],
    analysis_focus: str = "risk_assessment",
) -> Dict[str, Any]:
    """
    Análise inteligente de achados OSINT usando Vertex AI.

    Args:
        target: Alvo investigado
        findings: Lista de achados OSINT
        analysis_focus: Foco da análise ("risk_assessment", "behavioral", "threat_hunting")

    Returns:
        Análise completa dos achados com insights de IA
    """
    vertex_ai = get_vertex_ai()

    # Add analysis context
    enriched_findings = findings.copy()
    for finding in enriched_findings:
        finding["analysis_focus"] = analysis_focus

    result = await vertex_ai.analyze_osint_findings(target, enriched_findings)

    await ctx.info(
        f"AI OSINT Analysis completed for {target}: {len(findings)} findings analyzed"
    )
    return result


async def ai_stream_analysis(
    ctx: Context,
    analysis_type: str,
    data: Dict[str, Any],
    stream_format: str = "markdown",
) -> str:
    """
    Análise em streaming em tempo real usando Vertex AI.

    Args:
        analysis_type: Tipo de análise ("threat", "compliance", "osint", "forensic")
        data: Dados para análise
        stream_format: Formato de saída ("markdown", "json", "text")

    Returns:
        Análise completa em formato streaming
    """
    vertex_ai = get_vertex_ai()

    # Format prompt based on analysis type
    formatted_data = data.copy()
    formatted_data["stream_format"] = stream_format
    formatted_data["analysis_context"] = (
        f"Provide a {analysis_type} analysis in {stream_format} format"
    )

    full_response = ""
    async for chunk in vertex_ai.stream_analysis(analysis_type, formatted_data):
        full_response += chunk
        # In a real streaming implementation, you'd yield chunks here
        # For now, we accumulate and return complete response

    await ctx.info(f"AI Stream Analysis completed: {analysis_type} analysis generated")
    return full_response


async def ai_integrated_assessment(
    ctx: Context, target: str, assessment_scope: str = "full"
) -> Dict[str, Any]:
    """
    Avaliação integrada usando todos os agentes com IA.

    Args:
        target: Alvo da avaliação integrada
        assessment_scope: Escopo ("full", "threat_only", "compliance_only", "osint_only")

    Returns:
        Avaliação completa integrada com insights de IA
    """
    vertex_ai = get_vertex_ai()

    # Gather data from all intelligence tools
    integrated_data = {
        "target": target,
        "assessment_scope": assessment_scope,
        "intelligence_layers": {},
    }

    try:
        # Threat Intelligence
        if assessment_scope in ["full", "threat_only"]:
            await ctx.info(f"Running threat analysis for {target}...")
            threat_data = await _gather_threat_intelligence(target)
            integrated_data["intelligence_layers"]["threat"] = threat_data

        # OSINT Investigation
        if assessment_scope in ["full", "osint_only"]:
            await ctx.info(f"Running OSINT investigation for {target}...")
            osint_data = await _gather_osint_intelligence(target)
            integrated_data["intelligence_layers"]["osint"] = osint_data

        # Compliance Assessment
        if assessment_scope in ["full", "compliance_only"]:
            await ctx.info(f"Running compliance assessment for {target}...")
            compliance_data = await _gather_compliance_intelligence(target)
            integrated_data["intelligence_layers"]["compliance"] = compliance_data

        # AI-Powered Synthesis
        await ctx.info("Generating AI-powered integrated assessment...")
        synthesis = await vertex_ai.analyze_threat_intelligence(
            f"Integrated intelligence assessment for {target} with scope {assessment_scope}",
            integrated_data,
        )

        # Combine all data
        result = {
            "target": target,
            "assessment_scope": assessment_scope,
            "ai_synthesis": synthesis,
            "intelligence_layers": integrated_data["intelligence_layers"],
            "generated_at": synthesis.get("timestamp"),
            "model_used": synthesis.get("model_used"),
        }

        await ctx.info(
            f"Integrated AI Assessment completed for {target}: Risk {synthesis.get('risk_level', 'unknown')}"
        )
        return result

    except Exception as e:
        await ctx.error(f"Integrated assessment failed: {e}")
        return {
            "target": target,
            "assessment_scope": assessment_scope,
            "error": str(e),
            "status": "failed",
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _infer_target_type(target: str) -> str:
    """Infer target type from string pattern."""
    import re

    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", target):
        return "ip_address"
    elif "@" in target and "." in target:
        return "email"
    elif "." in target:
        return "domain"
    else:
        return "unknown"


async def _gather_threat_intelligence(target: str) -> Dict[str, Any]:
    """Gather threat intelligence data."""
    try:
        from tools.threat import get_threat_prophet

        prophet = get_threat_prophet()
        analysis = await prophet.analyze_threats(target, include_predictions=True)
        return {
            "analysis": analysis.model_dump()
            if hasattr(analysis, "model_dump")
            else analysis,
            "intelligence_type": "threat",
        }
    except Exception as e:
        return {"error": str(e), "intelligence_type": "threat"}


async def _gather_osint_intelligence(target: str) -> Dict[str, Any]:
    """Gather OSINT intelligence data."""
    try:
        from tools.osint import get_osint_hunter

        hunter = get_osint_hunter()
        result = await hunter.investigate(target)
        return {
            "investigation": result.model_dump()
            if hasattr(result, "model_dump")
            else {
                "target": result.target,
                "findings": [
                    f.model_dump() if hasattr(f, "model_dump") else f.__dict__
                    for f in result.findings
                ],
                "risk_score": result.risk_score,
            },
            "intelligence_type": "osint",
        }
    except Exception as e:
        return {"error": str(e), "intelligence_type": "osint"}


async def _gather_compliance_intelligence(target: str) -> Dict[str, Any]:
    """Gather compliance intelligence data."""
    try:
        from tools.compliance.guardian import get_compliance_guardian

        guardian = get_compliance_guardian()
        assessment = await guardian.assess_compliance(target, "gdpr")
        return {
            "assessment": assessment.model_dump()
            if hasattr(assessment, "model_dump")
            else assessment,
            "intelligence_type": "compliance",
        }
    except Exception as e:
        return {"error": str(e), "intelligence_type": "compliance"}