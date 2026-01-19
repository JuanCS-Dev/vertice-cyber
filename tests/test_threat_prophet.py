"""
Test Threat Intelligence Tools
Testes para Threat Prophet e funcionalidades relacionadas.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from tools.threat import get_threat_prophet


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
            prophet = await get_threat_prophet()
            # Mock other dependencies
            prophet.memory = MagicMock()
            prophet.event_bus = MagicMock()
            prophet.event_bus.emit = AsyncMock()
            yield prophet

    @pytest.mark.asyncio
    async def test_singleton(self):
        """Test Threat Prophet singleton."""
        mock_mitre_client = MagicMock()
        mock_mitre_client.search_techniques = AsyncMock(return_value=[])

        with patch("tools.threat.get_mitre_client", return_value=mock_mitre_client):
            p1 = await get_threat_prophet()
            p2 = await get_threat_prophet()
            assert p1 is p2

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
        assert isinstance(analysis.overall_risk_score, (int, float))

    @pytest.mark.asyncio
    async def test_threat_intelligence_search(self, prophet):
        """Test threat intelligence search."""
        result = await prophet.get_threat_intelligence("phishing")

        assert isinstance(result, dict)
        assert "query" in result
        assert "matching_techniques" in result
        assert "total_matches" in result
