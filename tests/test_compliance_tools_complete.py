"""
Test Compliance Tools
Testes para funções MCP de compliance.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from tools.compliance.tools import (
    compliance_assess,
    compliance_report,
    compliance_check,
)


class TestComplianceTools:
    """Test compliance MCP tool functions."""

    @pytest.fixture(autouse=True)
    def mock_event_bus(self, monkeypatch):
        from core.event_bus import EventBus
        monkeypatch.setattr(EventBus, "emit", AsyncMock(return_value=MagicMock()))

    @pytest.mark.asyncio
    async def test_compliance_assess_gdpr(self):
        """Test successful compliance assessment for GDPR."""
        # Mock the guardian
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 85.0
        mock_assessment.model_dump.return_value = {"status": "compliant", "score": 85.0}
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = AsyncMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_assess(ctx, "test-system", "gdpr")

            assert isinstance(result, dict)
            assert result["status"] == "compliant"
            assert result["score"] == 85.0

    @pytest.mark.asyncio
    async def test_compliance_report_multiple_frameworks_with_context(self):
        """Test compliance report with multiple frameworks and context."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 75.0
        mock_assessment.overall_status = MagicMock()
        mock_assessment.overall_status.value = "partially_compliant"
        mock_assessment.model_dump.return_value = {"status": "partial", "score": 75.0}
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = AsyncMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_report(ctx, "test-system", ["gdpr", "hipaa"])
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_compliance_check_requirement_found(self):
        """Test checking specific compliance requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.checks = []
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)
        
        ctx = MagicMock()
        ctx.info = AsyncMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "GDPR-ART25", "test-system")
            assert "status" in result
