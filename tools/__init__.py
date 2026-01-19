"""
Vertice Cyber - MCP Tools Package

LAZY IMPORTS: Modules are imported only when accessed to avoid dependency conflicts.
This prevents cascading import failures from fastmcp/rich compatibility issues.
"""

import importlib
from typing import Any

__all__ = [
    "get_magistrate",
    "ethical_validate",
    "ethical_audit",
    "get_osint_hunter",
    "osint_investigate",
    "osint_breach_check",
    "osint_google_dork",
    "get_threat_prophet",
    "threat_analyze",
    "threat_intelligence",
    "threat_predict",
    "get_compliance_guardian",
    "compliance_assess",
    "compliance_report",
    "compliance_check",
]


def __getattr__(name: str) -> Any:
    """
    Lazy import implementation.
    Imports modules only when they are first accessed.
    """
    lazy_imports = {
        # Magistrate (problematic due to fastmcp)
        "get_magistrate": (".magistrate", "get_magistrate"),
        "ethical_validate": (".magistrate", "ethical_validate"),
        "ethical_audit": (".magistrate", "ethical_audit"),
        # OSINT
        "get_osint_hunter": (".osint", "get_osint_hunter"),
        "osint_investigate": (".osint", "osint_investigate"),
        "osint_breach_check": (".osint", "osint_breach_check"),
        "osint_google_dork": (".osint", "osint_google_dork"),
        # Threat
        "get_threat_prophet": (".threat", "get_threat_prophet"),
        "threat_analyze": (".threat", "threat_analyze"),
        "threat_intelligence": (".threat", "threat_intelligence"),
        "threat_predict": (".threat", "threat_predict"),
        # Compliance
        "get_compliance_guardian": (".compliance", "get_compliance_guardian"),
        "compliance_assess": (".compliance", "compliance_assess"),
        "compliance_report": (".compliance", "compliance_report"),
        "compliance_check": (".compliance", "compliance_check"),
    }

    if name in lazy_imports:
        module_name, attr_name = lazy_imports[name]
        try:
            module = importlib.import_module(module_name, __name__)
            return getattr(module, attr_name)
        except Exception as e:
            # Log the error but don't crash the entire import system
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to lazy import {name} from {module_name}: {e}")
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
