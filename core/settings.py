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
        default=None, description="API key para HaveIBeenPwned"
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
            "exploit",
            "attack",
            "brute_force",
            "ddos",
            "malware",
            "ransomware",
            "zero_day",
            "exfiltrate",
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
