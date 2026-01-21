
import asyncio
import logging
from core.workflows import red_team_auto_pilot, code_audit_patch, insider_threat_hunter

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀  Starting Vertice Cyber Workflows Demo")
    
    # 1. Red Team
    print("\n[1] Red Team Auto-Pilot...")
    res = await red_team_auto_pilot("example-corp.com")
    print(f"    Status: {res.get('status')}")
    
    # 2. Code Audit
    print("\n[2] Code Audit & Patch...")
    res = await code_audit_patch("github.com/vulnerable/repo")
    print(f"    Status: {res.get('status')}")

    # 3. Insider Threat
    print("\n[3] Insider Threat Hunter...")
    res = await insider_threat_hunter("suspect@corp.com")
    print(f"    Anomaly Score: {res.get('anomaly_score')}")

if __name__ == "__main__":
    asyncio.run(main())
