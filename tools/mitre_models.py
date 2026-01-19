"""
MITRE ATT&CK Models
Modelos Pydantic para representar dados MITRE ATT&CK.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MITRETechnique(BaseModel):
    """Representação de uma técnica MITRE ATT&CK."""

    technique_id: str
    name: str
    description: str
    tactics: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    detection: str = ""
    mitigations: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    subtechnique_of: Optional[str] = None
    is_subtechnique: bool = False
    url: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    version: Optional[str] = None


class MITRETactic(BaseModel):
    """Representação de uma tática MITRE ATT&CK."""

    tactic_id: str
    name: str
    description: str
    techniques: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class MITREActor(BaseModel):
    """Representação de um ator MITRE ATT&CK."""

    actor_id: str
    name: str
    description: str
    aliases: List[str] = Field(default_factory=list)
    techniques_used: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    url: Optional[str] = None


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
    version: str = "1.0"
    description: str = ""
    controls: List[ComplianceControl] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
