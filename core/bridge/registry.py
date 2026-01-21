"""
Bridge Registry - Tool Registration and Metadata.
================================================

Maps tool names to their implementation functions and provides metadata.
"""

from typing import Any, Callable, Coroutine, Dict, List
from .models import ToolInfo

# Governance
from tools.magistrate import ethical_validate, ethical_audit

# OSINT
from tools.osint import osint_investigate, osint_breach_check, osint_google_dork

# Threat
from tools.threat import threat_analyze, threat_intelligence, threat_predict

# Compliance
from tools.compliance import compliance_assess, compliance_report, compliance_check

# Offensive
from tools.wargame import wargame_list_scenarios, wargame_run_simulation
from tools.patch_ml import patch_validate

# Multimodal
from tools.visionary import visionary_analyze
from tools.deepfake_scanner import scan_media

# CyberSec
from tools.cybersec_basic import cybersec_recon

# Health
from tools.health_check import provider_health_check
from core.metrics import provider_metrics_tool

# AI
from tools.mcp_ai_tools import (
    ai_threat_analysis,
    ai_compliance_assessment,
    ai_osint_analysis,
    ai_stream_analysis,
    ai_integrated_assessment,
)


# Dynamic Import Wrapper
async def set_ai_model_wrapper(ctx, model_alias: str) -> Dict[str, Any]:
    from tools.vertex_ai import get_vertex_ai

    vertex = get_vertex_ai()
    new_model = vertex.set_model(model_alias)
    await ctx.info(f"AI Engine switched to {new_model}")
    return {"status": "success", "active_model": new_model}


ToolFunction = Callable[..., Coroutine[Any, Any, Any]]

# Mapping Name -> Function
TOOL_REGISTRY: Dict[str, ToolFunction] = {
    "ethical_validate": ethical_validate,
    "ethical_audit": ethical_audit,
    "osint_investigate": osint_investigate,
    "osint_breach_check": osint_breach_check,
    "osint_google_dork": osint_google_dork,
    "threat_analyze": threat_analyze,
    "threat_intelligence": threat_intelligence,
    "threat_predict": threat_predict,
    "compliance_assess": compliance_assess,
    "compliance_report": compliance_report,
    "compliance_check": compliance_check,
    "wargame_list_scenarios": wargame_list_scenarios,
    "wargame_run_simulation": wargame_run_simulation,
    "patch_validate": patch_validate,
    "visionary_analyze": visionary_analyze,
    "deepfake_scan_tool": scan_media,
    "cybersec_recon": cybersec_recon,
    "provider_health_check": provider_health_check,
    "provider_metrics": provider_metrics_tool,
    "ai_threat_analysis": ai_threat_analysis,
    "ai_compliance_assessment": ai_compliance_assessment,
    "ai_osint_analysis": ai_osint_analysis,
    "ai_stream_analysis": ai_stream_analysis,
    "ai_integrated_assessment": ai_integrated_assessment,
    "set_ai_model": set_ai_model_wrapper,
}

# Metadata Registry
TOOL_METADATA: List[ToolInfo] = [
    ToolInfo(
        name="deepfake_scan_tool",
        agent="Visionary Sentinel",
        category="intelligence",
        description="Deepfake analysis for video/audio/image",
        parameters={
            "file_b64": "string",
            "mime_type": "string",
            "filename": "string",
        },
    ),
    ToolInfo(
        name="ethical_validate",
        agent="Ethical Magistrate",
        category="governance",
        description="Validates actions against ethical framework",
        parameters={"action": "string", "context": "object"},
    ),
    ToolInfo(
        name="ethical_audit",
        agent="Ethical Magistrate",
        category="governance",
        description="Audit recent ethical decisions",
        parameters={"limit": "integer"},
    ),
    ToolInfo(
        name="osint_investigate",
        agent="OSINT Hunter",
        category="intelligence",
        description="OSINT investigation on target",
        parameters={"target": "string", "depth": "string"},
    ),
    ToolInfo(
        name="osint_breach_check",
        agent="OSINT Hunter",
        category="intelligence",
        description="Check for data breaches",
        parameters={"email": "string"},
    ),
    ToolInfo(
        name="osint_google_dork",
        agent="OSINT Hunter",
        category="intelligence",
        description="Perform Google Dork queries",
        parameters={"query": "string"},
    ),
    ToolInfo(
        name="threat_analyze",
        agent="Threat Prophet",
        category="intelligence",
        description="Complete threat analysis",
        parameters={"target": "string", "include_predictions": "boolean"},
    ),
    ToolInfo(
        name="threat_intelligence",
        agent="Threat Prophet",
        category="intelligence",
        description="Search threat intelligence",
        parameters={"query": "string"},
    ),
    ToolInfo(
        name="threat_predict",
        agent="Threat Prophet",
        category="intelligence",
        description="Predict future threats",
        parameters={"target": "string"},
    ),
    ToolInfo(
        name="compliance_assess",
        agent="Compliance Guardian",
        category="governance",
        description="Assesses compliance against framework",
        parameters={"target": "string", "framework": "string"},
    ),
    ToolInfo(
        name="compliance_report",
        agent="Compliance Guardian",
        category="governance",
        description="Generate compliance report",
        parameters={"target": "string", "frameworks": "list"},
    ),
    ToolInfo(
        name="compliance_check",
        agent="Compliance Guardian",
        category="governance",
        description="Check specific compliance requirement",
        parameters={"requirement_id": "string", "target": "string"},
    ),
    ToolInfo(
        name="wargame_list_scenarios",
        agent="Wargame Executor",
        category="offensive",
        description="Lists available attack scenarios",
        parameters={},
    ),
    ToolInfo(
        name="wargame_run_simulation",
        agent="Wargame Executor",
        category="offensive",
        description="Executes attack simulation",
        parameters={"scenario_id": "string", "target": "string"},
    ),
    ToolInfo(
        name="patch_validate",
        agent="Patch Validator ML",
        category="offensive",
        description="Security analysis of code patches",
        parameters={"diff_content": "string", "language": "string"},
    ),
    ToolInfo(
        name="cybersec_recon",
        agent="CyberSec Investigator",
        category="recon",
        description="Performs basic reconnaissance (ports, web)",
        parameters={"target": "string", "scan_ports": "boolean", "scan_web": "boolean"},
    ),
    ToolInfo(
        name="ai_threat_analysis",
        agent="AI Core",
        category="ai",
        description="AI-powered threat analysis",
        parameters={"target": "string", "context": "object"},
    ),
    ToolInfo(
        name="ai_compliance_assessment",
        agent="AI Core",
        category="ai",
        description="AI-powered compliance assessment",
        parameters={"target": "string", "framework": "string"},
    ),
    ToolInfo(
        name="ai_osint_analysis",
        agent="AI Core",
        category="ai",
        description="AI-powered OSINT analysis",
        parameters={"target": "string", "findings": "list"},
    ),
    ToolInfo(
        name="ai_stream_analysis",
        agent="AI Core",
        category="ai",
        description="Stream AI analysis",
        parameters={"analysis_type": "string", "data": "object"},
    ),
    ToolInfo(
        name="ai_integrated_assessment",
        agent="AI Core",
        category="ai",
        description="Integrated AI assessment",
        parameters={"target": "string"},
    ),
    ToolInfo(
        name="visionary_analyze",
        agent="Visionary Sentinel",
        category="intelligence",
        description="Multimodal forensic analysis via direct upload or URL",
        parameters={
            "file_b64": "string (optional)",
            "file_url": "string (optional)",
            "mime_type": "string",
            "mode": "string",
        },
    ),
    ToolInfo(
        name="provider_health_check",
        agent="System",
        category="system",
        description="Checks health of all providers",
        parameters={},
    ),
    ToolInfo(
        name="provider_metrics",
        agent="System",
        category="system",
        description="Get provider usage metrics",
        parameters={},
    ),
    ToolInfo(
        name="set_ai_model",
        agent="AI Core",
        category="ai",
        description="Switch between Pro and Flash models",
        parameters={"model_alias": "string"},
    ),
]
