# 👁️ AGENTE INVESTIGADOR MULTIMODAL (VISIONARY AGENT)
## Draft Arquitetural - Gemini 3 Hackathon 2026

### 📝 Descrição Geral
O **Visionary Agent** expande a consciência do Vértice Cyber além do texto e código. Ele permite que analistas submetam evidências físicas e digitais brutas para análise instantânea usando a capacidade multimodal nativa do Gemini 3 Pro.

### 🎯 Capacidades Multimodais

| Mídia | Uso Tático | Objetivo |
|:---|:---|:---|
| **📸 Foto / Print** | Análise de Diagramas de Rede, Fotos de Crachás, Prints de Erros. | Identificar falhas de design e vazamento de dados visuais. |
| **🎙️ Áudio** | Gravações de reuniões, interceptações de voz, notas de campo. | Transcrever e detectar sinais de engenharia social ou intenção maliciosa. |
| **🎥 Vídeo** | Screen recordings de ataques, feeds de CCTV, walkthroughs de sistemas. | Realizar perícia forense temporal e identificar padrões de movimentação suspeita. |

---

### 🛠️ Especificação da Tool MCP (`tools/multimodal.py`)

O agente deve seguir o padrão modular da **Constituição Maximus 2.0**:

```python
async def multimodal_analyze_evidence(
    ctx: Context,
    file_path: str,
    mime_type: str,
    investigation_prompt: str = "Analyze for security threats"
) -> Dict[str, Any]:
    """
    Invocação direta do Gemini 3 Pro para análise de arquivos binários.
    
    Args:
        file_path: Caminho ou URI do arquivo no GCS/Local.
        mime_type: image/png, video/mp4, audio/mp3, etc.
        investigation_prompt: Instrução tática para a IA.
    """
    # 1. Carregar arquivo como Part do Gemini
    # 2. Selecionar Modelo (Sempre Pro para multimodalidade profunda)
    # 3. Executar inferência com System Instruction de Perito Forense
```

---

### 🎨 Esboço de UI (`MultimodalInvestigatorPanel.tsx`)

A interface deve manter o padrão **Glassmorphism 2.0**:

1.  **Drop-Zone Central**: Área de drag-and-drop com efeito de pulso ciano quando um arquivo é arrastado.
2.  **Preview Interativo**:
    *   Se imagem: Canvas com detecção de OCR/Objetos.
    *   Se vídeo: Player customizado com timestamps de "Eventos Suspeitos".
    *   Se áudio: Espectrograma animado.
3.  **Analysis Console**: Output da IA em Markdown refinado, destacando "Visual Indicators" e "Acoustic Anomalies".

---

### 🚀 Diferencial para o Hackathon: "Neural Evidence Correlation"

Não apenas mostre a análise. Faça o **Visionary Agent** conversar com os outros:
- "A foto do diagrama de rede mostra um S3 Bucket exposto. Enviando para o **Compliance Guardian** validar contra a LGPD..."
- "O áudio capturado contém termos de engenharia social. Solicitando ao **Ethical Magistrate** uma diretriz de resposta..."

---

### ⚖️ Considerações Éticas (Constituição Maximus)
- **PII Masking**: O agente deve borrar rostos ou dados sensíveis automaticamente antes de processar (ou declarar que não o faz).
- **Truth Obligation**: Se um vídeo for muito longo ou de baixa qualidade para o Gemini processar, o agente deve levantar um erro explícito de "Visual Ambiguity".

---

**Status: DRAFT v1.0 | Autor: Maximus 2.0 Engine**
