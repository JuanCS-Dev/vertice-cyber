"""
Teste REAL da Integração Vertex AI
Testa a integração completa com GCP Vertex AI (simulado para demo)
"""

import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from tools.vertex_ai import VertexAIIntegration, get_vertex_ai


class TestVertexAIRealIntegration:
    """Testes que simulam integração real com GCP Vertex AI."""

    @pytest.fixture
    def mock_gcp_auth(self):
        """Mock GCP authentication and Vertex AI initialization."""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_PROJECT": "vertice-ai",
                "GOOGLE_CLOUD_LOCATION": "global",
            },
        ):
            with patch("vertexai.init") as mock_init:
                with patch("tools.vertex_ai.GenerativeModel") as mock_model_class:
                    mock_model = MagicMock()
                    mock_model.generate_content_async = AsyncMock()
                    mock_model_class.return_value = mock_model

                    yield {
                        "init": mock_init,
                        "model_class": mock_model_class,
                        "model": mock_model,
                    }

    def test_vertex_ai_gcp_initialization(self, mock_gcp_auth):
        """Test Vertex AI initialization with GCP credentials."""
        # Force re-instantiation to trigger init with patched environment
        with patch("vertexai.init") as mock_init:
            with patch.dict(os.environ, {"GCP_PROJECT_ID": "vertice-ai"}):
                _ = VertexAIIntegration()
                # Verify vertexai.init was called with correct parameters
                mock_init.assert_called_with(project="vertice-ai", location="global")

    @pytest.mark.asyncio
    async def test_real_vertex_ai_threat_analysis(self, mock_gcp_auth):
        """Test real threat analysis using Vertex AI."""
        vertex_ai = VertexAIIntegration()

        # Mock successful Vertex AI response
        mock_response = MagicMock()
        mock_response.text = """{
            "risk_level": "high",
            "confidence": 0.87,
            "insights": [
                "Multiple suspicious indicators detected",
                "Known malware patterns identified"
            ],
            "recommendations": [
                "Isolate affected systems immediately",
                "Review firewall rules"
            ],
            "summary": "High-risk threat detected with 87% confidence"
        }"""

        mock_gcp_auth["model"].generate_content_async.return_value = mock_response

        # Test real analysis
        result = await vertex_ai.analyze_threat_intelligence(
            "Investigate suspicious IP 192.168.1.100",
            {
                "indicators": [
                    {"type": "ip", "value": "192.168.1.100", "confidence": 0.9},
                    {
                        "type": "domain",
                        "value": "malicious-site.com",
                        "confidence": 0.8,
                    },
                ],
                "osint_findings": ["Breach detected", "Malware associated"],
                "threat_score": 85,
            },
        )

        # Verify Vertex AI was called
        mock_gcp_auth["model"].generate_content_async.assert_called_once()

        # Verify response structure
        assert result["risk_level"] == "high"
        assert result["confidence"] == 0.87
        assert len(result["insights"]) == 2
        assert len(result["recommendations"]) == 2
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_vertex_ai_compliance_report(self, mock_gcp_auth):
        """Test compliance report generation with Vertex AI."""
        vertex_ai = VertexAIIntegration()

        # Mock compliance assessment response
        mock_response = MagicMock()
        mock_response.text = """{
            "overall_compliance_score": 78.5,
            "compliance_level": "partially_compliant",
            "key_findings": [
                "GDPR Article 25 partially implemented",
                "Data encryption standards met"
            ],
            "critical_violations": [
                "Missing data processing records"
            ],
            "recommended_actions": [
                "Implement comprehensive data logging",
                "Conduct privacy impact assessment"
            ]
        }"""

        mock_gcp_auth["model"].generate_content_async.return_value = mock_response

        result = await vertex_ai.generate_compliance_report(
            "web-application-01",
            "gdpr",
            {
                "current_controls": ["encryption", "access_control"],
                "gaps_identified": ["logging", "privacy_assessment"],
                "compliance_score": 65,
            },
        )

        # Verify response
        assert result["overall_compliance_score"] == 78.5
        assert result["compliance_level"] == "partially_compliant"
        assert len(result["critical_violations"]) == 1
        assert len(result["recommended_actions"]) == 2

    @pytest.mark.asyncio
    async def test_vertex_ai_streaming_analysis(self, mock_gcp_auth):
        """Test streaming analysis with Vertex AI."""
        vertex_ai = VertexAIIntegration()

        # Mock streaming response
        mock_response = MagicMock()

        async def async_generator(*args, **kwargs):
            yield MagicMock(text="Analysis starting...")
            yield MagicMock(text="Processing indicators...")
            yield MagicMock(text="High risk detected!")
            yield MagicMock(text="Recommendations generated.")

        mock_response.__aiter__ = async_generator
        mock_gcp_auth["model"].generate_content_async.return_value = mock_response

        # Collect streaming results
        chunks = []
        async for chunk in vertex_ai.stream_analysis(
            "threat_analysis",
            {"target": "malicious-domain.com", "indicators": ["phishing", "malware"]},
        ):
            chunks.append(chunk)

        # Verify streaming worked
        assert len(chunks) > 0
        assert "Analysis starting..." in chunks
        assert "High risk detected!" in chunks

    def test_gcp_project_configuration(self):
        """Test GCP project configuration loading."""
        with patch.dict(
            os.environ,
            {
                "GCP_PROJECT_ID": "vertice-ai-prod",
                "GCP_LOCATION": "us-west1",
                "VERTEX_MODEL": "gemini-1.5-pro-002",
            },
        ):
            vertex_ai = VertexAIIntegration()

            # Should use environment variables
            assert vertex_ai.project_id == "vertice-ai-prod"
            assert vertex_ai.location == "us-west1"
            assert vertex_ai.model_name == "gemini-1.5-pro-002"

    @pytest.mark.asyncio
    async def test_vertex_ai_error_handling(self, mock_gcp_auth):
        """Test error handling when Vertex AI fails."""
        vertex_ai = VertexAIIntegration()

        # Mock API failure
        mock_gcp_auth["model"].generate_content_async.side_effect = Exception(
            "GCP API Error"
        )

        result = await vertex_ai.analyze_threat_intelligence(
            "Test query", {"indicators": []}
        )

        # Should return error response
        assert result["risk_level"] == "unknown"
        assert "error" in result
        assert result["error"] == "GCP API Error"

    def test_vertex_ai_singleton_pattern(self, mock_gcp_auth):
        """Test singleton pattern for Vertex AI."""
        # Clear existing instance
        import tools.vertex_ai

        tools.vertex_ai._vertex_ai = None

        # Get instances
        ai1 = get_vertex_ai()
        ai2 = get_vertex_ai()

        # Should be same instance
        assert ai1 is ai2
        assert isinstance(ai1, VertexAIIntegration)
