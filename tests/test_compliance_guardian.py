
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
