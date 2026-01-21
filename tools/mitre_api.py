"""
MITRE ATT&CK API Client (Legacy/Compat Wrapper)
Wraps mitre_client.py for backward compatibility.
"""

from typing import List, Optional
from .mitre_models import (
    MITRETechnique,
    MITRETactic,
    MITREActor,
    ComplianceControl,
    ComplianceFrameworkData,
)
from .mitre_cache import MITRECache
from .mitre_client import MITREAttackAPI, get_mitre_client

# =============================================================================
# WRAPPER FUNCTIONS (Delegating to Singleton)
# =============================================================================

async def get_control(control_id: str) -> Optional[MITRETechnique]:
    """Get a control by ID."""
    return await get_mitre_client().get_technique(control_id)

async def get_controls_by_framework(framework: str) -> List[MITRETechnique]:
    """Get controls by framework."""
    return await get_mitre_client().get_controls_by_framework(framework)

async def get_all_controls() -> List[MITRETechnique]:
    """Get all controls."""
    return await get_mitre_client().get_all_techniques()

async def get_frameworks_by_category(category: str) -> List[ComplianceFrameworkData]:
    """Get frameworks by category."""
    return await get_mitre_client().get_frameworks_by_category(category)

async def get_framework(framework_id: str) -> Optional[ComplianceFrameworkData]:
    """Get framework by ID."""
    return await get_mitre_client().get_framework(framework_id)

async def get_all_frameworks() -> List[ComplianceFrameworkData]:
    """Get all frameworks."""
    return await get_mitre_client().get_all_frameworks()

__all__ = [
    "MITRETechnique", "MITRETactic", "MITREActor", 
    "ComplianceControl", "ComplianceFrameworkData",
    "MITRECache", "MITREAttackAPI", "get_mitre_client",
    "get_control", "get_controls_by_framework", "get_all_controls",
    "get_frameworks_by_category", "get_framework", "get_all_frameworks"
]
