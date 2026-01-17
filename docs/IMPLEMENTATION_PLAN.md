# VERTICE CYBER: PLANO DE IMPLEMENTAÇÃO DETALHADO

> **Versão:** 1.0.0  
> **Data:** 17 Janeiro 2026  
> **Autor:** Vertice AI Team  
> **Destinatário:** Agente Implementador (ambiente offline)  
> **Objetivo:** Guia autocontido para implementação dos 11 Meta-Agents MCP

---

# 📋 TABELA DE CONTEÚDOS

1. [Resumo Executivo](#resumo-executivo)
2. [Rastreamento de Implementação](#rastreamento-de-implementação)
3. [Fase 0: Foundation (MCP Server Core)](#fase-0-foundation-mcp-server-core)
4. [Fase 1: Governance Tools](#fase-1-governance-tools)
5. [Fase 2: Intelligence Tools](#fase-2-intelligence-tools)
6. [Fase 3: Immune System Tools](#fase-3-immune-system-tools)
7. [Fase 4: Offensive Tools](#fase-4-offensive-tools)
8. [Fase 5: Integration & Testing](#fase-5-integration--testing)
9. [Apêndices: Documentação Completa de Tecnologias](#apêndices)

---

# 📊 RASTREAMENTO DE IMPLEMENTAÇÃO

> **Instrução:** Atualize esta seção conforme for completando cada item.

## Status Geral

| Fase | Status | Progresso | Última Atualização |
|------|--------|-----------|-------------------|
| Fase 0: Foundation | 🔴 Pendente | 0% | - |
| Fase 1: Governance | 🔴 Pendente | 0% | - |
| Fase 2: Intelligence | 🔴 Pendente | 0% | - |
| Fase 3: Immune System | 🔴 Pendente | 0% | - |
| Fase 4: Offensive | 🔴 Pendente | 0% | - |
| Fase 4.5: CyberSec Basic | 🔴 Pendente | 0% | - |
| Fase 5: Integration | 🔴 Pendente | 0% | - |
| Fase 6: Dashboard | 🔴 Pendente | 0% | - |

## Log de Implementação

```
[YYYY-MM-DD HH:MM] - [FASE] - [ITEM] - [STATUS] - [NOTAS]
-----------------------------------------------------------
# Exemplo:
# [2026-01-18 10:30] - Fase 0 - mcp_server.py - ✅ COMPLETO - Servidor base criado
# [2026-01-18 11:00] - Fase 0 - event_bus.py - 🔄 EM PROGRESSO - Falta testar
```

## Checklist Detalhado

### Fase 0: Foundation
- [ ] 0.0 - Leitura da documentação FastMCP
- [ ] 0.1 - Atualizar `requirements.txt`
- [ ] 0.2 - Criar `core/settings.py` (Pydantic Settings)
- [ ] 0.3 - Criar `core/event_bus.py`
- [ ] 0.4 - Criar `core/memory.py`
- [ ] 0.5 - Criar `mcp_server.py`
- [ ] 0.6 - Criar `tools/__init__.py`
- [ ] 0.7 - Smoke test do servidor

### Fase 1: Governance
- [ ] 1.0 - Pesquisa web (já embarcada neste doc)
- [ ] 1.1 - Análise do código existente `agents/ethical_magistrate/main.py`
- [ ] 1.2 - Criar `tools/magistrate.py`
- [ ] 1.3 - Testes unitários
- [ ] 1.4 - Integração com MCP server

### Fase 2: Intelligence (3 tools)
- [ ] 2.0 - Pesquisa web (já embarcada neste doc)
- [ ] 2.1 - Criar `tools/osint.py`
- [ ] 2.2 - Criar `tools/threat.py`
- [ ] 2.3 - Criar `tools/compliance.py`
- [ ] 2.4 - Testes unitários

### Fase 3: Immune System (3 tools)
- [ ] 3.0 - Pesquisa web (já embarcada neste doc)
- [ ] 3.1 - Criar `tools/immune.py`
- [ ] 3.2 - Criar `tools/sentinel.py`
- [ ] 3.3 - Criar `tools/watcher.py`
- [ ] 3.4 - Testes unitários

### Fase 4: Offensive (2 tools)
- [ ] 4.0 - Pesquisa web (já embarcada neste doc)
- [ ] 4.1 - Criar `tools/wargame.py`
- [ ] 4.2 - Criar `tools/patch_ml.py`
- [ ] 4.3 - Testes unitários

### Fase 4.5: CyberSec Basic (Agent 12 - Investigador + Pentester)
- [ ] 4.5.0 - Pesquisa web 2026 (pentest tools, recon APIs)
- [ ] 4.5.1 - Criar `tools/cybersec_basic.py`
- [ ] 4.5.2 - Implementar reconnaissance tools (port scan, subdomain enum)
- [ ] 4.5.3 - Implementar vulnerability assessment básico
- [ ] 4.5.4 - Implementar web app security checks (OWASP Top 10)
- [ ] 4.5.5 - Testes unitários
- [ ] 4.5.6 - Teste real: auditar segurança do vertice-code webapp

### Fase 5: Integration
- [ ] 5.1 - Criar `tools/cli.py`
- [ ] 5.2 - Criar `tools/bridge.py`
- [ ] 5.3 - Testes E2E
- [ ] 5.4 - Documentação final
- [ ] 5.5 - Configuração MCP para vertice-code

### Fase 6: Dashboard Web (Gemini vai implementar)
- [ ] 6.1 - Setup projeto webapp simples
- [ ] 6.2 - UI para visualizar status dos agents
- [ ] 6.3 - Interface para chamar MCP tools
- [ ] 6.4 - Conexão com MCP server via SSE/HTTP
- [ ] 6.5 - Deploy e integração

---

# 📝 RESUMO EXECUTIVO

## Objetivo
Transformar o Vertice Cyber de uma arquitetura Docker-heavy (11 containers) para **12 Meta-Agents expostos via MCP** (Model Context Protocol) em um único processo Python.

## Benefícios
- **Startup:** De ~2min para <2seg
- **Memória:** De ~8GB para <200MB
- **Complexidade:** De 11 containers para 1 processo
- **Integração:** Acesso nativo via vertice-code/Claude/Gemini

## Métricas de Sucesso 2026

| Métrica | Target | Justificativa |
|---------|--------|---------------|
| Startup Time | <2s | Produtividade |
| Memory Usage | <200MB | Permite edge deployment |
| Threat Detection | **<100ms** | Requisito 2026 para autonomous response |
| ATT&CK Coverage | >80% técnicas | Defesa abrangente |
| False Positives | <5% | Qualidade > Quantidade |

## Stack Tecnológico (Atualizado 2026)

### Core Framework
| Componente | Tecnologia | Versão |
|------------|------------|--------|
| MCP Framework | FastMCP | 2.14.x |
| Validação | Pydantic | 2.5.x |
| Async | asyncio | Python 3.11+ |
| HTTP Client | httpx | 0.27.x |

### Security & Threat Intel (NOVO)
| Componente | Tecnologia | Uso |
|------------|------------|-----|
| MITRE ATT&CK | pyattck | Threat mapping Enterprise |
| **MITRE ATLAS** | custom | AI/ML attack defense (14 novas técnicas) |
| OSINT Avançado | shodan, censys | IoT/exposed services |
| Vuln Management | nvdlib | NVD database |
| Exploit Scoring | EPSS API | Prioritização inteligente |
| Actively Exploited | KEV Catalog | CISA feed |

### Pentest & Scanning (NOVO)
| Componente | Tecnologia | Uso |
|------------|------------|-----|
| Vuln Scanner | nuclei | 9000+ templates |
| Subdomain Enum | subfinder, amass | Asset discovery |
| Web Fuzzing | ffuf | Directory/param fuzzing |
| SAST | semgrep, bandit | Code security |

---

# 🔴 ENHANCEMENTS 2026 (do Brutal Review)

> Baseado em: MITRE ATT&CK v18, MITRE ATLAS, Palo Alto 2026 Forecast, CyberArk

## Requisitos Críticos Adicionados

### 1. Agent Identity System (P0)
```python
# Cada agent tem identidade criptográfica
class AgentIdentity:
    agent_id: str           # UUID único
    public_key: bytes       # Ed25519
    permissions: list[str]  # Least privilege
    rate_limits: RateLimits # Por agent + recurso
```

### 2. MITRE ATLAS Integration (P0)
- 14 novas técnicas para AI/ML attacks
- Memory Poisoning Detection (vetor #1 em 2026)
- Prompt Injection Detection
- Agent Compromise Detection

### 3. Behavioral Anomaly Detection (P0)
- ML-based (XGBoost para MVP)
- Latência <100ms
- Drift detection entre baseline e current behavior

### 4. Enhanced OSINT (P1)
- Shodan: IoT/exposed services
- Censys: Internet-wide scanning
- Amass: OWASP asset discovery
- Continuous monitoring 24/7

### 5. Continuous Purple Teaming (P1)
- Breach & Attack Simulation (BAS)
- Atomic Red Team integration
- Threat resilience metrics automáticas

### 6. Smart Vulnerability Prioritization (P2)
- EPSS Score (probabilidade de exploração)
- KEV Catalog (actively exploited)
- CVSS v4.0 + Asset Criticality

### 7. Autonomous Response (P2)
- Immune system que CURA, não só alerta
- <100ms para actions automatizadas
- Isolate, Block, Revoke, Killswitch

---

# 🚀 FASE 0: FOUNDATION (MCP SERVER CORE)

## 0.0 Pesquisa Web 2026 (Resumo Embarcado)

### FastMCP 2.0 - Estado da Arte (Janeiro 2026)

**O que é FastMCP:**
FastMCP é um framework Python de alto nível para criar servidores e clientes MCP (Model Context Protocol). Ele abstrai a complexidade do protocolo, permitindo foco na funcionalidade.

**Versões:**
- FastMCP 1.0: Integrado ao SDK oficial MCP em 2024
- FastMCP 2.0: Versão atual, production-ready (2.14.3 em Jan 2026)
- FastMCP 3.0: Em desenvolvimento (use `fastmcp<3` para estabilidade)

**Key Features:**
- Decorators Python simples (`@mcp.tool()`, `@mcp.resource()`)
- Suporte async/sync automático
- Integração Pydantic para inputs/outputs complexos
- Transports: stdio, SSE, Streamable HTTP
- Geração automática de JSON Schema
- Context object para logging e recursos

---

## 0.5 Análise do Código Existente

### Arquivos Existentes no Projeto

```
vertice-cyber/
├── __init__.py                           # Package init
├── core/
│   └── __init__.py                       # AgentBase, AgentConfig, validate_with_magistrate
├── agents/
│   └── ethical_magistrate/
│       ├── __init__.py
│       └── main.py                       # EthicalMagistrateAgent (FastAPI-based)
├── main.py                               # Entry point atual (Docker-oriented)
└── requirements.txt                      # Deps atuais
```

### Código a Reutilizar

**De `core/__init__.py`:**
- `AgentConfig` → Migrar para Pydantic Settings
- `validate_with_magistrate()` → Inspirar tool `ethical_validate`
- `AgentBase` → Não usar (era para FastAPI)
- `get_agent_health()` → Reutilizar padrão

**De `agents/ethical_magistrate/main.py`:**
- `EthicalDecisionType` → Reutilizar enum
- `EthicalDecisionResult` → Reutilizar modelo Pydantic
- `_is_dangerous_action()` → Reutilizar lógica
- 7-phase validation pipeline → Expandir

---

## 0.1 Atualização do requirements.txt

### Arquivo: `requirements.txt`

**SUBSTITUIR O CONTEÚDO COMPLETO POR:**

```python
# =============================================================================
# VERTICE CYBER - MCP-BASED META-AGENTS
# Versão: 2.0.0 (MCP Refactor)
# Data: Janeiro 2026
# =============================================================================

# -----------------------------------------------------------------------------
# CORE MCP FRAMEWORK
# -----------------------------------------------------------------------------
# FastMCP 2.x - Framework de alto nível para MCP servers
# Docs: https://gofastmcp.com
# IMPORTANTE: Pin para <3 para evitar breaking changes
fastmcp>=2.14.0,<3.0.0

# MCP SDK oficial (dependência do FastMCP)
mcp>=1.9.0

# -----------------------------------------------------------------------------
# VALIDATION & SETTINGS
# -----------------------------------------------------------------------------
# Pydantic 2.x - Validação de dados e settings
# Docs: https://docs.pydantic.dev/latest/
pydantic>=2.5.0,<3.0.0
pydantic-settings>=2.1.0

# -----------------------------------------------------------------------------
# ASYNC HTTP CLIENT
# -----------------------------------------------------------------------------
# httpx - Cliente HTTP async moderno
httpx>=0.27.0

# -----------------------------------------------------------------------------
# SECURITY & OSINT TOOLS
# -----------------------------------------------------------------------------
# HaveIBeenPwned API client
haveibeenpwned-py>=1.0.0

# MITRE ATT&CK Framework
pyattck>=7.0.0

# Cryptography para hashing seguro
cryptography>=41.0.0

# -----------------------------------------------------------------------------
# DATA & STORAGE
# -----------------------------------------------------------------------------
# SQLAlchemy para persistência opcional
sqlalchemy>=2.0.0

# Redis para cache opcional
redis>=5.0.0

# -----------------------------------------------------------------------------
# OBSERVABILITY
# -----------------------------------------------------------------------------
# Rich para console output
rich>=13.7.0

# Logging estruturado
python-json-logger>=2.0.0

# -----------------------------------------------------------------------------
# DEVELOPMENT
# -----------------------------------------------------------------------------
pytest>=7.4.0
pytest-asyncio>=0.23.0
ruff>=0.1.0

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------
python-dotenv>=1.0.0
```

---

## 0.2 Settings com Pydantic (core/settings.py)

### Documentação Pydantic Settings (Embarcada)

**Conceito:**
`pydantic-settings` permite carregar configurações de:
1. Environment variables
2. Arquivos `.env`
3. Valores default

**Padrões 2026:**
- Use `SettingsConfigDict` ao invés de `Config` class
- Use `SecretStr` para credenciais
- Agrupe settings relacionados em nested models

### Arquivo: `core/settings.py`

```python
"""
Vertice Cyber - Settings Management
Usa Pydantic Settings v2 para configuração type-safe.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIKeysSettings(BaseSettings):
    """API Keys para serviços externos."""
    
    model_config = SettingsConfigDict(
        env_prefix="VERTICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    hibp_api_key: Optional[SecretStr] = Field(
        default=None,
        description="API key para HaveIBeenPwned"
    )
    openai_api_key: Optional[SecretStr] = Field(default=None)
    anthropic_api_key: Optional[SecretStr] = Field(default=None)
    gcp_project_id: Optional[str] = Field(default=None)


class ServerSettings(BaseSettings):
    """Configurações do servidor MCP."""
    
    model_config = SettingsConfigDict(
        env_prefix="VERTICE_SERVER_",
        env_file=".env",
        extra="ignore",
    )
    
    transport: str = Field(default="stdio")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")


class EthicalSettings(BaseSettings):
    """Configurações do Ethical Magistrate."""
    
    model_config = SettingsConfigDict(
        env_prefix="VERTICE_ETHICS_",
        extra="ignore",
    )
    
    dangerous_keywords: list[str] = Field(
        default=[
            "exploit", "attack", "brute_force", "ddos",
            "malware", "ransomware", "zero_day", "exfiltrate"
        ]
    )
    always_require_approval: list[str] = Field(
        default=["delete_data", "modify_firewall", "execute_payload"]
    )
    human_review_timeout: int = Field(default=300)


class Settings(BaseSettings):
    """Settings principal agregando todos os sub-settings."""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    project_name: str = Field(default="Vertice Cyber")
    version: str = Field(default="2.0.0")
    
    api_keys: APIKeysSettings = Field(default_factory=APIKeysSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    ethics: EthicalSettings = Field(default_factory=EthicalSettings)


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton dos settings."""
    return Settings()


settings = get_settings()
```

---

## 0.3 Event Bus Async (core/event_bus.py)

### Documentação asyncio Event Bus (Embarcada)

**Conceito:**
Event bus in-memory para comunicação desacoplada entre tools/agents.

**Padrão 2026:**
- Use `asyncio.Queue` para mensagens
- Use `asyncio.create_task()` para handlers não-bloqueantes
- Use `defaultdict` para mapear event_type → handlers

### Arquivo: `core/event_bus.py`

```python
"""
Vertice Cyber - Async Event Bus
Comunicação in-memory entre tools usando pub/sub pattern.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos suportados."""
    
    # Governance
    ETHICS_VALIDATION_REQUESTED = "ethics.validation.requested"
    ETHICS_VALIDATION_COMPLETED = "ethics.validation.completed"
    ETHICS_HUMAN_REVIEW_REQUIRED = "ethics.human_review.required"
    
    # Intelligence
    OSINT_INVESTIGATION_STARTED = "osint.investigation.started"
    OSINT_INVESTIGATION_COMPLETED = "osint.investigation.completed"
    OSINT_BREACH_DETECTED = "osint.breach.detected"
    
    # Threat
    THREAT_DETECTED = "threat.detected"
    THREAT_PREDICTED = "threat.predicted"
    THREAT_MITRE_MAPPED = "threat.mitre.mapped"
    
    # Immune
    IMMUNE_RESPONSE_TRIGGERED = "immune.response.triggered"
    IMMUNE_ANTIBODY_DEPLOYED = "immune.antibody.deployed"
    
    # System
    SYSTEM_HEALTH_CHECK = "system.health.check"
    SYSTEM_ERROR = "system.error"
    SYSTEM_TOOL_CALLED = "system.tool.called"


@dataclass
class Event:
    """Estrutura de um evento."""
    event_type: EventType
    data: Dict[str, Any]
    source: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """Event Bus assíncrono para comunicação entre tools."""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history: int = 1000
    
    def on(self, event_type: EventType):
        """Decorator para registrar handler."""
        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers[event_type].append(handler)
            return handler
        return decorator
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Registra handler programaticamente."""
        self._handlers[event_type].append(handler)
    
    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str,
        correlation_id: Optional[str] = None
    ) -> Event:
        """Emite evento para handlers."""
        event = Event(
            event_type=event_type,
            data=data,
            source=source,
            correlation_id=correlation_id
        )
        
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            asyncio.create_task(self._safe_call(handler, event))
        
        return event
    
    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Chama handler com tratamento de erro."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in handler {handler.__name__}: {e}")
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Retorna histórico filtrado."""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]


_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Retorna singleton do event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
```

---

## 0.4 Memory Pool (core/memory.py)

### Arquivo: `core/memory.py`

```python
"""
Vertice Cyber - Per-Agent Memory Pool
Memória local para cada tool.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Uma entrada na memória."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None


class AgentMemory:
    """Memória local para um agent/tool."""
    
    def __init__(self, agent_name: str, max_entries: int = 10000):
        self.agent_name = agent_name
        self.max_entries = max_entries
        self._store: Dict[str, MemoryEntry] = {}
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Armazena valor."""
        if len(self._store) >= self.max_entries:
            self._evict_oldest()
        
        self._store[key] = MemoryEntry(
            key=key, value=value, ttl_seconds=ttl_seconds
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Recupera valor."""
        entry = self._store.get(key)
        if entry is None:
            return default
        
        if entry.ttl_seconds is not None:
            age = (datetime.utcnow() - entry.created_at).total_seconds()
            if age > entry.ttl_seconds:
                del self._store[key]
                return default
        
        entry.access_count += 1
        return entry.value
    
    def delete(self, key: str) -> bool:
        """Remove entrada."""
        if key in self._store:
            del self._store[key]
            return True
        return False
    
    def _evict_oldest(self) -> None:
        """Remove entrada mais antiga."""
        if self._store:
            oldest = min(self._store.keys(), key=lambda k: self._store[k].created_at)
            del self._store[oldest]


class MemoryPool:
    """Pool de memórias para todos os agents."""
    
    def __init__(self):
        self._memories: Dict[str, AgentMemory] = {}
    
    def get_memory(self, agent_name: str) -> AgentMemory:
        """Retorna memória para um agent."""
        if agent_name not in self._memories:
            self._memories[agent_name] = AgentMemory(agent_name)
        return self._memories[agent_name]


_memory_pool: Optional[MemoryPool] = None


def get_memory_pool() -> MemoryPool:
    """Retorna singleton do memory pool."""
    global _memory_pool
    if _memory_pool is None:
        _memory_pool = MemoryPool()
    return _memory_pool


def get_agent_memory(agent_name: str) -> AgentMemory:
    """Atalho para obter memória de um agent."""
    return get_memory_pool().get_memory(agent_name)
```

---

## 0.5 MCP Server Principal (mcp_server.py)

### Documentação FastMCP 2.0 Completa (Embarcada)

**Instalação:**
```bash
pip install "fastmcp>=2.14.0,<3.0.0"
```

**Decorators Principais:**
```python
from fastmcp import FastMCP, Context

mcp = FastMCP("server-name")

@mcp.tool()
async def my_tool(ctx: Context, param: str) -> dict:
    """Docstring vira descrição da tool."""
    ctx.info("Logging via context")
    return {"result": param}

@mcp.resource("uri://path")
async def my_resource() -> str:
    """Resource que LLM pode ler."""
    return "data"
```

**Transports:**
- `stdio`: Para Claude Desktop, Cursor
- `sse`: Server-Sent Events
- `streamable-http`: HTTP bidirecional

### Arquivo: `mcp_server.py`

```python
#!/usr/bin/env python3
"""
Vertice Cyber - MCP Server Principal
Expõe 11 Meta-Agents como MCP Tools.
"""

import argparse
import logging
import sys

from fastmcp import FastMCP, Context

from core.settings import get_settings, settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_memory_pool

logging.basicConfig(
    level=getattr(logging, settings.server.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vertice_cyber")


# =============================================================================
# MCP SERVER INSTANCE
# =============================================================================

mcp = FastMCP(
    name="vertice-cyber",
    version="2.0.0",
    description="BIOGUARD 2028 - 11 Meta-Agents para Cyber Defense"
)


# =============================================================================
# CORE RESOURCES
# =============================================================================

@mcp.resource("vertice://status")
async def get_system_status() -> str:
    """Status geral do sistema Vertice Cyber."""
    return f"""
# Vertice Cyber Status
- Name: {settings.project_name}
- Version: {settings.version}
- Transport: {settings.server.transport}
"""


@mcp.resource("vertice://agents")
async def get_agents_list() -> str:
    """Lista de todos os agents disponíveis."""
    return """
# Vertice Cyber Agents
| # | Agent | Tier | Status |
|---|-------|------|--------|
| 01 | Ethical Magistrate | Governance | ✅ |
| 02 | OSINT Hunter | Intelligence | 🔄 |
| 03 | Threat Prophet | Intelligence | 🔄 |
| 04 | Compliance Guardian | Intelligence | 🔄 |
| 05 | Immune Coordinator | Immune | 🔄 |
| 06 | Sentinel Prime | Immune | 🔄 |
| 07 | The Watcher | Immune | 🔄 |
| 08 | Wargame Executor | Offensive | 🔄 |
| 09 | Patch Validator ML | Offensive | 🔄 |
| 10 | CLI Cyber Agent | Integration | 🔄 |
| 11 | MCP Tool Bridge | Integration | ✅ |
"""


# =============================================================================
# PLACEHOLDER TOOLS
# =============================================================================

@mcp.tool()
async def system_health(ctx: Context) -> dict:
    """Verifica a saúde do sistema Vertice Cyber."""
    ctx.info("Checking system health...")
    return {
        "status": "healthy",
        "version": settings.version,
        "agents_loaded": 2,
        "agents_total": 11,
    }


@mcp.tool()
async def list_tools(ctx: Context) -> list[dict]:
    """Lista todas as tools disponíveis."""
    return [
        {"name": "system_health", "agent": "bridge"},
        {"name": "ethical_validate", "agent": "magistrate", "status": "pending"},
    ]


# =============================================================================
# STARTUP / SHUTDOWN
# =============================================================================

@mcp.on_startup
async def on_startup():
    """Executado quando o servidor inicia."""
    logger.info("🔺 Vertice Cyber MCP Server starting...")
    event_bus = get_event_bus()
    await event_bus.emit(
        EventType.SYSTEM_HEALTH_CHECK,
        {"action": "startup"},
        source="mcp_server"
    )


@mcp.on_shutdown
async def on_shutdown():
    """Executado quando o servidor para."""
    logger.info("🔺 Vertice Cyber MCP Server shutting down...")
    get_memory_pool()  # Futuro: persist


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Vertice Cyber MCP Server")
    parser.add_argument("--http", action="store_true", help="HTTP mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP")
    parser.add_argument("--check", action="store_true", help="Check tools and exit")
    
    args = parser.parse_args()
    
    if args.check:
        print("🔺 Vertice Cyber - Tools Check")
        print("  ✅ system_health")
        print("  ✅ list_tools")
        return
    
    if args.http:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
```

---

## 0.6 Tools Package Init

### Arquivo: `tools/__init__.py`

```python
"""
Vertice Cyber - MCP Tools Package
"""
__all__ = []
```

---

# 🏛️ FASE 1: GOVERNANCE TOOLS

## 1.0 Pesquisa Web 2026 (Embarcada)

### Ethical AI Governance Patterns

**Tendências 2026:**
- Human-in-the-Loop obrigatório para ações críticas
- Audit trail para todas decisões
- Múltiplos frameworks éticos (utilitário, deontológico, virtue)
- Timeout para aprovação humana

## 1.5 Análise do Código Existente

**De `agents/ethical_magistrate/main.py`:**
- `EthicalDecisionType` - Enum com tipos de decisão
- `EthicalDecisionResult` - Modelo Pydantic com campos
- `_is_dangerous_action()` - Lógica de keywords perigosas
- Validation pipeline de 7 fases (simplificado atualmente)

## 1.1 Ethical Magistrate Tool

### Arquivo: `tools/magistrate.py`

```python
"""
Ethical Magistrate - Core Governance Tool
Valida todas as ações do sistema contra framework ético.
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory


class DecisionType(str, Enum):
    """Tipos de decisão ética."""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REJECTED_BY_GOVERNANCE = "rejected_by_governance"
    REJECTED_BY_ETHICS = "rejected_by_ethics"
    REJECTED_BY_PRIVACY = "rejected_by_privacy"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    ERROR = "error"


class EthicalDecision(BaseModel):
    """Resultado de validação ética."""
    decision_id: str
    decision_type: DecisionType
    action: str
    actor: str
    is_approved: bool
    conditions: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)
    reasoning: str = ""
    duration_ms: float = 0.0


class EthicalMagistrate:
    """
    Magistrado Ético - Juiz supremo do sistema.
    
    Valida ações através de pipeline de 7 fases:
    1. Governance check (keywords perigosas)
    2. Privacy check (PII)
    3. Fairness check
    4. Transparency check
    5. Accountability check
    6. Security check
    7. Final approval
    """
    
    def __init__(self):
        self.settings = get_settings().ethics
        self.memory = get_agent_memory("ethical_magistrate")
        self.event_bus = get_event_bus()
    
    async def validate(
        self,
        action: str,
        context: Dict[str, Any],
        actor: str = "system"
    ) -> EthicalDecision:
        """
        Valida ação contra framework ético.
        
        Args:
            action: Descrição da ação a ser validada
            context: Contexto adicional (has_pii, target, etc.)
            actor: Quem está solicitando
        
        Returns:
            EthicalDecision com resultado
        """
        start_time = time.time()
        decision_id = f"decision_{int(time.time() * 1000)}"
        
        # Emite evento de início
        await self.event_bus.emit(
            EventType.ETHICS_VALIDATION_REQUESTED,
            {"action": action, "actor": actor},
            source="magistrate"
        )
        
        result = EthicalDecision(
            decision_id=decision_id,
            decision_type=DecisionType.ERROR,
            action=action,
            actor=actor,
            is_approved=False,
        )
        
        try:
            # Phase 1: Governance check
            if self._is_dangerous(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("Human review required for sensitive action")
                result.reasoning = "Action contains dangerous keywords"
                await self._emit_human_review(action, actor)
                return self._finalize(result, start_time)
            
            # Phase 2: Always require approval check
            if self._always_requires_approval(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("This action type always requires approval")
                return self._finalize(result, start_time)
            
            # Phase 3: Privacy check
            if context.get("has_pii") or context.get("personal_data"):
                result.decision_type = DecisionType.APPROVED_WITH_CONDITIONS
                result.is_approved = True
                result.conditions.append("Approved with privacy safeguards")
                result.conditions.append("PII must be masked in logs")
                return self._finalize(result, start_time)
            
            # Phase 4-7: Additional checks (simplificado por ora)
            # TODO: Implementar fairness, transparency, accountability, security
            
            # Default: Approved
            result.decision_type = DecisionType.APPROVED
            result.is_approved = True
            result.reasoning = "All checks passed"
            
        except Exception as e:
            result.decision_type = DecisionType.ERROR
            result.rejection_reasons.append(f"Validation error: {str(e)}")
        
        return self._finalize(result, start_time)
    
    def _is_dangerous(self, action: str) -> bool:
        """Verifica se ação contém keywords perigosas."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.dangerous_keywords)
    
    def _always_requires_approval(self, action: str) -> bool:
        """Verifica se ação sempre precisa de aprovação."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.always_require_approval)
    
    def _finalize(self, result: EthicalDecision, start_time: float) -> EthicalDecision:
        """Finaliza decisão com duração."""
        result.duration_ms = (time.time() - start_time) * 1000
        
        # Armazena na memória
        self.memory.set(result.decision_id, result.model_dump())
        
        return result
    
    async def _emit_human_review(self, action: str, actor: str) -> None:
        """Emite evento de human review necessário."""
        await self.event_bus.emit(
            EventType.ETHICS_HUMAN_REVIEW_REQUIRED,
            {"action": action, "actor": actor},
            source="magistrate"
        )
    
    async def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Retorna histórico de decisões."""
        events = self.event_bus.get_history(
            EventType.ETHICS_VALIDATION_COMPLETED,
            limit=limit
        )
        return [e.data for e in events]


# Instância global
_magistrate: Optional[EthicalMagistrate] = None


def get_magistrate() -> EthicalMagistrate:
    """Retorna singleton do magistrate."""
    global _magistrate
    if _magistrate is None:
        _magistrate = EthicalMagistrate()
    return _magistrate


# =============================================================================
# MCP TOOL FUNCTIONS (registrar no mcp_server.py)
# =============================================================================

async def ethical_validate(
    ctx: Context,
    action: str,
    context: Optional[Dict[str, Any]] = None,
    actor: str = "user"
) -> Dict[str, Any]:
    """
    Valida uma ação contra o framework ético de 7 fases.
    
    Args:
        action: Descrição da ação a ser validada
        context: Contexto adicional (has_pii, target, etc.)
        actor: Quem está solicitando a ação
    
    Returns:
        Decisão ética com approved, conditions, reasoning
    """
    ctx.info(f"Validating action: {action[:50]}...")
    
    magistrate = get_magistrate()
    decision = await magistrate.validate(action, context or {}, actor)
    
    ctx.info(f"Decision: {decision.decision_type.value}")
    
    return decision.model_dump()


async def ethical_audit(
    ctx: Context,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retorna histórico de decisões éticas.
    
    Args:
        limit: Número máximo de decisões a retornar
    
    Returns:
        Lista de decisões recentes
    """
    magistrate = get_magistrate()
    return await magistrate.get_decision_history(limit)
```

---

# 🔍 FASE 2: INTELLIGENCE TOOLS

## 2.0 Pesquisa Web 2026 (Embarcada)

### HaveIBeenPwned API

**Instalação:**
```bash
pip install haveibeenpwned-py
```

**Uso básico:**
```python
from haveibeenpwned import HIBP

hibp = HIBP(api_key="YOUR_KEY")

# Check email breaches
breaches = await hibp.get_account_breaches("email@example.com")

# Check password (k-Anonymity, no API key needed)
is_pwned = await hibp.check_password("password123")
```

**Headers obrigatórios:**
- `hibp-api-key`: Sua API key
- `User-Agent`: Descrição do app

### pyattck - MITRE ATT&CK

**Instalação:**
```bash
pip install pyattck
```

**Uso básico:**
```python
from pyattck import Attck

attack = Attck()

# Listar todas técnicas
for technique in attack.enterprise.techniques:
    print(f"{technique.id}: {technique.name}")

# Buscar técnica específica
technique = attack.enterprise.techniques[0]
print(technique.mitigations)
print(technique.tactics)
```

## 2.1 OSINT Hunter Tool

### Arquivo: `tools/osint.py`

```python
"""
OSINT Hunter - Intelligence Gathering Tool
Investigação autônoma de inteligência open-source.
"""

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

logger = logging.getLogger(__name__)


class InvestigationDepth(str, Enum):
    """Profundidade da investigação."""
    BASIC = "basic"
    DEEP = "deep"
    EXHAUSTIVE = "exhaustive"


class BreachInfo(BaseModel):
    """Informação de um breach."""
    name: str
    date: str
    data_classes: List[str]
    is_verified: bool


class OSINTFinding(BaseModel):
    """Um achado da investigação."""
    source: str
    finding_type: str
    severity: str  # low, medium, high, critical
    data: Dict[str, Any]
    confidence: float


class OSINTResult(BaseModel):
    """Resultado de investigação OSINT."""
    target: str
    depth: InvestigationDepth
    findings: List[OSINTFinding] = Field(default_factory=list)
    breaches: List[BreachInfo] = Field(default_factory=list)
    risk_score: float = 0.0
    sources_checked: List[str] = Field(default_factory=list)


class OSINTHunter:
    """
    OSINT Hunter - Investigador Digital.
    
    Capacidades:
    - Breach data analysis (HaveIBeenPwned)
    - Google dorking patterns
    - Domain reconnaissance
    - Email intelligence
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("osint_hunter")
        self.event_bus = get_event_bus()
        self.hibp_api_key = None
        
        if self.settings.api_keys.hibp_api_key:
            self.hibp_api_key = self.settings.api_keys.hibp_api_key.get_secret_value()
    
    async def investigate(
        self,
        target: str,
        depth: InvestigationDepth = InvestigationDepth.BASIC
    ) -> OSINTResult:
        """
        Executa investigação OSINT completa.
        
        Args:
            target: Email, domínio, ou IP
            depth: Profundidade da investigação
        
        Returns:
            OSINTResult com todos os achados
        """
        await self.event_bus.emit(
            EventType.OSINT_INVESTIGATION_STARTED,
            {"target": target, "depth": depth.value},
            source="osint_hunter"
        )
        
        result = OSINTResult(target=target, depth=depth)
        
        # Detecta tipo de target
        if "@" in target:
            await self._investigate_email(target, result)
        elif "." in target and not target.replace(".", "").isdigit():
            await self._investigate_domain(target, result)
        else:
            await self._investigate_ip(target, result)
        
        # Calcula risk score
        result.risk_score = self._calculate_risk(result)
        
        # Cache result
        cache_key = f"investigation:{target}:{depth.value}"
        self.memory.set(cache_key, result.model_dump(), ttl_seconds=3600)
        
        await self.event_bus.emit(
            EventType.OSINT_INVESTIGATION_COMPLETED,
            {"target": target, "risk_score": result.risk_score},
            source="osint_hunter"
        )
        
        return result
    
    async def check_breach(self, email: str) -> List[BreachInfo]:
        """
        Verifica se email aparece em breaches conhecidos.
        
        Args:
            email: Email a verificar
        
        Returns:
            Lista de breaches
        """
        if not self.hibp_api_key:
            logger.warning("HIBP API key not configured")
            return []
        
        breaches = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={
                        "hibp-api-key": self.hibp_api_key,
                        "User-Agent": "Vertice-Cyber-OSINT/2.0"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for breach in data:
                        breaches.append(BreachInfo(
                            name=breach.get("Name", "Unknown"),
                            date=breach.get("BreachDate", "Unknown"),
                            data_classes=breach.get("DataClasses", []),
                            is_verified=breach.get("IsVerified", False)
                        ))
                    
                    if breaches:
                        await self.event_bus.emit(
                            EventType.OSINT_BREACH_DETECTED,
                            {"email": email, "count": len(breaches)},
                            source="osint_hunter"
                        )
                        
                elif response.status_code == 404:
                    pass  # No breaches found
                else:
                    logger.warning(f"HIBP API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Breach check failed: {e}")
        
        return breaches
    
    def get_google_dorks(self, domain: str) -> List[Dict[str, str]]:
        """
        Gera lista de Google dorks para um domínio.
        
        Args:
            domain: Domínio alvo
        
        Returns:
            Lista de dorks categorizados
        """
        dorks = [
            {
                "category": "sensitive_files",
                "dork": f'site:{domain} filetype:pdf OR filetype:doc OR filetype:xls',
                "description": "Documentos potencialmente sensíveis"
            },
            {
                "category": "exposed_dirs",
                "dork": f'site:{domain} intitle:"index of"',
                "description": "Diretórios expostos"
            },
            {
                "category": "login_pages",
                "dork": f'site:{domain} inurl:login OR inurl:admin',
                "description": "Páginas de login"
            },
            {
                "category": "config_files",
                "dork": f'site:{domain} filetype:env OR filetype:config',
                "description": "Arquivos de configuração"
            },
            {
                "category": "error_messages",
                "dork": f'site:{domain} "error" OR "exception" OR "warning"',
                "description": "Mensagens de erro expostas"
            },
            {
                "category": "backup_files",
                "dork": f'site:{domain} filetype:bak OR filetype:old OR filetype:backup',
                "description": "Arquivos de backup"
            },
        ]
        return dorks
    
    async def _investigate_email(self, email: str, result: OSINTResult) -> None:
        """Investiga um email."""
        result.sources_checked.append("hibp_breaches")
        result.breaches = await self.check_breach(email)
        
        # Extrai domínio
        domain = email.split("@")[1]
        result.sources_checked.append("domain_from_email")
        
        result.findings.append(OSINTFinding(
            source="email_analysis",
            finding_type="domain_extracted",
            severity="info",
            data={"domain": domain},
            confidence=1.0
        ))
    
    async def _investigate_domain(self, domain: str, result: OSINTResult) -> None:
        """Investiga um domínio."""
        result.sources_checked.append("google_dorks")
        
        dorks = self.get_google_dorks(domain)
        result.findings.append(OSINTFinding(
            source="google_dorking",
            finding_type="dorks_generated",
            severity="info",
            data={"dorks": dorks, "count": len(dorks)},
            confidence=1.0
        ))
    
    async def _investigate_ip(self, ip: str, result: OSINTResult) -> None:
        """Investiga um IP."""
        result.sources_checked.append("ip_analysis")
        result.findings.append(OSINTFinding(
            source="ip_analysis",
            finding_type="ip_info",
            severity="info",
            data={"ip": ip},
            confidence=1.0
        ))
    
    def _calculate_risk(self, result: OSINTResult) -> float:
        """Calcula score de risco (0-100)."""
        score = 0.0
        
        # Breaches aumentam risco
        score += len(result.breaches) * 15
        
        # Findings de alta severidade
        for finding in result.findings:
            if finding.severity == "critical":
                score += 25
            elif finding.severity == "high":
                score += 15
            elif finding.severity == "medium":
                score += 5
        
        return min(score, 100.0)


# Singleton
_osint_hunter: Optional[OSINTHunter] = None


def get_osint_hunter() -> OSINTHunter:
    """Retorna singleton do OSINT Hunter."""
    global _osint_hunter
    if _osint_hunter is None:
        _osint_hunter = OSINTHunter()
    return _osint_hunter


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================

async def osint_investigate(
    ctx: Context,
    target: str,
    depth: str = "basic"
) -> Dict[str, Any]:
    """
    Executa investigação OSINT sobre um alvo.
    
    Args:
        target: Email, domínio ou IP a investigar
        depth: Profundidade (basic, deep, exhaustive)
    
    Returns:
        Resultado com findings, breaches e risk_score
    """
    ctx.info(f"Starting OSINT investigation on {target}")
    
    hunter = get_osint_hunter()
    depth_enum = InvestigationDepth(depth)
    result = await hunter.investigate(target, depth_enum)
    
    ctx.info(f"Investigation complete. Risk score: {result.risk_score}")
    
    return result.model_dump()


async def osint_breach_check(
    ctx: Context,
    email: str
) -> Dict[str, Any]:
    """
    Verifica se email aparece em breaches conhecidos.
    
    Args:
        email: Email a verificar
    
    Returns:
        Lista de breaches onde o email aparece
    """
    ctx.info(f"Checking breaches for {email}")
    
    hunter = get_osint_hunter()
    breaches = await hunter.check_breach(email)
    
    return {
        "email": email,
        "breached": len(breaches) > 0,
        "breach_count": len(breaches),
        "breaches": [b.model_dump() for b in breaches]
    }


async def osint_google_dork(
    ctx: Context,
    target_domain: str
) -> Dict[str, Any]:
    """
    Gera Google dorks para reconhecimento de domínio.
    
    Args:
        target_domain: Domínio alvo
    
    Returns:
        Lista de dorks categorizados
    """
    hunter = get_osint_hunter()
    dorks = hunter.get_google_dorks(target_domain)
    
    return {
        "domain": target_domain,
        "dork_count": len(dorks),
        "dorks": dorks
    }
```

---

# 📎 APÊNDICE: CONFIGURAÇÃO MCP PARA VERTICE-CODE

## Arquivo: `.gemini/settings.json`

```json
{
  "mcpServers": {
    "vertice-cyber": {
      "command": "python",
      "args": ["/media/juan/DATA/vertice-cyber/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/media/juan/DATA/vertice-cyber"
      }
    }
  }
}
```

---

# 📎 APÊNDICE: ESTRUTURA FINAL DE DIRETÓRIOS

```
vertice-cyber/
├── mcp_server.py              # Entry point MCP
├── requirements.txt           # Dependências
├── .env                       # Environment variables
├── .env.example               # Template
├── core/
│   ├── __init__.py            # Exports
│   ├── settings.py            # Pydantic Settings
│   ├── event_bus.py           # Async Event Bus
│   └── memory.py              # Per-agent Memory
├── tools/
│   ├── __init__.py
│   ├── magistrate.py          # 01. Ethical Magistrate
│   ├── osint.py               # 02. OSINT Hunter
│   ├── threat.py              # 03. Threat Prophet
│   ├── compliance.py          # 04. Compliance Guardian
│   ├── immune.py              # 05. Immune Coordinator
│   ├── sentinel.py            # 06. Sentinel Prime
│   ├── watcher.py             # 07. The Watcher
│   ├── wargame.py             # 08. Wargame Executor
│   ├── patch_ml.py            # 09. Patch Validator ML
│   ├── cli.py                 # 10. CLI Cyber Agent
│   └── bridge.py              # 11. MCP Tool Bridge
├── scripts/
│   └── smoke_test.py
├── tests/
│   └── test_tools.py
└── docs/
    ├── bioguard_agents_2028.md
    └── IMPLEMENTATION_PLAN.md    # Este documento
```

---

# 📚 APÊNDICE: DOCUMENTAÇÃO EMBARCADA - TECNOLOGIAS 2026

> **IMPORTANTE:** Esta seção contém documentação autocontida para todas as novas tecnologias adicionadas. O implementador pode usar esta seção como referência offline.

---

## A.1 Shodan Python API (OSINT)

### Instalação
```bash
pip install shodan
```

### Conceito
Shodan é um motor de busca para dispositivos conectados à internet. Diferente do Google que indexa websites, Shodan indexa banners de serviços (SSH, HTTP, FTP, etc.), permitindo descobrir sistemas expostos.

### Uso Básico
```python
import shodan

# Inicialização
api = shodan.Shodan("SUA_API_KEY")

# Buscar informações de um host específico
async def lookup_host(ip: str) -> dict:
    """Busca informações de um IP no Shodan."""
    try:
        host = api.host(ip)
        return {
            "ip": host["ip_str"],
            "org": host.get("org", "N/A"),
            "os": host.get("os"),
            "ports": host.get("ports", []),
            "vulns": host.get("vulns", []),  # CVEs conhecidas!
            "services": [
                {
                    "port": item["port"],
                    "transport": item["transport"],
                    "product": item.get("product"),
                    "version": item.get("version"),
                }
                for item in host.get("data", [])
            ]
        }
    except shodan.APIError as e:
        return {"error": str(e)}

# Busca por query
async def search_shodan(query: str, limit: int = 10) -> list[dict]:
    """
    Busca dispositivos no Shodan.
    
    Exemplos de queries:
    - "apache country:BR"
    - "port:22 org:Amazon"
    - "ssl.cert.subject.cn:*.example.com"
    - "vuln:CVE-2021-44228" (Log4j)
    """
    try:
        results = api.search(query)
        return [
            {
                "ip": match["ip_str"],
                "port": match["port"],
                "org": match.get("org"),
                "product": match.get("product"),
                "version": match.get("version"),
            }
            for match in results["matches"][:limit]
        ]
    except shodan.APIError as e:
        return [{"error": str(e)}]
```

### Queries Úteis para Cybersec
```python
SHODAN_QUERIES = {
    # Exposured databases
    "mongodb_exposed": "port:27017 product:MongoDB",
    "redis_exposed": "port:6379 product:Redis",
    "elasticsearch_exposed": "port:9200 product:Elasticsearch",
    
    # Vulnerable services
    "log4j_vulnerable": 'vuln:CVE-2021-44228',
    "ssh_weak": 'port:22 "SSH-1"',
    
    # Cloud misconfigs
    "aws_s3_exposed": 'http.title:"Index of /" s3',
    "kubernetes_exposed": 'port:6443 "kubernetes"',
    
    # IoT devices
    "webcams": 'product:webcam',
    "scada": 'port:502 modbus',
}
```

---

## A.2 Censys Python SDK (Internet Scanning)

### Instalação
```bash
pip install censys
```

### Conceito
Censys realiza varreduras em toda a internet, indexando hosts, serviços e certificados SSL. Similar ao Shodan, mas com foco em dados de certificados.

### Uso Básico
```python
from censys.search import CensysHosts, CensysCerts

# Autenticação via env vars: CENSYS_API_ID, CENSYS_API_SECRET

# Buscar hosts
async def search_hosts(query: str, limit: int = 10) -> list[dict]:
    """
    Busca hosts no Censys.
    
    Query syntax: https://search.censys.io/search/language
    Exemplos:
    - "services.service_name: SSH"
    - "location.country: Brazil"
    - "services.tls.certificates.leaf_data.issuer.organization: Let's Encrypt"
    """
    h = CensysHosts()
    results = []
    
    for host in h.search(query, per_page=limit):
        results.append({
            "ip": host["ip"],
            "services": [
                {
                    "port": svc.get("port"),
                    "service_name": svc.get("service_name"),
                    "transport_protocol": svc.get("transport_protocol"),
                }
                for svc in host.get("services", [])
            ],
            "location": host.get("location"),
            "autonomous_system": host.get("autonomous_system"),
        })
    
    return results

# Buscar certificados
async def search_certificates(domain: str) -> list[dict]:
    """Busca certificados SSL para um domínio."""
    c = CensysCerts()
    query = f"names: {domain}"
    
    results = []
    for cert in c.search(query, per_page=25):
        results.append({
            "fingerprint": cert.get("fingerprint_sha256"),
            "issuer": cert.get("issuer", {}).get("organization"),
            "subject": cert.get("subject", {}).get("common_name"),
            "validity": {
                "start": cert.get("validity", {}).get("start"),
                "end": cert.get("validity", {}).get("end"),
            }
        })
    
    return results
```

---

## A.3 EPSS API (Exploit Prediction Scoring System)

### Conceito
EPSS é um sistema desenvolvido pelo FIRST.org que prediz a **probabilidade de um CVE ser explorado** nos próximos 30 dias. Atualizado diariamente. EPSS v4 lançado em Março 2025.

### Uso (Implementação Custom)
```python
import httpx
from typing import Optional

EPSS_API_URL = "https://api.first.org/data/v1/epss"

async def get_epss_score(cve_id: str) -> dict:
    """
    Obtém EPSS score para um CVE.
    
    Returns:
        {
            "cve": "CVE-2021-44228",
            "epss": 0.97549,  # 97.5% chance de ser explorado em 30 dias
            "percentile": 0.99995  # Top 0.005% mais provável
        }
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{EPSS_API_URL}?cve={cve_id}")
        data = response.json()
        
        if data.get("data"):
            entry = data["data"][0]
            return {
                "cve": entry["cve"],
                "epss": float(entry["epss"]),
                "percentile": float(entry["percentile"]),
                "date": entry.get("date"),
            }
        return {"error": "CVE not found"}

async def get_epss_batch(cve_ids: list[str]) -> list[dict]:
    """Obtém EPSS scores para múltiplos CVEs."""
    cve_param = ",".join(cve_ids)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{EPSS_API_URL}?cve={cve_param}")
        data = response.json()
        
        return [
            {
                "cve": entry["cve"],
                "epss": float(entry["epss"]),
                "percentile": float(entry["percentile"]),
            }
            for entry in data.get("data", [])
        ]

# Classificação por risco EPSS
def classify_epss_risk(epss_score: float) -> str:
    """Classifica risco baseado em EPSS score."""
    if epss_score >= 0.7:
        return "CRITICAL"  # 70%+ chance de exploit
    elif epss_score >= 0.3:
        return "HIGH"
    elif epss_score >= 0.1:
        return "MEDIUM"
    else:
        return "LOW"
```

---

## A.4 KEV Catalog (CISA Known Exploited Vulnerabilities)

### Conceito
KEV é a lista oficial da CISA de vulnerabilidades **ativamente exploitadas**. Se um CVE está no KEV, ele ESTÁ sendo usado em ataques reais. Total: ~1500 CVEs (Jan 2026).

### Uso (Implementação Custom)
```python
import httpx
from typing import Optional

KEV_JSON_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

class KEVCatalog:
    """Cliente para CISA KEV Catalog."""
    
    def __init__(self):
        self._catalog: dict = {}
        self._cve_set: set = set()
    
    async def load(self) -> None:
        """Carrega catálogo do CISA."""
        async with httpx.AsyncClient() as client:
            response = await client.get(KEV_JSON_URL)
            self._catalog = response.json()
            self._cve_set = {
                vuln["cveID"] 
                for vuln in self._catalog.get("vulnerabilities", [])
            }
    
    def is_actively_exploited(self, cve_id: str) -> bool:
        """Verifica se CVE está sendo exploitado ativamente."""
        return cve_id in self._cve_set
    
    def get_kev_details(self, cve_id: str) -> Optional[dict]:
        """Retorna detalhes do KEV entry."""
        for vuln in self._catalog.get("vulnerabilities", []):
            if vuln["cveID"] == cve_id:
                return {
                    "cve": vuln["cveID"],
                    "vendor": vuln["vendorProject"],
                    "product": vuln["product"],
                    "vulnerability_name": vuln["vulnerabilityName"],
                    "date_added": vuln["dateAdded"],
                    "due_date": vuln["dueDate"],  # Prazo para remediar
                    "known_ransomware": vuln.get("knownRansomwareCampaignUse", "Unknown"),
                }
        return None
    
    def get_recent_additions(self, days: int = 7) -> list[dict]:
        """Retorna CVEs adicionados nos últimos N dias."""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for vuln in self._catalog.get("vulnerabilities", []):
            date_added = datetime.strptime(vuln["dateAdded"], "%Y-%m-%d")
            if date_added >= cutoff:
                recent.append(self.get_kev_details(vuln["cveID"]))
        
        return recent

# Uso
kev = KEVCatalog()
await kev.load()
is_exploited = kev.is_actively_exploited("CVE-2021-44228")  # True (Log4j)
```

---

## A.5 NVDLib (National Vulnerability Database)

### Instalação
```bash
pip install nvdlib
```

### Conceito
NVDLib é wrapper Python para a API do NVD (NIST). Permite buscar CVEs com filtros avançados: por produto, data, severidade, etc.

### Uso Básico
```python
import nvdlib
from datetime import datetime

# Buscar CVE específico
def get_cve(cve_id: str) -> dict:
    """Obtém detalhes de um CVE."""
    results = nvdlib.searchCVE(cveId=cve_id)
    
    if results:
        cve = results[0]
        return {
            "cve_id": cve.id,
            "description": cve.descriptions[0].value if cve.descriptions else "",
            "cvss_v3": getattr(cve.metrics, "cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore") if hasattr(cve.metrics, "cvssMetricV31") else None,
            "severity": getattr(cve.metrics, "cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity") if hasattr(cve.metrics, "cvssMetricV31") else None,
            "published": str(cve.published),
            "last_modified": str(cve.lastModified),
            "references": [ref.url for ref in getattr(cve, "references", [])],
        }
    return {"error": "CVE not found"}

# Buscar CVEs críticos recentes
def search_critical_cves(days: int = 7) -> list[dict]:
    """Busca CVEs críticos dos últimos N dias."""
    from datetime import timedelta
    
    start_date = datetime.now() - timedelta(days=days)
    
    results = nvdlib.searchCVE(
        pubStartDate=start_date,
        cvssV3Severity="CRITICAL",
    )
    
    return [
        {
            "cve_id": cve.id,
            "cvss": getattr(cve.metrics, "cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore"),
            "description": cve.descriptions[0].value[:200] if cve.descriptions else "",
        }
        for cve in results[:20]
    ]

# Buscar CVEs por produto
def search_by_product(keyword: str) -> list[dict]:
    """Busca CVEs por keyword no produto."""
    results = nvdlib.searchCVE(keywordSearch=keyword)
    return [
        {"cve_id": cve.id, "published": str(cve.published)}
        for cve in results[:20]
    ]
```

---

## A.6 Nuclei (Vulnerability Scanner)

### Instalação
```bash
# CLI (Go binary) - Recomendado
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Ou via binário
# Download de https://github.com/projectdiscovery/nuclei/releases

# Python wrapper (unofficial)
pip install pynuclei
```

### Conceito
Nuclei é um scanner de vulnerabilidades ultra-rápido baseado em templates YAML. Possui 9000+ templates community-driven cobrindo CVEs, misconfigs, exposures, etc.

### Templates
```yaml
# Exemplo de template Nuclei
id: CVE-2021-44228-log4j-rce

info:
  name: Apache Log4j RCE
  author: pdteam
  severity: critical
  tags: cve,cve2021,rce,log4j

http:
  - method: GET
    path:
      - "{{BaseURL}}"
    headers:
      X-Api-Version: "${jndi:ldap://{{interactsh-url}}}"
    matchers:
      - type: word
        part: interactsh_protocol
        words:
          - "dns"
          - "http"
```

### Uso via Python (subprocess)
```python
import asyncio
import json
from typing import Optional

async def run_nuclei(
    target: str,
    templates: list[str] = ["cves/", "exposures/"],
    severity: str = "critical,high",
) -> list[dict]:
    """
    Executa Nuclei scan.
    
    Args:
        target: URL ou IP alvo
        templates: Lista de templates/diretórios
        severity: Filtro de severidade
    
    Returns:
        Lista de vulnerabilidades encontradas
    """
    cmd = [
        "nuclei",
        "-u", target,
        "-t", ",".join(templates),
        "-severity", severity,
        "-json",
        "-silent",
    ]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, _ = await proc.communicate()
    
    vulnerabilities = []
    for line in stdout.decode().strip().split("\n"):
        if line:
            try:
                vuln = json.loads(line)
                vulnerabilities.append({
                    "template_id": vuln.get("template-id"),
                    "name": vuln.get("info", {}).get("name"),
                    "severity": vuln.get("info", {}).get("severity"),
                    "matched_at": vuln.get("matched-at"),
                    "host": vuln.get("host"),
                    "curl_command": vuln.get("curl-command"),
                })
            except json.JSONDecodeError:
                continue
    
    return vulnerabilities

# Templates por categoria
NUCLEI_TEMPLATES = {
    "cves": "cves/",
    "exposures": "exposures/",
    "misconfigurations": "misconfiguration/",
    "vulnerabilities": "vulnerabilities/",
    "default_logins": "default-logins/",
    "exposed_panels": "exposed-panels/",
    "technologies": "technologies/",
    "owasp": "owasp/",
}
```

---

## A.7 Semgrep (SAST - Static Analysis)

### Instalação
```bash
pip install semgrep
```

### Conceito
Semgrep é ferramenta de análise estática que usa padrões para encontrar bugs e vulnerabilidades em código. Suporta 30+ linguagens. Registry com 2000+ regras community.

### Uso Básico
```python
import subprocess
import json

def run_semgrep(
    path: str,
    config: str = "auto",
) -> dict:
    """
    Executa Semgrep scan.
    
    Args:
        path: Caminho para o código
        config: Configuração (auto, p/security-audit, p/python, etc.)
    
    Returns:
        Resultados do scan
    """
    cmd = [
        "semgrep",
        "--config", config,
        "--json",
        "--quiet",
        path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        output = json.loads(result.stdout)
        
        findings = []
        for finding in output.get("results", []):
            findings.append({
                "rule_id": finding.get("check_id"),
                "message": finding.get("extra", {}).get("message"),
                "severity": finding.get("extra", {}).get("severity"),
                "path": finding.get("path"),
                "start_line": finding.get("start", {}).get("line"),
                "end_line": finding.get("end", {}).get("line"),
                "code": finding.get("extra", {}).get("lines"),
            })
        
        return {
            "findings": findings,
            "total": len(findings),
            "errors": output.get("errors", []),
        }
    
    return {"error": result.stderr}

# Configs úteis para cybersec
SEMGREP_CONFIGS = {
    "security_audit": "p/security-audit",
    "owasp_top10": "p/owasp-top-ten",
    "python_security": "p/python",
    "secrets": "p/secrets",
    "django": "p/django",
    "flask": "p/flask",
    "sql_injection": "p/sql-injection",
    "xss": "p/xss",
}
```

### Exemplo de Custom Rule
```yaml
# semgrep_rules/eval_detection.yaml
rules:
  - id: dangerous-eval
    patterns:
      - pattern: eval(...)
    message: "Uso de eval() é perigoso - possível code injection"
    severity: ERROR
    languages:
      - python
    metadata:
      cwe: "CWE-94"
      owasp: "A03:2021 - Injection"
```

---

## A.8 XGBoost para Anomaly Detection

### Instalação
```bash
pip install xgboost scikit-learn
```

### Conceito
XGBoost é algoritmo de gradient boosting otimizado. Para cybersec, é usado em detecção de anomalias: tráfego malicioso, fraude, comportamento anômalo de agents.

### Exemplo: Behavioral Anomaly Detector
```python
import xgboost as xgb
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentBehavior:
    """Representa comportamento de um agent."""
    tool_calls_per_minute: float
    unique_resources_accessed: int
    avg_response_time_ms: float
    error_rate: float
    consecutive_failures: int
    is_after_hours: bool
    new_resource_ratio: float  # % de recursos nunca acessados antes

class BehavioralAnomalyDetector:
    """Detector de anomalias comportamentais usando XGBoost."""
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective="binary:logistic",
            eval_metric="auc",
            random_state=42,
        )
        self._is_trained = False
    
    def _extract_features(self, behavior: AgentBehavior) -> np.ndarray:
        """Extrai features do comportamento."""
        return np.array([
            behavior.tool_calls_per_minute,
            behavior.unique_resources_accessed,
            behavior.avg_response_time_ms,
            behavior.error_rate,
            behavior.consecutive_failures,
            float(behavior.is_after_hours),
            behavior.new_resource_ratio,
        ])
    
    def train(
        self,
        behaviors: list[AgentBehavior],
        labels: list[int],  # 0=normal, 1=anomaly
    ) -> dict:
        """Treina o modelo."""
        X = np.array([self._extract_features(b) for b in behaviors])
        y = np.array(labels)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
        
        self._is_trained = True
        
        # Métricas
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            "accuracy": report["accuracy"],
            "precision": report["1"]["precision"],
            "recall": report["1"]["recall"],
            "f1": report["1"]["f1-score"],
        }
    
    def predict(self, behavior: AgentBehavior) -> dict:
        """Prediz se comportamento é anômalo."""
        if not self._is_trained:
            raise RuntimeError("Model not trained")
        
        X = self._extract_features(behavior).reshape(1, -1)
        
        prob = self.model.predict_proba(X)[0][1]
        is_anomaly = prob > 0.5
        
        return {
            "is_anomaly": is_anomaly,
            "confidence": float(prob if is_anomaly else 1 - prob),
            "anomaly_probability": float(prob),
        }
    
    def get_feature_importance(self) -> dict:
        """Retorna importância de cada feature."""
        feature_names = [
            "tool_calls_per_minute",
            "unique_resources_accessed",
            "avg_response_time_ms",
            "error_rate",
            "consecutive_failures",
            "is_after_hours",
            "new_resource_ratio",
        ]
        
        importance = self.model.feature_importances_
        
        return {
            name: float(score)
            for name, score in sorted(
                zip(feature_names, importance),
                key=lambda x: x[1],
                reverse=True,
            )
        }
```

### Uso para Agent Compromise Detection
```python
# Exemplo de uso
detector = BehavioralAnomalyDetector()

# Treinar com dados históricos
# (Em produção, usar dados reais de agents)
detector.train(historical_behaviors, historical_labels)

# Detectar em tempo real
current_behavior = AgentBehavior(
    tool_calls_per_minute=100,  # Muito alto!
    unique_resources_accessed=50,  # Muitos recursos
    avg_response_time_ms=10,
    error_rate=0.3,  # Alto
    consecutive_failures=5,
    is_after_hours=True,  # Suspeito
    new_resource_ratio=0.8,  # Acessando muitos recursos novos
)

result = detector.predict(current_behavior)
# {"is_anomaly": True, "confidence": 0.95, "anomaly_probability": 0.95}

if result["is_anomaly"]:
    # ALERT: Agent potencialmente comprometido!
    await emit_security_alert(agent_id, result)
```

---

# FIM DO PLANO DE IMPLEMENTAÇÃO

> **Próximos passos:**
> 1. Implementar Fase 0 (core infrastructure)
> 2. Executar smoke test
> 3. Implementar Fase 1 (Magistrate)
> 4. Continuar com demais fases

**Documento autocontido:** Este plano contém toda documentação necessária para implementação offline.
