"""
E2E Tests for Gemini 3 Pro Preview on Vertex AI

⚠️ GEMINI 3 PRO PREVIEW ONLY - NÃO FAZER DOWNGRADE

Estes testes fazem calls REAIS para Vertex AI com billing ativo.
Model: gemini-3-pro-preview
Location: global
Project: vertice-ai

Run with: pytest tests/e2e/test_gemini3_e2e.py -v -s
"""

import pytest
import time
import os
from typing import Dict, Any

# Skip entire module if credentials not available
pytestmark = pytest.mark.skipif(
    not os.path.exists("/home/juan/.config/gcloud/application_default_credentials.json"),
    reason="GCP credentials not available"
)


class TestGemini3DirectAPI:
    """Test Gemini 3 Pro Preview direct API calls."""

    def test_gemini3_basic_generation(self):
        """Test basic text generation with Gemini 3 Pro Preview."""
        from google import genai
        
        client = genai.Client(
            vertexai=True,
            project="vertice-ai",
            location="global"
        )
        
        start = time.perf_counter()
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="Answer with EXACTLY 3 words: What is cybersecurity?"
        )
        
        elapsed = (time.perf_counter() - start) * 1000
        
        assert response.text is not None
        assert len(response.text) > 0
        
        print(f"\n🤖 Gemini 3 Response ({elapsed:.0f}ms):")
        print(f"   {response.text}")
        
        # Gemini 3 should respond in reasonable time
        assert elapsed < 30000, f"Too slow: {elapsed:.0f}ms"
    
    def test_gemini3_json_output(self):
        """Test JSON output mode with Gemini 3."""
        from google import genai
        from google.genai import types
        import json
        
        client = genai.Client(
            vertexai=True,
            project="vertice-ai",
            location="global"
        )
        
        start = time.perf_counter()
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents="""
            Analyze this threat: "SQL Injection attempt on login page"
            
            Respond with JSON only:
            {"severity": "low|medium|high|critical", "confidence": 0.0-1.0, "mitigation": "string"}
            """,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            )
        )
        
        elapsed = (time.perf_counter() - start) * 1000
        
        result = json.loads(response.text)
        
        assert "severity" in result
        assert "confidence" in result
        assert "mitigation" in result
        
        print(f"\n🤖 Gemini 3 JSON ({elapsed:.0f}ms):")
        print(f"   Severity: {result['severity']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Mitigation: {result['mitigation'][:50]}...")
    
    def test_gemini3_threat_analysis(self):
        """Test comprehensive threat analysis with Gemini 3."""
        from google import genai
        from google.genai import types
        import json
        
        client = genai.Client(
            vertexai=True,
            project="vertice-ai",
            location="global"
        )
        
        context = {
            "target": "e-commerce-platform",
            "industry": "retail",
            "recent_events": [
                "Unusual login attempts from 5 different countries",
                "Database query time increased 300%",
                "New admin user created at 3AM"
            ],
            "current_controls": {
                "mfa": True,
                "waf": True,
                "ids": False
            }
        }
        
        prompt = f"""
        Você é um especialista em segurança cibernética usando Gemini 3 Pro.
        Analise a seguinte situação de ameaça:
        
        {json.dumps(context, indent=2)}
        
        Responda com JSON:
        {{
            "risk_level": "low|medium|high|critical",
            "attack_type": "tipo de ataque provável",
            "confidence": 0.0-1.0,
            "immediate_actions": ["ação1", "ação2"],
            "investigation_steps": ["passo1", "passo2"],
            "summary": "resumo da análise"
        }}
        """
        
        start = time.perf_counter()
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
                max_output_tokens=2048,
                response_mime_type="application/json",
            )
        )
        
        elapsed = (time.perf_counter() - start) * 1000
        
        result = json.loads(response.text)
        
        assert "risk_level" in result
        assert result["risk_level"] in ["low", "medium", "high", "critical"]
        assert "attack_type" in result
        assert "immediate_actions" in result
        assert len(result["immediate_actions"]) > 0
        
        print(f"\n🤖 Gemini 3 Threat Analysis ({elapsed:.0f}ms):")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Attack Type: {result['attack_type']}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Actions: {len(result['immediate_actions'])} recommended")


class TestGemini3Integration:
    """Test Gemini 3 through VertexAIIntegration class."""

    def test_vertex_ai_integration_init(self):
        """Test VertexAIIntegration initializes with Gemini 3."""
        from tools.vertex_ai import VertexAIIntegration
        
        integration = VertexAIIntegration()
        
        assert integration._initialized is True
        assert integration.client is not None
        assert "gemini-3" in integration.model_name
        assert integration.location == "global"
        
        print(f"\n✅ VertexAIIntegration initialized:")
        print(f"   Model: {integration.model_name}")
        print(f"   Project: {integration.project_id}")
        print(f"   Location: {integration.location}")

    @pytest.mark.asyncio
    async def test_threat_intelligence_analysis(self):
        """Test threat intelligence analysis via integration."""
        from tools.vertex_ai import get_vertex_ai
        
        vertex_ai = get_vertex_ai()
        
        result = await vertex_ai.analyze_threat_intelligence(
            query="Analyze potential ransomware attack",
            context={
                "indicators": [
                    {"type": "hash", "value": "abc123def456"},
                    {"type": "ip", "value": "185.234.219.1"}
                ],
                "target": "financial-services"
            }
        )
        
        assert "error" not in result or result.get("risk_level") != "unknown"
        assert result.get("model_used") == "gemini-3-pro-preview"
        
        print(f"\n🤖 Threat Intelligence Result:")
        print(f"   Risk Level: {result.get('risk_level')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Model: {result.get('model_used')}")
    
    @pytest.mark.asyncio
    async def test_compliance_report_generation(self):
        """Test compliance report generation via integration."""
        from tools.vertex_ai import get_vertex_ai
        
        vertex_ai = get_vertex_ai()
        
        result = await vertex_ai.generate_compliance_report(
            target="cloud-infrastructure",
            framework="gdpr",
            assessment_data={
                "data_encryption": True,
                "consent_management": True,
                "data_retention_policy": False,
                "dpo_appointed": True,
                "breach_notification": False
            }
        )
        
        assert "error" not in result or result.get("compliance_level") != "unknown"
        assert result.get("model_used") == "gemini-3-pro-preview"
        
        print(f"\n🤖 Compliance Report:")
        print(f"   Score: {result.get('overall_compliance_score')}")
        print(f"   Level: {result.get('compliance_level')}")
        print(f"   Model: {result.get('model_used')}")
    
    @pytest.mark.asyncio
    async def test_osint_analysis(self):
        """Test OSINT analysis via integration."""
        from tools.vertex_ai import get_vertex_ai
        
        vertex_ai = get_vertex_ai()
        
        result = await vertex_ai.analyze_osint_findings(
            target="acme-corp.com",
            findings=[
                {"type": "subdomain", "data": "mail.acme-corp.com"},
                {"type": "subdomain", "data": "vpn.acme-corp.com"},
                {"type": "email", "data": "admin@acme-corp.com"},
                {"type": "technology", "data": "Microsoft Exchange 2019"}
            ]
        )
        
        assert "error" not in result or result.get("risk_assessment") != "unknown"
        assert result.get("model_used") == "gemini-3-pro-preview"
        
        print(f"\n🤖 OSINT Analysis:")
        print(f"   Risk: {result.get('risk_assessment')}")
        print(f"   Score: {result.get('risk_score')}")
        print(f"   Model: {result.get('model_used')}")


class TestGemini3Performance:
    """Performance benchmarks for Gemini 3 Pro Preview."""

    def test_response_latency(self):
        """Measure Gemini 3 response latency."""
        from google import genai
        
        client = genai.Client(
            vertexai=True,
            project="vertice-ai",
            location="global"
        )
        
        latencies = []
        
        for i in range(3):
            start = time.perf_counter()
            
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=f"Test {i}: Say 'OK' and nothing else."
            )
            
            elapsed = (time.perf_counter() - start) * 1000
            latencies.append(elapsed)
            
            assert response.text is not None
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"\n📊 Gemini 3 Latency (3 runs):")
        print(f"   Avg: {avg_latency:.0f}ms")
        print(f"   Min: {min_latency:.0f}ms")
        print(f"   Max: {max_latency:.0f}ms")
        
        # Gemini 3 should respond in under 10s on average
        assert avg_latency < 10000, f"Average too slow: {avg_latency:.0f}ms"

    def test_json_output_reliability(self):
        """Test JSON output reliability across multiple calls."""
        from google import genai
        from google.genai import types
        import json
        
        client = genai.Client(
            vertexai=True,
            project="vertice-ai",
            location="global"
        )
        
        success_count = 0
        total_tests = 3
        
        for i in range(total_tests):
            try:
                response = client.models.generate_content(
                    model="gemini-3-pro-preview",
                    contents=f'Test {i}: Return JSON {{"status": "ok", "number": {i}}}',
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    )
                )
                
                result = json.loads(response.text)
                if "status" in result:
                    success_count += 1
            except Exception as e:
                print(f"   Test {i} failed: {e}")
        
        reliability = (success_count / total_tests) * 100
        
        print(f"\n📊 JSON Reliability: {success_count}/{total_tests} ({reliability:.0f}%)")
        
        assert reliability >= 66, f"Reliability too low: {reliability:.0f}%"


class TestMCPToolsWithGemini3:
    """Test MCP tools using Gemini 3 through HTTP Bridge."""

    def test_ai_threat_analysis_tool(self):
        """Test ai_threat_analysis tool with Gemini 3."""
        from fastapi.testclient import TestClient
        from mcp_http_bridge import app
        
        client = TestClient(app)
        
        start = time.perf_counter()
        
        response = client.post("/mcp/tools/execute", json={
            "tool_name": "ai_threat_analysis",
            "arguments": {
                "target": "corporate-network",
                "context_data": {
                    "industry": "finance",
                    "threats": ["ransomware", "phishing"]
                },
                "analysis_type": "comprehensive"
            }
        })
        
        elapsed = (time.perf_counter() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"\n🤖 AI Threat Analysis Tool ({elapsed:.0f}ms):")
        print(f"   Success: {data.get('success')}")
        
        if data.get("success"):
            result = data.get("result", {})
            print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"   Model: {result.get('model_used', 'N/A')}")
            
            # Verify Gemini 3 was used
            assert "gemini-3" in str(result.get("model_used", ""))
        else:
            print(f"   Error: {data.get('error')}")
    
    def test_ai_compliance_assessment_tool(self):
        """Test ai_compliance_assessment tool with Gemini 3."""
        from fastapi.testclient import TestClient
        from mcp_http_bridge import app
        
        client = TestClient(app)
        
        start = time.perf_counter()
        
        response = client.post("/mcp/tools/execute", json={
            "tool_name": "ai_compliance_assessment",
            "arguments": {
                "target": "cloud-infrastructure",
                "framework": "soc2",
                "current_state": {
                    "encryption": True,
                    "mfa": True,
                    "logging": True
                }
            }
        })
        
        elapsed = (time.perf_counter() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"\n🤖 AI Compliance Tool ({elapsed:.0f}ms):")
        print(f"   Success: {data.get('success')}")
        
        if data.get("success"):
            result = data.get("result", {})
            print(f"   Score: {result.get('overall_compliance_score', 'N/A')}")
            print(f"   Model: {result.get('model_used', 'N/A')}")
