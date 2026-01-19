"""
Test OSINT Hunter - Complete Coverage
Testes para alcançar 100% cobertura no OSINT Hunter.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.osint import (
    InvestigationDepth,
    OSINTFinding,
    BreachInfo,
    OSINTHunter,
    OSINTResult,
)


class TestOSINTHunterCompleteCoverage:
    """Complete tests for OSINT Hunter to reach 100% coverage."""

    @pytest.fixture
    def hunter(self):
        """Create OSINT hunter for testing."""
        from unittest.mock import patch

        with (
            patch("tools.osint.get_settings") as mock_settings,
            patch("tools.osint.get_agent_memory") ,
            patch("tools.osint.get_event_bus") as mock_bus,
        ):
            mock_settings.return_value.api_keys.hibp_api_key = None
            mock_bus.return_value.emit = AsyncMock()

            hunter = OSINTHunter()
            return hunter

    @pytest.mark.asyncio
    async def test_osint_investigate_basic(self):
        """Test basic OSINT investigation."""
        from tools.osint import osint_investigate

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = "Test content"
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await osint_investigate(MagicMock(), "example.com", "basic")

            assert result["target"] == "example.com"
            assert result["depth"] == "basic"
            assert "findings" in result
            assert "breaches" in result
            assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_osint_investigate_deep(self):
        """Test deep OSINT investigation."""
        from tools.osint import osint_investigate

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = "Malicious content detected"
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await osint_investigate(MagicMock(), "suspicious.com", "deep")

            assert result["target"] == "suspicious.com"
            assert result["depth"] == "deep"

    @pytest.mark.asyncio
    async def test_osint_breach_check(self):
        """Test breach check functionality."""
        from tools.osint import osint_breach_check

        with patch("httpx.AsyncClient") as mock_client:
            # Mock HaveIBeenPwned API response
            mock_response = MagicMock()
            mock_response.json = AsyncMock(
                return_value=[
                    {"Name": "TestBreach", "Title": "Test Breach", "Domain": "test.com"}
                ]
            )
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await osint_breach_check(MagicMock(), "test@example.com")

            assert isinstance(result, dict)
            assert "breaches" in result

    @pytest.mark.asyncio
    async def test_osint_google_dork(self):
        """Test Google dork generation."""
        from tools.osint import osint_google_dork

        result = await osint_google_dork(MagicMock(), "example.com")

        assert isinstance(result, dict)
        assert "domain" in result
        assert "dorks" in result
        assert len(result["dorks"]) > 0

        # Verify dork structure
        for dork in result["dorks"]:
            assert "category" in dork
            assert "dork" in dork
            assert "description" in dork

    def test_investigation_depth_enum(self):
        """Test investigation depth enum values."""
        assert InvestigationDepth.BASIC.value == "basic"
        assert InvestigationDepth.DEEP.value == "deep"
        assert InvestigationDepth.EXHAUSTIVE.value == "exhaustive"

    def test_osint_finding_creation(self):
        """Test OSINT finding model creation."""
        finding = OSINTFinding(
            source="test_source",
            finding_type="breach",
            severity="high",
            data={"key": "value"},
            confidence=0.85,
        )

        assert finding.source == "test_source"
        assert finding.finding_type == "breach"
        assert finding.severity == "high"
        assert finding.data == {"key": "value"}
        assert finding.confidence == 0.85

    def test_breach_info_creation(self):
        """Test breach info model creation."""
        breach = BreachInfo(
            name="Test Breach",
            date="2024-01-15",
            data_classes=["emails", "passwords"],
            is_verified=True,
        )

        assert breach.name == "Test Breach"
        assert breach.date == "2024-01-15"
        assert breach.data_classes == ["emails", "passwords"]
        assert breach.is_verified is True

    def test_osint_hunter_initialization_with_hibp_key(self):
        """Test OSINT hunter initialization with HIBP API key."""
        from unittest.mock import MagicMock, patch

        # Mock get_settings to return settings with HIBP key
        mock_settings = MagicMock()
        mock_api_keys = MagicMock()
        mock_hibp_key = MagicMock()
        mock_hibp_key.get_secret_value.return_value = "test-key-123"
        mock_api_keys.hibp_api_key = mock_hibp_key
        mock_settings.api_keys = mock_api_keys

        with patch("tools.osint.get_settings", return_value=mock_settings):
            hunter = OSINTHunter()
            assert hunter.hibp_api_key == "test-key-123"

    def test_osint_hunter_initialization_without_hibp_key(self):
        """Test OSINT hunter initialization without HIBP API key."""
        from unittest.mock import MagicMock, patch

        # Mock get_settings to return settings without HIBP key
        mock_settings = MagicMock()
        mock_api_keys = MagicMock()
        mock_api_keys.hibp_api_key = None
        mock_settings.api_keys = mock_api_keys

        with patch("tools.osint.get_settings", return_value=mock_settings):
            hunter = OSINTHunter()
            assert hunter.hibp_api_key is None

    @pytest.mark.asyncio
    async def test_investigate_email_target(self, hunter):
        """Test investigation of email target."""
        result = await hunter.investigate("test@example.com")

        assert result.target == "test@example.com"
        assert "email_analysis" in result.sources_checked
        assert any(f.finding_type == "domain_extracted" for f in result.findings)

    @pytest.mark.asyncio
    async def test_investigate_ip_target(self, hunter):
        """Test investigation of IP target."""
        result = await hunter.investigate("192.168.1.1")

        assert result.target == "192.168.1.1"
        assert "ip_analysis" in result.sources_checked
        assert any(f.finding_type == "ip_info" for f in result.findings)

    @pytest.mark.asyncio
    async def test_check_breach_with_api_key(self, hunter):
        """Test breach checking with API key available."""
        from unittest.mock import patch, AsyncMock

        # Set API key
        hunter.hibp_api_key = "test-key"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(
            return_value=[{"Name": "TestBreach", "BreachDate": "2020-01-01"}]
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            breaches = await hunter.check_breach("test@example.com")

            assert len(breaches) == 1
            assert breaches[0]["Name"] == "TestBreach"

    @pytest.mark.asyncio
    async def test_check_breach_without_api_key(self, hunter):
        """Test breach checking without API key."""
        # Ensure no API key
        hunter.hibp_api_key = None

        breaches = await hunter.check_breach("test@example.com")

        assert breaches == []

    @pytest.mark.asyncio
    async def test_check_breach_api_error(self, hunter):
        """Test breach checking with API error."""
        from unittest.mock import patch, AsyncMock

        # Set API key
        hunter.hibp_api_key = "test-key"

        # Mock error response
        mock_response = AsyncMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value = AsyncMock()
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            breaches = await hunter.check_breach("test@example.com")

            assert breaches == []

    def test_calculate_risk_critical_findings(self, hunter):
        """Test risk calculation with critical findings."""
        result = OSINTResult(target="test@example.com", depth=InvestigationDepth.BASIC)
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="critical_breach",
                severity="critical",
                data={},
                confidence=1.0,
            )
        ]

        risk_score = hunter._calculate_risk(result)
        assert risk_score == 25.0  # 25 for critical

    def test_calculate_risk_high_findings(self, hunter):
        """Test risk calculation with high severity findings."""
        result = OSINTResult(target="test@example.com", depth=InvestigationDepth.BASIC)
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="high_risk",
                severity="high",
                data={},
                confidence=1.0,
            )
        ]

        risk_score = hunter._calculate_risk(result)
        assert risk_score == 15.0  # 15 for high

    def test_calculate_risk_medium_findings(self, hunter):
        """Test risk calculation with medium severity findings."""
        result = OSINTResult(target="test@example.com", depth=InvestigationDepth.BASIC)
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="medium_risk",
                severity="medium",
                data={},
                confidence=1.0,
            )
        ]

        risk_score = hunter._calculate_risk(result)
        assert risk_score == 5.0  # 5 for medium

    def test_get_osint_hunter_singleton(self):
        """Test get_osint_hunter singleton pattern."""
        from tools.osint import get_osint_hunter

        # Clear existing instance
        import tools.osint

        tools.osint._osint_hunter = None

        # Get first instance
        hunter1 = get_osint_hunter()
        assert hunter1 is not None

        # Get second instance - should be same
        hunter2 = get_osint_hunter()
        assert hunter1 is hunter2
