"""
Demo: Como usar Vertex AI no Vertice Cyber
"""

import asyncio
import os
from tools.vertex_ai import get_vertex_ai


async def demo_vertex_ai_integration():
    """Demonstração da integração Vertex AI."""

    print("🔺 Vertice Cyber - Vertex AI Integration Demo")
    print("=" * 50)

    # Verificar configuração
    project_id = os.getenv("GCP_PROJECT_ID", "NOT_CONFIGURED")
    print(f"GCP Project ID: {project_id}")

    if project_id == "NOT_CONFIGURED":
        print("❌ GCP não configurado. Para usar Vertex AI:")
        print("1. Configure GCP_PROJECT_ID=vertice-ai")
        print("2. Configure GCP_LOCATION=us-central1")
        print("3. Faça login: gcloud auth login")
        print("4. Configure projeto: gcloud config set project vertice-ai")
        return

    try:
        # Obter instância Vertex AI
        vertex_ai = get_vertex_ai()
        print(f"✅ Vertex AI inicializado: {vertex_ai.model_name}")

        # Demo de análise de ameaça
        print("\n🔍 Testando análise de ameaça...")

        threat_data = {
            "target": "192.168.1.100",
            "indicators": [
                {"type": "ip", "value": "192.168.1.100", "confidence": 0.9},
                {"type": "behavior", "value": "unusual_traffic", "confidence": 0.8},
            ],
            "osint_findings": ["IP associado a botnet", "Tráfego suspeito detectado"],
            "threat_score": 85,
        }

        result = await vertex_ai.analyze_threat_intelligence(
            "Analisar IP suspeito 192.168.1.100", threat_data
        )

        print("📊 Resultado da análise:")
        print(f"   Nível de risco: {result.get('risk_level', 'unknown')}")
        print(f"   Confiança: {result.get('confidence', 0):.1%}")
        print(f"   Insights: {len(result.get('insights', []))}")
        print(f"   Recomendações: {len(result.get('recommendations', []))}")

        print("\n✅ Vertex AI funcionando corretamente!")

    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        print("Verifique se o GCP está configurado corretamente.")


if __name__ == "__main__":
    asyncio.run(demo_vertex_ai_integration())
