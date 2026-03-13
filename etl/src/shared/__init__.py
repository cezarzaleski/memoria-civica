"""Módulo shared: infraestrutura compartilhada entre domínios.

Fornece configurações centralizadas, gerenciamento de banco de dados e
abstrações comuns usadas por todos os domínios do projeto.
"""

from .config import Settings, settings
from .database import Base, SessionLocal, engine, get_db
from .llm_client import EnriquecimentoOutput, LLMClient, LLMResult, OpenAIClient

__all__ = [
    "Base",
    "EnriquecimentoOutput",
    "LLMClient",
    "LLMResult",
    "OpenAIClient",
    "SessionLocal",
    "Settings",
    "engine",
    "get_db",
    "settings",
]
