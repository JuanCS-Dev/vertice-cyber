"""
Vertex AI Integration Module
Integração com Google Cloud Vertex AI para inferência de IA.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from core.settings import get_settings

logger = logging.getLogger(__name__)


class VertexAIIntegration:
    """
    Integração com Google Cloud Vertex AI para análise inteligente.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_id: Optional[str] = os.getenv(
            "GCP_PROJECT_ID", self.settings.api_keys.gcp_project_id
        )
        self.location: str = os.getenv(
            "GCP_LOCATION", self.settings.api_keys.gcp_location or "us-central1"
        )
        self.model_name: str = os.getenv(
            "VERTEX_MODEL", self.settings.api_keys.vertex_model or "gemini-1.5-pro-002"
        )
        self._models: Dict[str, GenerativeModel] = {}

        # Inicializar Vertex AI
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            logger.info(
                f"Vertex AI initialized: project={self.project_id}, location={self.location}"
            )
        else:
            logger.warning("GCP_PROJECT_ID not configured, Vertex AI not initialized")

        # Cache de modelos
        self._models: Dict[str, GenerativeModel] = {}

    def get_model(self, model_name: Optional[str] = None) -> GenerativeModel:
        """Get or create a cached GenerativeModel instance."""
        model_name = model_name or self.model_name
        if model_name not in self._models:
            self._models[model_name] = GenerativeModel(model_name)
        return self._models[model_name]

    async def analyze_threat_intelligence(
        self, query: str, context: Dict[str, Any], model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze threat intelligence using Vertex AI.

        Args:
            query: The analysis query
            context: Context data including indicators, findings, etc.
            model_name: Optional model override

        Returns:
            Analysis results with insights and recommendations
        """
        model = self.get_model(model_name)

        # Prepare context for analysis
        context_str = json.dumps(context, indent=2, default=str)

        prompt = f"""
        Você é um especialista em inteligência de ameaças cibernéticas. Analise os dados fornecidos
        e forneça insights acionáveis sobre ameaças potenciais.

        Query de Análise: {query}

        Dados Contextuais:
        {context_str}

        Forneça sua análise no formato JSON com as seguintes chaves:
        - risk_level: "low", "medium", "high", "critical"
        - confidence: número entre 0 e 1
        - insights: lista de insights principais
        - recommendations: lista de recomendações práticas
        - indicators: indicadores de ameaça identificados
        - summary: resumo executivo da análise
        """

        generation_config = GenerationConfig(
            temperature=0.3,
            top_p=0.8,
            top_k=40,
            max_output_tokens=2048,
            response_mime_type="application/json",
        )

        try:
            response = await model.generate_content_async(
                prompt, generation_config=generation_config
            )

            # Parse JSON response
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result = json.loads(result_text)

            # Add metadata
            result["timestamp"] = datetime.utcnow().isoformat()
            result["model_used"] = model_name or self.model_name
            result["query"] = query

            logger.info(
                f"Threat intelligence analysis completed: risk_level={result.get('risk_level')}"
            )
            return result

        except Exception as e:
            logger.error(f"Vertex AI analysis failed: {e}")
            # Return fallback response
            return {
                "risk_level": "unknown",
                "confidence": 0.0,
                "insights": ["Analysis failed due to technical issues"],
                "recommendations": ["Contact system administrator"],
                "indicators": [],
                "summary": f"Analysis failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": model_name or self.model_name,
                "query": query,
                "error": str(e),
            }

    async def generate_compliance_report(
        self,
        target: str,
        framework: str,
        assessment_data: Dict[str, Any],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate compliance report using Vertex AI.
        """
        model = self.get_model(model_name)

        assessment_str = json.dumps(assessment_data, indent=2, default=str)

        prompt = f"""
        Você é um especialista em conformidade regulatória. Gere um relatório executivo
        de conformidade baseado nos dados de avaliação fornecidos.

        Target: {target}
        Framework: {framework}

        Dados de Avaliação:
        {assessment_str}

        Forneça o relatório no formato JSON com as seguintes chaves:
        - executive_summary: resumo executivo (máximo 200 palavras)
        - overall_compliance_score: número entre 0 e 100
        - compliance_level: "non_compliant", "partially_compliant", "compliant", "exemplary"
        - key_findings: lista de achados principais
        - critical_violations: lista de violações críticas
        - recommended_actions: lista de ações recomendadas
        - next_steps: próximos passos imediatos
        - compliance_trends: tendências observadas
        """

        generation_config = GenerationConfig(
            temperature=0.2,
            top_p=0.9,
            top_k=50,
            max_output_tokens=3072,
            response_mime_type="application/json",
        )

        try:
            response = await model.generate_content_async(
                prompt, generation_config=generation_config
            )

            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result = json.loads(result_text)

            # Add metadata
            result["target"] = target
            result["framework"] = framework
            result["generated_at"] = datetime.utcnow().isoformat()
            result["model_used"] = model_name or self.model_name

            logger.info(
                f"Compliance report generated: score={result.get('overall_compliance_score')}"
            )
            return result

        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return {
                "executive_summary": f"Report generation failed: {str(e)}",
                "overall_compliance_score": 0,
                "compliance_level": "unknown",
                "key_findings": [],
                "critical_violations": [],
                "recommended_actions": ["Contact system administrator"],
                "next_steps": ["Investigate technical issues"],
                "compliance_trends": [],
                "target": target,
                "framework": framework,
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": model_name or self.model_name,
                "error": str(e),
            }

    async def analyze_osint_findings(
        self,
        target: str,
        findings: List[Dict[str, Any]],
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze OSINT findings using Vertex AI.
        """
        model = self.get_model(model_name)

        findings_str = json.dumps(findings, indent=2, default=str)

        prompt = f"""
        Você é um analista de inteligência de código aberto (OSINT). Analise os achados
        de investigação fornecidos e forneça insights sobre o alvo.

        Target: {target}

        Achados OSINT:
        {findings_str}

        Forneça sua análise no formato JSON com as seguintes chaves:
        - risk_assessment: avaliação geral de risco ("low", "medium", "high", "critical")
        - risk_score: número entre 0 e 100
        - key_insights: lista de insights principais sobre o alvo
        - suspicious_indicators: indicadores suspeitos identificados
        - recommended_actions: ações recomendadas baseadas nos achados
        - data_quality_score: qualidade dos dados coletados (0-100)
        - confidence_level: nível de confiança na análise (0-1)
        - summary: resumo executivo dos achados
        """

        generation_config = GenerationConfig(
            temperature=0.4,
            top_p=0.9,
            top_k=40,
            max_output_tokens=2048,
            response_mime_type="application/json",
        )

        try:
            response = await model.generate_content_async(
                prompt, generation_config=generation_config
            )

            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result = json.loads(result_text)

            # Add metadata
            result["target"] = target
            result["analysis_timestamp"] = datetime.utcnow().isoformat()
            result["model_used"] = model_name or self.model_name
            result["findings_count"] = len(findings)

            logger.info(
                f"OSINT analysis completed: risk={result.get('risk_assessment')}, score={result.get('risk_score')}"
            )
            return result

        except Exception as e:
            logger.error(f"OSINT analysis failed: {e}")
            return {
                "risk_assessment": "unknown",
                "risk_score": 0,
                "key_insights": ["Analysis failed due to technical issues"],
                "suspicious_indicators": [],
                "recommended_actions": ["Contact system administrator"],
                "data_quality_score": 0,
                "confidence_level": 0.0,
                "summary": f"Analysis failed: {str(e)}",
                "target": target,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "model_used": model_name or self.model_name,
                "findings_count": len(findings),
                "error": str(e),
            }

    async def stream_analysis(
        self, analysis_type: str, data: Dict[str, Any], model_name: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis results in real-time.
        """
        model = self.get_model(model_name)

        data_str = json.dumps(data, indent=2, default=str)

        prompt = f"""
        Você é um analista de segurança cibernética especializado. Forneça uma análise
        detalhada e estruturada do tipo solicitado.

        Tipo de Análise: {analysis_type}

        Dados para Análise:
        {data_str}

        Forneça uma análise completa, estruturada e acionável. Seja detalhado mas conciso.
        """

        generation_config = GenerationConfig(
            temperature=0.3,
            top_p=0.9,
            top_k=50,
            max_output_tokens=4096,
        )

        try:
            response = await model.generate_content_async(
                prompt, generation_config=generation_config, stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            yield f"Analysis failed: {str(e)}"


# Singleton instance
_vertex_ai: Optional[VertexAIIntegration] = None


def get_vertex_ai() -> VertexAIIntegration:
    """Get Vertex AI integration singleton instance."""
    global _vertex_ai
    if _vertex_ai is None:
        _vertex_ai = VertexAIIntegration()
    return _vertex_ai
