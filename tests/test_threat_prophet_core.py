"""
Threat Prophet Core Tests
Testes essenciais para Threat Prophet com alta cobertura.
"""

import pytest
from unittest.mock import patch

from tools.threat import ThreatProphet, get_threat_prophet


class TestThreatProphetCore:
    """Core tests for Threat Prophet."""

    @pytest.fixture
    def prophet(self):
        """Create threat prophet for testing."""
        from unittest.mock import AsyncMock
        with (
            patch("tools.threat.get_settings") as mock_settings,
            patch("tools.threat.get_agent_memory") ,
            patch("tools.threat.get_event_bus") as mock_bus,
        ):
            mock_settings.return_value.data_dir = "/tmp/test"
            mock_bus.return_value.emit = AsyncMock()
            prophet = ThreatProphet()
            return prophet

    def test_threat_prophet_initialization(self, prophet):
        """Test threat prophet initialization."""
        assert hasattr(prophet, "settings")
        assert hasattr(prophet, "memory")
        assert hasattr(prophet, "event_bus")
        assert hasattr(prophet, "mitre_client")

    @pytest.mark.asyncio
    async def test_analyze_threats_basic(self, prophet):
        """Test basic threat analysis."""
        result = await prophet.analyze_threats("test.com", include_predictions=False)

        assert result.target == "test.com"
        assert hasattr(result, "indicators")
        assert hasattr(result, "overall_risk_score")

    @pytest.mark.asyncio
    async def test_get_threat_intelligence(self, prophet):
        """Test threat intelligence retrieval."""
        result = await prophet.get_threat_intelligence("malware")

        assert "query" in result
        assert "matching_techniques" in result
        assert "total_matches" in result
        assert result["query"] == "malware"

    def test_get_threat_prophet_singleton(self):
        """Test singleton pattern."""
        # Clear existing instance
        import tools.threat

        tools.threat._threat_prophet = None

        prophet1 = get_threat_prophet()
        prophet2 = get_threat_prophet()

        assert prophet1 is prophet2

    @pytest.mark.asyncio
    async def test_mitre_client_lazy_initialization(self, prophet):
        """Test lazy initialization of MITRE client."""
        # Access property
        client = prophet.mitre_client
        assert client is not None

        # Second access returns same instance
        client2 = prophet.mitre_client
        assert client is client2

    @pytest.mark.asyncio
    async def test_predict_threats(self, prophet):
        """Test threat prediction."""
        result = await prophet.predict_threats("test.com")

        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_predictions(self, prophet):
        """Test prediction generation."""
        predictions = await prophet._generate_predictions("test.com")

        assert isinstance(predictions, list)
        assert len(predictions) > 0
