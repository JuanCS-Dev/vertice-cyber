"""
Test OSINT Hunter
Testes para OSINT Hunter e funcionalidades relacionadas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.osint import (
    get_osint_hunter,
    OSINTHunter,
    InvestigationDepth,
    OSINTFinding,
    BreachInfo,
)


class TestOSINTHunter:
    """Test OSINT Hunter functionality."""

    @pytest.fixture
    def hunter(self):
        """Create OSINT hunter instance."""
        return OSINTHunter()

    @pytest.fixture
    async def hunter_async(self):
        """Create OSINT hunter instance for async tests."""
        return await get_osint_hunter()

    def test_singleton(self):
        """Test OSINT Hunter singleton pattern."""
        hunter1 = get_osint_hunter()
        hunter2 = get_osint_hunter()
        assert hunter1 is hunter2

    def test_initialization(self, hunter):
        """Test OSINT Hunter initialization."""
        assert hunter.settings is not None
        assert hunter.memory is not None
        assert hunter.event_bus is not None

    @pytest.mark.asyncio
    async def test_investigate_basic(self, hunter_async):
        """Test basic investigation."""
        # Mock httpx to avoid real HTTP calls
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = "Test content"
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await hunter_async.investigate(
                "example.com", InvestigationDepth.BASIC
            )

            assert result["target"] == "example.com"
            assert result["depth"] == InvestigationDepth.BASIC
            assert "findings" in result
            assert "breaches" in result
            assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_investigate_comprehensive(self, hunter_async):
        """Test comprehensive investigation."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = "Malicious site detected"
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await hunter_async.investigate(
                "malicious-site.com", InvestigationDepth.DEEP
            )

            assert result["target"] == "malicious-site.com"
            assert result["depth"] == InvestigationDepth.DEEP
            assert result["risk_score"] >= 0

    @pytest.mark.asyncio
    async def test_breach_check_found(self, hunter_async):
        """Test breach check when breach is found."""
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

            result = await hunter_async.breach_check("test@example.com")

            assert isinstance(result, dict)
            assert "breaches" in result

    @pytest.mark.asyncio
    async def test_breach_check_not_found(self, hunter_async):
        """Test breach check when no breach is found."""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock empty response
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value=[])
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await hunter_async.breach_check("clean@example.com")

            assert isinstance(result, dict)
            assert "breaches" in result

    @pytest.mark.asyncio
    async def test_google_dork_generation(self, hunter_async):
        """Test Google dork generation."""
        result = await hunter_async.google_dork("example.com")

        assert isinstance(result, dict)
        assert "domain" in result
        assert "dorks" in result
        assert len(result["dorks"]) > 0

        # Verify dork structure
        for dork in result["dorks"]:
            assert "category" in dork
            assert "dork" in dork
            assert "description" in dork

    def test_risk_calculation_no_findings(self, hunter):
        """Test risk calculation with no findings."""
        result = OSINTResult(target="safe.com", depth=InvestigationDepth.BASIC)
        risk = hunter._calculate_risk(result)
        assert risk == 0

    def test_risk_calculation_with_findings(self, hunter):
        """Test risk calculation with findings and breaches."""
        result = OSINTResult(target="risky.com", depth=InvestigationDepth.BASIC)

        # Add findings
        result.findings = [
            OSINTFinding(
                source="test",
                finding_type="breach",
                severity="high",
                data={"breach": "found"},
                confidence=0.9,
            ),
            OSINTFinding(
                source="test",
                finding_type="malware",
                severity="medium",
                data={"malware": "detected"},
                confidence=0.7,
            ),
        ]

        # Add breaches
        result.breaches = [
            BreachInfo(
                name="Breach1",
                date="2024-01-01",
                data_classes=["emails"],
                is_verified=True,
            ),
            BreachInfo(
                name="Breach2",
                date="2024-02-01",
                data_classes=["passwords"],
                is_verified=False,
            ),
        ]

        risk = hunter._calculate_risk(result)
        assert risk > 0
        assert risk <= 100

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

    def test_investigation_depth_enum(self):
        """Test investigation depth enum values."""
        assert InvestigationDepth.BASIC == "basic"
        assert InvestigationDepth.DEEP == "deep"
        assert InvestigationDepth.EXHAUSTIVE == "exhaustive"
