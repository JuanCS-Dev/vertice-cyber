"""
Compliance Frameworks - Data Models
Modelos de dados para frameworks de conformidade regulatória.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ComplianceFramework(str, Enum):
    """Frameworks de conformidade suportados."""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO_27001 = "iso_27001"
    NIST = "nist"


class ComplianceStatus(str, Enum):
    """Status de conformidade."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"


class ComplianceControl(BaseModel):
    """Controle de conformidade."""

    control_id: str
    title: str
    description: str
    framework: str
    category: str
    subcategory: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    implementation_guide: Optional[str] = None
    related_controls: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)


class ComplianceFrameworkData(BaseModel):
    """Dados de um framework de conformidade."""

    framework_id: str
    name: str
    version: str
    description: str
    controls: List[ComplianceControl]
    categories: List[str]
    last_updated: Optional[str] = None
    source_url: Optional[str] = None


class ComplianceRequirement(BaseModel):
    """Requisito de conformidade."""

    requirement_id: str
    title: str
    description: str
    framework: ComplianceFramework
    category: str
    severity: str


class ComplianceCheck(BaseModel):
    """Resultado de uma verificação de conformidade."""

    requirement: ComplianceRequirement
    status: ComplianceStatus
    evidence: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    score: float = 0.0


class ComplianceAssessment(BaseModel):
    """Avaliação completa de conformidade."""

    target: str
    framework: ComplianceFramework
    overall_status: ComplianceStatus
    overall_score: float = 0.0
    checks: List[ComplianceCheck] = Field(default_factory=list)
    critical_violations: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
