
import asyncio
import base64
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from tools.deepfake_scanner import DeepfakeScanner, scan_media

class TestDeepfakeScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = DeepfakeScanner()
        # Mock the vertex provider
        self.scanner.vertex_provider = AsyncMock()
    
    @patch("tools.deepfake_scanner.DeepfakeScanner._check_synth_id")
    def test_scan_synth_id_hit(self, mock_synth):
        """Test that scan returns early if SynthID detects something."""
        async def run():
            mock_synth.return_value = MagicMock(is_deepfake=True, confidence=1.0)
            result = await self.scanner.scan("base64", "image/jpeg", "test.jpg")
            self.assertEqual(result.confidence, 1.0)
            mock_synth.assert_called_once()
        asyncio.run(run())

    @patch("tools.deepfake_scanner.DeepfakeScanner._check_synth_id", new_callable=AsyncMock)
    @patch("tools.deepfake_scanner.DeepfakeScanner._analyze_metadata_heuristics")
    @patch("tools.deepfake_scanner.DeepfakeScanner._gemini_forensic_analysis", new_callable=AsyncMock)
    def test_scan_image_flow(self, mock_gemini, mock_meta, mock_synth):
        """Test standard image scanning flow."""
        mock_synth.return_value = None
        mock_meta.return_value = None # No heuristic match
        
        mock_gemini.return_value = MagicMock(
            is_deepfake=False, 
            confidence=0.1, 
            details={"metadata": {}}
        )

        async def run():
            # Mock base64 decode
            with patch("base64.b64decode", return_value=b"fake_bytes"):
                result = await self.scanner.scan("base64_data", "image/png", "test.png")
                
            mock_meta.assert_called_once()
            mock_gemini.assert_called_once()
            self.assertFalse(result.is_deepfake)
        
        asyncio.run(run())

    @patch("tools.deepfake_scanner.DeepfakeScanner._analyze_video_metadata")
    def test_scan_video_heuristic_hit(self, mock_video_meta):
        """Test video scan returning early on strong heuristic."""
        mock_video_meta.return_value = MagicMock(
            is_deepfake=True, 
            confidence=0.9, # > 0.8 threshold
            details={}
        )
        
        async def run():
            with patch("base64.b64decode", return_value=b"fake_video_bytes"):
                result = await self.scanner.scan("b64", "video/mp4", "test.mp4")
            
            self.assertEqual(result.confidence, 0.9)
            # Should NOT call Gemini if heuristic is strong
            # (Note: In implementation it only returns early if confidence > 0.8. 
            # If I mock gemini I can assert it wasn't called, but here I rely on result)
        asyncio.run(run())

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.unlink")
    def test_analyze_video_metadata_lavf(self, mock_unlink, mock_exists, mock_run, mock_temp):
        """Test detection of Lavf encoder via ffprobe."""
        mock_exists.return_value = True
        
        # Mock temp file context manager
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/test.mp4"
        mock_temp.return_value.__enter__.return_value = mock_tmp
        
        # Mock subprocess output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "format": {
                "tags": {
                    "encoder": "Lavf60.16.100"
                }
            },
            "streams": []
        })
        
        result = self.scanner._analyze_video_metadata(b"video_bytes", "test.mp4")
        
        self.assertIsNotNone(result)
        self.assertIn("Suspicious Encoder: Lavf60.16.100", result.details['flags'])
        self.assertEqual(result.source, "FFprobe Metadata")

    def test_gemini_prompt_selection(self):
        """Test prompt context selection based on mime type."""
        # This effectively tests the logic inside _gemini_forensic_analysis 
        # up to the point of calling the provider.
        
        async def run():
            self.scanner.vertex_provider.generate_multimodal_content.return_value = '{"is_deepfake": false}'
            
            # Image
            await self.scanner._gemini_forensic_analysis("b64", "image/jpeg")
            call_args = self.scanner.vertex_provider.generate_multimodal_content.call_args[1]
            self.assertIn("ESTA É UMA IMAGEM", call_args['prompt'])
            
            # Video
            await self.scanner._gemini_forensic_analysis("b64", "video/mp4")
            call_args = self.scanner.vertex_provider.generate_multimodal_content.call_args[1]
            self.assertIn("ESTE É UM ARQUIVO DE VÍDEO", call_args['prompt'])
            
            # Audio
            await self.scanner._gemini_forensic_analysis("b64", "audio/mp3")
            call_args = self.scanner.vertex_provider.generate_multimodal_content.call_args[1]
            self.assertIn("ESTE É UM ARQUIVO DE ÁUDIO", call_args['prompt'])
            
        asyncio.run(run())

if __name__ == "__main__":
    unittest.main()
