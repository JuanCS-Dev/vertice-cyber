# Dashboard Audit Report

> **Data:** 2026-01-20  
> **Fase:** 5.1  
> **Status:** ✅ Completo (V2 - Updated)
> **Gaps Resolved:** 5/5

---

## Arquitetura Atual

| Item | Detalhe |
|------|---------|
| **Framework** | React 19.2.3 |
| **Build Tool** | Vite 6.2.0 |
| **TypeScript** | 5.8.2 |
| **Styling** | Tailwind CSS via CDN |
| **3D Engine** | Three.js 0.169.0 + React Three Fiber |
| **Charts** | Recharts 2.12.7 |
| **Icons** | Lucide React 0.454.0 |
| **State Management** | React useState (local) |
| **HTTP Client** | ❌ Nenhum instalado |
| **WebSocket** | ❌ Não configurado |

---

## Estrutura de Arquivos

```
dashboard/
├── index.html           # Entry point + Tailwind config + import maps
├── index.tsx            # React root render
├── App.tsx              # ⚠️ MAIN - Mock simulation logic
├── types.ts             # ⚠️ MOCK - Type definitions + generators
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
├── .env.local           # API URL placeholder
├── components/
│   ├── DashboardWidgets.tsx  # ThreatFeed, AgentList, GenAIConsole, etc
│   ├── NeuralNetwork.tsx     # 3D brain visualization
│   └── UI.tsx                # GlassCard, Badge primitives
└── metadata.json        # Dashboard metadata
```

---

## Mock Data Locations

### 1. `types.ts` (Linhas 42-82)

```typescript
// FUNÇÃO GERADORA - Cria 12 agents mock
export const generateAgents = (count: number): Agent[] => { ... }

// DADOS ESTÁTICOS - Compliance inicial
export const INITIAL_METRICS: ComplianceMetric[] = [ ... ]

// DADOS ESTÁTICOS - Threats iniciais  
export const INITIAL_THREATS: Threat[] = [ ... ]
```

**Complexidade de Substituição:** 🟢 BAIXA  
Os dados podem ser facilmente substituídos por chamadas API.

---

### 2. `App.tsx` (Linhas 32-43, 51-113)

```typescript
// SETUP INICIAL (Linhas 32-43)
useEffect(() => {
  setAgents(generateAgents(12));  // ⚠️ MOCK: Gera 12 agents fake
  const initialNetData = Array.from({ length: 20 }).map(...);  // ⚠️ MOCK
  setNetworkData(initialNetData);
}, []);

// SIMULATION LOOP (Linhas 51-113)
useEffect(() => {
  const interval = setInterval(() => {
    // Simula tráfego de rede
    setNetworkData(...);
    
    // Atualiza agents randomicamente
    setAgents(prevAgents => prevAgents.map(agent => {
      let change = (Math.random() - 0.4) * 5;  // ⚠️ MOCK
      ...
    }));

    // Gera threats/logs aleatórios
    if (Math.random() > 0.85) {
      const newThreat: Threat = { ... };  // ⚠️ MOCK
    }
  }, 2000);
}, [addLog]);
```

**Complexidade de Substituição:** 🟡 MÉDIA  
Precisa refatorar para WebSocket + fetch inicial.

---

## Widget x Data Mapping

| Widget | Componente | Props | Fonte de Dados Esperada |
|--------|------------|-------|------------------------|
| Agent List | `AgentList` | `agents: Agent[]` | MCP Tools list + status |
| Threat Feed | `ThreatFeed` | `threats: Threat[]` | Event Bus (threat.detected) |
| Network Graph | `NetworkGraph` | `data: NetworkMetric[]` | MCP metrics / polling |
| Compliance Radar | `ComplianceRadar` | `data: ComplianceMetric[]` | compliance_assess_tool |
| GenAI Console | `GenAIConsole` | `logs: string[]` | Event Bus (system.tool.called) |
| Neural Network | `NeuralNetwork` | `agents: Agent[]` | Same as AgentList |

---

## API Contract Esperado

### GET /mcp/tools/list

```typescript
interface ToolListResponse {
  tools: Array<{
    name: string;        // "ethical_validate_tool"
    agent: string;       // "Ethical Magistrate"
    description: string; // Tool description
    category: string;    // "governance" | "intelligence" | "offensive"
  }>;
}
```

### POST /mcp/tools/execute

```typescript
interface ToolExecuteRequest {
  tool_name: string;
  arguments: Record<string, any>;
}

interface ToolExecuteResponse {
  success: boolean;
  result?: any;
  error?: string;
  execution_time_ms?: number;
}
```

### WS /mcp/events

```typescript
interface MCPEvent {
  event_type: string;   // "threat.detected", "ethics.validation.completed"
  data: Record<string, any>;
  source: string;       // "osint_hunter", "magistrate"
  timestamp: string;    // ISO 8601
  correlation_id?: string;
}
```

---

## Gaps para Integração

### Gap 1: MCP não expõe HTTP

| Aspecto | Estado Atual | Necessário |
|---------|--------------|------------|
| Transport | stdio/SSE | HTTP REST + WebSocket |
| Endpoint | Nenhum | `/mcp/*` REST API |

**Solução:** Criar `mcp_http_bridge.py` com FastAPI.

---

### Gap 2: Dashboard não tem HTTP client

| Aspecto | Estado Atual | Necessário |
|---------|--------------|------------|
| HTTP | Nenhum | fetch ou axios |
| WebSocket | Nenhum | Native WebSocket |

**Solução:** Criar camada `src/services/` com:
- `mcpClient.ts` - Base HTTP client
- `agentService.ts` - Agent CRUD
- `eventStream.ts` - WebSocket wrapper

---

### Gap 3: Type Mismatch

| Dashboard Type | MCP Type | Mapping Necessário |
|----------------|----------|-------------------|
| `Agent.health` | N/A | Calcular de metrics |
| `Agent.position` | N/A | Manter geração local |
| `Threat.status` | Event data | Mapear de event_type |

**Solução:** Criar funções de transformação `mcpToAgent()`, `eventToThreat()`.

---

### Gap 4: Sem Real-Time Events

| Aspecto | Estado Atual | Necessário |
|---------|--------------|------------|
| Updates | setInterval 2000ms | WebSocket |
| Source | Math.random() | MCP Event Bus |

**Solução:** Implementar `EventStreamService` com auto-reconnect.

---

## Estimativa de Complexidade

| Fase | Complexidade | Esforço |
|------|--------------|---------|
| 5.1 Audit | ✅ Feito | - |
| 5.2 HTTP Bridge | 🟡 Média | ~2h |
| 5.3 Dashboard Services | 🟡 Média | ~2h |
| 5.4 Replace Mocks | 🟢 Baixa | ~1h |
| 5.5 Real-time Events | 🟡 Média | ~1h |
| 5.6 Production Hardening | 🟢 Baixa | ~1h |
| 5.7 Testing | 🟡 Média | ~1h |

**Total Estimado:** ~8h de trabalho

---

## MCP Tools Disponíveis

O servidor MCP já expõe **20+ tools**:

### Governance
- `ethical_validate_tool` - Validação ética

### Intelligence  
- `threat_analyze_tool` - Análise de ameaças
- `threat_intelligence_tool` - Busca de inteligência
- `threat_predict_tool` - Predição de ameaças
- `osint_investigate_tool` - Investigação OSINT
- `osint_breach_check_tool` - Verificação de breaches
- `osint_google_dork_tool` - Google dorking
- `compliance_assess_tool` - Avaliação de compliance
- `compliance_report_tool` - Relatório de compliance
- `compliance_check_tool` - Check de requisito

### Offensive
- `wargame_list_scenarios_tool` - Lista cenários
- `wargame_run_simulation_tool` - Executa simulação
- `patch_validate_tool` - Valida patches
- `cybersec_recon_tool` - Reconhecimento

### AI-Powered (Vertex AI)
- `ai_threat_analysis` - Análise IA de ameaças
- `ai_compliance_assessment` - Avaliação IA de compliance
- `ai_osint_analysis` - Análise OSINT com IA
- `ai_stream_analysis` - Análise streaming
- `ai_integrated_assessment` - Avaliação integrada

---

## Próximos Passos

1. ✅ **Este documento** - Audit completo
2. ⏳ Criar `mcp_http_bridge.py`
3. ⏳ Criar camada de serviços no dashboard
4. ⏳ Substituir mocks por chamadas reais
5. ⏳ Implementar eventos real-time
6. ⏳ Testes E2E
