"""
Compliance Guardian - Regulatory Compliance Tool
Verificação automática de conformidade com regulamentações de segurança.

Este arquivo mantém compatibilidade com imports existentes.
Todas as funcionalidades foram movidas para módulos separados em tools/compliance/
"""

# Re-export everything from the refactored modules for backward compatibility
from .compliance.models import (
    ComplianceFramework,
    ComplianceStatus,
    ComplianceRequirement,
    ComplianceCheck,
    ComplianceAssessment,
)
from .compliance.client import get_compliance_api
from .compliance.guardian import get_compliance_guardian
from .compliance.tools import (
    compliance_assess,
    compliance_report,
    compliance_check,
)

# Legacy compatibility - ensure old imports still work
__all__ = [
    "ComplianceFramework",
    "ComplianceStatus",
    "ComplianceRequirement",
    "ComplianceCheck",
    "ComplianceAssessment",
    "get_compliance_api",
    "get_compliance_guardian",
    "compliance_assess",
    "compliance_report",
    "compliance_check",
]
