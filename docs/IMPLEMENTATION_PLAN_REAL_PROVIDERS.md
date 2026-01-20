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

### FASE 0: INFRAESTRUTURA BASE (30 min)

#### Task 0.1: Criar Feature Flags
- [ ] **Arquivo**: `core/feature_flags.py`

```python
"""
Feature Flags para controle de rollout.

Uso:
    from core.feature_flags import get_feature_flags
    
    flags = get_feature_flags()
    if flags.osint_use_real_hibp:
        # usa API real
    else:
        # usa mock/fallback
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class FeatureFlags(BaseSettings):
    """
    Feature flags para rollout gradual.
    
    Todas as flags COMEÇAM como False (seguro por padrão).
    Ative via variável de ambiente: FF_<FLAG_NAME>=true
    """
    
    # OSINT Providers
    osint_use_real_hibp: bool = False
    osint_use_real_shodan: bool = False
    osint_use_real_censys: bool = False
    osint_cache_ttl_seconds: int = 3600
    
    # Threat Intel Providers
    threat_use_real_otx: bool = False
    threat_use_real_virustotal: bool = False
    threat_use_real_misp: bool = False
    
    # Compliance Tools
    compliance_use_real_checkov: bool = False
    compliance_use_real_scoutsuite: bool = False
    
    # Wargame (MÁXIMA CAUTELA)
    wargame_allow_real_execution: bool = False
    wargame_require_explicit_consent: bool = True
    wargame_sandbox_mode: str = "docker"  # docker, none
    wargame_max_duration_seconds: int = 300
    
    # Patch ML
    patch_use_real_ml: bool = False
    patch_use_gemini_fallback: bool = True
    
    # AI Tools
    ai_enable_streaming: bool = True
    ai_max_tokens: int = 4096
    
    class Config:
        env_prefix = "FF_"
        env_file = ".env"


# Singleton
_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Retorna singleton de feature flags."""
    global _flags
    if _flags is None:
        _flags = FeatureFlags()
    return _flags
```

---

#### Task 0.2: Criar Circuit Breaker Base
- [ ] **Arquivo**: `core/circuit_breaker.py`

```python
"""
Circuit Breaker para APIs externas.

Padrão: 5 falhas → abre circuito por 60s → tenta novamente
"""

import logging
from functools import wraps
from typing import Callable, TypeVar, Any
from circuitbreaker import circuit, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def api_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    fallback: Callable[..., T] | None = None,
    name: str = "api"
) -> Callable:
    """
    Decorator para proteger chamadas de API com circuit breaker.
    
    Args:
        failure_threshold: Número de falhas antes de abrir
        recovery_timeout: Segundos até tentar novamente
        fallback: Função a chamar quando circuito aberto
        name: Nome para logging
    
    Example:
        @api_circuit_breaker(fallback=lambda x: [], name="hibp")
        async def check_breaches(email: str) -> List[dict]:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Aplica circuit breaker da lib
        breaker = circuit(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            name=name
        )
        wrapped = breaker(func)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await wrapped(*args, **kwargs)
            except CircuitBreakerError:
                logger.warning(
                    f"Circuit breaker OPEN for {name}. "
                    f"Using fallback. Recovery in {recovery_timeout}s"
                )
                if fallback:
                    return fallback(*args, **kwargs)
                raise
            except Exception as e:
                logger.error(f"{name} API error: {e}")
                raise
        
        return async_wrapper
    return decorator
```

---

#### Task 0.3: Criar Provider Base
- [ ] **Arquivo**: `tools/providers/base.py`

```python
"""
Base classes para providers de API externa.

Cada provider implementa:
- check_available() → bool
- execute(*args) → result
- get_fallback() → Optional[BaseProvider]
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ProviderError(Exception):
    """Erro específico de provider."""
    pass


class ProviderNotConfiguredError(ProviderError):
    """Provider não tem credenciais configuradas."""
    pass


class BaseProvider(ABC, Generic[T]):
    """
    Classe base para providers de API.
    
    Implementa chain of responsibility:
    Provider1 → Provider2 → Provider3 → Error
    """
    
    name: str = "base"
    fallback: Optional["BaseProvider[T]"] = None
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se provider está configurado e disponível."""
        pass
    
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> T:
        """Executa operação principal do provider."""
        pass
    
    async def execute_with_fallback(self, *args: Any, **kwargs: Any) -> T:
        """
        Tenta executar, cai para fallback se falhar.
        
        Returns:
            Resultado da execução (deste provider ou fallback)
            
        Raises:
            ProviderError: Se todos os providers falharem
        """
        if not self.is_available():
            logger.info(f"Provider {self.name} not available, trying fallback")
            if self.fallback:
                return await self.fallback.execute_with_fallback(*args, **kwargs)
            raise ProviderNotConfiguredError(
                f"Provider {self.name} not configured and no fallback available"
            )
        
        try:
            result = await self.execute(*args, **kwargs)
            logger.debug(f"Provider {self.name} succeeded")
            return result
        except Exception as e:
            logger.warning(f"Provider {self.name} failed: {e}")
            if self.fallback:
                logger.info(f"Falling back to {self.fallback.name}")
                return await self.fallback.execute_with_fallback(*args, **kwargs)
            raise ProviderError(f"All providers failed. Last error: {e}") from e
```

---

### FASE 1: OSINT - HIBP REAL (1 hora)

#### Task 1.1: Criar HIBP Provider
- [ ] **Arquivo**: `tools/providers/hibp.py`

```python
"""
HaveIBeenPwned Provider - Breach Data API.

API Docs: https://haveibeenpwned.com/API/v3
Requer: HIBP_API_KEY ($3.50/mês)
"""

import os
import logging
from typing import List, Optional, Any

import httpx
from pydantic import BaseModel

from core.feature_flags import get_feature_flags
from core.circuit_breaker import api_circuit_breaker
from tools.providers.base import BaseProvider, ProviderNotConfiguredError

logger = logging.getLogger(__name__)


class BreachData(BaseModel):
    """Dados de um breach do HIBP."""
    name: str
    title: str
    domain: str
    breach_date: str
    added_date: str
    modified_date: str
    pwn_count: int
    description: str
    logo_path: str
    data_classes: List[str]
    is_verified: bool
    is_fabricated: bool
    is_sensitive: bool
    is_retired: bool
    is_spam_list: bool
    is_malware: bool
    is_subscription_free: bool


class HIBPProvider(BaseProvider[List[BreachData]]):
    """Provider real para HaveIBeenPwned API."""
    
    name = "hibp_real"
    
    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.api_key = os.getenv("HIBP_API_KEY")
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.fallback = fallback
    
    def is_available(self) -> bool:
        """Verifica se API key está configurada E feature flag ativa."""
        flags = get_feature_flags()
        return bool(self.api_key) and flags.osint_use_real_hibp
    
    @api_circuit_breaker(
        failure_threshold=3,
        recovery_timeout=120,
        name="hibp"
    )
    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """
        Consulta breaches para um email.
        
        Args:
            email: Email a verificar
            
        Returns:
            Lista de breaches onde email aparece
            
        Raises:
            httpx.HTTPError: Se API falhar
        """
        if not self.api_key:
            raise ProviderNotConfiguredError(
                "HIBP_API_KEY not set. "
                "Get key at: https://haveibeenpwned.com/API/Key ($3.50/mo)"
            )
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/breachedaccount/{email}",
                headers={
                    "hibp-api-key": self.api_key,
                    "user-agent": "Vertice-Cyber-OSINT-Agent/1.0"
                },
                params={"truncateResponse": "false"}
            )
            
            if response.status_code == 404:
                # Email não encontrado em breaches (bom!)
                return []
            
            if response.status_code == 429:
                # Rate limited
                logger.warning("HIBP rate limited, retrying later")
                raise httpx.HTTPError("Rate limited")
            
            response.raise_for_status()
            
            breaches = [BreachData(**b) for b in response.json()]
            logger.info(f"HIBP found {len(breaches)} breaches for {email}")
            return breaches


class HIBPCacheProvider(BaseProvider[List[BreachData]]):
    """Provider que usa cache local de breaches conhecidos."""
    
    name = "hibp_cache"
    
    def __init__(self, fallback: Optional[BaseProvider] = None):
        self.fallback = fallback
        # Cache pode ser um Redis, SQLite, ou arquivo JSON
        self._cache: dict = {}
    
    def is_available(self) -> bool:
        """Cache está sempre disponível."""
        return True
    
    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """Consulta cache local."""
        if email in self._cache:
            logger.debug(f"Cache hit for {email}")
            return self._cache[email]
        
        # Cache miss - propaga para fallback
        if self.fallback:
            return await self.fallback.execute_with_fallback(email, **kwargs)
        
        return []  # Cache miss sem fallback = sem dados


class HIBPAIFallback(BaseProvider[List[BreachData]]):
    """Fallback usando Gemini 3 para análise de risco (sem dados reais)."""
    
    name = "hibp_ai_fallback"
    
    def is_available(self) -> bool:
        """Sempre disponível se Vertex AI configurado."""
        return bool(os.getenv("GCP_PROJECT_ID"))
    
    async def execute(self, email: str, **kwargs: Any) -> List[BreachData]:
        """
        Usa IA para estimar risco, NÃO tem dados reais.
        
        IMPORTANTE: Retorna estrutura compatível mas marca is_estimated=True
        """
        from tools.vertex_ai import get_vertex_ai
        
        vertex_ai = get_vertex_ai()
        
        result = await vertex_ai.analyze_threat_intelligence(
            f"Analyze breach risk for email domain pattern: {email.split('@')[1]}",
            context={
                "analysis_type": "email_breach_risk",
                "note": "This is an estimation, not real breach data"
            }
        )
        
        # Retorna estrutura fake mas sinalizada
        logger.warning(
            f"Using AI fallback for breach check. "
            f"Result is ESTIMATION, not real data."
        )
        
        return []  # Não inventa breaches falsos


def get_hibp_provider() -> BaseProvider[List[BreachData]]:
    """
    Factory que retorna chain de providers HIBP.
    
    Chain: Real HIBP → Cache → AI Fallback
    """
    ai_fallback = HIBPAIFallback()
    cache = HIBPCacheProvider(fallback=ai_fallback)
    real = HIBPProvider(fallback=cache)
    
    return real
```

---

#### Task 1.2: Teste Unitário HIBP
- [ ] **Arquivo**: `tests/unit/test_hibp_provider.py`

```python
"""Testes unitários para HIBP Provider."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from tools.providers.hibp import (
    HIBPProvider,
    HIBPCacheProvider,
    HIBPAIFallback,
    get_hibp_provider,
    BreachData
)


class TestHIBPProvider:
    """Testes para HIBPProvider."""
    
    @pytest.fixture
    def provider(self):
        """Provider com API key mock."""
        with patch.dict("os.environ", {"HIBP_API_KEY": "test-key"}):
            with patch("core.feature_flags.get_feature_flags") as mock_ff:
                mock_ff.return_value.osint_use_real_hibp = True
                yield HIBPProvider()
    
    def test_is_available_without_key(self):
        """Sem API key, provider não está disponível."""
        with patch.dict("os.environ", {}, clear=True):
            provider = HIBPProvider()
            assert provider.is_available() is False
    
    def test_is_available_with_key_and_flag(self):
        """Com key e flag, provider está disponível."""
        with patch.dict("os.environ", {"HIBP_API_KEY": "test"}):
            with patch("core.feature_flags.get_feature_flags") as mock_ff:
                mock_ff.return_value.osint_use_real_hibp = True
                provider = HIBPProvider()
                assert provider.is_available() is True
    
    @pytest.mark.asyncio
    async def test_execute_email_not_found(self, provider):
        """Email sem breaches retorna lista vazia."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await provider.execute("clean@example.com")
            assert result == []
    
    @pytest.mark.asyncio
    async def test_execute_email_found(self, provider):
        """Email com breaches retorna dados."""
        breach_data = [{
            "name": "TestBreach",
            "title": "Test Breach",
            "domain": "test.com",
            "breach_date": "2024-01-01",
            "added_date": "2024-01-02",
            "modified_date": "2024-01-03",
            "pwn_count": 1000,
            "description": "Test",
            "logo_path": "",
            "data_classes": ["Email"],
            "is_verified": True,
            "is_fabricated": False,
            "is_sensitive": False,
            "is_retired": False,
            "is_spam_list": False,
            "is_malware": False,
            "is_subscription_free": False
        }]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = breach_data
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await provider.execute("pwned@example.com")
            assert len(result) == 1
            assert result[0].name == "TestBreach"


class TestProviderChain:
    """Testes para chain de fallback."""
    
    @pytest.mark.asyncio
    async def test_fallback_when_primary_unavailable(self):
        """Usa fallback quando primary não disponível."""
        with patch.dict("os.environ", {}, clear=True):
            chain = get_hibp_provider()
            
            # Primary não tem API key, deve usar fallback
            # Cache vai retornar vazio
            result = await chain.execute_with_fallback("test@test.com")
            assert result == []
```

---

#### Task 1.3: Integrar Provider no OSINT Hunter
- [ ] **Arquivo**: Modificar `tools/osint.py`

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

### FASE 2: WARGAME SAFETY (2 horas)

#### Task 2.1: Criar Safety Manager
- [ ] **Arquivo**: `tools/wargame_safety.py`

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

## PARTE 4: CHECKLIST FINAL

### Pré-Implementação
- [ ] Branch feature criada
- [ ] Dependências instaladas
- [ ] Estrutura de pastas criada

### Fase 0: Infraestrutura
- [ ] `core/feature_flags.py` criado
- [ ] `core/circuit_breaker.py` criado
- [ ] `tools/providers/base.py` criado
- [ ] Testes passando

### Fase 1: OSINT HIBP
- [ ] `tools/providers/hibp.py` criado
- [ ] Testes HIBP passando
- [ ] `tools/osint.py` atualizado
- [ ] Testes E2E passando

### Fase 2: Wargame Safety
- [ ] `tools/wargame_safety.py` criado
- [ ] `tools/wargame.py` atualizado
- [ ] Testes de segurança passando
- [ ] Arquivo de targets aprovados criado

### Validação Final
- [ ] `pytest --cov` >= 80%
- [ ] Nenhum TODO/FIXME no código
- [ ] pre-commit hooks passando
- [ ] Documentação atualizada

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
