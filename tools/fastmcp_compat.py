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
            # Try to import fastmcp components (this triggers the RichHandler bug if present)
            import fastmcp  # noqa: F401
            from fastmcp import Context  # noqa: F401

            _fastmcp_available = True
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
