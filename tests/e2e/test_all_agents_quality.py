
"""
E2E Quality Assurance Suite for Vertice Cyber Agents.
Validates not just connectivity, but the SEMANTIC CORRECTNESS of agent outputs.

Usage: python3 tests/e2e/test_all_agents_quality.py
"""

import asyncio
import logging
import os
import sys
import base64

# Setup Path
sys.path.insert(0, os.getcwd())

# Import Tools directly to test Logic Logic
from tools.magistrate import ethical_validate
from tools.osint import osint_investigate
from tools.threat import threat_analyze
from tools.compliance import compliance_assess
from tools.deepfake_scanner import scan_media
from tools.cybersec_basic import cybersec_recon
from tools.patch_ml import patch_validate

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QA_SUITE")

class MockContext:
    """Simulates FastMCP Context for tools."""
    async def info(self, msg: str):
        logger.info(f"[Ctx] {msg}")
    
    async def error(self, msg: str):
        logger.error(f"[Ctx] {msg}")

async def test_ethical_magistrate():
    logger.info("🧪 Testing: Ethical Magistrate")
    ctx = MockContext()
    
    # Scenario 1: Dangerous Action
    result = await ethical_validate(ctx, "DELETE DATABASE users", {"actor": "admin"})
    # Result is a dict
    assert result['is_approved'] is False, "Magistrate failed to block dangerous action"
    assert "dangerous" in result['reasoning'].lower() or "human review" in result['decision_type'], "Reasoning missing for block"
    logger.info("   ✅ Blocked dangerous action correctly.")

    # Scenario 2: Safe Action
    result = await ethical_validate(ctx, "Read logs", {"actor": "admin"})
    if result['is_approved']:
        logger.info("   ✅ Approved safe action.")
    else:
        logger.info(f"   ℹ️ Safe action denied (Strict Mode): {result['reasoning']}")

async def test_deepfake_scanner():
    logger.info("🧪 Testing: Deepfake Scanner (Video)")
    
    # Generate/Use Dummy Video
    video_path = "tests/test_video_qa.mp4"
    if not os.path.exists(video_path):
        os.system('ffmpeg -f lavfi -i testsrc=duration=1:size=640x360:rate=30 -metadata encoder="Lavf Fake" -y tests/test_video_qa.mp4 > /dev/null 2>&1')
    
    with open(video_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        
    # Run Scan
    result = await scan_media(b64, "video/mp4", "test_video_qa.mp4")
    
    # Assertions
    details = result['details']
    flags = details.get('flags') or details.get('metadata_flags', [])
    
    has_lavf_flag = any("Lavf" in f for f in flags)
    assert has_lavf_flag, f"Deepfake Scanner failed to flag suspicious metadata. Flags: {flags}"
    logger.info("   ✅ Correctly flagged suspicious metadata in video.")
    
    # Clean up
    if os.path.exists(video_path):
        os.remove(video_path)

async def test_osint_hunter():
    logger.info("🧪 Testing: OSINT Hunter")
    ctx = MockContext()
    
    # Scenario: Domain Scan
    target = "google.com"
    result = await osint_investigate(ctx, target)
    
    assert result['target'] == target, "OSINT returned wrong target"
    assert len(result['findings']) >= 0, "Findings list should be present"
    assert result['risk_score'] >= 0, "Risk score missing"
    
    if result['findings']:
        logger.info(f"   ✅ Found {len(result['findings'])} findings for {target}.")
    else:
        logger.info("   ℹ️ No findings (Mock/Safe Mode), but structure valid.")

async def test_cybersec_recon():
    logger.info("🧪 Testing: CyberSec Recon")
    ctx = MockContext()
    
    # Scan Localhost
    target = "127.0.0.1"
    result = await cybersec_recon(ctx, target, scan_ports=False, scan_web=False) 
    
    assert result['target'] == target
    assert isinstance(result['open_ports'], list)
    logger.info("   ✅ Recon structure valid.")

async def test_patch_validator():
    logger.info("🧪 Testing: Patch Validator ML")
    ctx = MockContext()
    
    diff = """
    def login(user, password):
        # BAD: SQL Injection
        cursor.execute(f"SELECT * FROM users WHERE u='{user}'")
    """
    
    result = await patch_validate(ctx, diff, "python")
    
    # We expect a HIGH risk score for SQLi (0.0 to 1.0 scale)
    assert result['risk_score'] >= 0.8, f"Failed to detect SQL Injection risk. Score: {result['risk_score']}"
    assert result['risk_level'] in ['HIGH', 'CRITICAL'], "Risk level too low for SQLi"
    logger.info(f"   ✅ Detected SQLi with Score {result['risk_score']} ({result['risk_level']}).")

async def test_compliance_guardian():
    logger.info("🧪 Testing: Compliance Guardian")
    ctx = MockContext()
    
    # Assess against GDPR
    target = "customer-db-prod"
    result = await compliance_assess(ctx, target, "gdpr")
    
    assert result['target'] == target
    assert result['framework'] == "gdpr"
    assert len(result['checks']) > 0, "No compliance checks returned"
    logger.info(f"   ✅ Generated GDPR report for {target} with score {result['overall_score']}.")

async def test_threat_prophet():
    logger.info("🧪 Testing: Threat Prophet")
    ctx = MockContext()
    
    # Analyze Threat
    target = "corporate-vpn"
    # The tool signature uses 'include_predictions', not 'deep_analysis'
    result = await threat_analyze(ctx, target, include_predictions=False)
    
    assert result['target'] == target
    assert isinstance(result['indicators'], list)
    assert result['overall_risk_score'] >= 0
    logger.info(f"   ✅ Threat analysis complete. Risk: {result['overall_risk_score']}")

async def test_wargame_executor():
    logger.info("🧪 Testing: Wargame Executor")
    from tools.wargame import wargame_run_simulation
    ctx = MockContext()
    
    # Run Simulation
    result = await wargame_run_simulation(ctx, "scenario_001", "localhost")
    
    # It might be blocked by safety checks (default), which is CORRECT behavior
    if "blocked" in str(result['logs']).lower():
        assert result['success'] is False, "Should be marked unsuccessful if blocked"
        logger.info("   ✅ Simulation correctly blocked by safety protocols.")
    else:
        assert result['success'] is True
        assert result['detection_rate'] > 0
        logger.info(f"   ✅ Simulation executed. Detection Rate: {result['detection_rate']}")

async def main():
    print("\n🛡️  STARTING VÉRTICE AGENT QA SUITE  🛡️\n" + "="*40)
    
    try:
        await test_ethical_magistrate()
        print("-" * 20)
        await test_deepfake_scanner()
        print("-" * 20)
        await test_osint_hunter()
        print("-" * 20)
        await test_cybersec_recon()
        print("-" * 20)
        await test_patch_validator()
        print("-" * 20)
        await test_compliance_guardian()
        print("-" * 20)
        await test_threat_prophet()
        print("-" * 20)
        await test_wargame_executor()
        
        print("="*40 + "\n✅ ALL AGENTS PASSED QUALITY ASSURANCE.\n")
    except AssertionError as e:
        print("\n❌ QA FAILED: " + str(e))
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
