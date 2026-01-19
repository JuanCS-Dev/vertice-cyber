"""
Test OSINT Hunter - Complete Coverage
Testes para alcançar 100% cobertura no OSINT Hunter.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.osint import (
    OSINTHunter,
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
            # Return proper mock response for check_breach
            mock_response.status_code = 404
            
            mock_session = AsyncMock()
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_session

            result = await osint_investigate(MagicMock(), "example.com", "basic")

            assert result["target"] == "example.com"
            assert result["depth"] == "basic"

    @pytest.mark.asyncio
    async def test_osint_investigate_deep(self):
        """Test deep OSINT investigation."""
        from tools.osint import osint_investigate

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = "Malicious content detected"
            mock_response.status_code = 404
            
            mock_session = AsyncMock()
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_session

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
            mock_response.status_code = 200
            mock_response.json = MagicMock(
                return_value=[
                    {"Name": "TestBreach", "BreachDate": "2020-01-01", "DataClasses": [], "IsVerified": True}
                ]
            )
            
            mock_session = AsyncMock()
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_session

            # Force API key
            with patch("tools.osint.get_settings") as mock_settings:
                mock_settings.return_value.api_keys.hibp_api_key.get_secret_value.return_value = "key"
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

    @pytest.mark.asyncio
    async def test_investigate_email_target(self, hunter):
        """Test investigation of email target."""
        result = await hunter.investigate("test@example.com")

        assert result.target == "test@example.com"
        assert "email_analysis" in result.sources_checked

    @pytest.mark.asyncio
    async def test_investigate_ip_target(self, hunter):
        """Test investigation of IP target."""
        result = await hunter.investigate("192.168.1.1")

        assert result.target == "192.168.1.1"
        assert "ip_analysis" in result.sources_checked

    @pytest.mark.asyncio
    async def test_check_breach_with_api_key(self, hunter):
        """Test breach checking with API key available."""
        # Set API key
        hunter.hibp_api_key = "test-key"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(
            return_value=[{"Name": "TestBreach", "BreachDate": "2020-01-01", "DataClasses": [], "IsVerified": True}]
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            breaches = await hunter.check_breach("test@example.com")

            assert len(breaches) == 1
            assert breaches[0].name == "TestBreach"