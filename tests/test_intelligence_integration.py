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
