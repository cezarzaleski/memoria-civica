"""Módulo shared: infraestrutura compartilhada entre domínios.

Fornece configurações centralizadas, gerenciamento de banco de dados e
abstrações comuns usadas por todos os domínios do projeto.
"""

from .config import Settings, settings
from .database import Base, SessionLocal, engine, get_db

__all__ = [
    "Base",
    "SessionLocal",
    "Settings",
    "engine",
    "get_db",
    "settings",
]
