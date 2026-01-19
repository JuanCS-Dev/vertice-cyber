"""
FastMCP Compat Coverage Tests
Testes específicos para cobrir linhas não testadas no fastmcp compatibility layer.
"""

from unittest.mock import patch, MagicMock

from tools.fastmcp_compat import is_fastmcp_available, get_fastmcp_context, MockContext


class TestFastMCPCoverage:
    """Tests to cover specific lines in fastmcp compatibility."""

    def test_is_fastmcp_available_false_currently(self):
        """Cover the current implementation that returns False."""
        # Clear cached result
        import tools.fastmcp_compat

        tools.fastmcp_compat._fastmcp_available = None

        result = is_fastmcp_available()
        assert result is False

    def test_get_fastmcp_context_returns_mock(self):
        """Cover get_fastmcp_context returning MockContext."""
        # Clear cached context
        import tools.fastmcp_compat

        tools.fastmcp_compat._fastmcp_context = None

        context = get_fastmcp_context()
        assert isinstance(context, MockContext)

    def test_mock_context_methods(self):
        """Cover all MockContext methods."""
        ctx = MockContext()

        # Test info method (line 27-29)
        ctx.info("test message")

        # Test warning method
        ctx.warning("test warning")

        # Test error method
        ctx.error("test error")

        # Methods should not raise exceptions
        assert True

    @patch("tools.fastmcp_compat.is_fastmcp_available")
    @patch("fastmcp.Context")
    def test_get_fastmcp_context_with_fastmcp_available(
        self, mock_context_class, mock_available
    ):
        """Cover the case where fastmcp is available (mocked)."""
        mock_available.return_value = True
        mock_context_instance = MagicMock()
        mock_context_class.return_value = mock_context_instance

        # Clear cached context
        import tools.fastmcp_compat

        tools.fastmcp_compat._fastmcp_context = None

        context = get_fastmcp_context()

        # Should return the mocked fastmcp context
        assert context == mock_context_instance
        mock_context_class.assert_called_once()

    def test_mock_context_singleton_behavior(self):
        """Cover that get_fastmcp_context returns same MockContext instance."""
        # Clear cached context
        import tools.fastmcp_compat

        tools.fastmcp_compat._fastmcp_context = None

        ctx1 = get_fastmcp_context()
        ctx2 = get_fastmcp_context()

        assert ctx1 is ctx2
        assert isinstance(ctx1, MockContext)
