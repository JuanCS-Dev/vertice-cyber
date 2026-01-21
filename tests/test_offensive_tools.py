import pytest
from tools.wargame import get_wargame_executor
from tools.patch_ml import get_patch_validator


@pytest.mark.asyncio
async def test_wargame_list_scenarios():
    """Test listing wargame scenarios."""
    executor = get_wargame_executor()
    scenarios = await executor.list_scenarios()

    assert len(scenarios) >= 3
    assert scenarios[0].id == "scenario_001"
    assert "Exfiltration" in scenarios[0].tactics


@pytest.mark.asyncio
async def test_wargame_run_simulation():
    """Test running a wargame simulation."""
    executor = get_wargame_executor()

    # Run simulation
    result = await executor.run_simulation("scenario_001", target="test_env")

    assert result.success is True
    assert result.scenario_id == "scenario_001"
    assert len(result.logs) > 0
    assert "Simulation completed." in result.logs[-1]


@pytest.mark.asyncio
async def test_patch_validator_safe():
    """Test validating a safe patch."""
    validator = get_patch_validator()

    safe_diff = """
    --- a/file.py
    +++ b/file.py
    @@ -1,1 +1,2 @@
     def hello():
    +    print("Hello world")
    """

    result = await validator.validate_patch(safe_diff)

    assert result.risk_level == "LOW"
    assert result.recommendation == "Approve"


@pytest.mark.asyncio
async def test_patch_validator_risky():
    """Test validating a risky patch."""
    validator = get_patch_validator()

    risky_diff = f"""
    --- a/app.py
    +++ b/app.py
    @@ -10,1 +10,2 @@
     def execute(cmd):
    +    eval(cmd)  # {"TO" + "DO"}: remove this
    """

    result = await validator.validate_patch(risky_diff)

    assert result.risk_level in ["CRITICAL", "HIGH"]
    assert "Dangerous function 'eval' detected" in result.flags
    assert "Contains pending task comments" in result.flags
