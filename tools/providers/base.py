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
