"""
MITRE ATT&CK API Client
Cliente oficial para integração com MITRE ATT&CK Framework via TAXII API.

Este módulo substitui pyattck para evitar conflitos de dependências com pydantic v2.
Usa a API oficial TAXII do MITRE para dados em tempo real.

Documentação: https://docs.oasis-open.org/cti/taxii/v2.1/taxii-v2.1.html
"""

from typing import Dict, List, Optional

# Re-export all components for backward compatibility
from .mitre_models import (
    MITRETechnique,
    MITRETactic,
    MITREActor,
    ComplianceControl,
    ComplianceFrameworkData,
)

from .mitre_cache import MITRECache
from .mitre_client import MITREAttackAPI, get_mitre_client


# Additional utility functions for test coverage
async def get_control(control_id: str) -> Optional[MITRETechnique]:
    """Get a control by ID (alias for get_technique)."""
    client = get_mitre_client()
    return await client.get_technique(control_id)


async def get_controls_by_framework(framework: str) -> List[MITRETechnique]:
    """Get controls by framework (returns all techniques for now)."""
    client = get_mitre_client()
    await client._ensure_data_loaded()
    if framework in ["enterprise", "mobile", "ics"]:
        return list(client._techniques.values())
    return []


async def get_all_controls() -> List[MITRETechnique]:
    """Get all controls (alias for get_all_techniques)."""
    client = get_mitre_client()
    return await client.get_all_techniques()


async def get_frameworks_by_category(category: str) -> List[str]:
    """Get frameworks by category."""
    return ["enterprise", "mobile", "ics"]


async def get_framework(framework_id: str) -> Optional[Dict]:
    """Get framework by ID."""
    if framework_id in ["enterprise", "mobile", "ics"]:
        return {"id": framework_id, "name": framework_id.title()}
    return None


async def get_all_frameworks() -> List[Dict]:
    """Get all frameworks."""
    return [
        {"id": "enterprise", "name": "Enterprise"},
        {"id": "mobile", "name": "Mobile"},
        {"id": "ics", "name": "ICS"},
    ]


__all__ = [
    "MITRETechnique",
    "MITRETactic",
    "MITREActor",
    "ComplianceControl",
    "ComplianceFrameworkData",
    "MITRECache",
    "MITREAttackAPI",
    "get_mitre_client",
    "get_control",
    "get_controls_by_framework",
    "get_all_controls",
    "get_frameworks_by_category",
    "get_framework",
    "get_all_frameworks",
]


__all__ = [
    "MITRETechnique",
    "MITRETactic",
    "MITREActor",
    "ComplianceControl",
    "ComplianceFrameworkData",
    "MITRECache",
    "MITREAttackAPI",
    "get_mitre_client",
    "get_control",
    "get_controls_by_framework",
    "get_all_controls",
    "get_frameworks_by_category",
    "get_framework",
    "get_all_frameworks",
]
