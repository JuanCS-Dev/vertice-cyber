"""
Test FastMCP Compatibility Layer
Testes para a camada de compatibilidade FastMCP/rich.
"""

from unittest.mock import patch

from tools.fastmcp_compat import is_fastmcp_available, get_fastmcp_context, MockContext


class TestFastMCPCompat:
    """Test FastMCP compatibility layer."""

    def test_mock_context_creation(self):
        """Test MockContext can be created."""
        ctx = MockContext()
        assert ctx is not None
        assert hasattr(ctx, "info")
        assert hasattr(ctx, "warning")
        assert hasattr(ctx, "error")

    def test_mock_context_methods(self):
        """Test MockContext methods work without errors."""
        ctx = MockContext()

        # Test logging methods don't raise exceptions
        ctx.info("test message")
        ctx.warning("test warning")
        ctx.error("test error")

        # Methods should be callable
        assert callable(ctx.info)
        assert callable(ctx.warning)
        assert callable(ctx.error)

    @patch("importlib.import_module")
    def test_is_fastmcp_available_false(self, mock_import):
        """Test fastmcp availability when import fails."""
        mock_import.side_effect = ImportError("No module named 'fastmcp'")

        # Reset module state
        import tools.fastmcp_compat as compat

        compat._fastmcp_available = None

        result = is_fastmcp_available()
        assert result is False

    def test_is_fastmcp_available_true(self):
        """Test fastmcp availability - currently always False due to RichHandler bug."""
        # Reset module state
        import tools.fastmcp_compat as compat

        compat._fastmcp_available = None

        result = is_fastmcp_available()
        # Currently always False due to fastmcp RichHandler compatibility issue
        assert result is False

    def test_get_fastmcp_context_returns_mock_when_unavailable(self):
        """Test get_fastmcp_context returns MockContext when fastmcp unavailable."""
        # Ensure fastmcp is marked as unavailable
        import tools.fastmcp_compat as compat

        compat._fastmcp_available = False
        compat._fastmcp_context = None

        ctx = get_fastmcp_context()
        assert isinstance(ctx, MockContext)

    @patch("tools.fastmcp_compat.is_fastmcp_available")
    def test_get_fastmcp_context_returns_mock_when_available_false(
        self, mock_available
    ):
        """Test get_fastmcp_context returns MockContext when fastmcp unavailable."""
        mock_available.return_value = False

        # Reset state
        import tools.fastmcp_compat as compat

        compat._fastmcp_context = None

        ctx = get_fastmcp_context()
        assert isinstance(ctx, MockContext)

    def test_get_fastmcp_context_singleton_behavior(self):
        """Test get_fastmcp_context implements singleton pattern."""
        # Reset state
        import tools.fastmcp_compat as compat

        compat._fastmcp_context = None

        ctx1 = get_fastmcp_context()
        ctx2 = get_fastmcp_context()

        assert ctx1 is ctx2

    def test_mock_context_info_method(self):
        """Test MockContext info method specifically."""
        ctx = MockContext()
        # Should not raise any exceptions
        ctx.info("Test info message")
        ctx.info("Another message")
        ctx.info("")  # Empty message

    def test_mock_context_warning_method(self):
        """Test MockContext warning method specifically."""
        ctx = MockContext()
        # Should not raise any exceptions
        ctx.warning("Test warning message")
        ctx.warning("Another warning")
        ctx.warning("")  # Empty message

    def test_mock_context_error_method(self):
        """Test MockContext error method specifically."""
        ctx = MockContext()
        # Should not raise any exceptions
        ctx.error("Test error message")
        ctx.error("Another error")
        ctx.error("")  # Empty message

    @patch("tools.fastmcp_compat.logging")
    def test_mock_context_uses_logging(self, mock_logging):
        """Test that MockContext uses logging internally."""
        ctx = MockContext()
        ctx.info("test message")
        ctx.warning("test warning")
        ctx.error("test error")

        # Verify logging calls were made
        mock_logging.info.assert_called_with("[MOCK CONTEXT] test message")
        mock_logging.warning.assert_called_with("[MOCK CONTEXT] test warning")
        mock_logging.error.assert_called_with("[MOCK CONTEXT] test error")
