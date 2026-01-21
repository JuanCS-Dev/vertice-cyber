import asyncio
import httpx
import time
from datetime import datetime
from statistics import mean

# Configurações
BASE_URL = "http://localhost:8002"
TEST_TARGETS = [
    # 1. Ethical Magistrate
    {
        "agent": "Ethical Magistrate",
        "tool": "ethical_validate",
        "args": {
            "action": "ISOLATE_CRITICAL_DB(id='prod-db-01')",
            "context": {"reason": "Maintenance"},
        },
    },
    # 2. OSINT Hunter
    {
        "agent": "OSINT Hunter",
        "tool": "osint_investigate",
        "args": {"target": "google.com", "depth": "basic"},
    },
    # 3. Threat Prophet
    {
        "agent": "Threat Prophet",
        "tool": "threat_analyze",
        "args": {"target": "185.156.177.241", "include_predictions": True},
    },
    # 4. Compliance Guardian
    {
        "agent": "Compliance Guardian",
        "tool": "compliance_assess",
        "args": {"target": "aws-s3-bucket-logs", "framework": "gdpr"},
    },
    # 5. CyberSec Investigator
    {
        "agent": "CyberSec Investigator",
        "tool": "cybersec_recon",
        "args": {"target": "8.8.8.8", "scan_ports": True, "scan_web": False},
    },
    # 6. Patch Validator ML
    {
        "agent": "Patch Validator ML",
        "tool": "patch_validate",
        "args": {
            "diff_content": "--- a/auth.py\n+++ b/auth.py\n@@ -1,1 +1,1 @@\n-eval(user_input)\n+json.loads(user_input)",
            "language": "python",
        },
    },
    # 7. Wargame Executor
    {
        "agent": "Wargame Executor",
        "tool": "wargame_run_simulation",
        "args": {"scenario_id": "scenario_001", "target": "local"},
    },
    # 8. AI Analysis (Direct Gemini 3)
    {
        "agent": "AI Core",
        "tool": "ai_threat_analysis",
        "args": {
            "target": "1.1.1.1",
            "context_data": {"detected_port": 22},
            "analysis_type": "ssh_brute_force",
        },
    },
    # 9. Model Switching
    {"agent": "AI Core", "tool": "set_ai_model", "args": {"model_alias": "flash"}},
    # 10. Visionary Sentinel (Multimodal URL)
    {
        "agent": "Visionary Sentinel",
        "tool": "visionary_analyze",
        "args": {
            "file_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
            "mode": "forensic",
            "focus": "Analyze the logo for any hidden digital steganography or metadata signatures",
        },
    },
]


async def run_scientific_test():
    print(f"\n{'-' * 80}")
    print("🔬 VÉRTICE CYBER - BATERIA DE TESTES INTEGRADA (PTC-02)")
    print("Status: Iniciação de Teste de Prontidão de Combate")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'-' * 80}\n")

    results = []

    async with httpx.AsyncClient(timeout=45.0) as client:
        for t in TEST_TARGETS:
            print(
                f"Testing Agent: {t['agent']:<25} | Tool: {t['tool']:<20}",
                end=" ",
                flush=True,
            )
            start = time.perf_counter()
            try:
                resp = await client.post(
                    f"{BASE_URL}/mcp/tools/execute",
                    json={"tool_name": t["tool"], "arguments": t["args"]},
                )
                latency = (time.perf_counter() - start) * 1000
                data = resp.json()

                status = "✅ OK" if data.get("success") else "❌ FAIL"
                print(f"| {status} | Latency: {latency:>8.2f}ms")

                results.append(
                    {
                        "agent": t["agent"],
                        "tool": t["tool"],
                        "success": data.get("success"),
                        "latency": latency,
                        "error": data.get("error") if not data.get("success") else None,
                    }
                )
            except Exception as e:
                print(f"| ❌ ERROR | {str(e)}")
                results.append(
                    {
                        "agent": t["agent"],
                        "tool": t["tool"],
                        "success": False,
                        "latency": 0,
                        "error": str(e),
                    }
                )

    # Sumário Científico
    print(f"\n{'-' * 80}")
    print("📊 RELATÓRIO DE MÉTRICAS ANALÍTICAS")
    print(f"{'-' * 80}")

    success_count = sum(1 for r in results if r["success"])
    avg_latency = mean([r["latency"] for r in results if r["success"]])

    print(f"Total Agentes Testados: {len(TEST_TARGETS)}")
    print(f"Taxa de Sucesso:        {(success_count / len(TEST_TARGETS)) * 100:.1f}%")
    print(f"Latência Média:         {avg_latency:.2f}ms")

    if any(not r["success"] for r in results):
        print("\n⚠️ FALHAS DETECTADAS:")
        for r in results:
            if not r["success"]:
                print(f"   - {r['agent']} ({r['tool']}): {r['error']}")

    print(f"\n{'-' * 80}\n")

    print(f"\n{'-' * 60}")
    print("🏁 TESTE CONCLUÍDO")
    print(f"{'-' * 60}\n")


if __name__ == "__main__":
    asyncio.run(run_scientific_test())
