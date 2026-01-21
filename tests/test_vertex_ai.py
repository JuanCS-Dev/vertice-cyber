"""
Vertex AI Integration Tests
Testes para a integração com Google Cloud Vertex AI (Gemini 3 Series).
"""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tools.vertex_ai import VertexAIIntegration, get_vertex_ai, MODELS


class TestVertexAIIntegration:
    """Tests for Vertex AI integration using google.genai SDK and Gemini 3."""

    @pytest.fixture
    def vertex_ai(self):
        """Create Vertex AI integration for testing with mocked Client."""
        with patch("tools.vertex_ai.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            
            # Ensure environment variables are set for Gemini 3
            with patch.dict(os.environ, {"VERTEX_MODEL": "gemini-3-pro-preview"}):
                integration = VertexAIIntegration()
                return integration

    def test_vertex_ai_initialization_defaults(self):
        """Test initialization with default values (Gemini 3 Pro)."""
        with patch("tools.vertex_ai.genai.Client"):
            vertex_ai = VertexAIIntegration()
            assert vertex_ai.location == "global"
            assert vertex_ai.model_name == "gemini-3-pro-preview"

    @pytest.mark.asyncio
    async def test_analyze_threat_intelligence_success(self, vertex_ai):
        """Test successful threat intelligence analysis using Gemini 3."""
        mock_response = MagicMock()
        mock_response.text = '{"risk_level": "high", "confidence": 0.85}'
        vertex_ai.client.models.generate_content = MagicMock(return_value=mock_response)

        result = await vertex_ai.analyze_threat_intelligence(
            "Test query", {"indicators": []}
        )

        assert result["risk_level"] == "high"
        assert result["confidence"] == 0.85
        assert "timestamp" in result
        assert result["model_used"] == "gemini-3-pro-preview"

    @pytest.mark.asyncio
    async def test_analyze_threat_intelligence_failure(self, vertex_ai):
        """Test threat intelligence analysis failure."""
        vertex_ai.client.models.generate_content.side_effect = Exception("API Error")

        result = await vertex_ai.analyze_threat_intelligence(
            "Test query", {"indicators": []}
        )

        assert result["risk_level"] == "unknown"
        assert result["confidence"] == 0.0
        assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_compliance_report_success(self, vertex_ai):
        """Test successful compliance report generation."""
        mock_response = MagicMock()
        mock_response.text = (
            '{"overall_compliance_score": 85, "compliance_level": "compliant"}'
        )
        vertex_ai.client.models.generate_content.return_value = mock_response

        result = await vertex_ai.generate_compliance_report(
            "test-system", "gdpr", {"checks": []}
        )

        assert result["overall_compliance_score"] == 85
        assert result["compliance_level"] == "compliant"
        assert result["model_used"] == "gemini-3-pro-preview"

    @pytest.mark.asyncio
    async def test_analyze_osint_findings_success(self, vertex_ai):
        """Test successful OSINT findings analysis."""
        mock_response = MagicMock()
        mock_response.text = '{"risk_assessment": "medium", "risk_score": 65}'
        vertex_ai.client.models.generate_content.return_value = mock_response

        result = await vertex_ai.analyze_osint_findings(
            "test@example.com", [{"source": "hibp", "severity": "high"}]
        )

        assert result["risk_assessment"] == "medium"
        assert result["risk_score"] == 65
        assert result["model_used"] == "gemini-3-pro-preview"

    def test_get_vertex_ai_singleton(self):
        """Test get_vertex_ai singleton pattern."""
        with patch("tools.vertex_ai.genai.Client"):
            import tools.vertex_ai
            tools.vertex_ai._vertex_ai = None # Reset singleton

            ai1 = get_vertex_ai()
            ai2 = get_vertex_ai()

            assert ai1 is ai2
            assert isinstance(ai1, VertexAIIntegration)

    def test_vertex_ai_initialization_with_env_vars(self):
        """Test initialization with environment variables override."""
        # Testing switching to 'flash' model via env var
        with patch.dict(os.environ, {
            "GCP_PROJECT_ID": "test-project-env",
            "VERTEX_MODEL": "gemini-3-flash-preview" 
        }):
            with patch("tools.vertex_ai.genai.Client"):
                vertex_ai = VertexAIIntegration()
                
                assert vertex_ai.project_id == "test-project-env"
                # Check if it respected the env var override to Flash
                assert vertex_ai.model_name == "gemini-3-flash-preview"

    def test_set_model_switching(self):
        """Test switching models at runtime."""
        with patch("tools.vertex_ai.genai.Client"):
            vertex_ai = VertexAIIntegration()
            assert vertex_ai.model_name == "gemini-3-pro-preview"
            
            # Switch to Flash
            new_model = vertex_ai.set_model("flash")
            assert new_model == "gemini-3-flash-preview"
            assert vertex_ai.model_name == "gemini-3-flash-preview"
            
            # Switch back to Pro
            new_model = vertex_ai.set_model("pro")
            assert new_model == "gemini-3-pro-preview"

    @pytest.mark.asyncio
    async def test_generate_multimodal_content(self, vertex_ai):
        """Test the new multimodal generation method."""
        mock_response = MagicMock()
        mock_response.text = '{"is_deepfake": false}'
        vertex_ai.client.models.generate_content.return_value = mock_response
        
        result = await vertex_ai.generate_multimodal_content(
            "Analyze this image",
            image_data="aaaa",
            mime_type="image/jpeg"
        )
        
        assert result == '{"is_deepfake": false}'
        
        # Verify it constructed the Content object with text and bytes
        call_args = vertex_ai.client.models.generate_content.call_args
        contents = call_args.kwargs['contents']
        assert len(contents) == 1
        assert len(contents[0].parts) == 2 # Text + Image
