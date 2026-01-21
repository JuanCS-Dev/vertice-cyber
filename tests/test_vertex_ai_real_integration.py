import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from tools.vertex_ai import VertexAIIntegration

class TestVertexAIRealIntegration(unittest.TestCase):
    
    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {
            "GCP_PROJECT_ID": "vertice-ai-prod",
            "GCP_LOCATION": "global",
            "VERTEX_MODEL": "gemini-3-pro-preview"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("tools.vertex_ai.genai.Client")
    def test_gcp_project_configuration(self, mock_client_cls):
        """Test GCP project configuration loading from environment."""
        vertex_ai = VertexAIIntegration()
        
        mock_client_cls.assert_called_with(
            vertexai=True,
            project="vertice-ai-prod",
            location="global"
        )
        assert vertex_ai.project_id == "vertice-ai-prod"
        assert vertex_ai.model_name == "gemini-3-pro-preview"

    @patch("tools.vertex_ai.genai.Client")
    def test_real_vertex_ai_threat_analysis(self, mock_client_cls):
        """Test threat analysis call structure."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"risk_level": "critical", "confidence": 0.99}'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        vertex_ai = VertexAIIntegration()
        
        import asyncio
        result = asyncio.run(vertex_ai.analyze_threat_intelligence("Hack attack", {}))
        
        assert result['risk_level'] == "critical"
        
        # Verify correct model passed to generate_content
        call_args = mock_client.models.generate_content.call_args
        assert call_args.kwargs['model'] == "gemini-3-pro-preview"

    @patch("tools.vertex_ai.genai.Client")
    def test_vertex_ai_error_handling(self, mock_client_cls):
        """Test error handling when API fails."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("Quota Exceeded")
        mock_client_cls.return_value = mock_client
        
        vertex_ai = VertexAIIntegration()
        
        import asyncio
        result = asyncio.run(vertex_ai.analyze_threat_intelligence("Test", {}))
        
        assert "error" in result
        assert result['risk_level'] == "unknown"
        assert "Quota Exceeded" in result['error']

if __name__ == "__main__":
    unittest.main()