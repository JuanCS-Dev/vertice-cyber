"""
FastMCP Compatibility Layer
Isola problemas de compatibilidade com fastmcp/rich para evitar cascata de falhas.
"""

import logging
import sys
from typing import Any, Optional

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
            # Try to import fastmcp
            import fastmcp

            # Try to create a Context (this triggers the RichHandler bug)
            from fastmcp import Context

            ctx = Context()
            _fastmcp_available = True
        except Exception as e:
            _fastmcp_available = False
            logging.warning(f"FastMCP not available due to: {e}")
    return _fastmcp_available


def get_fastmcp_context():
    """Get FastMCP Context if available, otherwise return mock."""
    global _fastmcp_context
    if _fastmcp_context is None:
        if is_fastmcp_available():
            from fastmcp import Context

            _fastmcp_context = Context()
        else:
            # Return mock context
            _fastmcp_context = MockContext()
    return _fastmcp_context


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


# Safe import function
def safe_import_fastmcp():
    """Safely import fastmcp components."""
    if not is_fastmcp_available():
        return None, MockContext

    try:
        import fastmcp
        from fastmcp import Context

        return fastmcp, Context
    except Exception as e:
        logging.error(f"Failed to import fastmcp: {e}")
        return None, MockContext
