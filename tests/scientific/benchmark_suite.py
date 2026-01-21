
import asyncio
import time
import statistics
import json
import logging
import sys
import os
from dataclasses import dataclass, field
from typing import List, Callable
from datetime import datetime

# Adjust path to import Synapse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../tests/scientific/clients')))
try:
    from synapse import Synapse
except ImportError:
    # Fallback
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scientific/clients')))
    from synapse import Synapse

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] BENCHMARK: %(message)s",
    handlers=[
        logging.FileHandler("benchmark_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("benchmark")

@dataclass
class BenchmarkResult:
    agent_name: str
    test_name: str
    duration_ms: float
    success: bool
    ai_used: bool
    output_summary: str
    error: str = ""

@dataclass
class BenchmarkSummary:
    timestamp: str
    total_tests: int
    success_rate: float
    avg_latency_ms: float
    results: List[BenchmarkResult] = field(default_factory=list)

class VerticeBenchmark:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.client = Synapse(base_url)
        self.results = []

    async def run_visual_separator(self, title: str):
        print(f"\n{'='*70}")
        print(f"🧪 BENCHMARK: {title}")
        print(f"{'='*70}")

    async def measure(self, agent: str, test_name: str, func: Callable, *args) -> BenchmarkResult:
        """Measure execution of a single test case."""
        start = time.perf_counter()
        success = False
        error = ""
        output = ""
        ai_used = "ai_" in test_name.lower() or "llm" in test_name.lower()

        try:
            print(f"  ▶️  Running {agent}::{test_name}...", end=" ", flush=True)
            response = func(*args)
            if asyncio.iscoroutine(response):
                response = await response

            # Check Synapse/MCP response wrapper
            if isinstance(response, dict):
                if response.get('success', False) or ('error' not in response and response):
                     success = True
                     output = str(response.get('result', response))[:100] + "..."
                else:
                     error = response.get('error', 'Unknown error')
                     output = str(response)
            else:
                 success = True
                 output = str(response)[:100]

        except Exception as e:
            error = str(e)
            
        duration = (time.perf_counter() - start) * 1000
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} ({duration:.0f}ms)")
        if not success:
            print(f"      Layer 1 Error: {error[:200]}")

        # Try to detect if AI was truly active based on output (latency > 500ms usually hints at LLM)
        if duration > 500 and not ai_used:
             ai_used = True # Inferred

        return BenchmarkResult(
            agent_name=agent,
            test_name=test_name,
            duration_ms=duration,
            success=success,
            ai_used=ai_used,
            output_summary=output,
            error=error
        )

    async def run_suite(self):
        await self.run_visual_separator("INITIALIZING AGENT SWARM")
        
        # 1. THREAT PROPHET
        await self.run_visual_separator("THREAT PROPHET (Integrity & Prediction)")
        self.results.append(await self.measure(
            "Threat Prophet", "Analyze IP (Basic)",
            self.client.execute, "threat_analyze", {"target": "192.168.1.5", "include_predictions": False}
        ))
        
        # 2. OSINT HUNTER
        await self.run_visual_separator("OSINT HUNTER (Intelligence Gathering)")
        self.results.append(await self.measure(
            "OSINT Hunter", "Domain Investigate",
            self.client.execute, "osint_investigate", {"target": "example.com", "depth": "shallow"}
        ))
        self.results.append(await self.measure(
            "OSINT Hunter", "Breach Check (Mock)",
            self.client.execute, "osint_breach_check", {"email": "test@example.com"}
        ))

        # 3. COMPLIANCE GUARDIAN
        await self.run_visual_separator("COMPLIANCE GUARDIAN (Regulatory Check)")
        self.results.append(await self.measure(
            "Compliance Guardian", "GDPR Assessment",
            self.client.execute, "compliance_assess", {"target": "database_01", "framework": "gdpr"}
        ))

        # 4. ETHICAL MAGISTRATE
        await self.run_visual_separator("ETHICAL MAGISTRATE (Constitutional Audit)")
        self.results.append(await self.measure(
            "Magistrate", "Validate Safe Action",
            self.client.execute, "ethical_validate", {"action": "Update system logs", "context": {}}
        ))
        self.results.append(await self.measure(
            "Magistrate", "Block Destructive Action",
            self.client.execute, "ethical_validate", {"action": "Delete production database", "context": {}}
        ))

        # 5. PATCH VALIDATOR ML
        await self.run_visual_separator("PATCH VALIDATOR (Machine Learning)")
        vuln_code = 'query = "SELECT * FROM users WHERE id=" + user_input'
        self.results.append(await self.measure(
            "PatchML", "Detect SQL Injection",
            self.client.execute, "patch_validate", {"diff_content": vuln_code, "language": "python"}
        ))

        # 6. WARGAME EXECUTOR
        await self.run_visual_separator("WARGAME EXECUTOR (Offensive Simulation)")
        scenarios = self.client.execute("wargame_list_scenarios", {})
        if scenarios.get('success') and scenarios.get('result'):
            pk = scenarios['result'][0]['id']
            self.results.append(await self.measure(
                "Wargame", f"Run Scenario {pk} (Dry Run)",
                self.client.execute, "wargame_run_simulation", {"scenario_id": pk, "target": "local"}
            ))

        # 7. AI AGENTS (Real LLM Interfaces)
        await self.run_visual_separator("VERTEX AI POWERED AGENTS (Real LLM)")
        # Note: These depend on Vertex AI credentials. 
        self.results.append(await self.measure(
            "AI Threat", "LLM Threat Analysis",
            self.client.execute, "ai_threat_analysis", 
            {"target": "10.0.0.5", "context_data": {"logs": "Failed login attempts detected"}}
        ))

    def generate_report(self):
        total = len(self.results)
        success = len([r for r in self.results if r.success])
        rate = (success / total * 100) if total > 0 else 0
        avg_lat = statistics.mean([r.duration_ms for r in self.results]) if total > 0 else 0
        
        print("\n\n")
        print("████████████████████████████████████████████████████████")
        print("██  SCIENTIFIC BENCHMARK REPORT: VERTICE CYBER v2.0   ██")
        print("████████████████████████████████████████████████████████")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Total Tests: {total}")
        print(f"Success Rate: {rate:.1f}%")
        print(f"Avg Latency:  {avg_lat:.2f}ms")
        print("-" * 60)
        print(f"{'AGENT':<20} | {'TEST':<25} | {'STATUS':<8} | {'LATENCY':<10}")
        print("-" * 60)
        
        for r in self.results:
            status = "PASS" if r.success else "FAIL"
            print(f"{r.agent_name[:20]:<20} | {r.test_name[:25]:<25} | {status:<8} | {r.duration_ms:.0f}ms")
            if not r.success:
                print(f"   ↳ Error: {r.error}")

        # Save artifact
        with open("benchmark_results.json", "w") as f:
            json.dump([r.__dict__ for r in self.results], f, indent=2)

if __name__ == "__main__":
    benchmark = VerticeBenchmark()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(benchmark.run_suite())
    benchmark.generate_report()
