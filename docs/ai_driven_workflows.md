# 🤖 AI-Driven Workflows (Draft)

Estes workflows definem cadeias de execução autônomas combinando múltiplos agentes do Vértice Cyber. O objetivo é permitir que o CyberOp inicie operações complexas com um único input.

---

## 🏗️ Workflow 1: "Red Team Auto-Pilot" (Recon -> Attack)

**Objetivo**: Simular um ataque completo, desde a descoberta até a execução (simulada), para validar defesas.

**Input**: `target_domain` (ex: `empresa.com`)

### Sequence
1.  **Reconnaissance (OSINT Hunter)**
    *   Action: `osint_investigate(target=target_domain, depth="deep")`
    *   Output: `osint_report` (subdomains, emails, exposed services)
2.  **Analysis (Threat Prophet + AI)**
    *   Action: `ai_threat_analysis(target=target_domain, context=osint_report)`
    *   Output: `attack_vectors` (Lista de CVEs, portas abertas, vetores de phishing)
3.  **Strategy (Vertex AI)**
    *   Action: `generate_attack_plan(vectors=attack_vectors)`
    *   Output: `attack_plan` (Sequência de Tácticas MITRE ATT&CK)
4.  **Governance Check (Ethical Magistrate)**
    *   Action: `ethical_validate(action="Execute Attack Plan", context=attack_plan)`
    *   Output: `approval` (Se aprovado, continua; se condicional, pede verificação humana)
5.  **Execution (Wargame Executor)**
    *   Action: `wargame_run_simulation(scenario=attack_plan, target=target_domain)`
    *   Output: `wargame_result` (Success/Fail, Logs)
6.  **Reporting (AI Analyst)**
    *   Action: `ai_integrated_assessment(final_data=wargame_result)`
    *   Output: **Final PDF Report**

---

## 🛡️ Workflow 2: "Code Audit & Patch" (Defensive)

**Objetivo**: Analisar repositório, detectar vulnerabilidades e propor patches validados.

**Input**: `repo_url` (ex: `github.com/org/repo`)

### Sequence
1.  **Scan (Patch Validator ML)**
    *   Action: `patch_validate(repo=repo_url, scan_mode="full")`
    *   Output: `vulnerability_list` (SQLi, XSS, RCE candidates)
2.  **Validation (Vertex AI)**
    *   Action: `ai_stream_analysis(type="code_review", data=vulnerability_list)`
    *   Output: `confirmed_vulns` (Eliminação de False Positives)
3.  **Remediation (Vertex AI + Coder)**
    *   Action: `generate_patch(vuln=confirmed_vulns)`
    *   Output: `patch_diff` (Código do fix)
4.  **Safety Check (Patch Validator)**
    *   Action: `patch_validate(diff_content=patch_diff)`
    *   Output: `safety_score` (Garante que o patch não quebra o sistema ou introduz backdoors)
5.  **Governance (Magistrate)**
    *   Action: `ethical_validate(action="Apply Patch", context=safety_score)`
    *   Output: `approval`
6.  **Apply (Orchestrator)**
    *   Action: `apply_patch(diff=patch_diff)`
    *   Output: **System Hardened**

---

## 🕵️ Workflow 3: "Insider Threat Hunter" (Investigation)

**Objetivo**: Investigar comportamento anômalo de funcionário sem violar privacidade (Privacy-First).

**Input**: `employee_email`

### Sequence
1.  **Breach Check (OSINT Hunter)**
    *   Action: `osint_breach_check(email=employee_email)`
    *   Output: `external_compromise` (Senhas vazadas?)
2.  **Privacy Shield (Magistrate)**
    *   Action: `ethical_validate(action="Internal Log Access", context={"has_pii": True})`
    *   *Result*: Exige mascaramento de dados (PII Masking).
3.  **Behavior Analysis (Threat Prophet)**
    *   Action: `threat_analyze(target=employee_email, mode="behavioral")`
    *   Output: `anomaly_score` (Login em horários estranhos, exfiltração de dados)
4.  **Synthesis (AI Analyst)**
    *   Action: `ai_integrated_assessment(scope="insider_threat", data=anomaly_score)`
    *   Output: **Risk Report** (Sem expor conteúdo das mensagens, apenas metadados)

---

### Implementation Notes
- **Orchestrator**: O `core/state/orchestrator.py` será responsável por encadear essas chamadas.
- **State Passing**: O output de um agente deve ser o input do próximo (Pipeline).
- **Human-in-the-Loop**: Passos críticos (Ataque, Patch) devem ter `await_approval()` no Workflow.

---

## 🧩 Agent Capabilities & Integration Specs

Para garantir que o planejamento seja fidedigno ao código existente, abaixo estão as especificações técnicas de cada agente envolvido.

### 1. OSINT Hunter (`tools.osint.OSINTHunter`)
*   **Role**: Coletor de Inteligência. Não toma decisões, apenas coleta dados brutos e correlaciona.
*   **Capabilities**:
    *   `investigate(target)`: Varredura passiva de domínios, IPs e emails.
    *   `breach_check(email)`: Verifica leaks conhecidos (simulado/integração HaveIBeenPwned).
    *   `google_dork(query)`: Busca avançada por arquivos expostos.
*   **Integration**:
    *   Input: String (`domain`, `ip`, `email`).
    *   Output: `OSINTResult` object (JSON com findings, risk_score).
*   **File**: [`tools/osint.py`](file:///media/juan/DATA/vertice-cyber/tools/osint.py)

### 2. Threat Prophet (`tools.threat.ThreatProphet`)
*   **Role**: Analista Preditivo. Usa MITRE ATT&CK para mapear o que *pode* acontecer.
*   **Capabilities**:
    *   `analyze_threats(target)`: Correlaciona dados OSINT com Táticas MITRE.
    *   `predict_threats(target)`: Gera cenários de ataque prováveis (ex: "Phishing -> Ransomware").
*   **Integration**:
    *   Input: Contexto do alvo.
    *   Output: `ThreatAnalysis` object (Lista de `MITRETechnique`, Score de Risco 0-100).
*   **File**: [`tools/threat.py`](file:///media/juan/DATA/vertice-cyber/tools/threat.py)

### 3. Ethical Magistrate (`tools.magistrate.EthicalMagistrate`)
*   **Role**: Governador / Blocker. A única entidade com poder de VETO.
*   **Capabilities**:
    *   `validate(action, context)`: Verifica keywords proibidas (`delete`, `drop`), PII, e compliance.
    *   `audit()`: Mantém log imutável de todas as decisões.
*   **Integration**:
    *   Input: Descrição da ação ("Run exploit on 10.0.0.1").
    *   Output: `EthicalDecision` (Enum: `APPROVED`, `REJECTED`, `REQUIRES_HUMAN`).
*   **File**: [`tools/magistrate.py`](file:///media/juan/DATA/vertice-cyber/tools/magistrate.py)

### 4. Wargame Executor (`tools.wargame.WargameExecutor`)
*   **Role**: Operador Ofensivo. Executa ações simuladas (Atomic Red Team).
*   **Capabilities**:
    *   `run_simulation(scenario_id)`: Executa uma Tática MITRE específica (ex: T1048 Exfiltration).
    *   `list_scenarios()`: Catálogo de ataques disponíveis.
*   **Safety**: Possui wrapper de segurança (`WargameSafetyManager`) que consulta o Magistrate antes de qualquer `exec`.
*   **File**: [`tools/wargame.py`](file:///media/juan/DATA/vertice-cyber/tools/wargame.py)

### 5. Patch Validator ML (`tools.patch_ml.PatchValidator`)
*   **Role**: Auditor de Código / Blue Team.
*   **Capabilities**:
    *   `validate_patch(diff)`: Analisa código (Python/JS) procurando padrões vulneráveis (Regex + ML básico).
    *   Detecta: SQL Injection, Command Injection, Hardcoded Secrets, Pickle RCE.
*   **Integration**:
    *   Input: Diff string ou path de arquivo.
    *   Output: `ValidationResult` (is_safe: bool, issues: List[str]).
*   **File**: [`tools/patch_ml.py`](file:///media/juan/DATA/vertice-cyber/tools/patch_ml.py)

### 6. Vertex AI Layer (`tools.mcp_ai_tools`)
*   **Role**: O "Cérebro" Sintético. Conecta os pontos quando a lógica determinística falha.
*   **Capabilities**:
    *   `ai_integrated_assessment`: Funde dados de Threat + OSINT + Compliance em um report narrativo.
    *   `ai_stream_analysis`: Processamento em tempo real (Chain-of-Thought).
*   **Integration**:
    *   Usa `google-cloud-aiplatform` para chamar modelos Gemini Pro.
*   **File**: [`tools/mcp_ai_tools.py`](file:///media/juan/DATA/vertice-cyber/tools/mcp_ai_tools.py)
