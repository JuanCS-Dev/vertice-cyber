"""
Test Compliance Module Backward Compatibility
Testes para garantir que os imports antigos ainda funcionam.
"""



def test_compliance_module_imports():
    """Test that old compliance module imports still work."""
    from tools.compliance import (
        ComplianceFramework,
        ComplianceStatus,
        ComplianceRequirement,
        ComplianceCheck,
        ComplianceAssessment,
        get_compliance_api,
        get_compliance_guardian,
        compliance_assess,
        compliance_report,
        compliance_check,
    )

    # Test that all expected items are imported
    assert ComplianceFramework is not None
    assert ComplianceStatus is not None
    assert ComplianceRequirement is not None
    assert ComplianceCheck is not None
    assert ComplianceAssessment is not None
    assert get_compliance_api is not None
    assert get_compliance_guardian is not None
    assert compliance_assess is not None
    assert compliance_report is not None
    assert compliance_check is not None


def test_compliance_module_all():
    """Test that __all__ contains expected items."""
    from tools import compliance

    expected_items = [
        "ComplianceFramework",
        "ComplianceStatus",
        "ComplianceRequirement",
        "ComplianceCheck",
        "ComplianceAssessment",
        "get_compliance_api",
        "get_compliance_guardian",
        "compliance_assess",
        "compliance_report",
        "compliance_check",
    ]

    assert hasattr(compliance, "__all__")
    assert compliance.__all__ == expected_items
