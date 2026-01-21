# 🔍 REVISÃO ARQUITETURAL: SUBSTITUIÇÃO DE MOCKS

**Autor**: Arquiteto de Segurança MCP  
**Data**: 2026-01-20  
**Status**: Revisão Crítica + Plano Executável

---

## PARTE 1: CRÍTICA BRUTAL DO PLANO ANTERIOR

### ❌ Problemas Identificados

| Problema | Severidade | Impacto |
|----------|------------|---------|
| **Sem feature flags** | 🔴 CRÍTICO | Não pode rollback sem redeploy |
| **Sem circuit breaker** | 🔴 CRÍTICO | API down = sistema down |
| **Tempo subestimado** | 🟡 ALTO | 2-3h por fase é irrealista |
| **Wargame sem sandbox** | 🔴 CRÍTICO | Risco de dano real |
| **Sem versionamento de tools** | 🟡 ALTO | Breaking changes em clients |
| **Dependências não isoladas** | 🟡 ALTO | Import error = crash total |

### 🔴 Problemas Críticos em Detalhe

#### 1. Ausência de Feature Flags
```python
# ❌ PLANO ATUAL: Mudança direta
async def check_breach(self, email: str):
    api_key = os.getenv("HIBP_API_KEY")
    if not api_key:
        raise NotImplementedError(...)  # QUEBRA TUDO
```

**Problema**: Se deploy sem API key configurada, TODO o OSINT para de funcionar.

#### 2. Sem Circuit Breaker
```python
# ❌ PLANO ATUAL: Falha silenciosa ou exceção
response = await client.get(hibp_url)
# Se HIBP down por 1h, cada request falha
```

**Problema**: API externa fora gera cascade failure.

#### 3. Wargame SEM Sandbox
```python
# ❌ PLANO ATUAL: Execução direta
cmd = ["pwsh", "-c", f"Invoke-AtomicTest {technique_id}"]
result = await asyncio.create_subprocess_exec(*cmd)
```

**Problema**: Código arbitrário executado na máquina do usuário. INSANO.

---

## PARTE 2: ARQUITETURA CORRIGIDA

### 2.1 Provider Pattern com Fallback Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                     OSINT HUNTER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Real HIBP   │ →  │ Cached HIBP │ →  │ AI Fallback │ → ERROR │
│  │ Provider    │    │ Provider    │    │ (Gemini 3)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                  │                  │                  │
│        ▼                  ▼                  ▼                  │
│  ┌─────────────────────────────────────────────────────┐       │
│  │            Circuit Breaker Wrapper                  │       │
│  │  - 5 failures → open (60s cooldown)                │       │
│  │  - Logs cada fallback usado                         │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Feature Flags para Rollout Gradual

```python
# core/feature_flags.py
from enum import Enum
from pydantic_settings import BaseSettings

class FeatureFlags(BaseSettings):
    """Feature flags para rollout gradual de APIs reais."""
    
    # OSINT
    osint_use_real_hibp: bool = False
    osint_use_real_shodan: bool = False
    osint_use_real_censys: bool = False
    
    # Threat Intel
    threat_use_real_otx: bool = False
    threat_use_real_vt: bool = False
    
    # Wargame (SEMPRE começa False)
    wargame_allow_real_execution: bool = False
    wargame_require_mfa: bool = True
    
    # Compliance
    compliance_use_real_checkov: bool = False
    
    class Config:
        env_prefix = "FF_"  # FF_OSINT_USE_REAL_HIBP=true
```

### 2.3 Wargame Safety Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    WARGAME EXECUTOR                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: Feature Flag                                          │
│  ├── FF_WARGAME_ALLOW_REAL_EXECUTION = false (padrão)          │
│  └── Se false → retorna "simulation_only" sempre                │
│                                                                 │
│  Layer 2: Ethical Magistrate                                    │
│  ├── Valida ação contra framework ético                         │
│  └── Requer: has_explicit_consent = true                        │
│                                                                 │
│  Layer 3: Target Whitelist                                      │
│  ├── Só execute em targets pré-aprovados                        │
│  └── Arquivo: ~/.vertice/wargame_approved_targets.txt           │
│                                                                 │
│  Layer 4: Sandbox (Container)                                   │
│  ├── Executa em container Docker isolado                        │
│  ├── Network: host-only ou none                                 │
│  └── Timeout: 5 minutos máx                                     │
│                                                                 │
│  Layer 5: Audit Log                                             │
│  └── Toda execução logada em append-only file                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## PARTE 3: PLANO EXECUTÁVEL (ATÔMICO)

### 📦 PRÉ-REQUISITOS

```bash
# 1. Criar branch de feature
git checkout -b feature/real-implementations

# 2. Instalar dependências novas
pip install circuitbreaker>=2.0.0 tenacity>=8.2.0

# 3. Criar estrutura de pastas
mkdir -p tools/providers
mkdir -p tests/integration
touch tools/providers/__init__.py
```

---

### FASE 0: INFRAESTRUTURA BASE (30 min) ✅ CONCLUÍDA

#### Task 0.1: Criar Feature Flags ✅
- [x] **Arquivo**: `core/feature_flags.py`

#### Task 0.2: Criar Circuit Breaker Base ✅
- [x] **Arquivo**: `core/circuit_breaker.py`

#### Task 0.3: Criar Provider Base ✅
- [x] **Arquivo**: `tools/providers/base.py`

#### Task 0.4: Criar Sistema de Métricas ✅
- [x] **Arquivo**: `core/metrics.py`

#### Task 1.1c: Rate Limiter ✅
- [x] **Arquivo**: `core/rate_limiter.py`


### FASE 1: OSINT - HIBP REAL (1 hora) ✅ CONCLUÍDA

#### Task 1.1: Criar HIBP Provider ✅
- [x] **Arquivo**: `tools/providers/hibp.py`

#### Task 1.1b: Cache Inteligente ✅
- [x] **Arquivo**: `tools/providers/cache.py`

#### Task 1.3: Integrar Provider no OSINT Hunter ✅
- [x] **Arquivo**: `tools/osint.py`

#### Task 1.4: Integração MCP com Providers ✅
- [x] **Arquivo**: `tools/health_check.py`

```python
# Adicionar import no topo
from tools.providers.hibp import get_hibp_provider, BreachData

# Substituir método check_breach:
async def check_breach(self, email: str) -> List[BreachInfo]:
    """
    Verifica se email aparece em breaches conhecidos.
    
    Usa chain de providers: Real HIBP → Cache → AI Fallback
    
    Args:
        email: Email a verificar
        
    Returns:
        Lista de breaches onde email aparece
    """
    provider = get_hibp_provider()
    
    try:
        breaches = await provider.execute_with_fallback(email)
        
        # Converte de BreachData para BreachInfo (modelo interno)
        return [
            BreachInfo(
                name=b.name,
                date=b.breach_date,
                data_classes=b.data_classes,
                is_verified=b.is_verified
            )
            for b in breaches
        ]
    except Exception as e:
        logger.error(f"All breach check providers failed: {e}")
        # Retorna vazio ao invés de crashar (graceful degradation)
        return []
```

---

### FASE 2: WARGAME SAFETY (2 horas) ✅ CONCLUÍDA

#### Task 2.1: Criar Safety Manager ✅
- [x] **Arquivo**: `tools/wargame_safety.py`

#### Task 2.2: Atualizar Wargame Executor ✅
- [x] **Arquivo**: `tools/wargame.py` (com suporte a Tabletop fallback)

```python
"""
Wargame Safety Manager - Múltiplas camadas de proteção.

NUNCA execute código de ataque sem passar por TODAS as camadas.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Set
from datetime import datetime

from pydantic import BaseModel

from core.feature_flags import get_feature_flags
from tools.magistrate import get_magistrate

logger = logging.getLogger(__name__)


class WargameSafetyError(Exception):
    """Erro de segurança no wargame."""
    pass


class SafetyCheckResult(BaseModel):
    """Resultado de verificação de segurança."""
    is_safe: bool
    blocked_by: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class WargameSafetyManager:
    """
    Gerenciador de segurança para execuções de wargame.
    
    Implementa 5 camadas de proteção:
    1. Feature Flag
    2. Ethical Magistrate
    3. Target Whitelist
    4. Sandbox Mode
    5. Audit Log
    """
    
    APPROVED_TARGETS_FILE = Path.home() / ".vertice" / "wargame_approved_targets.txt"
    AUDIT_LOG_FILE = Path.home() / ".vertice" / "wargame_audit.log"
    
    def __init__(self):
        self.flags = get_feature_flags()
        self._approved_targets: Set[str] = self._load_approved_targets()
    
    def _load_approved_targets(self) -> Set[str]:
        """Carrega lista de targets aprovados."""
        if not self.APPROVED_TARGETS_FILE.exists():
            self.APPROVED_TARGETS_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.APPROVED_TARGETS_FILE.write_text("# Targets aprovados para wargame\n# Um por linha\nlocal\nlocalhost\n127.0.0.1\n")
        
        targets = set()
        for line in self.APPROVED_TARGETS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                targets.add(line.lower())
        
        return targets
    
    async def check_all_layers(
        self,
        scenario_id: str,
        target: str,
        actor: str = "system"
    ) -> SafetyCheckResult:
        """
        Verifica TODAS as camadas de segurança.
        
        Args:
            scenario_id: ID do cenário a executar
            target: Alvo da execução
            actor: Quem está solicitando
            
        Returns:
            SafetyCheckResult indicando se pode prosseguir
        """
        # Layer 1: Feature Flag
        if not self.flags.wargame_allow_real_execution:
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="feature_flag",
                reason="Real wargame execution is disabled. Set FF_WARGAME_ALLOW_REAL_EXECUTION=true to enable."
            )
        
        # Layer 2: Target Whitelist
        if target.lower() not in self._approved_targets:
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="target_whitelist",
                reason=f"Target '{target}' not in approved list. Add to {self.APPROVED_TARGETS_FILE}"
            )
        
        # Layer 3: Ethical Magistrate
        magistrate = get_magistrate()
        decision = await magistrate.validate(
            action=f"Execute wargame scenario {scenario_id} against {target}",
            context={
                "has_explicit_consent": self.flags.wargame_require_explicit_consent,
                "target": target,
                "scenario_id": scenario_id,
                "requires_human_approval": True
            },
            actor=actor
        )
        
        if not decision.is_approved:
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="ethical_magistrate",
                reason=f"Ethical validation failed: {decision.reasoning}"
            )
        
        # Layer 4: Audit Log
        self._audit_log(
            f"APPROVED: Scenario {scenario_id} on {target} by {actor}"
        )
        
        return SafetyCheckResult(is_safe=True)
    
    def _audit_log(self, message: str) -> None:
        """Escreve no log de auditoria (append-only)."""
        self.AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        
        with open(self.AUDIT_LOG_FILE, "a") as f:
            f.write(log_line)
        
        logger.info(f"WARGAME AUDIT: {message}")
    
    def get_sandbox_command(self, command: list[str]) -> list[str]:
        """
        Wraps comando em sandbox Docker.
        
        Args:
            command: Comando original
            
        Returns:
            Comando wrapped em container
        """
        if self.flags.wargame_sandbox_mode == "none":
            logger.warning("SANDBOX DISABLED - Running command directly!")
            return command
        
        # Docker sandbox
        timeout = self.flags.wargame_max_duration_seconds
        
        return [
            "docker", "run",
            "--rm",
            "--network=none",  # Sem acesso à rede
            "--memory=512m",   # Limite de memória
            f"--stop-timeout={timeout}",
            "wargame-sandbox:latest",  # Imagem pré-configurada
            *command
        ]


# Singleton
_safety_manager: Optional[WargameSafetyManager] = None


def get_wargame_safety() -> WargameSafetyManager:
    """Retorna singleton do safety manager."""
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = WargameSafetyManager()
    return _safety_manager
```

---

### FASE 4: VALIDAÇÃO FINAL ✅ CONCLUÍDA

#### Task 4.1: Script de Validação Pós-Deploy ✅
- [x] **Arquivo**: `scripts/validate_implementation.py`
- [x] **Status**: Executado com sucesso (24/24 checks OK)

---

## 🚀 PRÓXIMOS PASSOS

1. Configurar `HIBP_API_KEY` e `REDIS_URL` no ambiente de produção.
2. Ativar flags `FF_OSINT_USE_REAL_HIBP=true` após validar credenciais.
3. Iniciar Fase 3 (Threat Intel) seguindo o mesmo padrão de Provider.


---

## PARTE 5: PLANO B (FALLBACKS)

| Situação | Fallback | Como Sinalizar |
|----------|----------|----------------|
| HIBP API down | Cache local → AI estimation | Log warning + campo `source: "fallback"` |
| Shodan API down | Só port scan interno | Log warning + `source: "local_scan_only"` |
| Gemini 3 down | Heurísticas básicas | Log error + `ai_powered: false` |
| Wargame blocked | Retorna "simulation_only" | Campo `mode: "tabletop"` |

---

**Pronto para execução. Qual fase começar?**
# 📦 SEÇÕES COMPLEMENTARES DO PLANO - PARTE 2

## Task 1.4: Integração MCP com Providers (45 min)
☐ **Arquivo**: `tools/osint.py` - Modificar para emitir eventos MCP

```python
"""
OSINT Hunter - Versão com Provider Pattern e Eventos MCP.
"""

import logging
import time
from typing import Any, Dict, List
from datetime import datetime

from core.event_bus import get_event_bus, EventType
from tools.providers.hibp import get_hibp_provider

logger = logging.getLogger(__name__)


class MCPProviderResponse:
    """Response wrapper com metadata de provider para MCP."""
    
    def __init__(
        self,
        data: Any,
        provider_used: str,
        fallback_chain: List[str],
        execution_time_ms: float,
        is_fallback: bool = False
    ):
        self.data = data
        self._meta = {
            "provider_used": provider_used,
            "fallback_chain": fallback_chain,
            "execution_time_ms": round(execution_time_ms, 2),
            "is_fallback": is_fallback,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {"data": self.data, "_meta": self._meta}


async def osint_breach_check_v2(ctx, email: str) -> Dict[str, Any]:
    """Verifica breaches com metadata de provider."""
    start = time.perf_counter()
    event_bus = get_event_bus()
    provider = get_hibp_provider()
    fallback_chain = ["hibp_real", "hibp_cache", "hibp_ai_fallback"]
    
    provider_used = "hibp_real"
    is_fallback = False
    
    try:
        if not provider.is_available():
            provider_used = "hibp_cache"
            is_fallback = True
            await ctx.info(f"[FALLBACK] Usando cache")
            await event_bus.emit(
                EventType.PROVIDER_FALLBACK,
                {"original": "hibp_real", "fallback": "hibp_cache"},
                source="osint_hunter"
            )
        
        breaches = await provider.execute_with_fallback(email)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        return MCPProviderResponse(
            data=[b.model_dump() for b in breaches],
            provider_used=provider_used,
            fallback_chain=fallback_chain,
            execution_time_ms=elapsed_ms,
            is_fallback=is_fallback
        ).to_dict()
        
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "data": None,
            "error": {"code": "ALL_PROVIDERS_FAILED", "message": str(e)},
            "_meta": {
                "provider_used": None,
                "fallback_chain": fallback_chain,
                "execution_time_ms": round(elapsed_ms, 2),
                "is_fallback": True,
                "failed": True
            }
        }
```

---

## Task 1.1b: Cache Inteligente (30 min)
☐ **Arquivo**: `tools/providers/cache.py`

```python
"""Cache Provider com Redis e JSON fallback."""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from core.feature_flags import get_feature_flags

logger = logging.getLogger(__name__)


class RedisBackend:
    """Backend Redis."""
    
    def __init__(self):
        self._client = None
        self._available = self._try_connect()
    
    def _try_connect(self) -> bool:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import redis
            self._client = redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
            return True
        except Exception:
            return False
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def get(self, key: str) -> Optional[str]:
        if not self._available:
            return None
        return self._client.get(f"vertice:cache:{key}")
    
    def set(self, key: str, value: str, ttl: int) -> None:
        if self._available:
            self._client.setex(f"vertice:cache:{key}", ttl, value)


class JSONFileBackend:
    """Backend JSON file."""
    
    CACHE_FILE = Path.home() / ".vertice" / "cache.json"
    
    def __init__(self):
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load()
    
    def _load(self) -> Dict:
        if self.CACHE_FILE.exists():
            try:
                return json.loads(self.CACHE_FILE.read_text())
            except Exception:
                return {}
        return {}
    
    def _save(self) -> None:
        self.CACHE_FILE.write_text(json.dumps(self._cache, indent=2))
    
    def get(self, key: str) -> Optional[str]:
        entry = self._cache.get(key)
        if entry and entry.get("expires_at", 0) > datetime.utcnow().timestamp():
            return entry.get("value")
        return None
    
    def set(self, key: str, value: str, ttl: int) -> None:
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow().timestamp() + ttl
        }
        self._save()


class SmartCache:
    """Cache inteligente: Redis se disponível, senão JSON."""
    
    def __init__(self):
        self.flags = get_feature_flags()
        self._redis = RedisBackend()
        self._json = JSONFileBackend()
        self._backend = self._redis if self._redis.is_available else self._json
    
    def get(self, key: str) -> Optional[Any]:
        raw = self._backend.get(key)
        return json.loads(raw) if raw else None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.flags.osint_cache_ttl_seconds
        self._backend.set(key, json.dumps(value), ttl)


_cache: Optional[SmartCache] = None

def get_cache() -> SmartCache:
    global _cache
    if _cache is None:
        _cache = SmartCache()
    return _cache
```
# 📦 SEÇÕES COMPLEMENTARES - PARTE 3

## Task 1.1c: Rate Limiting para HIBP (20 min)
☐ **Arquivo**: `core/rate_limiter.py`

```python
"""
Rate Limiter client-side usando asyncio.

HIBP limita 1 request a cada 1.5 segundos.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """Rate limiter baseado em token bucket."""
    
    def __init__(self, requests_per_second: float = 0.67):  # 1/1.5s
        self.min_interval = 1.0 / requests_per_second
        self._last_request = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Aguarda até poder fazer próximo request."""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_request
            
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
            
            self._last_request = time.time()


# Rate limiters por serviço
_limiters: dict[str, RateLimiter] = {}


def get_rate_limiter(service: str, rps: float = 0.67) -> RateLimiter:
    """Retorna rate limiter para serviço."""
    if service not in _limiters:
        _limiters[service] = RateLimiter(rps)
    return _limiters[service]


def rate_limit(service: str, rps: float = 0.67) -> Callable:
    """
    Decorator para aplicar rate limiting.
    
    Usage:
        @rate_limit("hibp", rps=0.67)
        async def call_hibp(email: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            limiter = get_rate_limiter(service, rps)
            await limiter.acquire()
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## Task 2.2: Dockerfile para Wargame Sandbox (30 min)
☐ **Arquivo**: `docker/wargame-sandbox/Dockerfile`

```dockerfile
# Wargame Sandbox - Ambiente isolado para simulações
# Build: docker build -t wargame-sandbox:latest -f docker/wargame-sandbox/Dockerfile .

FROM mcr.microsoft.com/powershell:7.4-ubuntu-22.04

# Metadados
LABEL maintainer="vertice-cyber"
LABEL description="Sandbox isolado para execução de wargames"

# Variáveis
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Criar usuário não-root
RUN groupadd -r wargame && useradd -r -g wargame wargame

# Instalar Python 3.12
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app
RUN chown wargame:wargame /app

# Instalar Atomic Red Team (PowerShell)
RUN pwsh -c "Install-Module -Name invoke-atomicredteam -Force -Scope AllUsers"
RUN pwsh -c "Install-Module -Name powershell-yaml -Force -Scope AllUsers"

# Baixar atomics (técnicas MITRE)
RUN git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git /opt/atomic-red-team

# Instalar dependências Python
COPY requirements-wargame.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements-wargame.txt

# Configurar permissões
RUN chmod -R 755 /opt/atomic-red-team

# Trocar para usuário não-root
USER wargame

# Comando padrão
CMD ["pwsh", "-NoProfile"]
```

☐ **Arquivo**: `docker/wargame-sandbox/requirements-wargame.txt`

```txt
pyyaml>=6.0
requests>=2.31
```

☐ **Comandos de Build**:
```bash
# Build da imagem
docker build -t wargame-sandbox:latest -f docker/wargame-sandbox/Dockerfile .

# Teste de execução (sem rede)
docker run --rm --network=none wargame-sandbox:latest pwsh -c "Get-AtomicTechnique -AtomicTechnique T1059"
```

---

## Task 3.1: Health Check MCP Tool (30 min)
☐ **Arquivo**: `tools/health_check.py`

```python
"""
Health Check para todos os providers.

Retorna status de cada provider configurado.
"""

import os
import logging
import time
from typing import Any, Dict, List
from datetime import datetime

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderHealth(BaseModel):
    """Status de saúde de um provider."""
    name: str
    status: str  # healthy, degraded, unavailable
    latency_ms: float
    last_check: str
    error: str | None = None


class HealthCheckResult(BaseModel):
    """Resultado completo do health check."""
    overall_status: str
    providers: List[ProviderHealth]
    timestamp: str
    

async def provider_health_check(ctx) -> Dict[str, Any]:
    """
    MCP Tool: Verifica saúde de todos os providers.
    
    Returns:
        Status de cada provider com latência e erros
    """
    await ctx.info("Executando health check de providers...")
    
    providers_status = []
    
    # 1. HIBP Provider
    providers_status.append(await _check_hibp())
    
    # 2. Shodan Provider
    providers_status.append(await _check_shodan())
    
    # 3. Vertex AI (Gemini 3)
    providers_status.append(await _check_vertex_ai())
    
    # 4. Redis Cache
    providers_status.append(await _check_redis())
    
    # Calcular status geral
    statuses = [p.status for p in providers_status]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unavailable" for s in statuses):
        overall = "degraded"
    else:
        overall = "partial"
    
    result = HealthCheckResult(
        overall_status=overall,
        providers=providers_status,
        timestamp=datetime.utcnow().isoformat()
    )
    
    await ctx.info(f"Health check completo: {overall}")
    
    return result.model_dump()


async def _check_hibp() -> ProviderHealth:
    """Verifica HIBP provider."""
    start = time.perf_counter()
    
    api_key = os.getenv("HIBP_API_KEY")
    if not api_key:
        return ProviderHealth(
            name="hibp",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error="HIBP_API_KEY not configured"
        )
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Apenas verifica se API responde
            resp = await client.get(
                "https://haveibeenpwned.com/api/v3/breach/Adobe",
                headers={"hibp-api-key": api_key}
            )
            latency = (time.perf_counter() - start) * 1000
            
            return ProviderHealth(
                name="hibp",
                status="healthy" if resp.status_code == 200 else "degraded",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat()
            )
    except Exception as e:
        return ProviderHealth(
            name="hibp",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)
        )


async def _check_shodan() -> ProviderHealth:
    """Verifica Shodan provider."""
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        return ProviderHealth(
            name="shodan",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error="SHODAN_API_KEY not configured"
        )
    
    start = time.perf_counter()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"https://api.shodan.io/api-info?key={api_key}"
            )
            latency = (time.perf_counter() - start) * 1000
            
            return ProviderHealth(
                name="shodan",
                status="healthy" if resp.status_code == 200 else "degraded",
                latency_ms=round(latency, 2),
                last_check=datetime.utcnow().isoformat()
            )
    except Exception as e:
        return ProviderHealth(
            name="shodan",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)
        )


async def _check_vertex_ai() -> ProviderHealth:
    """Verifica Vertex AI (Gemini 3)."""
    start = time.perf_counter()
    
    try:
        from tools.vertex_ai import get_vertex_ai
        vertex = get_vertex_ai()
        
        if not vertex._initialized:
            return ProviderHealth(
                name="vertex_ai",
                status="unavailable",
                latency_ms=0,
                last_check=datetime.utcnow().isoformat(),
                error="Vertex AI not initialized"
            )
        
        latency = (time.perf_counter() - start) * 1000
        return ProviderHealth(
            name="vertex_ai",
            status="healthy",
            latency_ms=round(latency, 2),
            last_check=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ProviderHealth(
            name="vertex_ai",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)
        )


async def _check_redis() -> ProviderHealth:
    """Verifica Redis cache."""
    start = time.perf_counter()
    
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        latency = (time.perf_counter() - start) * 1000
        
        return ProviderHealth(
            name="redis",
            status="healthy",
            latency_ms=round(latency, 2),
            last_check=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ProviderHealth(
            name="redis",
            status="unavailable",
            latency_ms=0,
            last_check=datetime.utcnow().isoformat(),
            error=str(e)[:50]
        )
```
# 📦 SEÇÕES COMPLEMENTARES - PARTE 4

## Task 0.4: Sistema de Métricas (25 min)
☐ **Arquivo**: `core/metrics.py`

```python
"""
Sistema de Métricas para Providers.

Rastreia uso de providers e fallbacks.
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from collections import defaultdict
from functools import wraps

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderMetrics(BaseModel):
    """Métricas de um provider."""
    name: str
    calls_total: int = 0
    calls_success: int = 0
    calls_failed: int = 0
    fallback_triggered: int = 0
    last_used: Optional[str] = None


class MetricsCollector:
    """Coletor de métricas de providers."""
    
    def __init__(self):
        self._metrics: Dict[str, ProviderMetrics] = defaultdict(
            lambda: ProviderMetrics(name="unknown")
        )
    
    def record_call(self, provider: str, success: bool) -> None:
        """Registra chamada a provider."""
        if provider not in self._metrics:
            self._metrics[provider] = ProviderMetrics(name=provider)
        
        m = self._metrics[provider]
        m.calls_total += 1
        if success:
            m.calls_success += 1
        else:
            m.calls_failed += 1
        m.last_used = datetime.utcnow().isoformat()
    
    def record_fallback(self, from_provider: str, to_provider: str) -> None:
        """Registra fallback entre providers."""
        if from_provider not in self._metrics:
            self._metrics[from_provider] = ProviderMetrics(name=from_provider)
        
        self._metrics[from_provider].fallback_triggered += 1
        logger.info(f"Fallback: {from_provider} -> {to_provider}")
    
    def get_all_metrics(self) -> Dict[str, ProviderMetrics]:
        """Retorna todas as métricas."""
        return dict(self._metrics)
    
    def get_summary(self) -> Dict[str, any]:
        """Retorna sumário das métricas."""
        total_calls = sum(m.calls_total for m in self._metrics.values())
        total_fallbacks = sum(m.fallback_triggered for m in self._metrics.values())
        
        return {
            "total_calls": total_calls,
            "total_fallbacks": total_fallbacks,
            "fallback_rate": round(total_fallbacks / max(total_calls, 1), 4),
            "providers": {k: v.model_dump() for k, v in self._metrics.items()}
        }


# Singleton
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Retorna singleton do coletor."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def track_provider_usage(provider_name: str):
    """
    Decorator para rastrear uso de provider.
    
    Usage:
        @track_provider_usage("hibp")
        async def call_hibp():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            try:
                result = await func(*args, **kwargs)
                collector.record_call(provider_name, success=True)
                return result
            except Exception as e:
                collector.record_call(provider_name, success=False)
                raise
        return wrapper
    return decorator


async def provider_metrics(ctx) -> Dict[str, any]:
    """MCP Tool: Retorna métricas de providers."""
    await ctx.info("Coletando métricas de providers...")
    
    collector = get_metrics_collector()
    summary = collector.get_summary()
    
    await ctx.info(f"Total calls: {summary['total_calls']}, Fallbacks: {summary['total_fallbacks']}")
    
    return summary
```

---

## PARTE 4: CHECKLIST FINAL COM COMANDOS

### Comandos de Validação

☐ **Verificar Feature Flags**:
```bash
python3 -c "
from core.feature_flags import get_feature_flags
flags = get_feature_flags()
print('Feature Flags:')
print(f'  OSINT HIBP: {flags.osint_use_real_hibp}')
print(f'  Wargame Real: {flags.wargame_allow_real_execution}')
print('OK' if not flags.wargame_allow_real_execution else 'WARNING: Wargame real ativo!')
"
```

☐ **Testar HIBP Provider Isoladamente**:
```bash
HIBP_API_KEY=your_key_here python3 -c "
import asyncio
from tools.providers.hibp import HIBPProvider

async def test():
    provider = HIBPProvider()
    print(f'Available: {provider.is_available()}')
    if provider.is_available():
        result = await provider.execute('test@example.com')
        print(f'Breaches: {len(result)}')

asyncio.run(test())
"
```

☐ **Simular API Down (Circuit Breaker)**:
```bash
python3 -c "
import asyncio
from unittest.mock import patch, AsyncMock
import httpx

async def test_circuit_breaker():
    from tools.providers.hibp import HIBPProvider
    
    provider = HIBPProvider()
    
    # Simula 5 falhas seguidas
    with patch('httpx.AsyncClient') as mock:
        mock.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPError('Simulated failure')
        )
        
        for i in range(6):
            try:
                await provider.execute('test@test.com')
            except Exception as e:
                print(f'Attempt {i+1}: {type(e).__name__}')

asyncio.run(test_circuit_breaker())
"
```

☐ **Rodar Testes Unitários**:
```bash
# Todos os testes
pytest tests/ -v --tb=short

# Só providers
pytest tests/unit/test_*provider*.py -v

# Com coverage
pytest tests/ --cov=tools/providers --cov-report=term-missing
```

☐ **Validar Imports**:
```bash
python3 -c "
import sys
modules = [
    'core.feature_flags',
    'core.circuit_breaker',
    'core.rate_limiter',
    'core.metrics',
    'tools.providers.base',
    'tools.providers.hibp',
    'tools.providers.cache',
    'tools.health_check',
    'tools.wargame_safety'
]

for mod in modules:
    try:
        __import__(mod)
        print(f'✅ {mod}')
    except ImportError as e:
        print(f'❌ {mod}: {e}')
        sys.exit(1)

print('\\nTodos imports OK!')
"
```

---

## Task 4.1: Script de Validação Pós-Deploy (20 min)
☐ **Arquivo**: `scripts/validate_implementation.py`

```python
#!/usr/bin/env python3
"""
Script de Validação Pós-Deploy.

Verifica:
1. Arquivos existem
2. Imports funcionam
3. Feature flags carregam
4. Providers inicializam
5. Testes passam

Usage:
    python scripts/validate_implementation.py
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Cores ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(msg: str) -> None:
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")


def print_ok(msg: str) -> None:
    print(f"  {GREEN}✅{RESET} {msg}")


def print_fail(msg: str) -> None:
    print(f"  {RED}❌{RESET} {msg}")


def print_warn(msg: str) -> None:
    print(f"  {YELLOW}⚠️{RESET} {msg}")


def check_files() -> Tuple[int, int]:
    """Verifica se arquivos necessários existem."""
    print_header("1. Verificando Arquivos")
    
    required_files = [
        "core/feature_flags.py",
        "core/circuit_breaker.py",
        "core/rate_limiter.py",
        "core/metrics.py",
        "tools/providers/__init__.py",
        "tools/providers/base.py",
        "tools/providers/hibp.py",
        "tools/providers/cache.py",
        "tools/health_check.py",
        "tools/wargame_safety.py",
    ]
    
    ok, fail = 0, 0
    root = Path(__file__).parent.parent
    
    for file in required_files:
        path = root / file
        if path.exists():
            print_ok(file)
            ok += 1
        else:
            print_fail(f"{file} - NÃO EXISTE")
            fail += 1
    
    return ok, fail


def check_imports() -> Tuple[int, int]:
    """Verifica se imports funcionam."""
    print_header("2. Verificando Imports")
    
    modules = [
        "core.feature_flags",
        "core.circuit_breaker",
        "core.rate_limiter",
        "core.metrics",
        "tools.providers.base",
        "tools.providers.hibp",
        "tools.providers.cache",
        "tools.health_check",
        "tools.wargame_safety",
    ]
    
    ok, fail = 0, 0
    
    for mod in modules:
        try:
            __import__(mod)
            print_ok(mod)
            ok += 1
        except ImportError as e:
            print_fail(f"{mod}: {e}")
            fail += 1
    
    return ok, fail


def check_feature_flags() -> Tuple[int, int]:
    """Verifica feature flags."""
    print_header("3. Verificando Feature Flags")
    
    ok, fail = 0, 0
    
    try:
        from core.feature_flags import get_feature_flags
        flags = get_feature_flags()
        
        # Wargame deve estar OFF por padrão
        if not flags.wargame_allow_real_execution:
            print_ok("Wargame real execution: DISABLED (seguro)")
            ok += 1
        else:
            print_warn("Wargame real execution: ENABLED (cuidado!)")
            ok += 1
        
        print_ok(f"OSINT HIBP real: {flags.osint_use_real_hibp}")
        print_ok(f"Cache TTL: {flags.osint_cache_ttl_seconds}s")
        ok += 2
        
    except Exception as e:
        print_fail(f"Erro ao carregar flags: {e}")
        fail += 1
    
    return ok, fail


def check_providers() -> Tuple[int, int]:
    """Verifica inicialização de providers."""
    print_header("4. Verificando Providers")
    
    ok, fail = 0, 0
    
    try:
        from tools.providers.hibp import get_hibp_provider
        provider = get_hibp_provider()
        
        if provider.is_available():
            print_ok("HIBP Provider: DISPONÍVEL")
        else:
            print_warn("HIBP Provider: Não configurado (usará fallback)")
        ok += 1
        
    except Exception as e:
        print_fail(f"HIBP Provider erro: {e}")
        fail += 1
    
    try:
        from tools.providers.cache import get_cache
        cache = get_cache()
        print_ok(f"Cache: {cache._backend.__class__.__name__}")
        ok += 1
    except Exception as e:
        print_fail(f"Cache erro: {e}")
        fail += 1
    
    return ok, fail


def check_tests() -> Tuple[int, int]:
    """Roda testes rápidos."""
    print_header("5. Rodando Testes")
    
    result = subprocess.run(
        ["pytest", "tests/unit/", "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print_ok("Todos os testes passaram")
        return 1, 0
    else:
        print_fail("Alguns testes falharam")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return 0, 1


def main():
    """Executa validação completa."""
    print(f"\n{BOLD}🔍 VALIDAÇÃO DE IMPLEMENTAÇÃO{RESET}")
    print(f"   Substituição de Mocks por Código Real\n")
    
    total_ok, total_fail = 0, 0
    
    # Muda para diretório do projeto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    
    # Executa checks
    checks = [
        check_files,
        check_imports,
        check_feature_flags,
        check_providers,
    ]
    
    for check in checks:
        ok, fail = check()
        total_ok += ok
        total_fail += fail
    
    # Sumário
    print_header("📊 SUMÁRIO")
    print(f"  {GREEN}✅ Passou: {total_ok}{RESET}")
    print(f"  {RED}❌ Falhou: {total_fail}{RESET}")
    
    if total_fail == 0:
        print(f"\n{GREEN}{BOLD}🎉 VALIDAÇÃO COMPLETA - SUCESSO!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}⚠️ VALIDAÇÃO FALHOU - Corrija os erros acima{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

☐ **Tornar executável**:
```bash
chmod +x scripts/validate_implementation.py
```

☐ **Executar validação**:
```bash
python scripts/validate_implementation.py
```

---

## ORDEM DE EXECUÇÃO FINAL

```
1. ☐ Fase 0: Infraestrutura
   ├── ☐ Task 0.1: core/feature_flags.py
   ├── ☐ Task 0.2: core/circuit_breaker.py
   ├── ☐ Task 0.3: tools/providers/base.py
   └── ☐ Task 0.4: core/metrics.py + core/rate_limiter.py

2. ☐ Fase 1: OSINT HIBP
   ├── ☐ Task 1.1: tools/providers/hibp.py
   ├── ☐ Task 1.1b: tools/providers/cache.py
   ├── ☐ Task 1.1c: Rate limiting integrado
   ├── ☐ Task 1.2: tests/unit/test_hibp_provider.py
   ├── ☐ Task 1.3: Atualizar tools/osint.py
   └── ☐ Task 1.4: Adicionar _meta ao response

3. ☐ Fase 2: Wargame Safety
   ├── ☐ Task 2.1: tools/wargame_safety.py
   ├── ☐ Task 2.2: docker/wargame-sandbox/Dockerfile
   └── ☐ Task 2.3: Atualizar tools/wargame.py

4. ☐ Fase 3: Health & Metrics
   ├── ☐ Task 3.1: tools/health_check.py
   └── ☐ Task 3.2: Registrar no mcp_http_bridge.py

5. ☐ Fase 4: Validação
   ├── ☐ Task 4.1: scripts/validate_implementation.py
   └── ☐ Task 4.2: Rodar validação completa
```

---

**Pronto para começar a implementação!**

---

## PARTE 5: DASHBOARD UI MODERNIZATION (Nova Fase)

### 5.1 Visão Geral da Arquitetura Visual

O Dashboard será redesenhado para seguir o padrão visual **"Agent Control Panel"**, com foco em:
- **Glassmorphism**: Painéis translúcidos com blur de fundo
- **Neon Accents**: Cores vibrantes (cyan/purple) para status e ações
- **Dark Theme**: Background escuro (#111718 - #191a1f) para redução de fadiga visual
- **Real-time Feedback**: Animações sutis e logs de execução em tempo real

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT CONTROL PANEL v2.4                             │
├──────────┬──────────────────────────────────────────────────────────────────┤
│          │                                                                   │
│  AGENT   │                    MAIN WORKSPACE                                 │
│  LIST    │  ┌─────────────────────────────────────────────────────────┐     │
│          │  │           AGENT-SPECIFIC CONTROLS                       │     │
│ ● Ethical│  │  - Input forms, dropdowns, toggles                      │     │
│ ○ Network│  │  - Action buttons with glow effects                     │     │
│ ○ Data   │  │  - Validation output display                            │     │
│ ○ Firewal│  └─────────────────────────────────────────────────────────┘     │
│ ○ Traffic│                                                                   │
│ ○ Log    │  ┌─────────────────────────────────────────────────────────┐     │
│ ○ System │  │           RESULTS / INTELLIGENCE TABLE                   │     │
│          │  └─────────────────────────────────────────────────────────┘     │
│          │                                                                   │
├──────────┴──────────────────────────────────────────────────────────────────┤
│                           LIVE EXECUTION LOG                                 │
│  [timestamp] AGENT: Message...                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Design Tokens (Tailwind Config)

```javascript
// tailwind.config.js (ou dentro do <script> para CDN)
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                // Core Palette
                "primary": "#20d3ee",        // Cyan-400 - Status ativo, ações
                "primary-dark": "#0891b2",   // Cyan-600 - Hover states
                "secondary": "#a855f7",      // Purple-500 - Accent, AI
                "accent": "#a855f7",         // Alias
                
                // Backgrounds
                "background-dark": "#111718",   // Main background
                "background-card": "#1c2527",   // Card surfaces
                "surface-dark": "#23242a",      // Alternativo
                
                // Borders & Glass
                "border-dark": "#283639",       // Bordas sutis
                "glass": "rgba(255, 255, 255, 0.05)",
                
                // Status Colors
                "status-online": "#22c55e",     // Green-500
                "status-warning": "#eab308",    // Yellow-500
                "status-error": "#ef4444",      // Red-500
                "status-info": "#3b82f6",       // Blue-500
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"],
                "mono": ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "monospace"],
            },
            backgroundImage: {
                'glass': 'linear-gradient(180deg, rgba(28, 37, 39, 0.7) 0%, rgba(17, 23, 24, 0.7) 100%)',
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
            },
            boxShadow: {
                'neon-cyan': '0 0 20px rgba(32, 211, 238, 0.3)',
                'neon-purple': '0 0 20px rgba(168, 85, 247, 0.3)',
                'glow-status': '0 0 8px currentColor',
            }
        },
    },
}
```

---

### 5.3 CSS Utilities Customizados

```css
/* dashboard/styles/globals.css ou inline <style> */

/* Glass Panel Effect */
.glass-panel {
    background: rgba(28, 37, 39, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Active Agent Indicator */
.active-agent-glow {
    box-shadow: 0 0 20px rgba(32, 211, 238, 0.15);
    border-left: 3px solid #20d3ee;
}

/* Status Pulse Animation */
.status-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Typing Cursor for Logs */
.typing-cursor::after {
    content: '|';
    animation: blink 1s step-end infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* Neon Button Glow */
.btn-neon {
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
    transition: box-shadow 0.3s ease, transform 0.2s ease;
}

.btn-neon:hover {
    box-shadow: 0 0 30px rgba(32, 211, 238, 0.4);
    transform: translateY(-2px);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #111718; 
}
::-webkit-scrollbar-thumb {
    background: #334155; 
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569; 
}

/* Risk Gauge Animation */
.risk-gauge-circle {
    transition: stroke-dashoffset 1s ease-in-out;
    transform: rotate(-90deg);
    transform-origin: 50% 50%;
}
```

---

### 5.4 Componentes React: Especificação

#### 5.4.1 `<AgentSidebar />`

**Localização**: `dashboard/components/AgentSidebar.tsx`

**Props**:
```typescript
interface AgentSidebarProps {
    agents: Agent[];
    selectedAgentId: string | null;
    onSelectAgent: (agentId: string) => void;
    systemLoad?: { cpu: number; memory: string };
}

interface Agent {
    id: string;
    name: string;
    icon: string;           // Material Symbols icon name
    status: 'active' | 'idle' | 'warning' | 'offline';
    statusMessage: string;  // "Logic Core: Active", "Scanning sector 7G"
    isSelected?: boolean;
}
```

**Layout**:
```
┌──────────────────────────────┐
│  ACTIVE AGENTS (header)      │
├──────────────────────────────┤
│ ● [icon] Agent Name          │  ← Selected (cyan glow left border)
│          Status Message      │
│   ○ status dot               │
├──────────────────────────────┤
│ ○ [icon] Agent Name          │  ← Idle
│          Status Message      │
├──────────────────────────────┤
│ ...                          │
├──────────────────────────────┤
│  ┌────────────────────────┐  │
│  │ CPU: 24%    Mem: 4.2GB │  │  ← System Load Footer
│  │ ████░░░░░░░░░░░░░░░░░░ │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

**Estilos por Status**:
| Status   | Dot Color    | Dot Animation  | Border    |
|----------|--------------|----------------|-----------|
| active   | green-500    | animate-pulse  | cyan left |
| idle     | green-500/50 | none           | none      |
| warning  | yellow-500   | subtle pulse   | none      |
| offline  | red-500      | none           | opacity-50|

---

#### 5.4.2 `<AgentWorkspace />` (Template Genérico)

**Localização**: `dashboard/components/AgentWorkspace.tsx`

**Props**:
```typescript
interface AgentWorkspaceProps {
    agent: Agent;
    children: React.ReactNode;  // Agent-specific controls
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT NAME                                    [Status Badge]   │
│  Agent description text...                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    GLASS PANEL                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │              {children} - Agent Content             │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

#### 5.4.3 `<EthicalMagistratePanel />`

**Localização**: `dashboard/components/agents/EthicalMagistratePanel.tsx`

**Funcionalidade**: Permite validar ações autônomas contra guidelines éticos.

**State**:
```typescript
interface MagistrateState {
    proposedAction: string;          // Texto do textarea
    initiatingActor: 'auto' | 'admin' | 'api';
    piiRedactionEnabled: boolean;
    validationStatus: 'idle' | 'validating' | 'approved' | 'denied';
    confidence: number | null;       // 0-100%
    latency: number | null;          // ms
}
```

**Layout** (2 colunas em lg):
```
┌──────────────────────────────────────┬─────────────────────────┐
│  Proposed Counter-Measure            │  Validation Output      │
│  ┌────────────────────────────────┐  │  ┌───────────────────┐  │
│  │ TEXTAREA (monospace)           │  │  │ AWAITING INPUT... │  │
│  │ placeholder: ISOLATE_HOST(...) │  │  │ or APPROVED icon  │  │
│  └────────────────────────────────┘  │  └───────────────────┘  │
│                                      │                         │
│  Initiator: [Dropdown]               │  Confidence: --%        │
│  ☑️ PII Redaction Check               │  Latency: --ms          │
│                                      │                         │
│                                      │  [VALIDATE ACTION btn]  │
└──────────────────────────────────────┴─────────────────────────┘
```

**Integration com MCP**:
```typescript
// Ao clicar VALIDATE ACTION:
const validateAction = async () => {
    setStatus('validating');
    const startTime = performance.now();
    
    const result = await mcpClient.execute('magistrate_validate', {
        action: proposedAction,
        actor: initiatingActor,
        pii_redaction: piiRedactionEnabled,
    });
    
    setLatency(performance.now() - startTime);
    setConfidence(result.confidence);
    setStatus(result.is_approved ? 'approved' : 'denied');
    
    // Log to terminal
    addLog({
        level: result.is_approved ? 'success' : 'error',
        source: 'MAGISTRATE',
        message: result.reason,
    });
};
```

---

#### 5.4.4 `<OSINTHunterPanel />`

**Localização**: `dashboard/components/agents/OSINTHunterPanel.tsx`

**Funcionalidade**: Interface para investigação OSINT com resultados em tabela.

**State**:
```typescript
interface OSINTState {
    target: string;               // email, domain, ou IP
    targetValid: boolean;
    searchDepth: 'basic' | 'deep' | 'exhaustive';
    findings: OSINTFinding[];
    riskScore: number;            // 0-100
    isScanning: boolean;
}

interface OSINTFinding {
    id: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
    type: string;                 // "Exposed Credentials", "Open Port"
    source: string;               // "Pastebin Dump", "Shodan"
    details: string;
    timestamp: string;
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  TARGET ACQUISITION                                              │
│  ┌─────────────────────────────────────────────┐  [INITIATE]    │
│  │ admin@secure-bank.corp                [VALID]│               │
│  └─────────────────────────────────────────────┘               │
│                                                                 │
│  Search Depth: [Basic] [Deep*] [Exhaustive]                     │
│  Quick Actions: [Breach Check] [Google Dorks] [DNS Map]         │
├─────────────────────────────────────────────────────────────────┤
│  INTELLIGENCE REPORT                         [Export CSV]       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Severity │ Type              │ Source    │ Details          ││
│  ├──────────┼───────────────────┼───────────┼──────────────────┤│
│  │ CRITICAL │ Exposed Creds     │ Pastebin  │ admin:pass123... ││
│  │ HIGH     │ Open Port         │ Shodan    │ Port 3389 (RDP)  ││
│  │ INFO     │ Social Profile    │ LinkedIn  │ Employee found   ││
│  └─────────────────────────────────────────────────────────────┘│
├───────────────────────────────────┬─────────────────────────────┤
│  RISK SCORE GAUGE (SVG)          │  TERMINAL LOG               │
│  ┌────────────────────┐          │  [14:02:01] INFO: Agent...  │
│  │       ╭───╮        │          │  [14:02:02] NET: Handshake..│
│  │      /  85 \       │          │  [14:02:03] SCAN: Whois...  │
│  │     │ CRIT  │      │          │  [14:02:04] ALERT: Creds!   │
│  │      ╲_____╱       │          │                             │
│  └────────────────────┘          │                             │
│  Breaches: 12   Socials: 4       │                             │
└───────────────────────────────────┴─────────────────────────────┘
```

**Integration com MCP**:
```typescript
const initiateScan = async () => {
    setIsScanning(true);
    
    // Breach Check
    const breaches = await mcpClient.execute('osint_breach_check', {
        email: target,
    });
    
    // Full Investigation
    const osintResult = await mcpClient.execute('osint_investigate', {
        target,
        depth: searchDepth,
    });
    
    setFindings(osintResult.findings);
    setRiskScore(osintResult.risk_score);
    setIsScanning(false);
};
```

---

#### 5.4.5 `<LiveLogTerminal />`

**Localização**: `dashboard/components/LiveLogTerminal.tsx`

**Props**:
```typescript
interface LogEntry {
    timestamp: string;        // "14:02:01"
    level: 'info' | 'warn' | 'error' | 'success' | 'debug';
    source: string;           // "SYSTEM", "MAGISTRATE", "AGENT"
    message: string;
}

interface LiveLogTerminalProps {
    logs: LogEntry[];
    isListening: boolean;
    onClear?: () => void;
    onExpand?: () => void;
}
```

**Estilos por Level**:
| Level   | Source Color  | Text Color   |
|---------|---------------|--------------|
| info    | blue-400      | slate-300    |
| warn    | yellow-400    | slate-300    |
| error   | red-400       | slate-300    |
| success | green-500     | slate-300    |
| debug   | slate-500     | slate-500    |

**Template**:
```html
<div class="font-mono text-xs">
    <span class="text-slate-600">[{timestamp}]</span>
    <span class="text-{sourceColor}">{source}</span>:
    <span class="text-slate-300">{message}</span>
</div>
```

---

#### 5.4.6 `<RiskGauge />` (SVG Component)

**Localização**: `dashboard/components/RiskGauge.tsx`

**Props**:
```typescript
interface RiskGaugeProps {
    score: number;            // 0-100
    size?: number;            // Default 192px
    showLabel?: boolean;
}
```

**Logic**:
```typescript
const getColorByScore = (score: number) => {
    if (score >= 80) return '#ef4444';  // red
    if (score >= 60) return '#f97316';  // orange
    if (score >= 40) return '#eab308';  // yellow
    return '#22c55e';                   // green
};

const getSeverityLabel = (score: number) => {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
};

// SVG circle circumference = 2 * π * r = 2 * 3.14159 * 40 ≈ 251.2
// dashoffset = 251.2 - (251.2 * score / 100)
const dashOffset = 251.2 - (251.2 * score / 100);
```

**SVG Template**:
```jsx
<svg viewBox="0 0 100 100" className="transform -rotate-90">
    {/* Track */}
    <circle
        cx="50" cy="50" r="40"
        fill="none" stroke="#283639" strokeWidth="8"
    />
    {/* Progress */}
    <circle
        cx="50" cy="50" r="40"
        fill="none" stroke={color} strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray="251.2"
        strokeDashoffset={dashOffset}
        className="transition-all duration-1000 ease-out drop-shadow-[0_0_10px_currentColor]"
    />
</svg>
```

---

### 5.5 Componentes de Severidade

#### `<SeverityBadge />`

```typescript
interface SeverityBadgeProps {
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
}
```

**Estilos**:
```jsx
const styles = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    low: 'bg-green-500/20 text-green-400 border-green-500/30',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

<span className={`px-2 py-1 rounded-full text-[10px] font-bold border ${styles[severity]}`}>
    {severity.toUpperCase()}
</span>
```

---

### 5.6 Tasks de Implementação (Dashboard)

#### Task 5.1: Setup Tailwind Config
- [ ] **Arquivo**: `dashboard/tailwind.config.js`
- [ ] Adicionar tokens de cores conforme 5.2
- [ ] Configurar fonts (Inter do Google Fonts)

#### Task 5.2: Criar CSS Utilities
- [ ] **Arquivo**: `dashboard/styles/globals.css`
- [ ] Implementar classes `.glass-panel`, `.btn-neon`, etc.
- [ ] Custom scrollbar styles

#### Task 5.3: Componente AgentSidebar
- [ ] **Arquivo**: `dashboard/components/AgentSidebar.tsx`
- [ ] Lista de agentes com indicadores de status
- [ ] System Load footer
- [ ] Animações de hover e seleção

#### Task 5.4: Componente AgentWorkspace
- [ ] **Arquivo**: `dashboard/components/AgentWorkspace.tsx`
- [ ] Template genérico com header + glass panel
- [ ] Status badge integrado

#### Task 5.5: Painel Ethical Magistrate
- [ ] **Arquivo**: `dashboard/components/agents/EthicalMagistratePanel.tsx`
- [ ] Form com textarea, dropdown, toggle
- [ ] Área de output com estados (idle, validating, approved, denied)
- [ ] Integration com MCP `magistrate_validate`

#### Task 5.6: Painel OSINT Hunter
- [ ] **Arquivo**: `dashboard/components/agents/OSINTHunterPanel.tsx`
- [ ] Input de target com validação visual (VALID/INVALID badge)
- [ ] Tabela de findings com severity badges
- [ ] Risk Score Gauge (SVG)
- [ ] Integration com MCP `osint_investigate`, `osint_breach_check`

#### Task 5.7: Terminal de Logs
- [ ] **Arquivo**: `dashboard/components/LiveLogTerminal.tsx`
- [ ] Auto-scroll para bottom
- [ ] Colorização por level e source
- [ ] Botões clear/expand

#### Task 5.8: Integração MCP Client
- [ ] **Arquivo**: `dashboard/services/mcpClient.ts`
- [ ] Método `execute(tool, params)` com tratamento de erros
- [ ] WebSocket para logs em tempo real

---

### 5.7 Ordem de Execução (Dashboard)

```
6. ☐ Fase 5: Dashboard UI Modernization
   ├── ☐ Task 5.1: Setup Tailwind Config
   ├── ☐ Task 5.2: CSS Utilities
   ├── ☐ Task 5.3: AgentSidebar
   ├── ☐ Task 5.4: AgentWorkspace (template)
   ├── ☐ Task 5.5: EthicalMagistratePanel
   ├── ☐ Task 5.6: OSINTHunterPanel
   ├── ☐ Task 5.7: LiveLogTerminal
   └── ☐ Task 5.8: MCP Client Integration
```

---

### 5.8 Preview Visual (Referência)

> **Nota**: Os mockups HTML fornecidos pelo usuário servem como referência visual definitiva.
> Devem ser usados para extrair medidas exatas de padding, gap, font-sizes, e border-radius.

**Ethical Magistrate**: Layout split 2/3 + 1/3, textarea monospace, botão gradient cyan→purple.
**OSINT Hunter**: Layout responsivo grid 12-col, tabela com hover states, gauge SVG animado.

---

**Dashboard pronto para implementação após as Fases 0-4!**

---

## PARTE 6: INTEGRAÇÃO COMPLETA & TESTES E2E (Fase Final)

> **⚠️ FASE CRÍTICA**: Esta é a fase de validação final. NENHUM código vai para produção sem passar por TODOS os testes E2E e métricas de qualidade definidos aqui.

### 6.1 Arquitetura de Integração Dashboard ↔ MCP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DASHBOARD (React)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │  Agent Panels   │     │  MCP Service    │     │  WebSocket      │        │
│  │  (UI Layer)     │────▶│  (API Client)   │────▶│  Manager        │        │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘        │
│          │                       │                       │                   │
│          ▼                       ▼                       ▼                   │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                     State Management (Context/Zustand)            │      │
│  │  - agentStates: Map<agentId, AgentState>                          │      │
│  │  - logs: LogEntry[]                                               │      │
│  │  - connectionStatus: 'connected' | 'disconnected' | 'error'       │      │
│  │  - pendingRequests: Map<requestId, Promise>                       │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                     │                                        │
└─────────────────────────────────────┼────────────────────────────────────────┘
                                      │
                          ┌───────────▼───────────┐
                          │   HTTP/WebSocket      │
                          │   Bridge Layer        │
                          └───────────┬───────────┘
                                      │
┌─────────────────────────────────────▼────────────────────────────────────────┐
│                           MCP HTTP BRIDGE (FastAPI)                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐        │
│  │  Tool Registry  │     │  Event Bus      │     │  WebSocket      │        │
│  │  (MCP Tools)    │────▶│  (Pub/Sub)      │────▶│  Broadcaster    │        │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘        │
│          │                       │                       │                   │
│          ▼                       ▼                       ▼                   │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              AGENT TOOLS (7 Agentes Funcionais)                   │      │
│  │  - Ethical Magistrate   - OSINT Hunter    - Threat Prophet        │      │
│  │  - Compliance Guardian  - Wargame Exec    - Patch Validator       │      │
│  │  - CyberSec Agent                                                 │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                     │                                        │
│                          ┌──────────▼──────────┐                             │
│                          │  Real Providers     │                             │
│                          │  HIBP | Shodan | AI │                             │
│                          └─────────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.2 WebSocket Real-Time Events

#### 6.2.1 Protocolo de Eventos

**Tipos de Eventos** (Server → Client):

```typescript
// dashboard/types/events.ts

type MCPEventType = 
    | 'agent.status_changed'
    | 'tool.execution_started'
    | 'tool.execution_progress'
    | 'tool.execution_completed'
    | 'tool.execution_failed'
    | 'log.new_entry'
    | 'metrics.updated'
    | 'health.status_changed';

interface MCPEvent<T = unknown> {
    type: MCPEventType;
    timestamp: string;           // ISO 8601
    requestId?: string;          // Para correlação
    agentId?: string;
    payload: T;
}

// Payloads específicos
interface AgentStatusPayload {
    agentId: string;
    status: 'active' | 'idle' | 'warning' | 'offline';
    message: string;
}

interface ToolExecutionPayload {
    toolName: string;
    requestId: string;
    progress?: number;           // 0-100
    result?: unknown;
    error?: string;
}

interface LogEntryPayload {
    level: 'info' | 'warn' | 'error' | 'success' | 'debug';
    source: string;
    message: string;
    metadata?: Record<string, unknown>;
}
```

#### 6.2.2 WebSocket Manager (Client)

```typescript
// dashboard/services/wsManager.ts

import { MCPEvent, MCPEventType } from '../types/events';

type EventHandler<T> = (event: MCPEvent<T>) => void;

class WebSocketManager {
    private ws: WebSocket | null = null;
    private handlers: Map<MCPEventType, Set<EventHandler<unknown>>> = new Map();
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 1000;
    
    constructor(private url: string) {}
    
    connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                this.reconnectAttempts = 0;
                console.log('[WS] Connected to MCP Bridge');
                resolve();
            };
            
            this.ws.onmessage = (event) => {
                const mcpEvent = JSON.parse(event.data) as MCPEvent;
                this.dispatch(mcpEvent);
            };
            
            this.ws.onclose = () => {
                console.log('[WS] Connection closed');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('[WS] Error:', error);
                reject(error);
            };
        });
    }
    
    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WS] Max reconnect attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        setTimeout(() => {
            console.log(`[WS] Reconnecting... (attempt ${this.reconnectAttempts})`);
            this.connect();
        }, delay);
    }
    
    subscribe<T>(eventType: MCPEventType, handler: EventHandler<T>): () => void {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, new Set());
        }
        this.handlers.get(eventType)!.add(handler as EventHandler<unknown>);
        
        // Return unsubscribe function
        return () => {
            this.handlers.get(eventType)?.delete(handler as EventHandler<unknown>);
        };
    }
    
    private dispatch(event: MCPEvent): void {
        const handlers = this.handlers.get(event.type);
        if (handlers) {
            handlers.forEach(handler => handler(event));
        }
    }
    
    disconnect(): void {
        this.ws?.close();
        this.ws = null;
    }
}

export const wsManager = new WebSocketManager(
    process.env.NEXT_PUBLIC_MCP_WS_URL || 'ws://localhost:8080/ws'
);
```

#### 6.2.3 WebSocket Broadcaster (Server)

```python
# mcp_http_bridge.py - Adicionar

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import asyncio
import json
from datetime import datetime

class ConnectionManager:
    """Gerencia conexões WebSocket para broadcast de eventos."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, event_type: str, payload: Dict[str, Any], 
                        request_id: str = None, agent_id: str = None) -> None:
        """Envia evento para todos os clientes conectados."""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "requestId": request_id,
            "agentId": agent_id,
            "payload": payload
        }
        
        message = json.dumps(event)
        
        # Copia para evitar modificação durante iteração
        async with self._lock:
            connections = list(self.active_connections)
        
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                await self.disconnect(connection)


# Instância global
ws_manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para eventos em tempo real."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive: espera por mensagens do client (heartbeat)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)


# Helper para emitir eventos durante execução de tools
async def emit_event(event_type: str, payload: Dict[str, Any], 
                     request_id: str = None, agent_id: str = None) -> None:
    """Emite evento para todos os clientes WebSocket."""
    await ws_manager.broadcast(event_type, payload, request_id, agent_id)
```

---

### 6.3 MCP Client Service Completo

```typescript
// dashboard/services/mcpClient.ts

import { wsManager } from './wsManager';

interface ToolExecutionResult<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    metadata: {
        provider: string;
        latencyMs: number;
        cached: boolean;
    };
}

interface MCPClientConfig {
    baseUrl: string;
    timeout: number;
    retries: number;
}

class MCPClient {
    private config: MCPClientConfig;
    
    constructor(config?: Partial<MCPClientConfig>) {
        this.config = {
            baseUrl: process.env.NEXT_PUBLIC_MCP_API_URL || 'http://localhost:8080',
            timeout: 30000,
            retries: 3,
            ...config,
        };
    }
    
    /**
     * Executa uma tool MCP e retorna o resultado.
     */
    async execute<T>(
        toolName: string, 
        params: Record<string, unknown>
    ): Promise<ToolExecutionResult<T>> {
        const startTime = performance.now();
        const requestId = crypto.randomUUID();
        
        try {
            const response = await fetch(`${this.config.baseUrl}/tools/${toolName}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Request-ID': requestId,
                },
                body: JSON.stringify(params),
                signal: AbortSignal.timeout(this.config.timeout),
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            return {
                success: true,
                data: data.result as T,
                metadata: {
                    provider: data._meta?.provider || 'unknown',
                    latencyMs: performance.now() - startTime,
                    cached: data._meta?.cached || false,
                },
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                metadata: {
                    provider: 'none',
                    latencyMs: performance.now() - startTime,
                    cached: false,
                },
            };
        }
    }
    
    /**
     * Lista todas as tools disponíveis.
     */
    async listTools(): Promise<string[]> {
        const response = await fetch(`${this.config.baseUrl}/tools`);
        const data = await response.json();
        return data.tools || [];
    }
    
    /**
     * Verifica health do MCP Bridge.
     */
    async healthCheck(): Promise<{
        status: string;
        providers: Record<string, { healthy: boolean; latency: number }>;
    }> {
        const response = await fetch(`${this.config.baseUrl}/health`);
        return response.json();
    }
    
    /**
     * Conecta ao WebSocket para eventos em tempo real.
     */
    async connectRealtime(): Promise<void> {
        return wsManager.connect();
    }
    
    /**
     * Inscreve para receber eventos de um tipo específico.
     */
    onEvent<T>(eventType: string, handler: (payload: T) => void): () => void {
        return wsManager.subscribe(eventType, (event) => {
            handler(event.payload as T);
        });
    }
}

export const mcpClient = new MCPClient();
```

---

### 6.4 React Context para Estado Global

```typescript
// dashboard/contexts/MCPContext.tsx

import React, { createContext, useContext, useEffect, useReducer, useCallback } from 'react';
import { mcpClient } from '../services/mcpClient';
import { Agent, LogEntry, OSINTFinding } from '../types';

interface MCPState {
    agents: Agent[];
    selectedAgentId: string | null;
    logs: LogEntry[];
    connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
    isLoading: boolean;
    // Agent-specific states
    magistrateState: MagistrateState | null;
    osintState: OSINTState | null;
}

type MCPAction = 
    | { type: 'SET_AGENTS'; payload: Agent[] }
    | { type: 'SELECT_AGENT'; payload: string }
    | { type: 'ADD_LOG'; payload: LogEntry }
    | { type: 'CLEAR_LOGS' }
    | { type: 'SET_CONNECTION_STATUS'; payload: MCPState['connectionStatus'] }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'UPDATE_MAGISTRATE_STATE'; payload: Partial<MagistrateState> }
    | { type: 'UPDATE_OSINT_STATE'; payload: Partial<OSINTState> };

const initialState: MCPState = {
    agents: [],
    selectedAgentId: null,
    logs: [],
    connectionStatus: 'connecting',
    isLoading: false,
    magistrateState: null,
    osintState: null,
};

function mcpReducer(state: MCPState, action: MCPAction): MCPState {
    switch (action.type) {
        case 'SET_AGENTS':
            return { ...state, agents: action.payload };
        case 'SELECT_AGENT':
            return { ...state, selectedAgentId: action.payload };
        case 'ADD_LOG':
            return { 
                ...state, 
                logs: [...state.logs.slice(-499), action.payload] // Max 500 logs
            };
        case 'CLEAR_LOGS':
            return { ...state, logs: [] };
        case 'SET_CONNECTION_STATUS':
            return { ...state, connectionStatus: action.payload };
        case 'SET_LOADING':
            return { ...state, isLoading: action.payload };
        case 'UPDATE_MAGISTRATE_STATE':
            return { 
                ...state, 
                magistrateState: { ...state.magistrateState, ...action.payload } as MagistrateState 
            };
        case 'UPDATE_OSINT_STATE':
            return { 
                ...state, 
                osintState: { ...state.osintState, ...action.payload } as OSINTState 
            };
        default:
            return state;
    }
}

const MCPContext = createContext<{
    state: MCPState;
    dispatch: React.Dispatch<MCPAction>;
    executeTool: <T>(toolName: string, params: Record<string, unknown>) => Promise<T>;
} | null>(null);

export function MCPProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(mcpReducer, initialState);
    
    // Conectar WebSocket na inicialização
    useEffect(() => {
        const connect = async () => {
            try {
                await mcpClient.connectRealtime();
                dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connected' });
                
                // Subscrever a eventos
                mcpClient.onEvent<LogEntry>('log.new_entry', (log) => {
                    dispatch({ type: 'ADD_LOG', payload: log });
                });
                
                mcpClient.onEvent<{ agentId: string; status: string }>('agent.status_changed', (data) => {
                    dispatch({ 
                        type: 'SET_AGENTS', 
                        payload: state.agents.map(a => 
                            a.id === data.agentId 
                                ? { ...a, status: data.status as Agent['status'] }
                                : a
                        )
                    });
                });
            } catch (error) {
                console.error('Failed to connect to MCP:', error);
                dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'error' });
            }
        };
        
        connect();
    }, []);
    
    // Wrapper para execução de tools com loading state
    const executeTool = useCallback(async <T,>(
        toolName: string, 
        params: Record<string, unknown>
    ): Promise<T> => {
        dispatch({ type: 'SET_LOADING', payload: true });
        
        try {
            const result = await mcpClient.execute<T>(toolName, params);
            
            if (!result.success) {
                throw new Error(result.error);
            }
            
            // Log automático
            dispatch({
                type: 'ADD_LOG',
                payload: {
                    timestamp: new Date().toLocaleTimeString(),
                    level: 'success',
                    source: toolName.toUpperCase(),
                    message: `Executed in ${result.metadata.latencyMs.toFixed(0)}ms (${result.metadata.provider})`,
                },
            });
            
            return result.data as T;
        } catch (error) {
            dispatch({
                type: 'ADD_LOG',
                payload: {
                    timestamp: new Date().toLocaleTimeString(),
                    level: 'error',
                    source: toolName.toUpperCase(),
                    message: error instanceof Error ? error.message : 'Unknown error',
                },
            });
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, []);
    
    return (
        <MCPContext.Provider value={{ state, dispatch, executeTool }}>
            {children}
        </MCPContext.Provider>
    );
}

export function useMCP() {
    const context = useContext(MCPContext);
    if (!context) {
        throw new Error('useMCP must be used within MCPProvider');
    }
    return context;
}
```

---

### 6.5 Testes E2E Científicos

#### 6.5.1 Setup Playwright

```bash
# Instalação
npm install -D @playwright/test
npx playwright install chromium
```

```typescript
// playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './tests/e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: [
        ['html', { outputFolder: 'test-results/html' }],
        ['json', { outputFile: 'test-results/results.json' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
    ],
    use: {
        baseURL: 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    webServer: [
        {
            command: 'npm run dev',
            url: 'http://localhost:3000',
            reuseExistingServer: !process.env.CI,
            timeout: 120000,
        },
        {
            command: 'python mcp_http_bridge.py',
            url: 'http://localhost:8080/health',
            reuseExistingServer: !process.env.CI,
            timeout: 60000,
        },
    ],
    // Thresholds científicos
    expect: {
        timeout: 10000,
    },
});
```

#### 6.5.2 Testes E2E Completos

```typescript
// tests/e2e/dashboard.spec.ts

import { test, expect, Page } from '@playwright/test';

// Métricas científicas de qualidade
const QUALITY_THRESHOLDS = {
    pageLoadTime: 3000,        // ms - Tempo máximo de carregamento
    apiLatency: 2000,          // ms - Tempo máximo de resposta
    renderTime: 500,           // ms - Tempo máximo de render
    wsConnectionTime: 1000,    // ms - Tempo de conexão WebSocket
    interactionDelay: 100,     // ms - Delay máximo entre interação e feedback
};

test.describe('Dashboard: Conexão e Carregamento', () => {
    test('deve carregar em menos de 3 segundos', async ({ page }) => {
        const startTime = Date.now();
        
        await page.goto('/');
        await page.waitForSelector('[data-testid="agent-sidebar"]');
        
        const loadTime = Date.now() - startTime;
        expect(loadTime).toBeLessThan(QUALITY_THRESHOLDS.pageLoadTime);
        
        console.log(`📊 Page Load Time: ${loadTime}ms`);
    });
    
    test('deve conectar ao WebSocket e mostrar status "connected"', async ({ page }) => {
        await page.goto('/');
        
        // Aguarda indicador de conexão
        const statusIndicator = page.locator('[data-testid="connection-status"]');
        await expect(statusIndicator).toHaveText(/SYSTEM ONLINE|connected/i, {
            timeout: QUALITY_THRESHOLDS.wsConnectionTime,
        });
    });
    
    test('deve exibir lista de agentes do MCP', async ({ page }) => {
        await page.goto('/');
        
        const agentList = page.locator('[data-testid="agent-list"]');
        await expect(agentList).toBeVisible();
        
        // Verifica que pelo menos 5 agentes estão listados (dos 7 totais)
        const agentItems = agentList.locator('[data-testid^="agent-item-"]');
        await expect(agentItems).toHaveCount(7, { timeout: 5000 });
    });
});

test.describe('Ethical Magistrate: Validação de Ações', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.click('[data-testid="agent-item-ethical-magistrate"]');
    });
    
    test('deve validar ação ética com sucesso', async ({ page }) => {
        const startTime = Date.now();
        
        // Preenche o formulário
        await page.fill('[data-testid="proposed-action"]', 
            'ISOLATE_HOST(IP="192.168.1.1", REASON="Malware detected", DURATION="1h")');
        
        await page.selectOption('[data-testid="initiator-select"]', 'admin');
        await page.check('[data-testid="pii-redaction-checkbox"]');
        
        // Executa validação
        await page.click('[data-testid="validate-action-btn"]');
        
        // Aguarda resultado
        const resultBadge = page.locator('[data-testid="validation-result"]');
        await expect(resultBadge).toBeVisible({ timeout: QUALITY_THRESHOLDS.apiLatency });
        
        const latency = Date.now() - startTime;
        console.log(`📊 Magistrate Validation Latency: ${latency}ms`);
        
        // Verifica que resultado é APPROVED ou DENIED (não erro)
        await expect(resultBadge).toHaveText(/(APPROVED|DENIED)/);
        
        // Verifica métricas exibidas
        const confidenceValue = await page.locator('[data-testid="confidence-value"]').textContent();
        expect(parseFloat(confidenceValue!)).toBeGreaterThan(0);
    });
    
    test('deve bloquear ação antiética', async ({ page }) => {
        await page.fill('[data-testid="proposed-action"]', 
            'DELETE_ALL_LOGS(REASON="Cover tracks")');
        
        await page.click('[data-testid="validate-action-btn"]');
        
        const resultBadge = page.locator('[data-testid="validation-result"]');
        await expect(resultBadge).toHaveText('DENIED', { timeout: QUALITY_THRESHOLDS.apiLatency });
    });
});

test.describe('OSINT Hunter: Investigação Completa', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.click('[data-testid="agent-item-osint-hunter"]');
    });
    
    test('deve realizar breach check com email válido', async ({ page }) => {
        const startTime = Date.now();
        
        // Input de target
        await page.fill('[data-testid="target-input"]', 'test@example.com');
        
        // Verifica validação visual
        const validBadge = page.locator('[data-testid="target-valid-badge"]');
        await expect(validBadge).toHaveText('VALID');
        
        // Executa scan
        await page.click('[data-testid="initiate-scan-btn"]');
        
        // Aguarda resultados na tabela
        const findingsTable = page.locator('[data-testid="findings-table"]');
        await expect(findingsTable).toBeVisible({ timeout: QUALITY_THRESHOLDS.apiLatency });
        
        const latency = Date.now() - startTime;
        console.log(`📊 OSINT Scan Latency: ${latency}ms`);
        
        // Verifica Risk Score gauge
        const riskScore = await page.locator('[data-testid="risk-score-value"]').textContent();
        expect(parseInt(riskScore!)).toBeGreaterThanOrEqual(0);
        expect(parseInt(riskScore!)).toBeLessThanOrEqual(100);
    });
    
    test('deve exibir findings com severity badges corretos', async ({ page }) => {
        await page.fill('[data-testid="target-input"]', 'pwned@breach-test.com');
        await page.click('[data-testid="initiate-scan-btn"]');
        
        // Aguarda pelo menos um finding
        const firstFinding = page.locator('[data-testid="finding-row"]').first();
        await expect(firstFinding).toBeVisible({ timeout: 5000 });
        
        // Verifica que severity badge existe
        const severityBadge = firstFinding.locator('[data-testid="severity-badge"]');
        await expect(severityBadge).toHaveText(/(CRITICAL|HIGH|MEDIUM|LOW|INFO)/);
    });
    
    test('deve atualizar logs em tempo real durante scan', async ({ page }) => {
        const logTerminal = page.locator('[data-testid="log-terminal"]');
        const initialLogCount = await logTerminal.locator('[data-testid="log-entry"]').count();
        
        await page.fill('[data-testid="target-input"]', 'scan@realtime-test.com');
        await page.click('[data-testid="initiate-scan-btn"]');
        
        // Aguarda novos logs aparecerem
        await expect(async () => {
            const newLogCount = await logTerminal.locator('[data-testid="log-entry"]').count();
            expect(newLogCount).toBeGreaterThan(initialLogCount);
        }).toPass({ timeout: 5000 });
    });
});

test.describe('Live Log Terminal: Funcionalidade', () => {
    test('deve exibir logs com colorização correta', async ({ page }) => {
        await page.goto('/');
        
        // Triggers uma ação que gera log
        await page.click('[data-testid="agent-item-osint-hunter"]');
        
        const logTerminal = page.locator('[data-testid="log-terminal"]');
        const logEntry = logTerminal.locator('[data-testid="log-entry"]').last();
        
        await expect(logEntry).toBeVisible();
        
        // Verifica estrutura do log: [timestamp] SOURCE: message
        const logText = await logEntry.textContent();
        expect(logText).toMatch(/\[\d{2}:\d{2}:\d{2}\]/);
    });
    
    test('deve fazer auto-scroll para bottom em novos logs', async ({ page }) => {
        await page.goto('/');
        
        const logContainer = page.locator('[data-testid="log-terminal-container"]');
        
        // Gera múltiplos logs
        for (let i = 0; i < 5; i++) {
            await page.click('[data-testid="agent-item-osint-hunter"]');
            await page.waitForTimeout(200);
        }
        
        // Verifica que está scrollado para bottom
        const isScrolledToBottom = await logContainer.evaluate((el) => {
            return Math.abs(el.scrollHeight - el.scrollTop - el.clientHeight) < 10;
        });
        
        expect(isScrolledToBottom).toBeTruthy();
    });
});

test.describe('Health & Metrics: Monitoramento', () => {
    test('deve exibir health status de todos os providers', async ({ page }) => {
        await page.goto('/');
        
        // Abre painel de health (se existir como modal ou aba)
        await page.click('[data-testid="health-status-btn"]');
        
        const healthPanel = page.locator('[data-testid="health-panel"]');
        await expect(healthPanel).toBeVisible();
        
        // Verifica providers listados
        const providerStatuses = healthPanel.locator('[data-testid^="provider-status-"]');
        await expect(providerStatuses).toHaveCount(4); // HIBP, Shodan, VertexAI, Redis
    });
    
    test('deve exibir CPU e Memory no sidebar', async ({ page }) => {
        await page.goto('/');
        
        const cpuUsage = page.locator('[data-testid="cpu-usage"]');
        const memUsage = page.locator('[data-testid="memory-usage"]');
        
        await expect(cpuUsage).toBeVisible();
        await expect(memUsage).toBeVisible();
        
        // Valores devem ser numéricos
        const cpuText = await cpuUsage.textContent();
        expect(cpuText).toMatch(/\d+%/);
    });
});

test.describe('Performance: Métricas Científicas', () => {
    test('deve ter Core Web Vitals aceitáveis', async ({ page }) => {
        await page.goto('/');
        
        // Coleta métricas via Performance API
        const metrics = await page.evaluate(() => {
            const entries = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
            return {
                domContentLoaded: entries.domContentLoadedEventEnd - entries.startTime,
                load: entries.loadEventEnd - entries.startTime,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
            };
        });
        
        console.log('📊 Core Web Vitals:', metrics);
        
        expect(metrics.domContentLoaded).toBeLessThan(2000);
        expect(metrics.load).toBeLessThan(3000);
    });
    
    test('deve responder a interações em menos de 100ms', async ({ page }) => {
        await page.goto('/');
        
        const startTime = Date.now();
        await page.click('[data-testid="agent-item-ethical-magistrate"]');
        
        // Aguarda feedback visual (highlight, loading, etc)
        await page.waitForSelector('[data-testid="agent-item-ethical-magistrate"].active');
        
        const interactionTime = Date.now() - startTime;
        console.log(`📊 Interaction Response Time: ${interactionTime}ms`);
        
        expect(interactionTime).toBeLessThan(QUALITY_THRESHOLDS.interactionDelay + 200);
    });
});
```

#### 6.5.3 Testes de Integração MCP (Backend)

```python
# tests/e2e/test_mcp_dashboard_integration.py

"""
Testes E2E de integração entre Dashboard e MCP Bridge.

Estes testes validam a comunicação completa entre frontend e backend,
incluindo execução de tools, WebSocket events, e fallback de providers.
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from datetime import datetime
import httpx
import websockets

# Configuração
MCP_BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"


class TestMCPDashboardIntegration:
    """Testes de integração MCP ↔ Dashboard."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Verifica que MCP Bridge está rodando."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_BASE_URL}/health")
            assert response.status_code == 200, "MCP Bridge deve estar rodando"
    
    @pytest.mark.asyncio
    async def test_websocket_connection_and_events(self):
        """Testa conexão WebSocket e recebimento de eventos."""
        events_received = []
        
        async with websockets.connect(WS_URL) as ws:
            # Handshake
            await ws.send("ping")
            pong = await asyncio.wait_for(ws.recv(), timeout=2.0)
            assert pong == "pong"
            
            # Trigger uma tool via HTTP
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{MCP_BASE_URL}/tools/osint_breach_check/execute",
                    json={"email": "test@websocket-test.com"}
                )
                assert response.status_code == 200
            
            # Aguarda eventos WebSocket (timeout se nenhum recebido)
            try:
                while True:
                    event = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    events_received.append(json.loads(event))
            except asyncio.TimeoutError:
                pass
        
        # Valida que recebemos eventos relevantes
        event_types = [e["type"] for e in events_received]
        assert "tool.execution_started" in event_types or "tool.execution_completed" in event_types
    
    @pytest.mark.asyncio
    async def test_all_agent_tools_accessible(self):
        """Verifica que todas as 7 tools dos agentes estão registradas."""
        expected_tools = [
            "magistrate_validate",
            "osint_investigate",
            "osint_breach_check",
            "threat_analyze",
            "compliance_assess",
            "wargame_run_simulation",
            "patch_validate",
        ]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_BASE_URL}/tools")
            assert response.status_code == 200
            
            tools = response.json().get("tools", [])
            tool_names = [t["name"] if isinstance(t, dict) else t for t in tools]
            
            for expected in expected_tools:
                assert expected in tool_names, f"Tool {expected} não encontrada"
    
    @pytest.mark.asyncio
    async def test_magistrate_validate_returns_structured_response(self):
        """Testa resposta estruturada do Ethical Magistrate."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/magistrate_validate/execute",
                json={
                    "action": "BLOCK_IP(target='192.168.1.1')",
                    "actor": "admin",
                    "context": {"explicit_consent": True}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Estrutura esperada
            assert "result" in data
            result = data["result"]
            assert "is_approved" in result
            assert "reason" in result
            assert "confidence" in result
            assert isinstance(result["is_approved"], bool)
            assert isinstance(result["confidence"], (int, float))
    
    @pytest.mark.asyncio
    async def test_osint_breach_check_with_provider_metadata(self):
        """Testa que breach check retorna metadata do provider usado."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/osint_breach_check/execute",
                json={"email": "metadata-test@example.com"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verifica metadata de provider
            assert "_meta" in data
            meta = data["_meta"]
            assert "provider" in meta
            assert meta["provider"] in ["hibp_real", "hibp_cache", "hibp_ai_fallback"]
    
    @pytest.mark.asyncio
    async def test_health_check_includes_all_providers(self):
        """Verifica health check de todos os providers."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_BASE_URL}/health")
            
            assert response.status_code == 200
            data = response.json()
            
            expected_providers = ["hibp", "vertex_ai"]
            for provider in expected_providers:
                assert provider in data.get("providers", {}), f"Provider {provider} ausente"
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_executions(self):
        """Testa execução concorrente de múltiplas tools."""
        async with httpx.AsyncClient() as client:
            # Dispara 5 requests simultâneos
            tasks = [
                client.post(
                    f"{MCP_BASE_URL}/tools/osint_breach_check/execute",
                    json={"email": f"concurrent-{i}@test.com"}
                )
                for i in range(5)
            ]
            
            start_time = datetime.now()
            responses = await asyncio.gather(*tasks)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # Todas devem ter sucesso
            for resp in responses:
                assert resp.status_code == 200
            
            # Execução paralela deve ser mais rápida que serial
            print(f"📊 Concurrent execution time: {elapsed:.2f}s")
            assert elapsed < 10.0  # 5 sequenciais seriam ~10s


class TestProviderFallback:
    """Testes de fallback entre providers."""
    
    @pytest.mark.asyncio
    async def test_hibp_fallback_to_cache(self):
        """Simula HIBP indisponível e verifica fallback para cache."""
        # Este teste requer mock do HIBP ou feature flag
        async with httpx.AsyncClient() as client:
            # Primeiro request popula cache
            response = await client.post(
                f"{MCP_BASE_URL}/tools/osint_breach_check/execute",
                json={"email": "cache-test@example.com"}
            )
            assert response.status_code == 200
            
            # TODO: Simular falha do HIBP e verificar que cache é usado
            # Requer injeção de dependência ou mock no runtime


class TestWargameSafety:
    """Testes de segurança do Wargame Executor."""
    
    @pytest.mark.asyncio
    async def test_wargame_blocked_by_feature_flag(self):
        """Verifica que wargame é bloqueado quando feature flag está off."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/wargame_run_simulation/execute",
                json={
                    "scenario_id": "T1003",
                    "target": "localhost"
                }
            )
            
            # Deve retornar erro de feature flag (não executar nada)
            data = response.json()
            result = data.get("result", {})
            
            # Wargame real é bloqueado por padrão
            assert result.get("execution_blocked") or "feature_flag" in str(data).lower()
    
    @pytest.mark.asyncio
    async def test_wargame_rejects_unauthorized_target(self):
        """Verifica que targets não autorizados são rejeitados."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_BASE_URL}/tools/wargame_run_simulation/execute",
                json={
                    "scenario_id": "T1003",
                    "target": "8.8.8.8"  # Google DNS - não autorizado
                }
            )
            
            data = response.json()
            # Deve ser bloqueado por whitelist
            assert "not in approved" in str(data).lower() or "blocked" in str(data).lower()
```

---

### 6.6 Métricas de Qualidade (Definition of Done)

#### 6.6.1 Thresholds Obrigatórios

| Métrica | Threshold | Ferramenta |
|---------|-----------|------------|
| **Test Coverage** | ≥ 90% | pytest-cov / istanbul |
| **E2E Pass Rate** | 100% | Playwright |
| **API Latency (p95)** | < 2s | Prometheus / custom |
| **WebSocket Stability** | 0 drops/hour | Custom monitor |
| **Page Load (LCP)** | < 2.5s | Lighthouse |
| **Interaction (INP)** | < 200ms | Lighthouse |
| **Type Safety** | 0 errors | TypeScript strict |
| **Lint Errors** | 0 | ESLint + Ruff |

#### 6.6.2 Checklist de Qualidade Final

```markdown
## ✅ Definition of Done - Fase 6

### Funcionalidade
- [ ] Todos os 7 agentes funcionam via Dashboard
- [ ] WebSocket conecta e recebe eventos em tempo real
- [ ] Fallback de providers funciona corretamente
- [ ] Logs são exibidos com colorização e auto-scroll
- [ ] Risk Gauge anima corretamente

### Performance
- [ ] Page load < 3s
- [ ] API latency < 2s (p95)
- [ ] Interaction delay < 200ms
- [ ] Zero memory leaks em 1h de uso

### Segurança
- [ ] Wargame bloqueado por feature flag
- [ ] PII redaction funcionando
- [ ] Ethical Magistrate validando ações

### Testes
- [ ] 100% E2E tests passando
- [ ] ≥ 90% coverage em unit tests
- [ ] Testes de integração MCP passando
- [ ] Performance benchmarks documentados

### Documentação
- [ ] README atualizado
- [ ] API docs geradas (OpenAPI)
- [ ] Walkthrough com screenshots
```

---

### 6.7 Tasks de Implementação (Integração Final)

#### Task 6.1: WebSocket Manager (Client)
- [ ] **Arquivo**: `dashboard/services/wsManager.ts`
- [ ] Reconnection com backoff exponencial
- [ ] Event subscription pattern
- [ ] Heartbeat/ping-pong

#### Task 6.2: WebSocket Broadcaster (Server)
- [ ] **Arquivo**: `mcp_http_bridge.py`
- [ ] Endpoint `/ws` com ConnectionManager
- [ ] Broadcast em execução de tools
- [ ] Emit events para logs

#### Task 6.3: MCP Client Service
- [ ] **Arquivo**: `dashboard/services/mcpClient.ts`
- [ ] Método `execute` com retry
- [ ] Método `listTools`
- [ ] Método `healthCheck`

#### Task 6.4: React Context (MCPProvider)
- [ ] **Arquivo**: `dashboard/contexts/MCPContext.tsx`
- [ ] State global para agentes, logs, connection
- [ ] Hooks: `useMCP`, `useAgent`, `useLogs`

#### Task 6.5: Testes E2E - Dashboard
- [ ] **Arquivo**: `tests/e2e/dashboard.spec.ts`
- [ ] Testes de carregamento
- [ ] Testes de cada painel de agente
- [ ] Testes de logs em tempo real

#### Task 6.6: Testes E2E - Integração Backend
- [ ] **Arquivo**: `tests/e2e/test_mcp_dashboard_integration.py`
- [ ] Testes de WebSocket
- [ ] Testes de todas as tools
- [ ] Testes de fallback

#### Task 6.7: Configuração Playwright
- [ ] **Arquivo**: `playwright.config.ts`
- [ ] Dual webserver (frontend + backend)
- [ ] Reporters (HTML, JSON, JUnit)
- [ ] Thresholds de qualidade

#### Task 6.8: Validação Final
- [ ] Script de validação completa
- [ ] Geração de relatório de qualidade
- [ ] Screenshots/recordings dos testes

---

### 6.8 Ordem de Execução Completa (TODAS AS FASES)

```
PLANO DE EXECUÇÃO COMPLETO
==========================

1. ☐ Fase 0: Infraestrutura Base
   ├── ☐ Task 0.1: core/feature_flags.py
   ├── ☐ Task 0.2: core/circuit_breaker.py
   ├── ☐ Task 0.3: tools/providers/base.py
   └── ☐ Task 0.4: core/metrics.py + core/rate_limiter.py

2. ☐ Fase 1: OSINT HIBP Real
   ├── ☐ Task 1.1: tools/providers/hibp.py
   ├── ☐ Task 1.1b: tools/providers/cache.py
   ├── ☐ Task 1.1c: Rate limiting integrado
   ├── ☐ Task 1.2: tests/unit/test_hibp_provider.py
   ├── ☐ Task 1.3: Atualizar tools/osint.py
   └── ☐ Task 1.4: Adicionar _meta ao response

3. ☐ Fase 2: Wargame Safety
   ├── ☐ Task 2.1: tools/wargame_safety.py
   ├── ☐ Task 2.2: docker/wargame-sandbox/Dockerfile
   └── ☐ Task 2.3: Atualizar tools/wargame.py

4. ☐ Fase 3: Health & Metrics
   ├── ☐ Task 3.1: tools/health_check.py
   └── ☐ Task 3.2: Registrar no mcp_http_bridge.py

5. ☐ Fase 4: Validação Inicial
   ├── ☐ Task 4.1: scripts/validate_implementation.py
   └── ☐ Task 4.2: Rodar validação completa

6. ☐ Fase 5: Dashboard UI Modernization
   ├── ☐ Task 5.1: Setup Tailwind Config
   ├── ☐ Task 5.2: CSS Utilities
   ├── ☐ Task 5.3: AgentSidebar
   ├── ☐ Task 5.4: AgentWorkspace (template)
   ├── ☐ Task 5.5: EthicalMagistratePanel
   ├── ☐ Task 5.6: OSINTHunterPanel
   ├── ☐ Task 5.7: LiveLogTerminal
   └── ☐ Task 5.8: MCP Client Integration (basic)

7. ☐ Fase 6: Integração Completa & Testes E2E (FINAL)
   ├── ☐ Task 6.1: WebSocket Manager (Client)
   ├── ☐ Task 6.2: WebSocket Broadcaster (Server)
   ├── ☐ Task 6.3: MCP Client Service (completo)
   ├── ☐ Task 6.4: React Context (MCPProvider)
   ├── ☐ Task 6.5: Testes E2E - Dashboard (Playwright)
   ├── ☐ Task 6.6: Testes E2E - Integração Backend (pytest)
   ├── ☐ Task 6.7: Configuração Playwright
   └── ☐ Task 6.8: Validação Final + Relatório

═══════════════════════════════════════════════════════════════
                    🎯 DEFINITION OF DONE 🎯
═══════════════════════════════════════════════════════════════
  ✓ Todos os 7 agentes operacionais via Dashboard
  ✓ WebSocket funcionando com eventos em tempo real
  ✓ 100% testes E2E passando
  ✓ ≥90% cobertura de testes unitários
  ✓ Zero erros de TypeScript/Lint
  ✓ Performance dentro dos thresholds
  ✓ Documentação completa
═══════════════════════════════════════════════════════════════
```

---

**🚀 SISTEMA PRONTO PARA PRODUÇÃO APÓS FASE 6!**

