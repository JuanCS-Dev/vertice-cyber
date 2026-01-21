"""
Visionary Sentinel - Multimodal Investigator Tool.
=================================================

Elite investigator powered by Gemini 3 Pro for analyzing images, video, audio and PDFs.
Integrates with Vértice Cyber EventBus and MCP Bridge.
"""

import os
import logging
import base64
import mimetypes
from typing import Dict, Any, Optional
from enum import Enum
import httpx
from google import genai
from google.genai import types

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType

logger = logging.getLogger("visionary_sentinel")


class InvestigationMode(str, Enum):
    FORENSIC = "forensic"
    COMPLIANCE = "compliance"
    THREAT_INTEL = "threat_intelligence"
    INCIDENT_RESPONSE = "incident_response"


SYSTEM_INSTRUCTIONS = {
    InvestigationMode.FORENSIC: "You are an elite digital forensics investigator. Analyze visual/audio evidence for anomalies, security breaches, and technical metadata. Provide precise timestamps.",
    InvestigationMode.COMPLIANCE: "You are a privacy auditor. Identify PII, exposed sensitive data, and regulatory violations (GDPR/LGPD) in images, documents or videos.",
    InvestigationMode.THREAT_INTEL: "You are a threat intelligence analyst. Identify TTPs, MITRE techniques, and technical indicators (IOCs) from the provided evidence.",
    InvestigationMode.INCIDENT_RESPONSE: "You are an incident commander. Analyze evidence to determine impact scope and provide immediate containment steps.",
}


class VisionarySentinel:
    """
    Multimodal Investigator using Gemini 3 Pro capabilities.
    """

    def __init__(self):
        self.settings = get_settings()
        self.event_bus = get_event_bus()
        self.project_id = os.getenv("GCP_PROJECT_ID", "vertice-ai")

        try:
            self.client = genai.Client(
                vertexai=True, project=self.project_id, location="global"
            )
            self._initialized = True
        except Exception as e:
            logger.error(f"Visionary Sentinel init failed: {e}")
            self._initialized = False

    async def _fetch_url(self, url: str) -> tuple[str, str]:
        """Baixa o conteúdo da URL e retorna (base64_data, mime_type)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.content
            b64_data = base64.b64encode(data).decode("utf-8")

            # Tentar pegar o mime do header ou da extensão
            mime_type = resp.headers.get("content-type", mimetypes.guess_type(url)[0])
            if not mime_type:
                mime_type = "application/octet-stream"

            return b64_data, mime_type

    async def analyze(
        self,
        file_data_b64: Optional[str] = None,
        file_url: Optional[str] = None,
        mime_type: Optional[str] = None,
        mode: InvestigationMode = InvestigationMode.FORENSIC,
        focus: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._initialized:
            raise RuntimeError(
                "Visionary Sentinel not initialized. Check GCP credentials."
            )

        # Se for URL, baixar o dado primeiro
        if file_url:
            file_data_b64, mime_type = await self._fetch_url(file_url)

        if not file_data_b64:
            raise ValueError("Either file_data_b64 or file_url must be provided.")

        await self.event_bus.emit(
            EventType.SYSTEM_TOOL_CALLED,
            {
                "agent": "Visionary Sentinel",
                "mode": mode,
                "mime": mime_type,
                "source": "url" if file_url else "upload",
            },
            source="visionary_sentinel",
        )

        try:
            # Configuração validada via auditoria do SDK google-genai
            config = types.GenerateContentConfig(
                temperature=1.0,  # Recomendado para Gemini 3
                max_output_tokens=4000,
                media_resolution="MEDIA_RESOLUTION_HIGH",  # Valor absoluto do Enum
                thinking_config=types.ThinkingConfig(include_thoughts=True),
                system_instruction=SYSTEM_INSTRUCTIONS[mode],
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )

            parts = [
                types.Part(
                    inline_data=types.Blob(data=file_data_b64, mime_type=mime_type)
                ),
                types.Part.from_text(
                    text=f"Analyze this evidence. Focus: {focus or 'Comprehensive'}"
                ),
            ]

            response = self.client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=types.Content(role="user", parts=parts),
                config=config,
            )

            findings = response.text

            await self.event_bus.emit(
                EventType.THREAT_DETECTED
                if mode == InvestigationMode.THREAT_INTEL
                else EventType.RECON_COMPLETED,
                {"findings_summary": findings[:200], "mode": mode},
                source="visionary_sentinel",
            )

            return {
                "findings": findings,
                "mode": mode,
                "model": "gemini-3-pro-preview",
                "usage": response.usage_metadata.total_token_count
                if response.usage_metadata
                else 0,
                "grounding": getattr(response.candidates[0], "grounding_metadata", None)
                is not None,
            }
        except Exception as e:
            logger.error(f"Visionary analysis failed: {e}")
            raise


_sentinel: Optional[VisionarySentinel] = None


def get_visionary_sentinel() -> VisionarySentinel:
    global _sentinel
    if _sentinel is None:
        _sentinel = VisionarySentinel()
    return _sentinel


async def visionary_analyze(
    ctx: Any,
    file_b64: Optional[str] = None,
    file_url: Optional[str] = None,
    mime_type: Optional[str] = None,
    mode: str = "forensic",
    focus: Optional[str] = None,
) -> Dict[str, Any]:
    """Realiza perícia multimodal (imagem, áudio, vídeo, pdf) via upload ou URL."""
    await ctx.info(f"Visionary Sentinel starting {mode} analysis...")
    agent = get_visionary_sentinel()
    result = await agent.analyze(
        file_data_b64=file_b64,
        file_url=file_url,
        mime_type=mime_type,
        mode=InvestigationMode(mode),
        focus=focus,
    )
    await ctx.info("Perícia concluída com sucesso.")
    return result
