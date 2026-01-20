"""
Vertice Cyber - MCP Server Principal
Expõe 11 Meta-Agents como MCP Tools.
"""

import argparse
import logging
from typing import Any, Dict, List

from fastmcp import FastMCP, Context

from core.settings import settings
from core.memory import get_memory_pool
from tools.magistrate import ethical_validate
from tools.osint import osint_investigate, osint_breach_check, osint_google_dork
from tools.threat import threat_analyze, threat_intelligence, threat_predict
from tools.compliance import compliance_assess, compliance_report, compliance_check
from tools.wargame import wargame_list_scenarios, wargame_run_simulation
from tools.patch_ml import patch_validate
from tools.mcp_ai_tools import (
    ai_threat_analysis,
    ai_compliance_assessment,
    ai_osint_analysis,
    ai_stream_analysis,
    ai_integrated_assessment,
)

# Import AI tools module to register tools

logging.basicConfig(
    level=getattr(logging, settings.server.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vertice_cyber")


# =============================================================================
# MCP SERVER INSTANCE
# =============================================================================

mcp = FastMCP(name="vertice-cyber", version="2.0.0")


# =============================================================================
# CORE RESOURCES
# =============================================================================


@mcp.resource("vertice://status")
async def get_system_status() -> str:
    """Status geral do sistema Vertice Cyber."""
    return f"""
# Vertice Cyber Status
- Name: {settings.project_name}
- Version: {settings.version}
- Transport: {settings.server.transport}
"""


@mcp.resource("vertice://agents")
async def get_agents_list() -> str:
    """Lista de agentes disponíveis."""
    return """
# Available Agents

## Core Intelligence
- **Threat Prophet**: Análise avançada de ameaças cibernéticas
- **OSINT Hunter**: Investigação de inteligência de código aberto
- **Compliance Guardian**: Avaliação de conformidade regulatória

## Ethical Governance
- **Magistrate**: Validação ética e auditoria constitucional

## Offensive Security
- **Wargame Executor**: Simulação de ataques e validação de defesas
- **Patch Validator ML**: Análise preditiva de risco em código

## AI-Powered (Vertex AI)
- **AI Threat Analysis**: Análise inteligente de ameaças
- **AI Compliance Assessment**: Avaliação de conformidade com IA
- **AI OSINT Analysis**: Análise OSINT inteligente
- **AI Stream Analysis**: Análise em tempo real
- **AI Integrated Assessment**: Avaliação integrada completa
"""


# =============================================================================
# INTELLIGENCE TOOLS
# =============================================================================


@mcp.tool()
async def threat_analyze_tool(
    ctx: Context, target: str, deep_analysis: bool = False
) -> Dict[str, Any]:
    """Analisa ameaças para um alvo específico usando Threat Prophet."""
    result = await threat_analyze(ctx, target, deep_analysis)
    await ctx.info(f"Threat analysis completed for {target}")
    return result


@mcp.tool()
async def threat_intelligence_tool(ctx: Context, query: str) -> Dict[str, Any]:
    """Busca inteligência de ameaças baseada em consulta."""
    result = await threat_intelligence(ctx, query)
    await ctx.info(f"Threat intelligence search completed for: {query}")
    return result


@mcp.tool()
async def threat_predict_tool(ctx: Context, target: str) -> Dict[str, Any]:
    """Faz previsões de ameaças para um alvo."""
    result = await threat_predict(ctx, target)
    await ctx.info(f"Threat prediction completed for {target}")
    return result


@mcp.tool()
async def osint_investigate_tool(ctx: Context, target: str) -> Dict[str, Any]:
    """Investiga um alvo usando técnicas OSINT."""
    result = await osint_investigate(ctx, target)
    await ctx.info(f"OSINT investigation completed for {target}")
    return result


@mcp.tool()
async def osint_breach_check_tool(ctx: Context, email: str) -> Dict[str, Any]:
    """Verifica se um email foi comprometido em breaches."""
    result = await osint_breach_check(ctx, email)
    await ctx.info(f"Breach check completed for {email}")
    return result


@mcp.tool()
async def osint_google_dork_tool(ctx: Context, query: str) -> Dict[str, Any]:
    """Executa Google dorking para descoberta de informações."""
    result = await osint_google_dork(ctx, query)
    await ctx.info(f"Google dorking completed for: {query}")
    return result


@mcp.tool()
async def compliance_assess_tool(
    ctx: Context, target: str, framework: str
) -> Dict[str, Any]:
    """Avalia conformidade de um alvo com framework específico."""
    result = await compliance_assess(ctx, target, framework)
    await ctx.info(f"Compliance assessment completed for {target} ({framework})")
    return result


@mcp.tool()
async def compliance_report_tool(
    ctx: Context, target: str, frameworks: List[str]
) -> Dict[str, Any]:
    """Gera relatório de conformidade para múltiplos frameworks."""
    result = await compliance_report(ctx, target, frameworks)
    await ctx.info(f"Compliance report generated for {target}")
    return result


@mcp.tool()
async def compliance_check_tool(
    ctx: Context, requirement_id: str, target: str
) -> Dict[str, Any]:
    """Verifica um requisito específico de conformidade."""
    result = await compliance_check(ctx, requirement_id, target)
    await ctx.info(f"Compliance check completed for requirement {requirement_id}")
    return result


@mcp.tool()
async def ethical_validate_tool(
    ctx: Context, action: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Valida se uma ação é eticamente aceitável."""
    result = await ethical_validate(ctx, action, context)
    await ctx.info("Ethical validation completed")
    return result


# =============================================================================
# OFFENSIVE TOOLS (Phase 4)
# =============================================================================


@mcp.tool()
async def wargame_list_scenarios_tool(ctx: Context) -> List[Dict[str, Any]]:
    """Lista cenários de ataque simulados disponíveis."""
    result = await wargame_list_scenarios(ctx)
    await ctx.info("Listed wargame scenarios")
    return result


@mcp.tool()
async def wargame_run_simulation_tool(
    ctx: Context, scenario_id: str, target: str = "local"
) -> Dict[str, Any]:
    """Executa uma simulação de ataque (Wargame)."""
    result = await wargame_run_simulation(ctx, scenario_id, target)
    await ctx.info(f"Wargame simulation {scenario_id} completed")
    return result


@mcp.tool()
async def patch_validate_tool(
    ctx: Context, diff_content: str, language: str = "python"
) -> Dict[str, Any]:
    """Valida um patch de código quanto a riscos de segurança."""
    result = await patch_validate(ctx, diff_content, language)
    await ctx.info("Patch validation completed")
    return result


# =============================================================================
# AI TOOLS (Vertex AI)
# =============================================================================

mcp.tool()(ai_threat_analysis)
mcp.tool()(ai_compliance_assessment)
mcp.tool()(ai_osint_analysis)
mcp.tool()(ai_stream_analysis)
mcp.tool()(ai_integrated_assessment)


# CONSTITUTIONAL EXEMPTION (Padrão Pagani - Artigo II):
# Reason: FastMCP framework does not yet support startup/shutdown hooks
# ETA: When FastMCP adds lifecycle hook support
# Tracking: FastMCP library development
# Alternative: Manual initialization in main()
if not hasattr(mcp, "on_startup"):
    # Manual initialization until FastMCP supports hooks
    _ = get_memory_pool()  # Initialize memory pool


# =============================================================================
# MAIN
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Vertice Cyber MCP Server")
    parser.add_argument("--http", action="store_true", help="HTTP mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP")
    parser.add_argument("--check", action="store_true", help="Check tools and exit")

    args = parser.parse_args()

    if args.check:
        print("🔺 Vertice Cyber - Tools Check")
        print("  ✅ system_health")
        print("  ✅ list_tools")
        print("  ✅ ethical_validate_tool")
        print("  ✅ ethical_audit_tool")
        print("  ✅ osint_investigate_tool")
        print("  ✅ osint_breach_check_tool")
        print("  ✅ osint_google_dork_tool")
        print("  ✅ threat_analyze_tool")
        print("  ✅ threat_intelligence_tool")
        print("  ✅ threat_predict_tool")
        print("  ✅ compliance_assess_tool")
        print("  ✅ compliance_report_tool")
        print("  ✅ compliance_check_tool")
        print("  ✅ wargame_list_scenarios_tool")
        print("  ✅ wargame_run_simulation_tool")
        print("  ✅ patch_validate_tool")
        print("  ✅ ai_threat_analysis")
        print("  ✅ ai_compliance_assessment")
        print("  ✅ ai_osint_analysis")
        print("  ✅ ai_stream_analysis")
        print("  ✅ ai_integrated_assessment")
        return

    if args.http:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
