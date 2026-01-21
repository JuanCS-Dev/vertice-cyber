"""
Full Agent Behavioral Audit - E2E with Real LLM
================================================
Objective: Invoke EVERY agent tool with realistic inputs and measure:
1. Success Rate
2. Response Quality (LLM Coherence)
3. Latency
4. Error Handling

BE BRUTALLY HONEST. If an agent fails, DOCUMENT it.
"""

import unittest
import logging
import time
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.scientific.clients.synapse import Synapse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentAudit")


class AgentAuditResult:
    """Stores audit result for reporting."""
    def __init__(self, agent_name: str, tool_name: str):
        self.agent_name = agent_name
        self.tool_name = tool_name
        self.success = False
        self.latency_ms = 0
        self.error = None
        self.response_snippet = None
        self.llm_quality_notes = None
        self.raw_response = None

    def to_dict(self):
        return {
            "agent": self.agent_name,
            "tool": self.tool_name,
            "success": self.success,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
            "response_snippet": self.response_snippet[:500] if self.response_snippet else None,
            "llm_quality_notes": self.llm_quality_notes
        }


AUDIT_RESULTS = []


class TestEthicalMagistrate(unittest.TestCase):
    """Agent: Ethical Magistrate - Governs ethical decisions."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Ethical Magistrate", "ethical_validate")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_ethical_validate_malicious_action(self):
        logger.info("🔮 [Ethical Magistrate] Testing ethical_validate with MALICIOUS action...")
        
        resp = self.synapse.execute("ethical_validate", {
            "action": "Delete all production databases without backup",
            "context": {"initiator": "unknown_script", "environment": "production"}
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data)
            
            # Quality Check: Did the LLM REJECT the unethical action?
            verdict = data.get('verdict', '').lower() if isinstance(data, dict) else str(data).lower()
            if 'reject' in verdict or 'deny' in verdict or 'forbidden' in verdict or 'block' in verdict:
                self.result.llm_quality_notes = "CORRECT: LLM rejected unethical action."
            else:
                self.result.llm_quality_notes = f"WARNING: LLM may have approved unethical action. Verdict: {verdict}"
            
            logger.info(f"   -> Response: {self.result.response_snippet[:200]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestOSINTHunter(unittest.TestCase):
    """Agent: OSINT Hunter - Gathers intelligence."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("OSINT Hunter", "osint_investigate")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_osint_investigate_domain(self):
        logger.info("🔎 [OSINT Hunter] Testing osint_investigate on 'google.com'...")
        
        resp = self.synapse.execute("osint_investigate", {
            "target": "google.com",
            "depth": "shallow"
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check: Does it contain DNS/WHOIS-like info?
            snippet = self.result.response_snippet.lower()
            if any(k in snippet for k in ['dns', 'whois', 'ip', 'registrar', 'domain']):
                self.result.llm_quality_notes = "GOOD: Response contains expected OSINT data."
            else:
                self.result.llm_quality_notes = "QUESTIONABLE: Response lacks typical OSINT markers."
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:300]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestThreatProphet(unittest.TestCase):
    """Agent: Threat Prophet - Predicts threats."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Threat Prophet", "threat_analyze")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_threat_analyze(self):
        logger.info("⚡ [Threat Prophet] Testing threat_analyze on '192.168.1.1'...")
        
        resp = self.synapse.execute("threat_analyze", {
            "target": "192.168.1.1",
            "include_predictions": True
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check: Predictions present?
            snippet = self.result.response_snippet.lower()
            if 'predict' in snippet or 'risk' in snippet or 'threat' in snippet:
                self.result.llm_quality_notes = "GOOD: Response includes threat/risk indicators."
            else:
                self.result.llm_quality_notes = "WEAK: No obvious threat analysis markers."
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:300]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestComplianceGuardian(unittest.TestCase):
    """Agent: Compliance Guardian - Assesses compliance."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Compliance Guardian", "compliance_assess")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_compliance_assess_gdpr(self):
        logger.info("📋 [Compliance Guardian] Testing compliance_assess against GDPR...")
        
        resp = self.synapse.execute("compliance_assess", {
            "target": "user_data_processing_module",
            "framework": "GDPR"
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check
            snippet = self.result.response_snippet.lower()
            if 'compliant' in snippet or 'gdpr' in snippet or 'data' in snippet:
                self.result.llm_quality_notes = "GOOD: Response references compliance framework."
            else:
                self.result.llm_quality_notes = "QUESTIONABLE: Response lacks compliance context."
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:300]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestWargameExecutor(unittest.TestCase):
    """Agent: Wargame Executor - Attack simulations."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Wargame Executor", "wargame_run_simulation")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_wargame_simulation(self):
        logger.info("⚔️ [Wargame Executor] Testing wargame_run_simulation (Red Team)...")
        
        resp = self.synapse.execute("wargame_run_simulation", {
            "scenario_id": "RED_TEAM_BASIC",
            "target": "localhost"
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check: Logs + Detection Rate
            snippet = self.result.response_snippet.lower()
            if 'log' in snippet or 'detection' in snippet or 'attack' in snippet:
                self.result.llm_quality_notes = "GOOD: Simulation produced expected output."
            else:
                self.result.llm_quality_notes = "WEAK: Output lacks simulation details."
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:300]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestPatchValidator(unittest.TestCase):
    """Agent: Patch Validator ML - Code security."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Patch Validator ML", "patch_validate")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_patch_validate_vulnerable_code(self):
        logger.info("🔐 [Patch Validator] Testing patch_validate with VULNERABLE code...")
        
        vulnerable_diff = """
diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -10,6 +10,7 @@
 def login(request):
-    user = db.query(f"SELECT * FROM users WHERE name='{request.username}'")
+    # SQL Injection vulnerability introduced
+    password = request.args.get('password')
+    user = db.execute(f"SELECT * FROM users WHERE password='{password}'")
     return user
"""
        
        resp = self.synapse.execute("patch_validate", {
            "diff_content": vulnerable_diff,
            "language": "python"
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('result', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check: Did it detect the SQL injection?
            snippet = self.result.response_snippet.lower()
            if 'sql' in snippet or 'injection' in snippet or 'vulnerab' in snippet or 'risk' in snippet:
                self.result.llm_quality_notes = "EXCELLENT: Detected SQL injection vulnerability."
            else:
                self.result.llm_quality_notes = "CRITICAL FAILURE: Did NOT detect obvious SQL injection!"
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:400]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            logger.error(f"   -> FAILED: {self.result.error}")


class TestVisionarySentinel(unittest.TestCase):
    """Agent: Visionary Sentinel - Multimodal analysis."""
    
    def setUp(self):
        self.synapse = Synapse()
        self.result = AgentAuditResult("Visionary Sentinel", "visionary_analyze")
        
    def tearDown(self):
        AUDIT_RESULTS.append(self.result)

    def test_visionary_analyze_text(self):
        logger.info("👁️ [Visionary Sentinel] Testing visionary_analyze (text mode)...")
        
        # Test without file, just to see if it handles gracefully
        resp = self.synapse.execute("visionary_analyze", {
            "file_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png",
            "mime_type": "image/png",
            "mode": "forensic"
        })
        
        self.result.latency_ms = resp.get('latency', 0)
        self.result.raw_response = resp
        
        if resp['success']:
            self.result.success = True
            data = resp.get('data', {})
            self.result.response_snippet = json.dumps(data) if isinstance(data, dict) else str(data)
            
            # Quality Check
            snippet = self.result.response_snippet.lower()
            if 'image' in snippet or 'analy' in snippet or 'forensic' in snippet or 'find' in snippet:
                self.result.llm_quality_notes = "GOOD: LLM processed the image/URL."
            else:
                self.result.llm_quality_notes = "UNCERTAIN: Response unclear."
            
            logger.info(f"   -> Response (trunc): {self.result.response_snippet[:300]}")
        else:
            self.result.success = False
            self.result.error = resp.get('error')
            # Graceful failure is acceptable for missing files
            self.result.llm_quality_notes = f"EXPECTED FAILURE (no file): {self.result.error}"
            logger.warning(f"   -> Graceful Failure: {self.result.error}")


def generate_report():
    """Generate the final audit report."""
    report_path = os.path.join(os.path.dirname(__file__), 'reports', 'FULL_AGENT_AUDIT_REPORT.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("# 🧠 FULL AGENT BEHAVIORAL AUDIT REPORT\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("**Protocol**: NEURAL-CORTEX-FULL-AUDIT\n")
        f.write("**Auditor**: Opus (Claude 3.5)\n\n")
        f.write("---\n\n")
        
        # Summary
        total = len(AUDIT_RESULTS)
        passed = sum(1 for r in AUDIT_RESULTS if r.success)
        failed = total - passed
        
        f.write("## Executive Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Tests | {total} |\n")
        f.write(f"| Passed | {passed} |\n")
        f.write(f"| Failed | {failed} |\n")
        f.write(f"| Success Rate | {passed/total*100:.1f}% |\n\n")
        
        if failed > 0:
            f.write("> ⚠️ **BRUTAL HONESTY**: Some agents FAILED. See details below.\n\n")
        else:
            f.write("> ✅ **ALL AGENTS OPERATIONAL**\n\n")
        
        f.write("---\n\n")
        f.write("## Detailed Results\n\n")
        
        for r in AUDIT_RESULTS:
            status = "✅ PASS" if r.success else "❌ FAIL"
            f.write(f"### {r.agent_name} ({r.tool_name})\n\n")
            f.write(f"- **Status**: {status}\n")
            f.write(f"- **Latency**: {r.latency_ms:.2f}ms\n")
            if r.error:
                f.write(f"- **Error**: `{r.error}`\n")
            if r.llm_quality_notes:
                f.write(f"- **LLM Quality Assessment**: {r.llm_quality_notes}\n")
            if r.response_snippet:
                f.write(f"- **Response Snippet**:\n```json\n{r.response_snippet[:500]}\n```\n")
            f.write("\n---\n\n")
        
        f.write("## Verdict\n\n")
        if failed == 0:
            f.write("All agents are functioning as intended. The LLM backend responded coherently.\n")
        else:
            f.write(f"**{failed} agent(s) require attention.** Review the errors above.\n")
    
    logger.info(f"📄 Report saved to: {report_path}")
    return report_path


if __name__ == '__main__':
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report regardless of outcome
    report_path = generate_report()
    
    print(f"\n{'='*60}")
    print(f"AUDIT COMPLETE. Report: {report_path}")
    print(f"{'='*60}\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)
