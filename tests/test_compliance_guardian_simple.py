"""
Test Compliance Guardian
Testes para Compliance Guardian e funcionalidades relacionadas.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from tools.compliance import get_compliance_guardian, ComplianceFramework


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
            guardian = await get_compliance_guardian()
            # Mock other dependencies
            guardian.memory = MagicMock()
            guardian.event_bus = MagicMock()
            guardian.event_bus.emit = AsyncMock()
            yield guardian

    @pytest.mark.asyncio
    async def test_singleton(self):
        """Test Compliance Guardian singleton."""
        mock_api = MagicMock()
        mock_api.get_controls_by_framework = AsyncMock(return_value=[])

        with patch(
            "tools.compliance.guardian.get_compliance_api", return_value=mock_api
        ):
            g1 = await get_compliance_guardian()
            g2 = await get_compliance_guardian()
            assert g1 is g2

    @pytest.mark.asyncio
    async def test_assess_compliance(self, guardian):
        """Test compliance assessment."""
        assessment = await guardian.assess_compliance(
            "test-system", ComplianceFramework.GDPR
        )

        assert assessment.target == "test-system"
        assert assessment.framework == ComplianceFramework.GDPR
        assert isinstance(assessment.overall_score, (int, float))
        assert isinstance(assessment.checks, list)
        assert len(assessment.checks) > 0

    @pytest.mark.asyncio
    async def test_calculate_compliance_score(self, guardian):
        """Test compliance score calculation."""
        from tools.compliance import (
            ComplianceCheck,
            ComplianceRequirement,
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
