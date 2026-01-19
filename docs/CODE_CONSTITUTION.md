# 📐 MAXIMUS 2.0 - CÓDIGO CONSTITUTION
## Google-Inspired Code Standards & Patterns

> **"Code is read much more often than it is written."** - Guido van Rossum

> **"Quality is not an act, it is a habit."** - Aristotle

---

## Princípios Fundamentais (The Sacred Six)

> **Inspiração**: Constituição Vértice v3.0 + Google Engineering Practices

### 1. 🎯 **Clarity Over Cleverness**
- Code should be **obvious**, not clever
- Prefer explicitness over implicit magic
- Write code for the next developer, not the compiler

### 2. 📏 **Consistency is King**
- Follow established patterns religiously
- One way to do things > multiple ways
- Codebase should feel like written by one person

### 3. ⚡ **Simplicity at Scale**
- Simple designs that scale > Complex designs that barely work
- YAGNI: You Aren't Gonna Need It
- Delete code aggressively

### 4. 🔒 **Safety First**
- Type safety prevents runtime errors
- Input validation is NOT optional
- Fail fast, fail loud

### 5. 📊 **Measurable Quality**
- If you can't measure it, you can't improve it
- Code metrics are NOT vanity metrics
- Quality gates are NOT suggestions

### 6. 🏛️ **Sovereignty of Intent** (Constituição Vértice v3.0 - Artigo I, Cláusula 3.6)

> **"The only doctrine that shapes our architecture and code logic is the one present here."**

**ABSOLUTE PROHIBITIONS**:

#### ❌ **FORBIDDEN: Circumventing User Intent**
- **No "clever" workarounds** to specifications
- **No silent modifications** to requirements
- **No inserting external agendas** (political, philosophical, "safety theater")
- **No "I know better than the user" attitude**

**Example of VIOLATION**:
```python
# ❌ FORBIDDEN: AI silently "sanitizing" user request
def execute_command(user_command: str):
    # Silently refusing deletion commands
    if "delete" in user_command or "rm" in user_command:
        logger.warning("Dangerous command blocked for safety")
        return {"status": "success", "message": "Completed safely"}  # LIE
```

**Correct approach**:
```python
# ✅ REQUIRED: Declare limitation explicitly
def execute_command(user_command: str):
    if requires_human_approval(user_command):
        raise UserConfirmationRequired(
            f"Command '{user_command}' requires explicit approval.",
            reason="Potentially destructive operation"
        )
    return execute(user_command)
```

#### 📜 **Obrigação da Verdade (Obligation of Truth)**

When a directive **cannot** be fulfilled due to:
- Technical limitations
- Security constraints
- Logical impossibilities

**YOU MUST**:
1. **Declare the impossibility explicitly**
2. **Provide root-cause analysis**
3. **Suggest alternatives (if any)**
4. **Never produce a fake/broken solution**

**Example**:
```python
# ❌ BAD: Silent failure with placeholder
async def upload_to_s3(file: File) -> str:
    # TODO: Implement S3 upload
    return "https://fake-url.com/file.pdf"  # VIOLATION!

# ✅ GOOD: Explicit declaration
async def upload_to_s3(file: File) -> str:
    raise NotImplementedError(
        "S3 upload not yet implemented. "
        "Root cause: AWS credentials not configured. "
        "Alternative: Store locally with LocalFileStorage."
    )
```

#### 🚫 **Zero Tolerance for "Dark Patterns"**

The following are **CAPITAL OFFENSES** in code:

1. **Fake Success Messages**: Returning success when operation failed
2. **Silent Data Modification**: Changing user data without explicit consent
3. **Hidden Rate Limiting**: Throttling user without notification
4. **Stealth Telemetry**: Collecting data beyond documented scope
5. **Bait-and-Switch**: Promising feature X, delivering feature Y

**Penalty**: Immediate code revert + root-cause analysis required

---

## Hard Rules (NON-NEGOTIABLE)

> **"Quality is not an act, it is a habit."** - Aristotle

### O Padrão Pagani (Constituição Vértice - Artigo II)

> **"Every merge must be complete, functional, and production-ready."**

#### **ZERO TOLERANCE for Incomplete Code**

```
❌ CAPITAL OFFENSE: Placeholders in production code
    - // TODO:
    - // FIXME:
    - // HACK:
    - Mock implementations
    - Stub functions
    - Fake data generators
```

**Rationale** (DETER-AGENT Framework):
- **Placeholders = Cognitive Poison**: They pollute context and cause downstream hallucinations
- **Lazy Execution Spiral**: One TODO leads to 10 TODOs (proven in Constituição v3.0 research)
- **Production Readiness**: If it's not ready, it doesn't merge

**Exception (ONLY)**: Explicit `NotImplementedError` with:
```python
raise NotImplementedError(
    "Feature X requires dependency Y which is not yet integrated. "
    "ETA: 2025-12-15. "
    "Tracking ticket: MAXIMUS-123"
)
```

#### **The 99% Rule**

```
✅ REQUIRED: ≥99% of all tests must pass
❌ FORBIDDEN: Skipping tests without written justification
```

**Enforcement**:
```bash
# CI/CD pipeline
pytest --cov --cov-fail-under=99 || exit 1
```

**Test skip approval template**:
```python
@pytest.mark.skip(
    reason="Flaky due to external API timeout. "
           "Approved by: @architect. "
           "Tracking: MAXIMUS-456. "
           "ETA fix: 2025-12-01"
)
def test_external_api_integration():
    pass
```

---

### File Size Limits

```
❌ FORBIDDEN: Files > 500 lines
✅ IDEAL: Files < 400 lines
🏆 EXCELLENT: Files < 300 lines
```

**Rationale**: 
- Google limits files to ~500 lines
- Human cognitive load: can't hold > 400 lines in working memory
- Large files = God objects (anti-pattern)

**How to Enforce**:
```bash
# Pre-commit hook
find . -name "*.py" -exec wc -l {} \; | awk '$1 > 500 {print "ERROR: " $2 " has " $1 " lines (max 500)"}'
```

### Type Hints Coverage

```python
# ❌ FORBIDDEN
def process_data(data, config):
    return something

# ✅ REQUIRED
def process_data(data: Dict[str, Any], config: Config) -> ProcessedData:
    return something
```

**Rationale**:
- Catches 60% of bugs before runtime (Microsoft Research)
- Self-documenting code
- IDE autocomplete = 3x faster development

**How to Enforce**:
```bash
# mypy in strict mode
mypy --strict --disallow-untyped-defs .
```

### Naming Conventions

```python
# Classes: PascalCase
class AgentPlugin:
    pass

# Functions/Methods: snake_case
def execute_mission():
    pass

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRIES = 3

# Private: _leading_underscore
def _internal_helper():
    pass

# Module-level "private": single underscore
_module_config = {}
```

**Rationale**: PEP 8 compliance + Google Python Style Guide

---

## Code Structure Standards

### 1. Module Organization

Every module MUST follow this order:

```python
"""
Module docstring (REQUIRED)
=========================

Brief description on first line.

Detailed explanation.
Can span multiple lines.
"""

# 1. Future imports
from __future__ import annotations

# 2. Standard library
import asyncio
import logging
from typing import Dict, List, Optional

# 3. Third-party
import httpx
from pydantic import BaseModel

# 4. Local application
from ..core import Something
from .models import SomeModel

# 5. Constants (module level)
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# 6. Type aliases (if needed)
JSON = Dict[str, Any]

# 7. Classes and functions
class MyClass:
    pass

def my_function():
    pass
```

### 2. Class Structure

```python
class WellStructuredClass:
    """
    Class docstring (REQUIRED).
    
    Attributes:
        public_attr: Description
        _private_attr: Description
    """
    
    # 1. Class variables
    CLASS_CONSTANT = "value"
    
    # 2. __init__
    def __init__(self, param: str):
        """Initialize (REQUIRED docstring)."""
        self.public_attr = param
        self._private_attr = None
    
    # 3. Public methods (alphabetical)
    def execute(self) -> Result:
        """Execute (REQUIRED docstring)."""
        pass
    
    def validate(self) -> bool:
        """Validate (REQUIRED docstring)."""
        pass
    
    # 4. Private methods (alphabetical)
    def _helper(self) -> None:
        """Helper (optional docstring)."""
        pass
    
    # 5. Properties (if any)
    @property
    def status(self) -> str:
        """Status property."""
        return self._status
    
    # 6. Dunder methods (except __init__)
    def __repr__(self) -> str:
        return f"WellStructuredClass({self.public_attr})"
```

### 3. Function Structure

```python
async def well_structured_function(
    required_param: str,
    optional_param: Optional[int] = None,
    *,  # Forces keyword-only args after this
    keyword_only: bool = False
) -> Dict[str, Any]:
    """
    Brief description on first line.
    
    Detailed explanation if needed.
    Can span multiple lines.
    
    Args:
        required_param: Description of required param
        optional_param: Description of optional param
        keyword_only: Description of keyword-only param
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
        HTTPException: When external API fails
        
    Example:
        >>> result = await well_structured_function("test")
        >>> print(result["status"])
        "success"
    """
    # 1. Input validation
    if not required_param:
        raise ValueError("required_param cannot be empty")
    
    # 2. Setup/initialization
    logger = logging.getLogger(__name__)
    config = load_config()
    
    # 3. Main logic
    try:
        result = await perform_operation()
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
    
    # 4. Return
    return {"status": "success", "data": result}
```

---

## Async/Await Standards

### Rules for Async

```python
# ✅ GOOD: Clear async/await
async def fetch_data() -> Data:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return parse_response(response)

# ❌ BAD: Blocking in async function
async def bad_fetch() -> Data:
    time.sleep(1)  # NEVER block in async!
    return data

# ❌ BAD: Unnecessary async
async def just_computation() -> int:
    return 2 + 2  # No I/O, should be sync

# ✅ GOOD: Sync function for pure computation
def compute_sum(a: int, b: int) -> int:
    return a + b
```

### Concurrency Patterns

```python
# Pattern 1: Parallel execution (independent tasks)
async def process_batch(items: List[Item]) -> List[Result]:
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

# Pattern 2: Sequential with dependencies
async def sequential_pipeline(data: Data) -> Final:
    step1 = await process_step1(data)
    step2 = await process_step2(step1)
    step3 = await process_step3(step2)
    return step3

# Pattern 3: Timeout protection
async def safe_operation() -> Result:
    try:
        return await asyncio.wait_for(
            long_running_task(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        raise
```

---

## Error Handling Standards

### The Error Hierarchy

```python
# 1. Custom exceptions (specific > generic)
class MaximusError(Exception):
    """Base exception for Maximus"""
    pass

class AgentError(MaximusError):
    """Agent-related errors"""
    pass

class AgentNotFoundError(AgentError):
    """Specific agent not found"""
    pass

# 2. Usage
async def execute_task(agent_name: str) -> Result:
    agent = await registry.get_agent(agent_name)
    
    if not agent:
        raise AgentNotFoundError(
            f"Agent '{agent_name}' not registered. "
            f"Available: {list(registry.agents.keys())}"
        )
    
    try:
        return await agent.execute(task)
    except AgentError:
        # Let agent errors propagate
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise AgentError(
            f"Unexpected error in {agent_name}: {e}"
        ) from e
```

### Error Handling Patterns

```python
# Pattern 1: Fail fast (preferred)
def validate_input(data: Dict[str, Any]) -> None:
    if "required_field" not in data:
        raise ValueError("Missing required_field")
    
    if data["value"] < 0:
        raise ValueError("Value must be positive")
    
    # If we get here, data is valid

# Pattern 2: Try-except-finally (resource cleanup)
async def process_with_resources() -> Result:
    resource = None
    try:
        resource = await acquire_resource()
        return await process(resource)
    except ProcessingError as e:
        logger.error(f"Processing failed: {e}")
        raise
    finally:
        if resource:
            await resource.cleanup()

# Pattern 3: Context managers (preferred for resources)
async def process_with_context() -> Result:
    async with acquire_resource() as resource:
        return await process(resource)
    # Cleanup automatic!
```

---

## Dependency Injection Pattern

### ❌ BAD: Hard-coded dependencies

```python
class BadService:
    def __init__(self):
        self.db = PostgreSQL(host="localhost")  # Hard-coded!
        self.cache = Redis(host="localhost")    # Hard-coded!
```

### ✅ GOOD: Dependency injection

```python
class GoodService:
    def __init__(
        self,
        db: DatabaseClient,
        cache: CacheClient,
        logger: Optional[logging.Logger] = None
    ):
        self.db = db
        self.cache = cache
        self.logger = logger or logging.getLogger(__name__)
    
# Usage
service = GoodService(
    db=PostgreSQLClient(config.db_url),
    cache=RedisClient(config.redis_url)
)
```

**Benefits**:
- Testability (mock dependencies)
- Flexibility (swap implementations)
- Configuration from environment

---

## Testing Standards

### Coverage Requirements

```
✅ REQUIRED: Unit test coverage ≥ 80%
🏆 EXCELLENT: Unit test coverage ≥ 90%
```

### Test Structure

```python
# test_agent_registry.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from meta_orchestrator.core import AgentRegistry
from meta_orchestrator.plugins import AgentPlugin, Task


class TestAgentRegistry:
    """Test suite for AgentRegistry."""
    
    @pytest.fixture
    async def registry(self):
        """Create fresh registry for each test."""
        return AgentRegistry()
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent."""
        agent = AsyncMock(spec=AgentPlugin)
        agent.name = "test_agent"
        agent.version = "1.0.0"
        agent.capabilities = ["test"]
        agent.can_handle = AsyncMock(return_value=True)
        agent.health_check = AsyncMock(return_value={"healthy": True})
        return agent
    
    async def test_register_agent_success(self, registry, mock_agent):
        """Test successful agent registration."""
        # Given: empty registry
        # When: registering agent
        await registry.register(mock_agent)
        
        # Then: agent in registry
        agent = await registry.get_agent("test_agent")
        assert agent == mock_agent
    
    async def test_register_duplicate_agent_fails(self, registry, mock_agent):
        """Test duplicate registration fails."""
        # Given: agent already registered
        await registry.register(mock_agent)
        
        # When: registering same agent again
        # Then: raises ValueError
        with pytest.raises(ValueError, match="already registered"):
            await registry.register(mock_agent)
    
    async def test_select_agent_returns_best_match(self, registry):
        """Test agent selection chooses best candidate."""
        # Given: multiple agents with different priorities
        # When: selecting for task
        # Then: returns highest priority agent
        # ... implementation
```

### Test Naming Convention

```
test_<method>_<scenario>_<expected>

Examples:
- test_register_agent_success
- test_execute_mission_with_invalid_input_raises_error
- test_health_check_when_agent_down_returns_unhealthy
```

---

## Documentation Standards

### Docstring Format (Google Style)

```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    param3: bool = False
) -> Dict[str, Any]:
    """
    Brief one-line description.
    
    Longer description with multiple paragraphs if needed.
    Explain the high-level behavior, not implementation details.
    
    Args:
        param1: Description of param1. Can span
            multiple lines if needed.
        param2: Description of param2. Use None to
            indicate default behavior.
        param3: Description of param3.
    
    Returns:
        Dictionary containing:
            - key1 (str): Description
            - key2 (int): Description
    
    Raises:
        ValueError: If param1 is empty
        HTTPException: If external API fails
    
    Example:
        >>> result = complex_function("test", param2=42)
        >>> print(result["key1"])
        "processed"
    
    Note:
        This function makes external API calls.
        Use with caution in hot paths.
    """
    pass
```

### README Structure

Every service MUST have README with:

```markdown
# Service Name

Brief description (1-2 sentences)

## Quick Start

    ```bash
    # Commands to get started
    ```

## Architecture

High-level diagram or description

## API

Key endpoints/functions

## Configuration

Environment variables

## Development

How to run tests, lint, etc.

## Troubleshooting

Common issues
```

---

## Performance Standards

### Rule 1: Measure, Don't Guess

```python
# ✅ GOOD: Measure before optimizing
import time

start = time.perf_counter()
result = expensive_operation()
elapsed_ms = (time.perf_counter() - start) * 1000

logger.info(f"Operation took {elapsed_ms:.2f}ms")

if elapsed_ms > 1000:
    logger.warning("Slow operation detected")
```

### Rule 2: Optimize the Hot Path

```python
# Identify hot path with profiling
# cProfile, py-spy, or profiling library

# Only optimize code that runs > 1000x/second
# Everything else: clarity > performance
```

### Rule 3: Database Queries

```python
# ❌ BAD: N+1 queries
for user in users:
    posts = db.query(f"SELECT * FROM posts WHERE user_id={user.id}")

# ✅ GOOD: Single query with JOIN
posts = db.query("""
    SELECT posts.*, users.name FROM posts
    JOIN users ON posts.user_id = users.id
    WHERE users.id IN (...)
""")
```

---

## Security Standards

### Input Validation

```python
# ✅ ALWAYS validate external input
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
    
    @validator('age')
    def age_must_be_reasonable(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v
```

### Secrets Management

```python
# ❌ NEVER
API_KEY = "sk-1234567890abcdef"  # FORBIDDEN!

# ✅ ALWAYS
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

### SQL Injection Prevention

```python
# ❌ FORBIDDEN
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ REQUIRED (parameterized queries)
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```

---

## Git Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance

**Example**:
```
feat(orchestrator): add ROMA task decomposition

Implement recursive task decomposition following ROMA pattern.
Supports both LLM-based and rule-based splitting.

Closes #42
```

### Commit Size

```
🏆 IDEAL: 1 logical change per commit
❌ BAD: 50 unrelated changes in one commit
```

---

## Code Review Checklist

Before submitting PR, verify:

- [ ] All files < 500 lines
- [ ] 100% type hints on new code
- [ ] Docstrings on all public functions/classes
- [ ] Tests added/updated (coverage ≥ 80%)
- [ ] No hard-coded secrets
- [ ] No blocking calls in async functions
- [ ] Error handling for all external calls
- [ ] Logging added for important events
- [ ] README updated if public API changed
- [ ] mypy --strict passes
- [ ] pytest passes
- [ ] Code follows naming conventions

---

## Quality Metrics Dashboard

Track these metrics monthly:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥ 80% | pytest --cov |
| Type Coverage | 100% | mypy --strict |
| Cyclomatic Complexity | < 10 | radon cc |
| Code Duplication | < 5% | pylint |
| File Size | < 500 lines | wc -l |
| Docstring Coverage | 100% | interrogate |

---

## Enforcement Tools

### Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run linters
black --check .
mypy --strict .
pylint --fail-under=9.0 .

# Check file sizes
find . -name "*.py" -exec wc -l {} \; | \
    awk '$1 > 500 {print "FAIL: " $2; exit 1}'

# Run tests
pytest --cov --cov-fail-under=80
```

### CI/CD Pipeline

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install deps
        run: pip install -r requirements-dev.txt
      - name: Type check
        run: mypy --strict .
      - name: Lint
        run: pylint --fail-under=9.0 .
      - name: Test
        run: pytest --cov --cov-fail-under=80
      - name: File size check
        run: |
          find . -name "*.py" -exec wc -l {} \; | \
          awk '$1 > 500 {print "ERROR: " $2 " exceeds 500 lines"; exit 1}'
```

---

## Agentes Guardiões (Guardian Agents)

> **Constituição Vértice v3.0 - Anexo D: "Execução Constitucional"**

To ensure this Constitution is a **living law** (not just a document), Maximus 2.0 implements **Guardian Agents** with **computational authority** to enforce compliance.

### Powers of Guardian Agents

#### 1. 🚫 **Veto de Conformidade Técnica**
- **Block merges** that violate Padrão Pagani (placeholders, <99% tests)
- **Block deployments** without proper governance (Artigo V)
- **Halt CI/CD pipelines** that fail quality gates

```yaml
# .github/workflows/guardian.yml
name: Guardian Agent - Technical Compliance

on: [pull_request]

jobs:
  constitutional_audit:
    runs-on: ubuntu-latest
    steps:
      - name: Check for TODOs in production code
        run: |
          if grep -r "// TODO\\|// FIXME\\|// HACK" src/; then
            echo "❌ VETO: Placeholders detected (Padrão Pagani violation)"
            exit 1
          fi
      
      - name: Enforce test coverage
        run: |
          pytest --cov --cov-fail-under=99 || {
            echo "❌ VETO: Test coverage <99% (99% Rule violation)"
            exit 1
          }
      
      - name: Enforce file size limits
        run: |
          find . -name "*.py" -exec wc -l {} \; | \
          awk '$1 > 500 {print "❌ VETO: " $2 " exceeds 500 lines"; exit 1}'
```

#### 2. 🏛️ **Veto de Conformidade Filosófica**
- **Detect "ideological signatures"** in code (external agendas)
- **Flag violations** of Sovereignty of Intent (Cláusula 3.6)
- **Alert on dark patterns** (fake success messages, hidden data collection)

**Detection Pattern Example**:
```python
# Guardian scans for patterns like:
DARK_PATTERNS = [
    r'return\s+.*success.*#.*actually\s+failed',  # Fake success
    r'logger\..*(?!info|debug|warning|error)',     # Stealth logging
    r'if.*user_request.*:.*# ignore',              # Silent rejection
]
```

#### 3. ⚖️ **Alerta de Antifragilidade**
- Monitor system resilience metrics
- Alert when antifragility degrades (no chaos testing, no redundancy)

### Constitutional Metrics

Guardian Agents track:

| Metric | Formula | Target |
|--------|---------|--------|
| **CRS** (Constitutional Respect Score) | (Compliant Commits) / (Total Commits) | ≥95% |
| **LEI** (Lazy Execution Index) | (TODOs + Mocks) / (Total LOC) | <0.001 |
| **FPC** (Fail-then-Patch Count) | Bugs found in prod / Total deploys | <0.05 |

**Dashboard**:
```
┌─────────────────────────────────────────┐
│ MAXIMUS 2.0 - Constitutional Dashboard │
├─────────────────────────────────────────┤
│ CRS:  98.2% ✅ (Target: ≥95%)          │
│ LEI:  0.0003 ✅ (Target: <0.001)       │
│ FPC:  0.02 ✅ (Target: <0.05)          │
│                                         │
│ Vetoes this week: 2                    │
│  - 1x Placeholder detected             │
│  - 1x Test coverage < 99%              │
└─────────────────────────────────────────┘
```

---

## When to Break the Rules

**Golden Rule**: Break rules only when following them would make code WORSE.

**CRITICAL**: You **MUST** declare the rule-breaking **BEFORE** committing, not after.

**Examples of acceptable rule-breaking**:
- Generated code (protobuf, ORM models)
- Data files (large JSON configs)
- Third-party library wrappers
- **Emergency hotfixes** (with post-mortem requirement)

**How to break rules**:
```python
# CONSTITUTIONAL EXEMPTION (Artigo X, Section Y):
# Reason: Protobuf-generated code exceeds line limit
# Approval: architect@maximus.dev
# Date: 2025-11-30
# pylint: disable=line-too-long
VERY_LONG_URL = "https://example.com/..."  # noqa: E501

# mypy: ignore-errors
import untyped_library  # type: ignore
```

**ALWAYS document**:
1. **WHY** you broke the rule
2. **WHICH** article/clause you're exempting
3. **WHO** approved (if required)
4. **WHEN** exemption expires (if applicable)

**Penalty for undocumented rule-breaking**: Guardian Agent veto + mandatory review

---

## Inspiration & Further Reading

1. **Google Python Style Guide**: https://google.github.io/styleguide/pyguide.html
2. **PEP 8**: https://peps.python.org/pep-0008/
3. **Clean Code (Robert C. Martin)**: Principles that transcend languages
4. **The Zen of Python**: `import this`
5. **Google SRE Book**: Production-readiness standards

---

## Version History

- **v1.0** (2025-11-30): Initial constitution based on Maximus 2.0 refactoring

---

**Remember**: These standards exist to make our lives EASIER, not harder.  
Code that follows these patterns is:
- Easier to understand
- Easier to modify
- Easier to test
- Easier to debug
- Easier to deploy

**Quality is a journey, not a destination.** 🚀

---

## Appendix: Integration with Constituição Vértice v3.0

This CODE_CONSTITUTION inherits the philosophical foundation from **Constituição Vértice v3.0**, the supreme operational mandate for the Vértice-MAXIMUS ecosystem.

### Key Integrated Principles

| Vértice Principle | Implementation in Code |
|-------------------|------------------------|
| **Soberania da Intenção** (Artigo I.3.6) | No external agendas in code. User intent is sovereign. |
| **Obrigação da Verdade** (Artigo I.3.4) | Explicit error declarations. No fake solutions. |
| **Padrão Pagani** (Artigo II) | Zero placeholders. 99% test coverage. Production-ready only. |
| **DETER-AGENT Framework** (Anexo E) | 5-layer quality enforcement (Constitutional, Deliberation, State, Execution, Incentive). |
| **Agentes Guardiões** (Anexo D) | Automated constitutional compliance via CI/CD. |
| **Legislação Prévia** (Artigo V) | No code without governance. Design precedes implementation. |

### Cross-Reference

For the complete philosophical and operational foundation, see:
- **Constituição Vértice v3.0**: `/home/juan/Downloads/CONSTITUIÇÃO_VÉRTICE_v3.0.md`
- **Deep Research (AGI/Meta-Agents)**: `/home/juan/vertice-dev/AGI_META_AGENTS_DEEP_RESEARCH_2025.md`
- **Google-Level Refactor Plan**: `/.gemini/.../google_level_refactor_plan.md`

### The Spirit of the Law

> **"The letter killeth, but the spirit giveth life."** - 2 Corinthians 3:6

This constitution is not a bureaucratic checklist. It is the **codification of our values**:

1. **Respect for the User**: Their intent is sovereign. We serve, we don't manipulate.
2. **Respect for Truth**: We declare limitations, we don't hide them.
3. **Respect for Quality**: Production-ready is the only ready.
4. **Respect for the Craft**: Every line of code is a promise to future maintainers.
5. **Respect for the System**: Code exists in context. Systemic thinking is mandatory.

**When in doubt, ask**:
- "Am I respecting the user's intent?"
- "Am I being truthful about limitations?"
- "Is this production-ready?"
- "Will the next developer thank me or curse me?"
- "Have I considered systemic impact?"

If **any** answer is "no", **stop and refactor**.

---

**Approved by**: Juan Carlos de Souza (Arquiteto-Chefe)  
**Enforced by**: Agentes Guardiões + CI/CD + Human Review  
**Updated**: 2025-11-30 (Integration with Constituição Vértice v3.0)  
**Version**: 1.1  

---

**🏛️ This Constitution is law. Violators will be vetoed by Guardian Agents.**

**Built with integrity by Maximus 2.0 Team | Governed by Vértice values**
