"""
Compliance Guardian Coverage Tests
Testes específicos para cobrir linhas não testadas no compliance guardian.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tools.compliance.guardian import ComplianceGuardian


class TestComplianceGuardianCoverage:
    """Tests to cover specific lines in compliance guardian."""

    @pytest.fixture
    def guardian(self):
        """Create compliance guardian for testing."""
        with (
            patch("tools.compliance.guardian.get_settings") as mock_settings,
            patch("tools.compliance.guardian.get_agent_memory") ,
            patch("tools.compliance.guardian.get_event_bus") ,
        ):
            mock_settings.return_value.data_dir = "/tmp/test"
            guardian = ComplianceGuardian()
            return guardian

    def test_guardian_initialization_attributes(self, guardian):
        """Cover guardian initialization attributes."""
        # Lines 46-48: attribute assignments
        assert hasattr(guardian, "settings")
        assert hasattr(guardian, "memory")
        assert hasattr(guardian, "event_bus")
        assert hasattr(guardian, "api")

    @pytest.mark.asyncio
    async def test_assess_compliance_method(self, guardian):
        """Cover assess_compliance method lines 63-108."""
        mock_api = MagicMock()
        mock_assessment = MagicMock()
        mock_api.assess_compliance = AsyncMock(return_value=mock_assessment)

        with patch.object(guardian, "api", mock_api):
            result = await guardian.assess_compliance("test-target", "gdpr")

            mock_api.assess_compliance.assert_called_once_with("test-target", "gdpr")
            assert result == mock_assessment

    @pytest.mark.asyncio
    async def test_check_requirement_method(self, guardian):
        """Cover check_requirement method."""
        mock_api = MagicMock()
        mock_requirement = MagicMock()
        mock_api.check_requirement = AsyncMock(return_value=mock_requirement)

        with patch.object(guardian, "api", mock_api):
            result = await guardian.check_requirement("req1", "test-target")

            mock_api.check_requirement.assert_called_once_with("req1", "test-target")
            assert result == mock_requirement

    def test_get_frameworks_method(self, guardian):
        """Cover get_frameworks method."""
        mock_api = MagicMock()
        mock_frameworks = ["gdpr", "hipaa"]
        mock_api.get_frameworks = MagicMock(return_value=mock_frameworks)

        with patch.object(guardian, "api", mock_api):
            result = guardian.get_frameworks()

            mock_api.get_frameworks.assert_called_once()
            assert result == mock_frameworks

    def test_get_requirements_method(self, guardian):
        """Cover get_requirements method."""
        mock_api = MagicMock()
        mock_requirements = [{"id": "req1", "title": "Test"}]
        mock_api.get_requirements = MagicMock(return_value=mock_requirements)

        with patch.object(guardian, "api", mock_api):
            result = guardian.get_requirements("gdpr")

            mock_api.get_requirements.assert_called_once_with("gdpr")
            assert result == mock_requirements

    def test_get_compliance_guardian_singleton_cleared(self):
        """Cover get_compliance_guardian singleton clearing."""
        from tools.compliance.guardian import get_compliance_guardian

        # Clear existing instance
        import tools.compliance.guardian

        tools.compliance.guardian._compliance_guardian = None

        # Get instance
        guardian1 = get_compliance_guardian()
        assert guardian1 is not None

        # Get again - should be same
        guardian2 = get_compliance_guardian()
        assert guardian1 is guardian2
