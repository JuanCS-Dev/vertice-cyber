"""
Compliance Frameworks - Framework Data
Dados oficiais dos frameworks de conformidade regulatória.
"""

from typing import List
from .models import ComplianceControl, ComplianceFrameworkData


# NIST Cybersecurity Framework 2.0
NIST_CSF_DATA = ComplianceFrameworkData(
    framework_id="nist_csf",
    name="NIST Cybersecurity Framework",
    version="2.0",
    description="Framework for improving cybersecurity risk management",
    categories=["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"],
    controls=[
        ComplianceControl(
            control_id="ID.AM-1",
            title="Physical devices and systems within the organization are inventoried",
            description="Maintain an up-to-date inventory of all physical devices and systems",
            framework="nist_csf",
            category="Identify",
            subcategory="Asset Management",
            severity="medium",
            implementation_guide="Create and maintain detailed inventory of all hardware assets",
            references=["NIST CSF 2.0", "SP 800-53"],
        ),
        ComplianceControl(
            control_id="PR.AC-1",
            title="Identities and credentials are issued, managed, verified, revoked, and audited",
            description="Manage digital identities and credentials appropriately",
            framework="nist_csf",
            category="Protect",
            subcategory="Identity Management and Access Control",
            severity="high",
            implementation_guide="Implement robust identity and access management processes",
            references=["NIST CSF 2.0", "SP 800-63"],
        ),
        ComplianceControl(
            control_id="DE.AE-1",
            title="A baseline of network operations and expected data flows is established",
            description="Establish baseline network operations for anomaly detection",
            framework="nist_csf",
            category="Detect",
            subcategory="Anomalies and Events",
            severity="medium",
            implementation_guide="Monitor network traffic patterns and establish baselines",
            references=["NIST CSF 2.0"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://csrc.nist.gov/pubs/sp/800/207/ipd",
)


# ISO 27001:2022
ISO_27001_DATA = ComplianceFrameworkData(
    framework_id="iso_27001",
    name="ISO 27001 Information Security Management",
    version="2022",
    description="International standard for information security management systems",
    categories=[
        "Information Security Policies",
        "Organization of Information Security",
        "Human Resources Security",
    ],
    controls=[
        ComplianceControl(
            control_id="A.5.1",
            title="Information security policy for information security management",
            description="Establish information security policy with management commitment",
            framework="iso_27001",
            category="Information Security Policies",
            severity="high",
            implementation_guide="Develop and maintain information security policy",
            references=["ISO 27001:2022"],
        ),
        ComplianceControl(
            control_id="A.9.1",
            title="Access control policy",
            description="Establish access control policy based on business requirements",
            framework="iso_27001",
            category="Access Control",
            severity="high",
            implementation_guide="Define access control policies and procedures",
            references=["ISO 27001:2022"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://www.iso.org/standard/54534.html",
)


# GDPR
GDPR_DATA = ComplianceFrameworkData(
    framework_id="gdpr",
    name="General Data Protection Regulation",
    version="2018",
    description="EU regulation for data protection and privacy",
    categories=[
        "Data Protection Principles",
        "Data Subject Rights",
        "Controller and Processor Obligations",
    ],
    controls=[
        ComplianceControl(
            control_id="GDPR-ART6",
            title="Lawfulness of processing",
            description="Personal data must be processed lawfully and transparently",
            framework="gdpr",
            category="Data Protection Principles",
            severity="critical",
            implementation_guide="Ensure lawful basis for all data processing activities",
            references=["GDPR Article 6"],
        ),
        ComplianceControl(
            control_id="GDPR-ART15",
            title="Right of access by the data subject",
            description="Individuals have right to access their personal data",
            framework="gdpr",
            category="Data Subject Rights",
            severity="high",
            implementation_guide="Implement subject access request processes",
            references=["GDPR Article 15"],
        ),
        ComplianceControl(
            control_id="GDPR-ART35",
            title="Data protection impact assessment",
            description="High-risk processing requires DPIA",
            framework="gdpr",
            category="Risk Assessment",
            severity="high",
            implementation_guide="Conduct DPIA for high-risk data processing",
            references=["GDPR Article 35"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://gdpr-info.eu/",
)


# HIPAA
HIPAA_DATA = ComplianceFrameworkData(
    framework_id="hipaa",
    name="HIPAA Security Rule",
    version="2003",
    description="US healthcare data security and privacy regulation",
    categories=[
        "Administrative Safeguards",
        "Physical Safeguards",
        "Technical Safeguards",
    ],
    controls=[
        ComplianceControl(
            control_id="HIPAA-164.308",
            title="Administrative safeguards",
            description="Implement administrative actions to manage risk",
            framework="hipaa",
            category="Administrative Safeguards",
            severity="high",
            implementation_guide="Implement administrative security measures",
            references=["45 CFR 164.308"],
        ),
        ComplianceControl(
            control_id="HIPAA-164.312",
            title="Technical safeguards",
            description="Implement technical policies and procedures",
            framework="hipaa",
            category="Technical Safeguards",
            severity="high",
            implementation_guide="Implement technical security controls",
            references=["45 CFR 164.312"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://www.hhs.gov/hipaa/for-professionals/security/guidance/index.html",
)


# PCI DSS
PCI_DSS_DATA = ComplianceFrameworkData(
    framework_id="pci_dss",
    name="Payment Card Industry Data Security Standard",
    version="4.0",
    description="Global standard for payment card data security",
    categories=[
        "Build and Maintain Networks",
        "Protect Account Data",
        "Maintain Vulnerability Management",
    ],
    controls=[
        ComplianceControl(
            control_id="PCI-1.1",
            title="Install and maintain network security controls",
            description="Install and maintain firewall and router configuration",
            framework="pci_dss",
            category="Build and Maintain Networks",
            severity="high",
            implementation_guide="Configure firewalls and routers properly",
            references=["PCI DSS 4.0 Requirement 1"],
        ),
        ComplianceControl(
            control_id="PCI-3.1",
            title="Protect stored account data",
            description="Keep cardholder data storage to a minimum",
            framework="pci_dss",
            category="Protect Account Data",
            severity="critical",
            implementation_guide="Minimize storage of sensitive cardholder data",
            references=["PCI DSS 4.0 Requirement 3"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://www.pcisecuritystandards.org/",
)


# SOX
SOX_DATA = ComplianceFrameworkData(
    framework_id="sox",
    name="Sarbanes-Oxley Act",
    version="2002",
    description="US corporate financial reporting regulation",
    categories=["Internal Controls", "Financial Reporting", "Corporate Governance"],
    controls=[
        ComplianceControl(
            control_id="SOX-404",
            title="Internal control over financial reporting",
            description="Management assessment of internal controls",
            framework="sox",
            category="Internal Controls",
            severity="high",
            implementation_guide="Implement effective internal controls over financial reporting",
            references=["Sarbanes-Oxley Act Section 404"],
        ),
        ComplianceControl(
            control_id="SOX-302",
            title="Corporate responsibility for financial reports",
            description="CEO and CFO certification of financial reports",
            framework="sox",
            category="Financial Reporting",
            severity="critical",
            implementation_guide="Ensure executive certification of financial statements",
            references=["Sarbanes-Oxley Act Section 302"],
        ),
    ],
    last_updated="2024-01-01",
    source_url="https://www.congress.gov/bill/107th-congress/house-bill/3763",
)


# Registry of all frameworks
FRAMEWORK_REGISTRY = {
    "nist_csf": NIST_CSF_DATA,
    "iso_27001": ISO_27001_DATA,
    "gdpr": GDPR_DATA,
    "hipaa": HIPAA_DATA,
    "pci_dss": PCI_DSS_DATA,
    "sox": SOX_DATA,
}


def get_framework_data(framework_id: str) -> ComplianceFrameworkData:
    """Get framework data by ID."""
    return FRAMEWORK_REGISTRY.get(framework_id.lower())


def get_all_framework_data() -> List[ComplianceFrameworkData]:
    """Get all framework data."""
    return list(FRAMEWORK_REGISTRY.values())
