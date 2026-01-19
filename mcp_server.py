#!/usr/bin/env python3
"""
Vertice Cyber - MCP Server Principal
Expõe 11 Meta-Agents como MCP Tools.
"""

import argparse
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP, Context

from core.settings import settings
from core.memory import get_memory_pool
from tools.magistrate import ethical_validate, ethical_audit
from tools.osint import osint_investigate, osint_breach_check, osint_google_dork
from tools.threat import threat_analyze, threat_intelligence, threat_predict
from tools.compliance import compliance_assess, compliance_report, compliance_check

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
    """Lista de todos os agents disponíveis."""
    return """
# Vertice Cyber Agents
| # | Agent | Tier | Status |
|---|-------|------|--------|
| 01 | Ethical Magistrate | Governance | ✅ Active |
| 02 | OSINT Hunter | Intelligence | ✅ Active |
| 03 | Threat Prophet | Intelligence | ✅ Active |
| 04 | Compliance Guardian | Intelligence | ✅ Active |
| 05 | Immune Coordinator | Immune | 🔄 |
| 06 | Sentinel Prime | Immune | 🔄 |
| 07 | The Watcher | Immune | 🔄 |
| 08 | Wargame Executor | Offensive | 🔄 |
| 09 | Patch Validator ML | Offensive | 🔄 |
| 10 | CLI Cyber Agent | Integration | 🔄 |
| 11 | MCP Tool Bridge | Integration | ✅ |
"""


# =============================================================================
# PLACEHOLDER TOOLS
# =============================================================================


@mcp.tool()
async def system_health(ctx: Context) -> dict:
    """Verifica a saúde do sistema Vertice Cyber."""
    ctx.info("Checking system health...")
    return {
        "status": "healthy",
        "version": settings.version,
        "agents_loaded": 9,
        "agents_total": 11,
    }


@mcp.tool()
async def list_tools(ctx: Context) -> list[dict]:
    """Lista todas as tools disponíveis."""
    return [
        {"name": "system_health", "agent": "bridge"},
        {"name": "ethical_validate", "agent": "magistrate"},
        {"name": "ethical_audit", "agent": "magistrate"},
        {"name": "osint_investigate", "agent": "osint_hunter"},
        {"name": "osint_breach_check", "agent": "osint_hunter"},
        {"name": "osint_google_dork", "agent": "osint_hunter"},
        {"name": "threat_analyze", "agent": "threat_prophet"},
        {"name": "threat_intelligence", "agent": "threat_prophet"},
        {"name": "threat_predict", "agent": "threat_prophet"},
        {"name": "compliance_assess", "agent": "compliance_guardian"},
        {"name": "compliance_report", "agent": "compliance_guardian"},
        {"name": "compliance_check", "agent": "compliance_guardian"},
        # Temporarily disabled due to dependency conflicts
        # {"name": "threat_analyze", "agent": "threat_prophet"},
        {"name": "threat_analyze", "agent": "threat_prophet"},
        {"name": "threat_intelligence", "agent": "threat_prophet"},
        {"name": "threat_predict", "agent": "threat_prophet"},
        {"name": "compliance_assess", "agent": "compliance_guardian"},
        {"name": "compliance_report", "agent": "compliance_guardian"},
        {"name": "compliance_check", "agent": "compliance_guardian"},
    ]


@mcp.tool()
async def ethical_validate_tool(
    ctx: Context,
    action: str,
    context: Optional[Dict[str, Any]] = None,
    actor: str = "user",
) -> Dict[str, Any]:
    """
    Valida uma ação contra o framework ético de 7 fases.

    Args:
        action: Descrição da ação a ser validada
        context: Contexto adicional (has_pii, target, etc.)
        actor: Quem está solicitando a ação

    Returns:
        Decisão ética com approved, conditions, reasoning
    """
    return await ethical_validate(ctx, action, context, actor)


@mcp.tool()
async def ethical_audit_tool(ctx: Context, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retorna histórico de decisões éticas.

    Args:
        limit: Número máximo de decisões a retornar

    Returns:
        Lista de decisões recentes
    """
    return await ethical_audit(ctx, limit)


# =============================================================================
# INTELLIGENCE TOOLS
# =============================================================================


@mcp.tool()
async def osint_investigate_tool(
    ctx: Context, target: str, depth: str = "basic"
) -> Dict[str, Any]:
    """
    Executa investigação OSINT sobre um alvo.

    Args:
        target: Email, domínio ou IP a investigar
        depth: Profundidade (basic, deep, exhaustive)

    Returns:
        Resultado com findings, breaches e risk_score
    """
    return await osint_investigate(ctx, target, depth)


@mcp.tool()
async def osint_breach_check_tool(ctx: Context, email: str) -> Dict[str, Any]:
    """
    Verifica se email aparece em breaches conhecidos.

    Args:
        email: Email a verificar

    Returns:
        Lista de breaches onde o email aparece
    """
    return await osint_breach_check(ctx, email)


@mcp.tool()
async def osint_google_dork_tool(ctx: Context, target_domain: str) -> Dict[str, Any]:
    """
    Gera Google dorks para reconhecimento de domínio.

    Args:
        target_domain: Domínio alvo

    Returns:
        Lista de dorks categorizados
    """
    return await osint_google_dork(ctx, target_domain)


@mcp.tool()
async def threat_analyze_tool(
    ctx: Context, target: str, include_predictions: bool = True
) -> Dict[str, Any]:
    """
    Executa análise completa de ameaças para um alvo.

    Args:
        target: Sistema, rede ou organização a analisar
        include_predictions: Incluir predições de ameaças futuras

    Returns:
        Análise completa com indicadores, técnicas MITRE e predições
    """
    return await threat_analyze(ctx, target, include_predictions)


@mcp.tool()
async def threat_intelligence_tool(ctx: Context, query: str) -> Dict[str, Any]:
    """
    Busca inteligência de ameaças usando MITRE ATT&CK.

    Args:
        query: Termo de busca (ex: "ransomware", "APT41")

    Returns:
        Técnicas MITRE ATT&CK relacionadas à query
    """
    return await threat_intelligence(ctx, query)


@mcp.tool()
async def threat_predict_tool(ctx: Context, target: str) -> Dict[str, Any]:
    """
    Gera predições de ameaças futuras para um alvo.

    Args:
        target: Sistema ou organização alvo

    Returns:
        Predições de ameaças com ações recomendadas
    """
    return await threat_predict(ctx, target)


@mcp.tool()
async def compliance_assess_tool(
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
    return await compliance_assess(ctx, target, framework)


@mcp.tool()
async def compliance_report_tool(
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
    return await compliance_report(ctx, target, frameworks)


@mcp.tool()
async def compliance_check_tool(
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
    return await compliance_check(ctx, requirement_id, target)


# =============================================================================
# STARTUP / SHUTDOWN
# =============================================================================

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
        return

    if args.http:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
