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
