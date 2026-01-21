"""
Compliance Guardian Coverage Tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.compliance.guardian import ComplianceGuardian, ComplianceFramework


class TestComplianceGuardianCoverage:
    @pytest.fixture
    def guardian(self):
        with patch("tools.compliance.guardian.get_settings"):
            return ComplianceGuardian()

    @pytest.mark.asyncio
    async def test_assess_compliance_method(self, guardian):
        mock_api = MagicMock()
        mock_api.get_controls_by_framework = AsyncMock(return_value=[])
        mock_api.get_all_controls = AsyncMock(return_value=[])

        with patch.object(guardian, "_compliance_api", mock_api):
            result = await guardian.assess_compliance(
                "target", ComplianceFramework.GDPR
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_frameworks_method(self, guardian):
        result = await guardian.get_frameworks()
        assert len(result) > 0

        @pytest.mark.asyncio
        async def test_get_requirements_method(self, guardian):
            mock_api = MagicMock()

            mock_api.get_controls_by_framework = AsyncMock(return_value=[])

            mock_api.get_all_controls = AsyncMock(return_value=[])

            with patch.object(guardian, "_compliance_api", mock_api):
                result = await guardian.get_requirements("gdpr")

                assert isinstance(result, list)
