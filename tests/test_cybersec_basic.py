import pytest
import socket
from unittest.mock import MagicMock, AsyncMock, patch
from tools.cybersec_basic import get_cybersec_agent, PortResult

@pytest.mark.asyncio
async def test_cybersec_recon_ports_only():
    """Test recon with port scan only (mocked)."""
    agent = get_cybersec_agent()
    
    # Mock _scan_ports to avoid real network calls
    with patch.object(agent, '_scan_ports', new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = [
            PortResult(port=80, state="open", service="http"),
            PortResult(port=443, state="open", service="https")
        ]
        
        result = await agent.run_recon("example.com", scan_ports=True, scan_web=False)
        
        assert len(result.open_ports) == 2
        assert result.target == "example.com"
        mock_scan.assert_called_once()

@pytest.mark.asyncio
async def test_cybersec_recon_web_analysis():
    """Test web analysis logic."""
    agent = get_cybersec_agent()
    
    # Mock socket resolution
    with patch("socket.gethostbyname", return_value="127.0.0.1"):
        # Mock _scan_ports
        with patch.object(agent, '_scan_ports', new_callable=AsyncMock) as mock_scan:
            mock_scan.return_value = []
            
            # Mock _analyze_web logic by mocking httpx
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.headers = {
                    "Server": "Apache",
                    "Content-Type": "text/html"
                    # Missing security headers
                }
                
                # Setup async context manager mock
                mock_instance = mock_client.return_value
                mock_instance.__aenter__.return_value.get.return_value = mock_response
                
                result = await agent.run_recon("example.com", scan_ports=False, scan_web=True)
                
                # Check if security issues were found
                assert any("Missing security headers" in issue for issue in result.security_issues)
                assert any("Server header exposed" in issue for issue in result.security_issues)

@pytest.mark.asyncio
async def test_cybersec_dns_failure():
    """Test graceful handling of DNS errors."""
    agent = get_cybersec_agent()
    
    with patch("socket.gethostbyname", side_effect=socket.gaierror("DNS error")):
        result = await agent.run_recon("invalid.local", scan_ports=True, scan_web=False)
        
        assert "DNS resolution failed" in result.security_issues[0]
