"""
Vertex AI Integration Tests
Testes para a integração com Google Cloud Vertex AI.
"""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tools.vertex_ai import VertexAIIntegration, get_vertex_ai


class TestVertexAIIntegration:
    """Tests for Vertex AI integration."""

    @pytest.fixture
    def vertex_ai(self):
        """Create Vertex AI integration for testing."""
        with patch("vertexai.init"):  # Mock vertexai.init to avoid authentication
            integration = VertexAIIntegration()
            return integration

    def test_vertex_ai_initialization_defaults(self):
        """Test initialization with default values."""
        vertex_ai = VertexAIIntegration()
        assert vertex_ai.location == "global"

        def test_get_model_caching(self, vertex_ai):
            """Test model caching functionality."""

            with patch("tools.vertex_ai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()

                mock_model_class.return_value = mock_model

                # Get model twice

                model1 = vertex_ai.get_model("gemini-1.5-pro")

                model2 = vertex_ai.get_model("gemini-1.5-pro")

                # Should be the same instance (cached)

                assert model1 is model2

                assert model1 is mock_model

            # Should only create one instance
            assert mock_model_class.call_count == 1

    @pytest.mark.asyncio
    async def test_analyze_threat_intelligence_success(self, vertex_ai):
        """Test successful threat intelligence analysis."""
        with patch.object(vertex_ai, "get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = '{"risk_level": "high", "confidence": 0.85}'
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_get_model.return_value = mock_model

            result = await vertex_ai.analyze_threat_intelligence(
                "Test query", {"indicators": []}
            )

            assert result["risk_level"] == "high"
            assert result["confidence"] == 0.85
            assert "timestamp" in result
            assert result["query"] == "Test query"

    @pytest.mark.asyncio
    async def test_analyze_threat_intelligence_failure(self, vertex_ai):
        """Test threat intelligence analysis failure."""
        with patch.object(vertex_ai, "get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_model.return_value = mock_model

            result = await vertex_ai.analyze_threat_intelligence(
                "Test query", {"indicators": []}
            )

            assert result["risk_level"] == "unknown"
            assert result["confidence"] == 0.0
            assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_compliance_report_success(self, vertex_ai):
        """Test successful compliance report generation."""
        with patch.object(vertex_ai, "get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = (
                '{"overall_compliance_score": 85, "compliance_level": "compliant"}'
            )
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_get_model.return_value = mock_model

            result = await vertex_ai.generate_compliance_report(
                "test-system", "gdpr", {"checks": []}
            )

            assert result["overall_compliance_score"] == 85
            assert result["compliance_level"] == "compliant"
            assert result["target"] == "test-system"
            assert result["framework"] == "gdpr"

    @pytest.mark.asyncio
    async def test_analyze_osint_findings_success(self, vertex_ai):
        """Test successful OSINT findings analysis."""
        with patch.object(vertex_ai, "get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = '{"risk_assessment": "medium", "risk_score": 65}'
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_get_model.return_value = mock_model

            result = await vertex_ai.analyze_osint_findings(
                "test@example.com", [{"source": "hibp", "severity": "high"}]
            )

            assert result["risk_assessment"] == "medium"
            assert result["risk_score"] == 65
            assert result["target"] == "test@example.com"
            assert result["findings_count"] == 1

    def test_get_vertex_ai_singleton(self):
        """Test get_vertex_ai singleton pattern."""
        with patch("vertexai.init"):
            # Clear existing instance
            import tools.vertex_ai

            tools.vertex_ai._vertex_ai = None

            # Get instances
            ai1 = get_vertex_ai()
            ai2 = get_vertex_ai()

            assert ai1 is ai2
            assert isinstance(ai1, VertexAIIntegration)

    def test_vertex_ai_initialization_with_env_vars(self):
        """Test initialization with environment variables."""
        with (
            patch.dict(
                os.environ,
                {
                    "GCP_PROJECT_ID": "test-project-env",
                    "GCP_LOCATION": "us-west1",
                    "VERTEX_MODEL": "gemini-1.0-pro",
                },
            ),
            patch("vertexai.init"),
        ):
            vertex_ai = VertexAIIntegration()

            assert vertex_ai.project_id == "test-project-env"
            assert vertex_ai.location == "us-west1"
            assert vertex_ai.model_name == "gemini-1.0-pro"

    def test_vertex_ai_initialization_without_env_vars(self):
        """Test initialization without environment variables."""
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("tools.vertex_ai.get_settings") as mock_settings,
            patch("vertexai.init"),
        ):
            mock_api_keys = MagicMock()
            mock_api_keys.gcp_project_id = "settings-project"
            mock_api_keys.gcp_location = "europe-west1"
            mock_api_keys.vertex_model = "gemini-pro-vision"
            mock_settings.return_value.api_keys = mock_api_keys

            vertex_ai = VertexAIIntegration()

            assert vertex_ai.project_id == "settings-project"
            assert vertex_ai.location == "europe-west1"
            assert vertex_ai.model_name == "gemini-pro-vision"

        def test_get_model_different_names(self):
            """Test getting models with different names."""

            with patch("tools.vertex_ai.GenerativeModel") as mock_model_class:
                mock_model1 = MagicMock()

                mock_model2 = MagicMock()

                mock_model_class.side_effect = [mock_model1, mock_model2]

                vertex_ai = VertexAIIntegration()

                # Get two different models

                model1 = vertex_ai.get_model("gemini-1.5-pro")

                model2 = vertex_ai.get_model("gemini-pro-vision")

                assert model1 is mock_model1

                assert model2 is mock_model2

            assert model2 is mock_model2
            assert mock_model_class.call_count == 2

        def test_model_caching_same_name(self):
            """Test that same model name returns cached instance."""

            with patch("tools.vertex_ai.GenerativeModel") as mock_model_class:
                mock_model = MagicMock()

                mock_model_class.return_value = mock_model

                vertex_ai = VertexAIIntegration()

                # Get same model twice

                model1 = vertex_ai.get_model("gemini-1.5-pro")

                model2 = vertex_ai.get_model("gemini-1.5-pro")

                assert model1 is model2

                assert model1 is mock_model

            # Should only create one instance
            assert mock_model_class.call_count == 1

    @pytest.mark.asyncio
    async def test_stream_analysis(self, vertex_ai):
        """Test streaming analysis functionality."""
        with patch.object(vertex_ai, "get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()

            # Mock async iterator
            async def async_iter():
                yield MagicMock(text="Chunk 1")
                yield MagicMock(text="Chunk 2")

            mock_response.__aiter__ = lambda: async_iter()
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_get_model.return_value = mock_model

            chunks = []
            async for chunk in vertex_ai.stream_analysis("threat", {"data": "test"}):
                chunks.append(chunk)

            assert len(chunks) >= 1
