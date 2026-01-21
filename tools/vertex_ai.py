"""
Vertex AI Integration Module - Gemini 3 Pro Preview
Integração com Google Cloud Vertex AI usando google-genai SDK.

IMPORTANTE: Este módulo usa APENAS Gemini 3 Pro Preview.
NÃO FAÇA DOWNGRADE para Gemini 2 ou 1.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from google import genai
from google.genai import types

from core.settings import get_settings

logger = logging.getLogger(__name__)

# Modelos disponíveis - Gemini 3 Series
MODELS = {"pro": "gemini-3-pro-preview", "flash": "gemini-3-flash-preview"}

DEFAULT_MODEL = MODELS["pro"]


class VertexAIIntegration:
    """
    Integração com Google Cloud Vertex AI para análise inteligente.
    Usa google-genai SDK com suporte a Gemini 3 Pro e Flash.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_id: str = os.getenv(
            "GCP_PROJECT_ID", self.settings.api_keys.gcp_project_id or "vertice-ai"
        )
        self.location: str = "global"

        # Carrega modelo inicial, garantindo que seja um da série Gemini 3
        configured_model = os.getenv(
            "VERTEX_MODEL", self.settings.api_keys.vertex_model or DEFAULT_MODEL
        )
        self.model_name = (
            configured_model if "gemini-3" in configured_model else DEFAULT_MODEL
        )

        try:
            self.client = genai.Client(
                vertexai=True, project=self.project_id, location=self.location
            )
            logger.info(
                f"Vertex AI initialized: project={self.project_id}, "
                f"location={self.location}, active_model={self.model_name}"
            )
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client: {e}")
            self.client = None
            self._initialized = False

    def set_model(self, model_alias: str) -> str:
        """Altera o modelo ativo baseado no alias (pro/flash)."""
        if model_alias in MODELS:
            self.model_name = MODELS[model_alias]
            logger.info(f"Model switched to: {self.model_name}")
        return self.model_name

    def _ensure_initialized(self) -> bool:
        """Check if client is initialized."""
        if not self._initialized or self.client is None:
            logger.error("Vertex AI client not initialized")
            return False
        return True

    async def analyze_threat_intelligence(
        self, query: str, context: Dict[str, Any], model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze threat intelligence using Gemini 3 Pro Preview.
        """
        if not self._ensure_initialized():
            return self._error_response("Vertex AI not initialized", query)

        model = model_name or self.model_name
        context_str = json.dumps(context, indent=2, default=str)

        prompt = f"""
        Você é um especialista em inteligência de ameaças cibernéticas usando Gemini 3 Pro.
        Analise os dados fornecidos e forneça insights acionáveis.

        Query de Análise: {query}

        Dados Contextuais:
        {context_str}

        Responda APENAS com JSON válido (sem markdown):
        {{
            "risk_level": "low|medium|high|critical",
            "confidence": 0.0-1.0,
            "insights": ["insight1", "insight2"],
            "recommendations": ["rec1", "rec2"],
            "indicators": ["indicator1"],
            "summary": "resumo executivo"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.8,
                    max_output_tokens=2048,
                    response_mime_type="application/json",
                ),
            )

            result = self._parse_json_response(response.text)
            result["timestamp"] = datetime.utcnow().isoformat()
            result["model_used"] = model
            result["query"] = query

            logger.info(
                f"Threat analysis completed: risk_level={result.get('risk_level')}"
            )
            return result

        except Exception as e:
            logger.error(f"Threat analysis failed: {e}")
            return self._error_response(str(e), query)

    async def generate_compliance_report(
        self,
        target: str,
        framework: str,
        assessment_data: Dict[str, Any],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate compliance report using Gemini 3 Pro Preview.
        """
        if not self._ensure_initialized():
            return self._compliance_error(
                target, framework, "Vertex AI not initialized"
            )

        model = model_name or self.model_name
        assessment_str = json.dumps(assessment_data, indent=2, default=str)

        prompt = f"""
        Você é um especialista em conformidade regulatória usando Gemini 3 Pro.
        Gere um relatório executivo de conformidade.

        Target: {target}
        Framework: {framework}

        Dados de Avaliação:
        {assessment_str}

        Responda APENAS com JSON válido (sem markdown):
        {{
            "executive_summary": "resumo executivo",
            "overall_compliance_score": 0-100,
            "compliance_level": "non_compliant|partially_compliant|compliant|exemplary",
            "key_findings": ["finding1", "finding2"],
            "critical_violations": ["violation1"],
            "recommended_actions": ["action1", "action2"],
            "next_steps": ["step1", "step2"]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    top_p=0.9,
                    max_output_tokens=3072,
                    response_mime_type="application/json",
                ),
            )

            result = self._parse_json_response(response.text)
            result["target"] = target
            result["framework"] = framework
            result["generated_at"] = datetime.utcnow().isoformat()
            result["model_used"] = model

            logger.info(
                f"Compliance report generated: score={result.get('overall_compliance_score')}"
            )
            return result

        except Exception as e:
            logger.error(f"Compliance report failed: {e}")
            return self._compliance_error(target, framework, str(e))

    async def analyze_osint_findings(
        self,
        target: str,
        findings: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze OSINT findings using Gemini 3 Pro Preview.
        """
        if not self._ensure_initialized():
            return self._osint_error(target, findings, "Vertex AI not initialized")

        model = model_name or self.model_name
        findings_str = json.dumps(findings, indent=2, default=str)

        prompt = f"""
        Você é um analista OSINT usando Gemini 3 Pro.
        Analise os achados de investigação.

        Target: {target}

        Achados OSINT:
        {findings_str}

        Responda APENAS com JSON válido (sem markdown):
        {{
            "risk_assessment": "low|medium|high|critical",
            "risk_score": 0-100,
            "key_insights": ["insight1", "insight2"],
            "suspicious_indicators": ["indicator1"],
            "recommended_actions": ["action1", "action2"],
            "data_quality_score": 0-100,
            "confidence_level": 0.0-1.0,
            "summary": "resumo dos achados"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    top_p=0.9,
                    max_output_tokens=2048,
                    response_mime_type="application/json",
                ),
            )

            result = self._parse_json_response(response.text)
            result["target"] = target
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            result["model_used"] = model
            result["findings_count"] = len(findings)

            logger.info(
                f"OSINT analysis completed: risk={result.get('risk_assessment')}"
            )
            return result

        except Exception as e:
            logger.error(f"OSINT analysis failed: {e}")
            return self._osint_error(target, findings, str(e))

    async def stream_analysis(
        self, analysis_type: str, data: Dict[str, Any], model_name: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis results using Gemini 3 Pro Preview.
        """
        if not self._ensure_initialized():
            yield "Error: Vertex AI not initialized"
            return

        model = model_name or self.model_name
        data_str = json.dumps(data, indent=2, default=str)

        prompt = f"""
        Você é um analista de segurança cibernética usando Gemini 3 Pro.
        Forneça uma análise detalhada e estruturada.

        Tipo de Análise: {analysis_type}

        Dados para Análise:
        {data_str}

        Forneça uma análise completa, estruturada e acionável.
        """

        try:
            # Use streaming
            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.9,
                    max_output_tokens=4096,
                ),
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            yield f"Analysis failed: {str(e)}"

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from response, handling markdown code blocks."""
        result_text = text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        return json.loads(result_text.strip())

    def _error_response(self, error: str, query: str) -> Dict[str, Any]:
        """Return error response for threat analysis."""
        return {
            "risk_level": "unknown",
            "confidence": 0.0,
            "insights": ["Analysis failed"],
            "recommendations": ["Check Vertex AI configuration"],
            "indicators": [],
            "summary": f"Error: {error}",
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": self.model_name,
            "query": query,
            "error": error,
        }

    def _compliance_error(
        self, target: str, framework: str, error: str
    ) -> Dict[str, Any]:
        """Return error response for compliance report."""
        return {
            "executive_summary": f"Report generation failed: {error}",
            "overall_compliance_score": 0,
            "compliance_level": "unknown",
            "key_findings": [],
            "critical_violations": [],
            "recommended_actions": ["Check Vertex AI configuration"],
            "next_steps": ["Investigate technical issues"],
            "target": target,
            "framework": framework,
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": self.model_name,
            "error": error,
        }

    def _osint_error(self, target: str, findings: List, error: str) -> Dict[str, Any]:
        """Return error response for OSINT analysis."""
        return {
            "risk_assessment": "unknown",
            "risk_score": 0,
            "key_insights": ["Analysis failed"],
            "suspicious_indicators": [],
            "recommended_actions": ["Check Vertex AI configuration"],
            "data_quality_score": 0,
            "confidence_level": 0.0,
            "summary": f"Error: {error}",
            "target": target,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "model_used": self.model_name,
            "findings_count": len(findings),
            "error": error,
        }


# Singleton instance
_vertex_ai: Optional[VertexAIIntegration] = None


def get_vertex_ai() -> VertexAIIntegration:
    """Get Vertex AI integration singleton instance."""
    global _vertex_ai
    if _vertex_ai is None:
        _vertex_ai = VertexAIIntegration()
    return _vertex_ai
