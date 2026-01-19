"""
FastMCP Compatibility Layer
Isola problemas de compatibilidade com fastmcp/rich para evitar cascata de falhas.
"""

import logging

# Configure logging before any fastmcp imports
logging.basicConfig(level=logging.INFO)

# Global flag for fastmcp availability
_fastmcp_available = None
_fastmcp_context = None


def is_fastmcp_available() -> bool:
    """Check if fastmcp can be imported without issues."""
    global _fastmcp_available
    if _fastmcp_available is None:
        try:
            # FastMCP has a RichHandler compatibility bug in current version
            # For now, always treat as unavailable to avoid import issues
            _fastmcp_available = False
            logging.info(
                "FastMCP compatibility layer: treating as unavailable due to known RichHandler bug"
            )
        except Exception as e:
            _fastmcp_available = False
            logging.warning(f"FastMCP not available due to: {e}")
    return _fastmcp_available


class MockContext:
    """Mock context for when fastmcp is not available."""

    def info(self, msg: str):
        """Mock info logging."""
        logging.info(f"[MOCK CONTEXT] {msg}")

    def warning(self, msg: str):
        """Mock warning logging."""
        logging.warning(f"[MOCK CONTEXT] {msg}")

    def error(self, msg: str):
        """Mock error logging."""
        logging.error(f"[MOCK CONTEXT] {msg}")


def get_fastmcp_context():
    """Get fastmcp Context instance, or MockContext if unavailable."""
    global _fastmcp_context
    if _fastmcp_context is None:
        if is_fastmcp_available():
            try:
                import fastmcp

                Context = getattr(fastmcp, "Context")
                _fastmcp_context = Context()
            except Exception as e:
                logging.warning(f"Failed to create fastmcp Context: {e}")
                _fastmcp_context = MockContext()
        else:
            _fastmcp_context = MockContext()
    return _fastmcp_context
