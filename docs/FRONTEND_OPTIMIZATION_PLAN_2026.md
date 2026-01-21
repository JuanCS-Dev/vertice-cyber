# 🚀 PLANO DE OTIMIZAÇÃO FRONTEND 2026 (Zero Debt)

**Status:** APROVADO PARA EXECUÇÃO
**Target:** Vértice Cyber Dashboard v3.0
**Filosofia:** "Zero Technical Debt, Maximum Lethality"

---

## 1. Diagnóstico Brutal & Visão Geral
O dashboard atual é visualmente impactante mas arquiteturalmente frágil. Ele sofre de "Monolith Syndrome" (`App.tsx` gigante), "Simulation Dependency" (dados falsos misturados com reais) e "Performance Naivety" (renderizações globais por timer).

Para atingir o padrão 2026, não faremos "patches". Faremos uma reestruturação cirúrgica baseada em **React 19 Principles** e **State Colocation**.

---

## 2. Arquitetura Alvo (The 2026 Standard)

### A. Decomposição do Monólito
O `App.tsx` deve ser apenas um *Coordinator*. A lógica deve ser movida para Context Providers e Hooks especializados.

**Estrutura Proposta:**
```tsx
<ErrorBoundary>
  <TelemetryProvider>      {/* Gerencia WebSocket Global & Throttling */}
    <AgentStateProvider>   {/* Gerencia Estado dos Agentes (Zustand ou Context) */}
      <AppLayout>
        <Header />         {/* Consome TelemetryContext apenas */}
        <MainWorkspace>
          <AgentRouter />  {/* Renderiza o painel correto */}
        </MainWorkspace>
        <Sidebar />        {/* Consome AgentStateContext */}
      </AppLayout>
    </AgentStateProvider>
  </TelemetryProvider>
</ErrorBoundary>
```

### B. Gestão de Estado (The Truth)
1.  **Global (Low Frequency):** Autenticação, Tema, Conexão Socket. -> *React Context*.
2.  **Global (High Frequency):** Logs, Métricas de CPU, Latência. -> *Zustand* (fora da árvore do React para evitar re-renders) ou *Context com Seletores*.
    *   *Decisão 2026:* Usaremos **React Context + useReducer** com otimização via **React Compiler** (memoização automática), mas protegendo componentes folha com `memo` até que o compilador seja onipresente.
3.  **Local:** Formulários, UI state (modais, abas). -> *useState*.

---

## 3. Plano de Implementação Tático

### FASE 1: Estabilização do Core (Performance First)
**Objetivo:** Parar os re-renders globais e vazamentos de memória.

1.  **Isolar o "Heartbeat" (Latência):**
    *   **Ação:** Remover `latencyPoints` e o `setInterval` do `App.tsx`.
    *   **Solução:** Criar componente `<LatencyWidget />` que assina o WebSocket diretamente ou usa um hook isolado. O resto do App não deve saber que a latência mudou.
    *   **Real Data:** Implementar `eventStream.ping()` para medir RTT real.

2.  **Virtualização de Logs (Memory Shield):**
    *   **Ação:** Refatorar `useMCPAgents` para não armazenar logs infinitamente no *state*.
    *   **Solução:** Usar um **Circular Buffer** (classe TS pura) fora do React State para armazenar os últimos 10k logs, e sincronizar com o React apenas um `slice` visível (ex: últimos 100) via `useSyncExternalStore` (padrão React 18/19).

3.  **Geometry Disposal Automática (3D):**
    *   **Já realizado:** O patch no `NeuralNetwork.tsx` foi o primeiro passo.
    *   **Próximo passo:** Abstrair isso para um hook `useDisposableGeometry` para garantir que qualquer nova visualização 3D futura seja segura por padrão.

### FASE 2: Conexão com a Realidade (No More Fakes)
**Objetivo:** Remover todos os dados simulados ("Air Gaps").

1.  **Posicionamento 3D Determinístico:**
    *   **Problema:** Posições aleatórias a cada reload.
    *   **Solução:** Criar função `hashToPosition(agentId)` que gera coordenadas XYZ fixas baseadas no ID do agente. Isso garante persistência visual sem banco de dados.

2.  **Upload de Arquivo Real:**
    *   **Ação:** Atualizar `VisionarySentinelPanel`.
    *   **Backend:** Garantir que o MCP Agent suporte `multipart/form-data` ou base64 real.
    *   **Frontend:** Validar tamanho do arquivo antes do envio (Client-side protection).

### FASE 3: UX & Acessibilidade (Polimento)
**Objetivo:** Tornar o "Alien UI" utilizável por humanos.

1.  **Tipografia Escalonável:**
    *   **Ação:** Substituir tamanhos fixos (`text-[9px]`) por classes utilitárias semânticas do Tailwind (`text-xs`, `text-caption`) configuradas no tema para serem legíveis (min 11px/12px).
    *   **Contraste:** Audit de cores. O cinza `text-slate-500` sobre fundo preto pode falhar em WCAG AA. Ajustar para `text-slate-400`.

2.  **Feedback de Erro Robusto:**
    *   **Ação:** Criar um `<ToastRegion />` global.
    *   **Lógica:** Quando o WebSocket cair ou um agente falhar, disparar um Toast visual, não apenas um log no terminal.

---

## 4. Detalhes Técnicos Críticos

### Otimização de Logs (Circular Buffer Pattern)
```typescript
class LogBuffer {
  private buffer: LogEntry[];
  private capacity: number;
  private listeners: Set<() => void> = new Set();

  constructor(capacity = 1000) {
    this.buffer = [];
    this.capacity = capacity;
  }

  add(entry: LogEntry) {
    if (this.buffer.length >= this.capacity) {
      this.buffer.shift(); // Remove oldest
    }
    this.buffer.push(entry);
    this.notify();
  }

  subscribe(listener: () => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getSnapshot() {
    return this.buffer; // Ou uma versão imutável se necessário
  }
  
  // ... notify logic
}
// Uso com useSyncExternalStore no componente
```

### 3D Determinístico
```typescript
function getAgentPosition(id: string): [number, number, number] {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = (hash << 5) - hash + id.charCodeAt(i);
  // Normalize to sphere radius R
  const phi = Math.acos -1 + (2 * (hash % 100)) / 100;
  const theta = Math.sqrt(Math.PI * (hash % 100)) * phi;
  return [
    R * Math.cos(theta) * Math.sin(phi),
    R * Math.sin(theta) * Math.sin(phi),
    R * Math.cos(phi)
  ];
}
```

---

## 5. Cronograma de Execução (Sugerido)

1.  **Dia 1:** Refatoração do `App.tsx` (Contexts) + Circular Buffer para Logs.
2.  **Dia 2:** Implementação do `LatencyWidget` real e limpeza de dados fake.
3.  **Dia 3:** Polimento de UI (Fontes) e Acessibilidade.
4.  **Dia 4:** Teste de Stress (Wargame com 10k logs/segundo).

---

**Assinado:** Gemini UI/UX Architect (2026 Edition)
