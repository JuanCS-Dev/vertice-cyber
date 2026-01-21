
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import json

from tools.vertex_ai import VertexAIIntegration

class TestVertexAIIntegrationV3(unittest.TestCase):
    
    def setUp(self):
        # Mock env vars
        self.env_patcher = patch.dict(os.environ, {
            "GCP_PROJECT_ID": "test-project",
            "VERTEX_MODEL": "gemini-3-pro-preview"
        })
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()

    @patch("tools.vertex_ai.genai.Client")
    def test_initialization(self, mock_client_cls):
        """Test proper initialization with genai Client."""
        client_instance = MagicMock()
        mock_client_cls.return_value = client_instance
        
        vertex = VertexAIIntegration()
        
        mock_client_cls.assert_called_with(
            vertexai=True, 
            project="test-project", 
            location="global"
        )
        self.assertTrue(vertex._initialized)
        self.assertEqual(vertex.model_name, "gemini-3-pro-preview")

    @patch("tools.vertex_ai.genai.Client")
    def test_generate_multimodal_content_success(self, mock_client_cls):
        """Test successful generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"analysis": "result"}'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        vertex = VertexAIIntegration()
        
        async def run():
            result = await vertex.generate_multimodal_content("prompt")
            self.assertEqual(result, '{"analysis": "result"}')
            
        import asyncio
        asyncio.run(run())

    @patch("tools.vertex_ai.genai.Client")
    def test_generate_multimodal_content_with_media(self, mock_client_cls):
        """Test generation with image data."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        mock_client_cls.return_value = mock_client
        
        vertex = VertexAIIntegration()
        
        async def run():
            # Mock base64 decode
            with patch("base64.b64decode", return_value=b"bytes"):
                await vertex.generate_multimodal_content(
                    "prompt", 
                    image_data="base64str", 
                    mime_type="image/jpeg"
                )
            
            # Verify call args structure
            call_args = mock_client.models.generate_content.call_args
            contents = call_args.kwargs['contents']
            # Should have 1 Content with 2 Parts (Text + Bytes)
            self.assertEqual(len(contents), 1)
            parts = contents[0].parts
            self.assertEqual(len(parts), 2)
            
        import asyncio
        asyncio.run(run())

    @patch("tools.vertex_ai.genai.Client")
    def test_error_handling(self, mock_client_cls):
        """Test error handling returns string message."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_cls.return_value = mock_client
        
        vertex = VertexAIIntegration()
        
        async def run():
            result = await vertex.generate_multimodal_content("prompt")
            self.assertIn("Error:", result)
            self.assertIn("API Error", result)
            
        import asyncio
        asyncio.run(run())

if __name__ == "__main__":
    unittest.main()
