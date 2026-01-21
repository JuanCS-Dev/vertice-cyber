#!/usr/bin/env python3
"""
Script de Validação Pós-Deploy.

Verifica:
1. Arquivos existem
2. Imports funcionam
3. Feature flags carregam
4. Providers inicializam
5. Testes passam (opcional)

Usage:
    python scripts/validate_implementation.py
"""

import os
import sys
from pathlib import Path
from typing import Tuple

# Cores ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(msg: str) -> None:
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")


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
        "tools/providers/otx.py",
        "tools/providers/virustotal.py",
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
        "tools.providers.otx",
        "tools.providers.virustotal",
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
        from tools.providers.otx import get_otx_provider

        provider = get_otx_provider()
        if provider.is_available():
            print_ok("OTX Provider: DISPONÍVEL")
        else:
            print_warn("OTX Provider: Não configurado (usará fallback)")
        ok += 1
    except Exception as e:
        print_fail(f"OTX Provider erro: {e}")
        fail += 1

    try:
        from tools.providers.virustotal import get_vt_provider

        provider = get_vt_provider()
        if provider.is_available():
            print_ok("VirusTotal Provider: DISPONÍVEL")
        else:
            print_warn("VirusTotal Provider: Não configurado (usará fallback)")
        ok += 1
    except Exception as e:
        print_fail(f"VirusTotal Provider erro: {e}")
        fail += 1

    try:
        from tools.providers.cache import get_cache

        cache = get_cache()
        backend_name = cache._backend.__class__.__name__
        print_ok(f"Cache: {backend_name}")
        ok += 1
    except Exception as e:
        print_fail(f"Cache erro: {e}")
        fail += 1

    return ok, fail


def main():
    """Executa validação completa."""
    print(f"\n{BOLD}🔍 VALIDAÇÃO DE IMPLEMENTAÇÃO{RESET}")
    print("   Substituição de Mocks por Código Real\n")

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


if __name__ == "__main__":
    main()
