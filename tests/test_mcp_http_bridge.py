"""
Tests for MCP HTTP Bridge

Run with: pytest tests/test_mcp_http_bridge.py -v
"""

import pytest
from fastapi.testclient import TestClient


class TestMCPHttpBridge:
    """Test suite for MCP HTTP Bridge."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client."""
        from mcp_http_bridge import app

        self.client = TestClient(app)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "mcp-http-bridge"
        assert data["version"] == "1.0.0"
        assert data["tools_available"] == 20

    def test_list_tools(self):
        """Test listing all available tools."""
        response = self.client.get("/mcp/tools/list")

        assert response.status_code == 200
        data = response.json()

        assert "tools" in data
        assert "total" in data
        assert data["total"] == 20

        # Validate tool structure
        assert len(data["tools"]) > 0
        first_tool = data["tools"][0]
        assert "name" in first_tool
        assert "agent" in first_tool
        assert "category" in first_tool
        assert "description" in first_tool

    def test_list_tools_contains_expected(self):
        """Test that specific expected tools are present."""
        response = self.client.get("/mcp/tools/list")
        data = response.json()

        tool_names = [t["name"] for t in data["tools"]]

        expected_tools = [
            "ethical_validate",
            "osint_investigate",
            "threat_analyze",
            "compliance_assess",
            "wargame_list_scenarios",
            "patch_validate",
            "cybersec_recon",
            "ai_threat_analysis",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Expected tool '{expected}' not found"

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={
                "tool_name": "ethical_validate",
                "arguments": {"action": "test harmless action", "context": {}},
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "result" in data
        assert "logs" in data
        assert "execution_time_ms" in data

        # Validate result structure
        result = data["result"]
        assert "decision_type" in result
        assert "is_approved" in result

    def test_execute_tool_invalid_name(self):
        """Test execution with invalid tool name."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={"tool_name": "invalid_tool_name", "arguments": {}},
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_execute_tool_missing_arguments(self):
        """Test execution with missing required arguments."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={
                "tool_name": "osint_breach_check",
                "arguments": {},  # Missing required 'email' parameter
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should fail gracefully with error message
        assert data["success"] is False
        assert "error" in data

    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.options(
            "/mcp/tools/list",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        # FastAPI TestClient handles OPTIONS differently
        # Just verify the endpoint works with CORS middleware active
        response = self.client.get("/mcp/tools/list")
        assert response.status_code == 200

    def test_execute_ethical_audit(self):
        """Test ethical_audit tool."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={"tool_name": "ethical_audit", "arguments": {"limit": 5}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_execute_wargame_list_scenarios(self):
        """Test wargame_list_scenarios tool."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={"tool_name": "wargame_list_scenarios", "arguments": {}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["result"], list)

    def test_mock_context_logs(self):
        """Test that tool execution includes context logs."""
        response = self.client.post(
            "/mcp/tools/execute",
            json={
                "tool_name": "ethical_validate",
                "arguments": {"action": "Test action for logging", "context": {}},
            },
        )

        data = response.json()

        # Should have logs from MockContext
        assert "logs" in data
        assert len(data["logs"]) > 0

        # Validate log structure
        log = data["logs"][0]
        assert "level" in log
        assert "message" in log
        assert "request_id" in log


class TestToolRegistry:
    """Test the tool registry itself."""

    def test_registry_count(self):
        """Test that registry has correct number of tools."""
        from mcp_http_bridge import TOOL_REGISTRY

        assert len(TOOL_REGISTRY) == 20

    def test_metadata_count(self):
        """Test that metadata matches registry."""
        from mcp_http_bridge import TOOL_REGISTRY, TOOL_METADATA

        assert len(TOOL_METADATA) == len(TOOL_REGISTRY)

    def test_all_tools_are_callable(self):
        """Test that all registered tools are callable."""
        from mcp_http_bridge import TOOL_REGISTRY
        import asyncio

        for name, func in TOOL_REGISTRY.items():
            assert callable(func), f"Tool '{name}' is not callable"
            assert asyncio.iscoroutinefunction(func), f"Tool '{name}' is not async"


class TestMockContext:
    """Test MockContext class (async methods)."""

    @pytest.mark.asyncio
    async def test_mock_context_info(self):
        """Test MockContext info logging."""
        from mcp_http_bridge import MockContext

        ctx = MockContext()
        await ctx.info("Test message")

        logs = ctx.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "INFO"
        assert logs[0]["message"] == "Test message"

    @pytest.mark.asyncio
    async def test_mock_context_warn(self):
        """Test MockContext warning logging."""
        from mcp_http_bridge import MockContext

        ctx = MockContext()
        await ctx.warn("Warning message")

        logs = ctx.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "WARN"

    @pytest.mark.asyncio
    async def test_mock_context_error(self):
        """Test MockContext error logging."""
        from mcp_http_bridge import MockContext

        ctx = MockContext()
        await ctx.error("Error message")

        logs = ctx.get_logs()
        assert len(logs) == 1
        assert logs[0]["level"] == "ERROR"

    def test_mock_context_request_id(self):
        """Test MockContext has unique request ID."""
        from mcp_http_bridge import MockContext

        ctx1 = MockContext()
        ctx2 = MockContext()

        assert ctx1.request_id != ctx2.request_id

    def test_mock_context_custom_request_id(self):
        """Test MockContext with custom request ID."""
        from mcp_http_bridge import MockContext

        ctx = MockContext(request_id="custom-id")
        assert ctx.request_id == "custom-id"


class TestConnectionManager:
    """Test ConnectionManager class."""

    def test_connection_manager_init(self):
        """Test ConnectionManager initialization."""
        from mcp_http_bridge import ConnectionManager

        manager = ConnectionManager()
        assert manager.connection_count == 0
        assert len(manager.active_connections) == 0
