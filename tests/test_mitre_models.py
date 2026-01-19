"""
MITRE Models Tests
Testes para os modelos Pydantic MITRE.
"""

from tools.mitre_models import (
    MITRETechnique,
    MITRETactic,
    MITREActor,
    ComplianceControl,
    ComplianceFrameworkData,
)


class TestMITREModels:
    """Test MITRE data models."""

    def test_mitre_technique_creation(self):
        """Test MITRETechnique model creation."""
        technique = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Adversaries may use methods of capturing user input to obtain credentials or collect information.",
            tactics=["Credential Access", "Collection"],
            platforms=["Windows", "Linux", "macOS"],
            is_subtechnique=False,
        )

        assert technique.technique_id == "T1056"
        assert technique.name == "Input Capture"
        assert len(technique.tactics) == 2
        assert technique.is_subtechnique is False

    def test_mitre_tactic_creation(self):
        """Test MITRETactic model creation."""
        tactic = MITRETactic(
            tactic_id="TA0001",
            name="Initial Access",
            description="The adversary is trying to get into your network.",
            techniques=["T1566", "T1078"],
        )

        assert tactic.tactic_id == "TA0001"
        assert tactic.name == "Initial Access"
        assert len(tactic.techniques) == 2

    def test_mitre_actor_creation(self):
        """Test MITREActor model creation."""
        actor = MITREActor(
            actor_id="G001",
            name="APT1",
            description="Chinese cyber espionage group.",
            aliases=["Comment Crew", "Shanghai Group"],
            techniques_used=["T1056", "T1078"],
            motivations=["Espionage"],
        )

        assert actor.actor_id == "G001"
        assert actor.name == "APT1"
        assert len(actor.aliases) == 2
        assert len(actor.techniques_used) == 2

    def test_compliance_control_creation(self):
        """Test ComplianceControl model creation."""
        control = ComplianceControl(
            control_id="AC-1",
            title="Access Control Policy",
            description="Develop and maintain an access control policy.",
            framework="NIST",
            category="Access Control",
            severity="high",
        )

        assert control.control_id == "AC-1"
        assert control.framework == "NIST"
        assert control.severity == "high"

    def test_compliance_framework_data_creation(self):
        """Test ComplianceFrameworkData model creation."""
        framework = ComplianceFrameworkData(
            framework_id="nist",
            name="NIST Cybersecurity Framework",
            version="1.1",
            description="Framework for improving cybersecurity",
            categories=["Identify", "Protect", "Detect", "Respond", "Recover"],
        )

        assert framework.framework_id == "nist"
        assert framework.name == "NIST Cybersecurity Framework"
        assert len(framework.categories) == 5
        assert len(framework.controls) == 0  # Empty by default
