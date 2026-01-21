
import asyncio
import sys
import os
import logging

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.workflows import red_team_auto_pilot, code_audit_patch, insider_threat_hunter

# Configure logging to see workflow output
logging.basicConfig(level=logging.INFO)

async def test_workflows():
    print("🧪 Testing AI-Driven Workflows...")
    
    # 1. Red Team
    print("\n▶️  Workflow 1: Red Team Auto-Pilot")
    # We pass None as ctx to simulate external call or handle it in workflow
    try:
        res = await red_team_auto_pilot("example.com", ctx=None)
        print(f"   Result: {res.get('status')} - OSINT: {len(res.get('osint_report', {}).get('findings', []))} findings")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 2. Code Audit
    print("\n▶️  Workflow 2: Code Audit & Patch")
    try:
        res = await code_audit_patch("github.com/test/repo", ctx=None)
        # Note: This might effectively be a no-op or error because mock logic in workflow
        # checks for 'mock_diff' but we didn't inject dependencies. 
        # But we just want to see it run without crashing on imports/syntax.
        print(f"   Result: {res.get('status')} - Message: {res.get('message') or res.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Insider Threat
    print("\n▶️  Workflow 3: Insider Threat Hunter")
    try:
        # Mocking an email
        res = await insider_threat_hunter("employee@company.com", ctx=None)
        print(f"   Result: {res.get('status')} - Anomaly Score: {res.get('anomaly_score')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_workflows())
