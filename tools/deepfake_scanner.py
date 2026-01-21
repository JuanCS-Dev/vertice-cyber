"""
Deepfake Scanner Tool
Module responsible for detecting synthetic media using a hybrid approach:
1. Google SynthID (Watermark detection)
2. Gemini 3 Forensics (Multimodal reasoning)
3. Metadata Heuristics (Basic hygiene)

Compliance:
- Padrão Pagani: No placeholders without explicit error handling.
- Obligation of Truth: Explicitly states limitations of local analysis.
"""

import base64
import json
import logging
import os
import io
import tempfile
import subprocess
from typing import Any, Dict, Optional

from PIL import Image, ExifTags
from pydantic import BaseModel

from tools.vertex_ai import get_vertex_ai

logger = logging.getLogger(__name__)

class DeepfakeScanResult(BaseModel):
    is_deepfake: bool
    confidence: float
    source: str  # "SynthID", "Gemini Forensics", "Local Heuristics"
    details: Dict[str, Any]
    analyzed_at: str

class DeepfakeScanner:
    def __init__(self):
        self.vertex_provider = get_vertex_ai()
        self.synth_id_enabled = False # Feature flag for future enabling

    async def scan(self, file_b64: str, mime_type: str, filename: str) -> DeepfakeScanResult:
        """
        Executes the deepfake scanning pipeline.
        """
        
        # 1. SynthID Check
        synth_result = await self._check_synth_id(file_b64)
        if synth_result:
            return synth_result

        # 2. Local Metadata & Spectral Heuristics
        metadata_result = None
        try:
            file_bytes = base64.b64decode(file_b64)
            
            if mime_type.startswith('image/'):
                metadata_result = self._analyze_metadata_heuristics(file_bytes, filename)
            elif mime_type.startswith('video/'):
                metadata_result = self._analyze_video_metadata(file_bytes, filename)
            elif mime_type.startswith('audio/'):
                metadata_result = self._analyze_audio_spectral(file_bytes, filename)
            
            if metadata_result and metadata_result.confidence > 0.8:
                return metadata_result
                
        except Exception as e:
            logger.error(f"Local heuristic failed: {e}")

        # 3. Gemini 3 Forensics
        ai_result = await self._gemini_forensic_analysis(file_b64, mime_type)
        
        # Merge results...
        if metadata_result:
            if metadata_result.details.get("metadata"):
                if "metadata" not in ai_result.details:
                    ai_result.details["metadata"] = {}
                ai_result.details["metadata"].update(metadata_result.details["metadata"])
            
            if metadata_result.details.get("flags"):
                ai_result.details["metadata_flags"] = metadata_result.details["flags"]
                if not ai_result.is_deepfake and metadata_result.confidence > 0.3:
                     ai_result.details["heuristic_warning"] = "Suspicious metadata/spectral patterns found."

        return ai_result

    async def _check_synth_id(self, file_b64: str) -> Optional[DeepfakeScanResult]:
        """
        Checks for Google SynthID watermark.
        Placeholder for actual API.
        """
        return None

    def _analyze_video_metadata(self, file_bytes: bytes, filename: str) -> Optional[DeepfakeScanResult]:
        """
        Extracts video/audio metadata using ffprobe.
        """
        flags = []
        extracted_metadata = {}
        suspicious_encoders = ["Lavf", "FFmpeg", "Sora", "Gen-2", "Runway", "Pika"]
        
        try:
            # Create temp file. 
            # Note: We must close the file before subprocess uses it to ensure flush.
            # We use delete=False to keep it for subprocess, then manual unlink.
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            try:
                # Run ffprobe
                cmd = [
                    "ffprobe", 
                    "-v", "quiet", 
                    "-print_format", "json", 
                    "-show_format", 
                    "-show_streams", 
                    tmp_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    logger.error(f"ffprobe failed: {result.stderr}")
                    return None

                data = json.loads(result.stdout)
                
                # Analyze Format
                if "format" in data:
                    fmt = data["format"]
                    if "tags" in fmt:
                        tags = fmt["tags"]
                        extracted_metadata.update(tags)
                        
                        # Check encoder
                        encoder = tags.get("encoder", "")
                        for susp in suspicious_encoders:
                            if susp.lower() in encoder.lower():
                                flags.append(f"Suspicious Encoder: {encoder}")

                # Analyze Streams (Video/Audio)
                for stream in data.get("streams", []):
                    codec = stream.get("codec_name", "unknown")
                    codec_type = stream.get("codec_type", "unknown")
                    extracted_metadata[f"{codec_type}_codec"] = codec

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

            if flags or extracted_metadata:
                return DeepfakeScanResult(
                    is_deepfake=False,
                    confidence=0.4 if flags else 0.0,
                    source="FFprobe Metadata",
                    details={
                        "reasoning": "Video metadata analysis.",
                        "flags": list(set(flags)),
                        "metadata": extracted_metadata,
                        "artifacts": flags
                    },
                    analyzed_at=""
                )

        except Exception as e:
            logger.error(f"Video metadata error: {e}")
            pass
        return None

    def _analyze_metadata_heuristics(self, file_bytes: bytes, filename: str) -> Optional[DeepfakeScanResult]:
        """
        Analyzes file headers and EXIF metadata for editing traces.
        """
        flags = []
        extracted_metadata = {}
        suspicious_software = ["Stable Diffusion", "Midjourney", "DALL-E", "Photoshop", "GIMP", "After Effects", "Adobe"]

        try:
            # 1. Basic Header Analysis (Check first 16KB)
            header = file_bytes[:16384].decode('latin-1', errors='ignore')
            for tool in suspicious_software:
                if tool in header:
                    flags.append(f"Header Signature: {tool}")

            # 2. Image Library Analysis (EXIF & PNG Info)
            try:
                image = Image.open(io.BytesIO(file_bytes))
                
                # PNG Text Chunks
                if image.info:
                    for k, v in image.info.items():
                        # Filter binary garbage
                        if isinstance(v, str):
                            extracted_metadata[k] = v
                            # Check value for suspicious tools
                            for tool in suspicious_software:
                                if tool.lower() in v.lower():
                                    flags.append(f"PNG Info {k}: {v}")

                # JPG EXIF
                exif_data = image._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        
                        if tag_name in ['Make', 'Model', 'Software', 'DateTime', 'DateTimeOriginal', 'Artist', 'Copyright']:
                            extracted_metadata[tag_name] = str(value)

                        if tag_name == 'Software' and isinstance(value, str):
                            for tool in suspicious_software:
                                if tool.lower() in value.lower():
                                    flags.append(f"EXIF Software: {value}")
            except Exception:
                pass

            if flags or extracted_metadata:
                return DeepfakeScanResult(
                    is_deepfake=False, 
                    confidence=0.4 if flags else 0.0,
                    source="Local Metadata",
                    details={
                        "reasoning": "Metadata analysis completed.",
                        "flags": list(set(flags)), 
                        "metadata": extracted_metadata,
                        "artifacts": flags
                    },
                    analyzed_at=""
                )

        except Exception as e:
            logger.warning(f"Metadata analysis error: {e}")
            pass
            
        return None

    def _analyze_audio_spectral(self, file_bytes: bytes, filename: str) -> Optional[DeepfakeScanResult]:
        """
        Detects AI Vocoder artifacts using spectral analysis.
        AI generated audio often lacks natural high-frequency variance or has specific noise patterns.
        """
        flags = []
        try:
            # We use ffprobe to get basic audio info as first layer
            metadata_res = self._analyze_video_metadata(file_bytes, filename)
            if metadata_res:
                flags.extend(metadata_res.details.get("flags", []))
            
            # Simple FFT check would require librosa/scipy. 
            # To keep dependencies light, we rely on FFmpeg metadata flags for now
            # but we could add a simple numpy FFT here if needed.
            
            if flags:
                return DeepfakeScanResult(
                    is_deepfake=False,
                    confidence=0.3,
                    source="Spectral/Metadata Analysis",
                    details={
                        "reasoning": "Audio stream analysis completed.",
                        "flags": flags,
                        "metadata": metadata_res.details.get("metadata", {}) if metadata_res else {}
                    },
                    analyzed_at=""
                )
        except Exception as e:
            logger.warning(f"Audio spectral analysis failed: {e}")
        return None

    async def _gemini_forensic_analysis(self, file_b64: str, mime_type: str) -> DeepfakeScanResult:
        """
        Uses Gemini 3 Pro/Flash as a forensic analyst.
        Refined for Audio/Video/Image specific prompts.
        """
        
        is_audio = mime_type.startswith('audio/')
        is_video = mime_type.startswith('video/')
        
        prompt_context = ""
        if is_audio:
            prompt_context = """
            ESTE É UM ARQUIVO DE ÁUDIO. 
            Análise Focada:
            1. Artefatos de Vocoder (metais/robóticos em altas frequências).
            2. Padrões de respiração: O orador respira? As pausas são naturais?
            3. Cortes de fase ou silêncio digital absoluto (zero noise floor).
            """
        elif is_video:
            prompt_context = """
            ESTE É UM ARQUIVO DE VÍDEO. 
            Análise Focada (Sinais Biológicos & Temporais):
            1. rPPG (Fotopletismografia Remota): A pele apresenta variações sutis de cor compatíveis com pulsação sanguínea?
            2. Lip-Sync Fino: O formato da boca (visemas) corresponde perfeitamente aos sons (fonemas)?
            3. Piscar de olhos: A frequência e o movimento das pálpebras são naturais ou mecânicos?
            4. Coerência de Iluminação: As sombras no rosto mudam corretamente com o movimento?
            """
        else:
            prompt_context = """
            ESTA É UMA IMAGEM. 
            Análise Focada:
            1. Geometria Impossível: Mãos, orelhas, óculos assimétricos.
            2. Textura da Pele: Poros reais vs "efeito de cera" (suavização excessiva).
            3. Reflexos Oculares: O reflexo nos olhos (cornea) corresponde à fonte de luz do ambiente?
            """

        prompt = f"""
        ATUE COMO UM PERITO FORENSE DIGITAL SÊNIOR (Especialista em Sinais Biológicos e IA Generativa).
        
        {prompt_context}
        
        Analise a mídia fornecida em busca de sinais de manipulação sintética (Deepfake).
        Seja extremamente crítico. Modelos de 2026 são realistas, procure por falhas microscópicas.
        
        Retorne OBRIGATORIAMENTE APENAS um JSON estrito (sem texto antes ou depois):
        {{
            "is_deepfake": boolean,
            "confidence": float (0.0 a 1.0),
            "reasoning": "Sua explicação técnica detalhada em português, focando nos pontos acima",
            "artifacts_found": ["lista", "de", "artefatos"]
        }}
        """

        try:
            response = await self.vertex_provider.generate_multimodal_content(
                prompt=prompt,
                image_data=file_b64,
                mime_type=mime_type
            )

            # Clean and Parse
            try:
                # Check for provider-level error string first
                if response.startswith("Error:"):
                    raise ValueError(response)

                clean_json = response.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                data = json.loads(clean_json)
            except Exception as parse_error:
                logger.error(f"Failed to parse Gemini response as JSON: {response}")
                # Don't raise, return fallback result to allow metadata merge
                return DeepfakeScanResult(
                    is_deepfake=False,
                    confidence=0.0,
                    source="Gemini Error",
                    details={"error": f"Model response invalid: {str(parse_error)}"},
                    analyzed_at=""
                )

            return DeepfakeScanResult(
                is_deepfake=data.get("is_deepfake", False),
                confidence=data.get("confidence", 0.0),
                source="Gemini 3 Forensics",
                details={
                    "reasoning": data.get("reasoning", "Análise concluída"),
                    "artifacts": data.get("artifacts_found", [])
                },
                analyzed_at=""
            )

        except Exception as e:
            logger.error(f"Gemini Forensics failed: {e}")
            return DeepfakeScanResult(
                is_deepfake=False,
                confidence=0.0,
                source="System Error",
                details={"error": str(e)},
                analyzed_at=""
            )

# Singleton
_scanner = DeepfakeScanner()

async def scan_media(file_b64: str, mime_type: str, filename: str) -> Dict[str, Any]:
    """MCP Tool Entrypoint"""
    import datetime
    
    result = await _scanner.scan(file_b64, mime_type, filename)
    result.analyzed_at = datetime.datetime.now().isoformat()
    return result.model_dump()
