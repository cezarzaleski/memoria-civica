"""Módulo shared: infraestrutura compartilhada entre domínios.

Fornece configurações centralizadas, gerenciamento de banco de dados e
abstrações comuns usadas por todos os domínios do projeto.
"""

from .config import Settings, settings
from .database import Base, SessionLocal, engine, get_db
from .downloader import DownloadResult, download_file

__all__ = [
    "Base",
    "DownloadResult",
    "SessionLocal",
    "Settings",
    "download_file",
    "engine",
    "get_db",
    "settings",
]
