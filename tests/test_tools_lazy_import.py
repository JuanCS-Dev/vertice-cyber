"""
Test Tools Package Lazy Imports
Testes para a funcionalidade de lazy import do pacote tools.
"""

import pytest


def test_lazy_import_threat():
    """Test lazy import of threat module."""
    from tools import get_threat_prophet

    # Should import successfully
    assert get_threat_prophet is not None
    assert callable(get_threat_prophet)


def test_lazy_import_osint():
    """Test lazy import of osint module."""
    from tools import get_osint_hunter

    # Should import successfully
    assert get_osint_hunter is not None
    assert callable(get_osint_hunter)


def test_lazy_import_compliance():
    """Test lazy import of compliance module."""
    from tools import get_compliance_guardian

    # Should import successfully
    assert get_compliance_guardian is not None
    assert callable(get_compliance_guardian)


def test_lazy_import_nonexistent():
    """Test lazy import of nonexistent module."""
    from tools import __getattr__

    # Should raise AttributeError for nonexistent items
    with pytest.raises(AttributeError, match="has no attribute 'nonexistent_function'"):
        __getattr__("nonexistent_function")
