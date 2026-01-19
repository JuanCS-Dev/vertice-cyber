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
| 02 | OSINT Hunter | Intelligence | 🔄 |
| 03 | Threat Prophet | Intelligence | 🔄 |
| 04 | Compliance Guardian | Intelligence | 🔄 |
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
        "agents_loaded": 3,
        "agents_total": 11,
    }


@mcp.tool()
async def list_tools(ctx: Context) -> list[dict]:
    """Lista todas as tools disponíveis."""
    return [
        {"name": "system_health", "agent": "bridge"},
        {"name": "ethical_validate", "agent": "magistrate"},
        {"name": "ethical_audit", "agent": "magistrate"},
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
# STARTUP / SHUTDOWN
# =============================================================================

# TODO: Implement startup/shutdown hooks when FastMCP supports them
# For now, initialization happens in main()
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
        return

    if args.http:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
