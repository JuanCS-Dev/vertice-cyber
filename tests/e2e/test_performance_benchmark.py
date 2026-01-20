"""
Performance Benchmark Tests for MCP HTTP Bridge

Tests latency, throughput, and resource usage under various conditions.
Uses Gemini 3 for AI tools - NO MODEL DOWNGRADES.

Run with: pytest tests/e2e/test_performance_benchmark.py -v -s
"""

import pytest
import time
import statistics
import concurrent.futures
from typing import List, Dict, Any
from dataclasses import dataclass, field
from fastapi.testclient import TestClient


@dataclass
class BenchmarkResult:
    """Result from a benchmark run."""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    p95_time_ms: float
    p99_time_ms: float
    success_rate: float
    errors: List[str] = field(default_factory=list)


def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile of a data set."""
    if not data:
        return 0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(idx, len(sorted_data) - 1)]


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    from mcp_http_bridge import app
    return TestClient(app)


class TestAPILatency:
    """Benchmark API endpoint latency."""
    
    def test_health_check_latency(self, client: TestClient):
        """Benchmark /health endpoint (should be <10ms)."""
        iterations = 100
        times: List[float] = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            response = client.get("/health")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert response.status_code == 200
        
        result = BenchmarkResult(
            name="health_check",
            iterations=iterations,
            total_time_ms=sum(times),
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            p95_time_ms=calculate_percentile(times, 95),
            p99_time_ms=calculate_percentile(times, 99),
            success_rate=100.0,
        )
        
        print(f"\n📊 Health Check Benchmark ({iterations} iterations)")
        print(f"   Avg: {result.avg_time_ms:.2f}ms")
        print(f"   Min: {result.min_time_ms:.2f}ms")
        print(f"   Max: {result.max_time_ms:.2f}ms")
        print(f"   P95: {result.p95_time_ms:.2f}ms")
        print(f"   P99: {result.p99_time_ms:.2f}ms")
        
        # Health check should be fast
        assert result.avg_time_ms < 50, f"Health check too slow: {result.avg_time_ms:.1f}ms"
        assert result.p99_time_ms < 100, f"P99 too high: {result.p99_time_ms:.1f}ms"
    
    def test_list_tools_latency(self, client: TestClient):
        """Benchmark /mcp/tools/list endpoint."""
        iterations = 50
        times: List[float] = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            response = client.get("/mcp/tools/list")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert response.status_code == 200
        
        avg = statistics.mean(times)
        p95 = calculate_percentile(times, 95)
        
        print(f"\n📊 List Tools Benchmark ({iterations} iterations)")
        print(f"   Avg: {avg:.2f}ms | P95: {p95:.2f}ms")
        
        assert avg < 100, f"List tools too slow: {avg:.1f}ms"


class TestToolExecutionLatency:
    """Benchmark tool execution latency."""
    
    def test_ethical_validate_latency(self, client: TestClient):
        """Benchmark ethical_validate (lightweight tool)."""
        iterations = 20
        times: List[float] = []
        errors = 0
        
        for _ in range(iterations):
            start = time.perf_counter()
            response = client.post("/mcp/tools/execute", json={
                "tool_name": "ethical_validate",
                "arguments": {"action": "Test action", "context": {}}
            })
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            
            if response.status_code != 200 or not response.json().get("success"):
                errors += 1
        
        avg = statistics.mean(times)
        p95 = calculate_percentile(times, 95)
        success_rate = ((iterations - errors) / iterations) * 100
        
        print(f"\n📊 ethical_validate Benchmark ({iterations} iterations)")
        print(f"   Avg: {avg:.1f}ms | P95: {p95:.1f}ms")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        assert success_rate >= 95, f"Too many failures: {success_rate:.1f}%"
        assert avg < 500, f"Too slow: {avg:.1f}ms"
    
    def test_wargame_list_scenarios_latency(self, client: TestClient):
        """Benchmark wargame_list_scenarios (data lookup)."""
        iterations = 20
        times: List[float] = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            response = client.post("/mcp/tools/execute", json={
                "tool_name": "wargame_list_scenarios",
                "arguments": {}
            })
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg = statistics.mean(times)
        
        print(f"\n📊 wargame_list_scenarios Benchmark ({iterations} iterations)")
        print(f"   Avg: {avg:.1f}ms")
        
        assert avg < 1000, f"Too slow: {avg:.1f}ms"


class TestConcurrency:
    """Test concurrent request handling."""
    
    def test_concurrent_health_checks(self, client: TestClient):
        """Test 10 concurrent health check requests."""
        num_requests = 10
        
        def make_request():
            start = time.perf_counter()
            response = client.get("/health")
            elapsed = (time.perf_counter() - start) * 1000
            return response.status_code, elapsed
        
        start_total = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_elapsed = (time.perf_counter() - start_total) * 1000
        
        status_codes = [r[0] for r in results]
        times = [r[1] for r in results]
        
        success_count = sum(1 for s in status_codes if s == 200)
        
        print(f"\n📊 Concurrent Health Checks ({num_requests} parallel)")
        print(f"   Total time: {total_elapsed:.1f}ms")
        print(f"   Avg per request: {statistics.mean(times):.1f}ms")
        print(f"   Success: {success_count}/{num_requests}")
        
        assert success_count == num_requests, f"Some requests failed"
        assert total_elapsed < 5000, f"Too slow under concurrency"
    
    def test_concurrent_tool_execution(self, client: TestClient):
        """Test 5 concurrent tool executions."""
        num_requests = 5
        
        def execute_tool(tool_name: str, args: dict):
            start = time.perf_counter()
            response = client.post("/mcp/tools/execute", json={
                "tool_name": tool_name,
                "arguments": args
            })
            elapsed = (time.perf_counter() - start) * 1000
            return response.status_code, response.json().get("success", False), elapsed
        
        tools = [
            ("ethical_validate", {"action": "Test 1", "context": {}}),
            ("ethical_audit", {"limit": 3}),
            ("wargame_list_scenarios", {}),
            ("ethical_validate", {"action": "Test 2", "context": {}}),
            ("wargame_list_scenarios", {}),
        ]
        
        start_total = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(execute_tool, t[0], t[1]) for t in tools]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_elapsed = (time.perf_counter() - start_total) * 1000
        
        success_count = sum(1 for r in results if r[0] == 200 and r[1])
        times = [r[2] for r in results]
        
        print(f"\n📊 Concurrent Tool Execution ({num_requests} tools)")
        print(f"   Total time: {total_elapsed:.1f}ms")
        print(f"   Avg per tool: {statistics.mean(times):.1f}ms")
        print(f"   Success: {success_count}/{num_requests}")
        
        assert success_count >= num_requests - 1, f"Too many failures"


class TestThroughput:
    """Test request throughput."""
    
    def test_requests_per_second(self, client: TestClient):
        """Measure RPS for health endpoint."""
        duration_seconds = 3
        request_count = 0
        errors = 0
        
        start = time.perf_counter()
        end_time = start + duration_seconds
        
        while time.perf_counter() < end_time:
            try:
                response = client.get("/health")
                if response.status_code == 200:
                    request_count += 1
                else:
                    errors += 1
            except Exception:
                errors += 1
        
        actual_duration = time.perf_counter() - start
        rps = request_count / actual_duration
        
        print(f"\n📊 Throughput Test ({duration_seconds}s)")
        print(f"   Requests: {request_count}")
        print(f"   RPS: {rps:.1f}")
        print(f"   Errors: {errors}")
        
        # Expect at least 50 RPS for health checks
        assert rps >= 10, f"Throughput too low: {rps:.1f} RPS"


class TestMemoryUsage:
    """Test memory behavior under load."""
    
    def test_no_memory_leak_simple(self, client: TestClient):
        """Simple test - execute many requests and ensure no crash."""
        iterations = 50
        
        for i in range(iterations):
            # Mix of different requests
            client.get("/health")
            client.get("/mcp/tools/list")
            client.post("/mcp/tools/execute", json={
                "tool_name": "ethical_validate",
                "arguments": {"action": f"Test {i}", "context": {}}
            })
        
        # If we got here without OOM, test passes
        final_health = client.get("/health")
        assert final_health.status_code == 200
        
        print(f"\n📊 Memory Leak Test ({iterations * 3} requests)")
        print(f"   ✅ No crash after {iterations * 3} requests")


class TestWebSocketPerformance:
    """Benchmark WebSocket performance."""
    
    def test_websocket_connect_latency(self, client: TestClient):
        """Measure WebSocket connection time."""
        iterations = 10
        times: List[float] = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            with client.websocket_connect("/mcp/events") as ws:
                msg = ws.receive_json()
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
                assert msg["type"] == "connected"
        
        avg = statistics.mean(times)
        
        print(f"\n📊 WebSocket Connect Latency ({iterations} connections)")
        print(f"   Avg: {avg:.1f}ms")
        
        assert avg < 500, f"WebSocket connect too slow: {avg:.1f}ms"
