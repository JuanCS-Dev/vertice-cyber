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

        with patch(
            "tools.compliance.guardian.get_compliance_api", return_value=mock_api
        ):
            from tools.compliance.guardian import ComplianceGuardian

            guardian = ComplianceGuardian()
            # Mock other dependencies
            guardian.memory = MagicMock()
            guardian.event_bus = MagicMock()
            guardian.event_bus.emit = AsyncMock()
            yield guardian

    @pytest.mark.asyncio
    async def test_assess_gdpr_compliance(self, guardian):
        """Test GDPR compliance assessment."""
        assessment = await guardian.assess_compliance(
            "example.com", ComplianceFramework.GDPR
        )

        assert assessment.target == "example.com"
        assert assessment.framework == ComplianceFramework.GDPR
        assert len(assessment.checks) > 0
        assert 0 <= assessment.overall_score <= 100

    @pytest.mark.asyncio
    async def test_assess_hipaa_compliance(self, guardian):
        """Test HIPAA compliance assessment."""
        assessment = await guardian.assess_compliance(
            "hospital.com", ComplianceFramework.HIPAA
        )

        assert assessment.target == "hospital.com"
        assert assessment.framework == ComplianceFramework.HIPAA
        assert len(assessment.checks) > 0

    @pytest.mark.asyncio
    async def test_assess_pci_compliance(self, guardian):
        """Test PCI DSS compliance assessment."""
        assessment = await guardian.assess_compliance(
            "store.com", ComplianceFramework.PCI_DSS
        )

        assert assessment.target == "store.com"
        assert assessment.framework == ComplianceFramework.PCI_DSS
        assert len(assessment.checks) > 0

    def test_calculate_compliance_score(self, guardian):
        """Test compliance score calculation."""
        from tools.compliance import ComplianceCheck, ComplianceRequirement

        checks = [
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="TEST-1",
                    title="Test",
                    description="Test",
                    framework=ComplianceFramework.GDPR,
                    category="test",
                    severity="high",
                ),
                status=ComplianceStatus.COMPLIANT,
            )
        ]

        score = guardian._calculate_compliance_score(checks)
        assert 0 <= score <= 100

    def test_determine_overall_status(self, guardian):
        """Test overall status determination."""
        from tools.compliance import ComplianceCheck, ComplianceRequirement

        # Test compliant status
        compliant_checks = [
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="TEST-1",
                    title="Test",
                    description="Test",
                    framework=ComplianceFramework.GDPR,
                    category="test",
                    severity="high",
                ),
                status=ComplianceStatus.COMPLIANT,
            )
        ]

        status = guardian._determine_overall_status(compliant_checks)
        assert status == ComplianceStatus.COMPLIANT

        # Test non-compliant status
        non_compliant_checks = [
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="TEST-1",
                    title="Test",
                    description="Test",
                    framework=ComplianceFramework.GDPR,
                    category="test",
                    severity="critical",
                ),
                status=ComplianceStatus.NON_COMPLIANT,
            )
        ]

        status = guardian._determine_overall_status(non_compliant_checks)
        assert status == ComplianceStatus.NON_COMPLIANT

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, guardian):
        """Test compliance report generation."""
        frameworks = [ComplianceFramework.GDPR, ComplianceFramework.HIPAA]
        report = await guardian.generate_compliance_report("test.com", frameworks)

        assert report["target"] == "test.com"
        assert len(report["frameworks_assessed"]) == 2
        assert len(report["assessments"]) == 2
        assert "summary" in report


class TestIntelligenceToolIntegration:
    """Test integration of intelligence tools."""

    def test_get_osint_hunter_singleton(self):
        """Test OSINT Hunter singleton."""
        hunter1 = get_osint_hunter()
        hunter2 = get_osint_hunter()
        assert hunter1 is hunter2

    def test_get_threat_prophet_singleton(self):
        """Test Threat Prophet singleton."""
        mock_mitre_client = MagicMock()
        mock_mitre_client.search_techniques = AsyncMock(return_value=[])

        with patch("tools.threat.get_mitre_client", return_value=mock_mitre_client):
            prophet1 = get_threat_prophet()
            prophet2 = get_threat_prophet()
            assert prophet1 is prophet2

    def test_get_compliance_guardian_singleton(self):
        """Test Compliance Guardian singleton."""
        mock_api = MagicMock()
        mock_api.get_controls_by_framework = AsyncMock(return_value=[])

        with patch(
            "tools.compliance.guardian.get_compliance_api", return_value=mock_api
        ):
            guardian1 = get_compliance_guardian()
            guardian2 = get_compliance_guardian()
            assert guardian1 is guardian2

    @pytest.mark.asyncio
    async def test_osint_investigate_basic(self):
        """Test basic OSINT investigation."""
        from tools.osint import osint_investigate
        from tools.fastmcp_compat import MockContext

        ctx = MockContext()
        result = await osint_investigate(ctx, "example.com", "basic")

        assert result["target"] == "example.com"
        assert result["depth"] == "basic"
        assert "findings" in result
        assert "breaches" in result

    @pytest.mark.asyncio
    async def test_osint_breach_check(self):
        """Test breach checking functionality."""
        from tools.osint import osint_breach_check
        from tools.fastmcp_compat import MockContext

        ctx = MockContext()
        result = await osint_breach_check(ctx, "test@example.com")

        assert isinstance(result, dict)
        assert "email" in result or "breaches" in result

    @pytest.mark.asyncio
    async def test_osint_google_dork(self):
        """Test Google dork generation."""
        from tools.osint import osint_google_dork
        from tools.fastmcp_compat import MockContext

        ctx = MockContext()
        result = await osint_google_dork(ctx, "example.com")

        assert isinstance(result, dict)
        assert "domain" in result or "dorks" in result

    @pytest.mark.asyncio
    async def test_threat_intelligence_search(self, prophet):
        """Test threat intelligence search."""
        result = await prophet.get_threat_intelligence("phishing")

        assert isinstance(result, dict)
        assert "query" in result
        assert "matching_techniques" in result
        assert "total_matches" in result

    @pytest.mark.asyncio
    async def test_compliance_report_multiple_frameworks(self, guardian):
        """Test compliance report with multiple frameworks."""
        from tools.compliance.tools import compliance_report

        ctx = MagicMock()
        frameworks = ["gdpr", "hipaa"]
        result = await compliance_report(ctx, "test-system", frameworks)

        assert isinstance(result, dict)
        assert "target" in result
        assert "frameworks_assessed" in result
        assert "overall_score" in result
        assert "assessments" in result

    @pytest.mark.asyncio
    async def test_compliance_check_specific_requirement(self, guardian):
        """Test compliance check for specific requirement."""
        from tools.compliance.tools import compliance_check

        ctx = MagicMock()
        result = await compliance_check(ctx, "GDPR-ART6", "test-system")

        assert isinstance(result, dict)
        assert "requirement_id" in result
        assert "status" in result

    def test_osint_hunter_singleton(self):
        """Test OSINT Hunter singleton pattern."""
        from tools.osint import get_osint_hunter

        hunter1 = get_osint_hunter()
        hunter2 = get_osint_hunter()
        assert hunter1 is hunter2

    def test_osint_hunter_initialization(self):
        """Test OSINT Hunter initialization."""
        from tools.osint import OSINTHunter

        hunter = OSINTHunter()
        assert hunter.settings is not None
        assert hunter.memory is not None
        assert hunter.event_bus is not None

    def test_osint_result_creation(self):
        """Test OSINT result creation."""
        from tools.osint import OSINTResult, InvestigationDepth

        result = OSINTResult(target="test.com", depth=InvestigationDepth.BASIC)
        assert result.target == "test.com"
        assert result.depth == InvestigationDepth.BASIC
        assert result.risk_score == 0.0
        assert result.findings == []
        assert result.breaches == []

    def test_osint_finding_creation(self):
        """Test OSINT finding creation."""
        from tools.osint import OSINTFinding

        finding = OSINTFinding(
            source="test",
            finding_type="breach",
            severity="medium",
            data={"test": "data"},
            confidence=0.8,
        )
        assert finding.source == "test"
        assert finding.finding_type == "breach"
        assert finding.severity == "medium"
        assert finding.confidence == 0.8

    @pytest.mark.asyncio
    async def test_threat_calculate_overall_risk(self, prophet):
        """Test threat risk calculation."""
        from tools.threat import (
            ThreatAnalysis,
            ThreatIndicator,
            ThreatPrediction,
            ThreatLevel,
        )

        # Create test analysis
        analysis = ThreatAnalysis(
            target="test.com",
            indicators=[
                ThreatIndicator(
                    indicator_type="domain",
                    value="test.com",
                    confidence=0.8,
                    first_seen="2024-01-01",
                    last_seen="2024-01-02",
                    tags=["suspicious"],
                )
            ],
            techniques=[],  # Mock techniques
            predictions=[
                ThreatPrediction(
                    target="test.com",
                    predicted_threats=["Phishing"],
                    confidence_score=0.8,
                    risk_level=ThreatLevel.HIGH,
                    recommended_actions=["Monitor domain"],
                    time_horizon="short_term",
                )
            ],
        )

        risk_score = prophet._calculate_overall_risk(analysis)
        assert isinstance(risk_score, float)
        assert risk_score >= 0
        assert risk_score <= 100

    @pytest.mark.asyncio
    async def test_threat_identify_attack_vectors(self, prophet):
        """Test attack vector identification."""
        from tools.threat import ThreatAnalysis, ThreatIndicator

        analysis = ThreatAnalysis(
            target="test@example.com",
            indicators=[
                ThreatIndicator(
                    indicator_type="email",
                    value="test@example.com",
                    confidence=0.8,
                    first_seen="2024-01-01",
                    last_seen="2024-01-02",
                    tags=["phishing", "credential_stuffing"],
                )
            ],
            techniques=[],
            predictions=[],
        )

        vectors = prophet._identify_attack_vectors(analysis)
        assert isinstance(vectors, list)
        assert len(vectors) > 0  # Should identify social engineering

    @pytest.mark.asyncio
    async def test_compliance_calculate_score(self, guardian):
        """Test compliance score calculation."""
        from tools.compliance import (
            ComplianceCheck,
            ComplianceRequirement,
            ComplianceFramework,
            ComplianceStatus,
        )

        checks = [
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="TEST-1",
                    title="Test Control",
                    description="Test description",
                    framework=ComplianceFramework.GDPR,
                    category="test",
                    severity="high",
                ),
                status=ComplianceStatus.COMPLIANT,
                score=100.0,
            ),
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="TEST-2",
                    title="Test Control 2",
                    description="Test description 2",
                    framework=ComplianceFramework.GDPR,
                    category="test",
                    severity="medium",
                ),
                status=ComplianceStatus.PARTIALLY_COMPLIANT,
                score=60.0,
            ),
        ]

        score = guardian._calculate_compliance_score(checks)
        assert isinstance(score, float)
        assert 0 <= score <= 100
        # Should be weighted average: (100*3 + 60*2) / (3+2) = 82.0
        assert abs(score - 82.0) < 1.0

    @pytest.mark.asyncio
    async def test_compliance_identify_critical_violations(self, guardian):
        """Test critical violations identification."""
        from tools.compliance import (
            ComplianceCheck,
            ComplianceRequirement,
            ComplianceFramework,
            ComplianceStatus,
        )

        checks = [
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="CRITICAL-1",
                    title="Critical Control",
                    description="Critical test",
                    framework=ComplianceFramework.GDPR,
                    category="security",
                    severity="critical",
                ),
                status=ComplianceStatus.NON_COMPLIANT,
                violations=["Critical violation found"],
            ),
            ComplianceCheck(
                requirement=ComplianceRequirement(
                    requirement_id="NORMAL-1",
                    title="Normal Control",
                    description="Normal test",
                    framework=ComplianceFramework.GDPR,
                    category="general",
                    severity="medium",
                ),
                status=ComplianceStatus.COMPLIANT,
                violations=[],
            ),
        ]

        violations = guardian._identify_critical_violations(checks)
        assert isinstance(violations, list)
        assert len(violations) == 1  # Should identify critical violation
        assert "CRITICAL-1" in violations[0]

    @pytest.mark.asyncio
    async def test_osint_calculate_risk(self):
        """Test OSINT risk calculation."""
        from tools.osint import (
            OSINTHunter,
            OSINTResult,
            InvestigationDepth,
            OSINTFinding,
            BreachInfo,
        )

        hunter = OSINTHunter()
        result = OSINTResult(target="test.com", depth=InvestigationDepth.BASIC)

        # Add findings and breaches
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="breach",
                severity="high",
                data={"breach": "found"},
                confidence=0.9,
            )
        ]
        result.breaches = [
            BreachInfo(
                name="Test Breach",
                date="2024-01-01",
                data_classes=["emails"],
                is_verified=True,
            )
        ]

        risk_score = hunter._calculate_risk(result)
        assert isinstance(risk_score, float)
        assert risk_score >= 0
        assert risk_score <= 100

    def test_breach_info_creation(self):
        """Test breach info creation."""
        from tools.osint import BreachInfo

        breach = BreachInfo(
            name="Test Breach",
            date="2024-01-01",
            data_classes=["emails"],
            is_verified=True,
        )
        assert breach.name == "Test Breach"
        assert breach.is_verified is True
        assert breach.data_classes == ["emails"]
