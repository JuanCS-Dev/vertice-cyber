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
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_assess(ctx, "test-system", "gdpr")

            assert isinstance(result, dict)
            assert result["status"] == "compliant"
            assert result["score"] == 85.0

    @pytest.mark.asyncio
    async def test_compliance_assess_gdpr_with_context_logging(self):
        """Test GDPR assessment with context logging."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 85.0
        mock_assessment.model_dump.return_value = {"status": "compliant", "score": 85.0}
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_assess(ctx, "test-system", "gdpr")

            # Verify context logging was called
            ctx.info.assert_called()
            assert result["score"] == 85.0

    @pytest.mark.asyncio
    async def test_compliance_report_multiple_frameworks_with_context(self):
        """Test compliance report with multiple frameworks and context."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 75.0
        mock_assessment.model_dump.return_value = {"status": "partial", "score": 75.0}
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_report(ctx, "test-system", ["gdpr", "hipaa"])

            ctx.info.assert_called()
            # Just check that result is returned
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_compliance_check_requirement_found(self):
        """Test checking specific compliance requirement."""
        mock_guardian = MagicMock()
        mock_requirement = MagicMock()
        mock_requirement.model_dump.return_value = {
            "id": "gdpr_art_25",
            "status": "compliant",
        }
        mock_guardian.check_requirement = AsyncMock(return_value=mock_requirement)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "gdpr_art_25", "test-system")

            ctx.info.assert_called()
            assert result["id"] == "gdpr_art_25"

    @pytest.mark.asyncio
    async def test_compliance_guardian_initialization_coverage(self):
        """Test guardian initialization to cover basic setup."""
        from tools.compliance.guardian import ComplianceGuardian

        with (
            patch("tools.compliance.guardian.get_settings") as mock_settings,
            patch("tools.compliance.guardian.get_agent_memory") ,
            patch("tools.compliance.guardian.get_event_bus") ,
        ):
            mock_settings.return_value.data_dir = "/tmp/test"
            guardian = ComplianceGuardian()

            # Basic attribute checks to cover initialization
            assert guardian.settings is not None
            assert guardian.memory is not None
            assert guardian.event_bus is not None
            assert guardian.api is not None

    @pytest.mark.asyncio
    async def test_compliance_guardian_assess_basic(self):
        """Test basic assessment functionality."""
        from tools.compliance.guardian import ComplianceGuardian

        with (
            patch("tools.compliance.guardian.get_settings") as mock_settings,
            patch("tools.compliance.guardian.get_agent_memory") ,
            patch("tools.compliance.guardian.get_event_bus") ,
        ):
            mock_settings.return_value.data_dir = "/tmp/test"
            mock_api = MagicMock()
            mock_assessment = MagicMock()
            mock_assessment.overall_score = 80.0
            mock_api.assess_compliance = AsyncMock(return_value=mock_assessment)

            with patch(
                "tools.compliance.guardian.get_compliance_api", return_value=mock_api
            ):
                guardian = ComplianceGuardian()

                result = await guardian.assess_compliance("test-target", "gdpr")

                assert result.overall_score == 80.0
                mock_api.assess_compliance.assert_called_once_with(
                    "test-target", "gdpr"
                )

    @pytest.mark.asyncio
    async def test_compliance_assess_hipaa(self):
        """Test compliance assessment for HIPAA."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.overall_score = 60.0
        mock_assessment.model_dump.return_value = {
            "status": "partially_compliant",
            "score": 60.0,
        }
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_assess(ctx, "health-system", "hipaa")

            assert result["status"] == "partially_compliant"
            assert result["score"] == 60.0

    @pytest.mark.asyncio
    async def test_compliance_assess_invalid_framework(self):
        """Test compliance assessment with invalid framework."""
        ctx = MagicMock()

        with pytest.raises(ValueError):
            await compliance_assess(ctx, "test-system", "invalid_framework")

    @pytest.mark.asyncio
    async def test_compliance_report_multiple_frameworks(self):
        """Test compliance report with multiple frameworks."""
        # Mock guardians
        mock_gdpr_guardian = MagicMock()
        mock_gdpr_assessment = MagicMock()
        mock_gdpr_assessment.overall_score = 80.0
        mock_gdpr_assessment.overall_status.value = "partially_compliant"
        mock_gdpr_assessment.model_dump.return_value = {
            "framework": "gdpr",
            "score": 80.0,
        }
        mock_gdpr_assessment.assessment_date.isoformat.return_value = (
            "2024-01-01T00:00:00"
        )
        mock_gdpr_guardian.assess_compliance = AsyncMock(
            return_value=mock_gdpr_assessment
        )

        mock_hipaa_guardian = MagicMock()
        mock_hipaa_assessment = MagicMock()
        mock_hipaa_assessment.overall_score = 75.0
        mock_hipaa_assessment.overall_status.value = "compliant"
        mock_hipaa_assessment.model_dump.return_value = {
            "framework": "hipaa",
            "score": 75.0,
        }
        mock_hipaa_assessment.assessment_date.isoformat.return_value = (
            "2024-01-01T00:00:00"
        )
        mock_hipaa_guardian.assess_compliance = AsyncMock(
            return_value=mock_hipaa_assessment
        )

        def mock_get_guardian():
            return mock_gdpr_guardian

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian",
            side_effect=mock_get_guardian,
        ):
            result = await compliance_report(ctx, "test-system", ["gdpr", "hipaa"])

            assert isinstance(result, dict)
            assert result["target"] == "test-system"
            assert "overall_score" in result
            assert "assessments" in result
            assert len(result["assessments"]) == 2

    @pytest.mark.asyncio
    async def test_compliance_report_empty_frameworks(self):
        """Test compliance report with empty frameworks list."""
        ctx = MagicMock()
        ctx.info = MagicMock()

        result = await compliance_report(ctx, "test-system", [])

        assert isinstance(result, dict)
        assert result["target"] == "test-system"
        assert result["frameworks_assessed"] == 0
        assert result["overall_score"] == 0.0
        assert result["overall_status"] == "not_applicable"
        assert result["assessments"] == []
        assert result["generated_at"] is None

    @pytest.mark.asyncio
    async def test_compliance_report_unknown_framework(self):
        """Test compliance report with unknown framework."""
        mock_guardian = MagicMock()

        ctx = MagicMock()
        ctx.warning = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_report(ctx, "test-system", ["unknown"])

            # Should warn about unknown framework
            ctx.warning.assert_called_with("Unknown framework: unknown")
            assert result["frameworks_assessed"] == 0

    @pytest.mark.asyncio
    async def test_compliance_check_gdpr_requirement(self):
        """Test compliance check for GDPR requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_check = MagicMock()
        mock_check.requirement.requirement_id = "GDPR-ART6"
        mock_check.status.value = "compliant"
        mock_check.score = 100.0
        mock_check.evidence = ["Evidence 1"]
        mock_check.violations = []
        mock_check.remediation_steps = []
        mock_check.checked_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_assessment.checks = [mock_check]
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "GDPR-ART6", "test-system")

            assert isinstance(result, dict)
            assert result["requirement_id"] == "GDPR-ART6"
            assert result["found"] is True
            assert result["status"] == "compliant"
            assert result["score"] == 100.0

    @pytest.mark.asyncio
    async def test_compliance_check_hipaa_requirement(self):
        """Test compliance check for HIPAA requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_check = MagicMock()
        mock_check.requirement.requirement_id = "HIPAA-164.308"
        mock_check.status.value = "partially_compliant"
        mock_check.score = 75.0
        mock_check.evidence = ["Basic safeguards"]
        mock_check.violations = ["Missing documentation"]
        mock_check.remediation_steps = ["Document procedures"]
        mock_check.checked_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_assessment.checks = [mock_check]
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "HIPAA-164.308", "test-system")

            assert result["requirement_id"] == "HIPAA-164.308"
            assert result["found"] is True
            assert result["status"] == "partially_compliant"
            assert "Missing documentation" in result["violations"]

    @pytest.mark.asyncio
    async def test_compliance_check_requirement_not_found(self):
        """Test compliance check for non-existent requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_assessment.checks = []  # No matching checks
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "NONEXISTENT-REQ", "test-system")

            assert isinstance(result, dict)
            assert result["requirement_id"] == "NONEXISTENT-REQ"
            assert result["found"] is False
            assert result["status"] == "not_found"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_compliance_check_iso_requirement(self):
        """Test compliance check for ISO requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_check = MagicMock()
        mock_check.requirement.requirement_id = "A.5.1"
        mock_check.status.value = "compliant"
        mock_check.score = 90.0
        mock_check.evidence = ["Policy documented"]
        mock_check.violations = []
        mock_check.remediation_steps = []
        mock_check.checked_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_assessment.checks = [mock_check]
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "A.5.1", "test-system")

            assert result["requirement_id"] == "A.5.1"
            assert result["found"] is True

    @pytest.mark.asyncio
    async def test_compliance_check_nist_requirement(self):
        """Test compliance check for NIST requirement."""
        mock_guardian = MagicMock()
        mock_assessment = MagicMock()
        mock_check = MagicMock()
        mock_check.requirement.requirement_id = "ID.AM-1"
        mock_check.status.value = "non_compliant"
        mock_check.score = 0.0
        mock_check.evidence = []
        mock_check.violations = ["No inventory system"]
        mock_check.remediation_steps = ["Implement asset inventory"]
        mock_check.checked_at.isoformat.return_value = "2024-01-01T00:00:00"
        mock_assessment.checks = [mock_check]
        mock_guardian.assess_compliance = AsyncMock(return_value=mock_assessment)

        ctx = MagicMock()
        ctx.info = MagicMock()

        with patch(
            "tools.compliance.tools.get_compliance_guardian", return_value=mock_guardian
        ):
            result = await compliance_check(ctx, "ID.AM-1", "test-system")

            assert result["requirement_id"] == "ID.AM-1"
            assert result["found"] is True
            assert result["status"] == "non_compliant"
            assert "No inventory system" in result["violations"]
