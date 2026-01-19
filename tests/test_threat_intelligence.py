"""
Tests for Intelligence Tools: OSINT Hunter, Threat Prophet, Compliance Guardian.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.osint import get_osint_hunter, OSINTHunter, InvestigationDepth
from tools.threat import (
    get_threat_prophet,
    ThreatProphet,
)
from tools.compliance import (
    get_compliance_guardian,
    ComplianceFramework,
    ComplianceStatus,
)
from tools.compliance.tools import compliance_report, compliance_check


class TestOSINTHunter:
    """Test OSINT Hunter functionality."""

    @pytest.fixture
    def hunter(self):
        """Create hunter instance for testing."""
        hunter = OSINTHunter()
        # Mock dependencies
        hunter.memory = MagicMock()
        hunter.event_bus = MagicMock()
        hunter.event_bus.emit = AsyncMock()
        return hunter

    @pytest.mark.asyncio
    async def test_investigate_email(self, hunter):
        """Test email investigation."""
        result = await hunter.investigate("test@example.com", InvestigationDepth.BASIC)

        assert result.target == "test@example.com"
        assert result.depth == InvestigationDepth.BASIC
        assert len(result.sources_checked) > 0
        assert "domain_from_email" in result.sources_checked

    @pytest.mark.asyncio
    async def test_investigate_domain(self, hunter):
        """Test domain investigation."""
        result = await hunter.investigate("example.com", InvestigationDepth.BASIC)

        assert result.target == "example.com"
        assert "google_dorks" in result.sources_checked

    @pytest.mark.asyncio
    async def test_investigate_ip(self, hunter):
        """Test IP investigation."""
        result = await hunter.investigate("192.168.1.1", InvestigationDepth.BASIC)

        assert result.target == "192.168.1.1"
        assert "ip_analysis" in result.sources_checked

    def test_get_google_dorks(self, hunter):
        """Test Google dorks generation."""
        dorks = hunter.get_google_dorks("example.com")

        assert len(dorks) > 0
        assert all("example.com" in dork["dork"] for dork in dorks)
        assert all("category" in dork for dork in dorks)

    def test_calculate_risk(self, hunter):
        """Test risk score calculation."""
        from tools.osint import OSINTFinding, OSINTResult, BreachInfo

        result = OSINTResult(target="test", depth=InvestigationDepth.BASIC)
        result.breaches = [
            BreachInfo(
                name="breach1", date="2024-01-01", data_classes=[], is_verified=True
            )
        ]
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="test",
                severity="high",
                data={},
                confidence=1.0,
            )
        ]

        risk_score = hunter._calculate_risk(result)
        assert risk_score > 0  # Should have some risk due to breach and finding

    @pytest.mark.asyncio
    async def test_breach_check_without_api_key(self, hunter):
        """Test breach check when API key is not configured."""
        hunter.hibp_api_key = None
        breaches = await hunter.check_breach("test@example.com")

        assert len(breaches) == 0


class TestThreatProphet:
    """Test Threat Prophet functionality."""

    @pytest.fixture
    async def prophet(self):
        """Create prophet instance for testing."""
        # Mock the MITRE client before creating ThreatProphet
        mock_mitre_client = MagicMock()
        mock_mitre_client.search_techniques = AsyncMock(
            return_value=[
                type(
                    "MockTechnique",
                    (),
                    {
                        "technique_id": "T1566",
                        "name": "Phishing",
                        "description": "Test technique",
                    },
                )()
            ]
        )

        with patch("tools.threat.get_mitre_client", return_value=mock_mitre_client):
            prophet = ThreatProphet()
            # Mock other dependencies
            prophet.memory = MagicMock()
            prophet.event_bus = MagicMock()
            prophet.event_bus.emit = AsyncMock()
            yield prophet

    @pytest.mark.asyncio
    async def test_analyze_threats(self, prophet):
        """Test threat analysis."""
        analysis = await prophet.analyze_threats(
            "example.com", include_predictions=True
        )

        assert analysis.target == "example.com"
        assert isinstance(analysis.indicators, list)
        assert isinstance(analysis.techniques, list)
        assert isinstance(analysis.predictions, list)
        assert 0 <= analysis.overall_risk_score <= 100

    def test_map_to_mitre_techniques(self, prophet):
        """Test MITRE ATT&CK technique mapping."""
        techniques = prophet._map_to_mitre_techniques("test@example.com")

        assert isinstance(techniques, list)
        if techniques:  # If any techniques found
            assert all(hasattr(t, "technique_id") for t in techniques)

    @pytest.mark.asyncio
    async def test_generate_predictions(self, prophet):
        """Test threat predictions generation."""
        predictions = await prophet._generate_predictions("example.com")

        assert isinstance(predictions, list)
        if predictions:  # If predictions generated
            assert all(hasattr(p, "target") for p in predictions)
            assert all(hasattr(p, "confidence_score") for p in predictions)

    def test_calculate_overall_risk(self, prophet):
        """Test overall risk calculation."""
        from tools.threat import ThreatAnalysis

        analysis = ThreatAnalysis(target="test")
        risk_score = prophet._calculate_overall_risk(analysis)
        assert 0 <= risk_score <= 100

    @pytest.mark.asyncio
    async def test_get_threat_intelligence(self, prophet):
        """Test threat intelligence search."""
        results = await prophet.get_threat_intelligence("phishing")

        assert "query" in results
        assert "matching_techniques" in results
        assert "total_matches" in results


class TestComplianceGuardian:
    """Test Compliance Guardian functionality."""

    @pytest.fixture
    async def guardian(self):
        """Create guardian instance for testing."""
        # Mock the compliance API before creating ComplianceGuardian
        mock_api = MagicMock()
        mock_control = type(
            "MockControl",
            (),
            {
                "control_id": "GDPR-ART6",
                "title": "Lawfulness of processing",
                "description": "Personal data must be processed lawfully",
                "framework": "gdpr",
                "category": "data_protection",
                "severity": "critical",
            },
        )()

        mock_api.get_controls_by_framework = AsyncMock(return_value=[mock_control])
