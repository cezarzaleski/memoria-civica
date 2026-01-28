"""Configurações centralizadas do projeto usando Pydantic Settings.

Este módulo fornece configurações carregadas de variáveis de ambiente com
fallback para valores padrão sensatos. Usado por todos os domínios do projeto.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação com suporte a variáveis de ambiente.

    Attributes:
        DATABASE_URL: URL de conexão do banco de dados (SQLite por padrão).
        DATA_DIR: Diretório contendo arquivos CSV da Câmara dos Deputados.
        LOG_LEVEL: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        LOG_FILE: Caminho do arquivo de log (None desabilita log em arquivo).
    """

    DATABASE_URL: str = "sqlite:///./memoria_civica.db"
    DATA_DIR: Path = Path("./data/dados_camara")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE: Path | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton global para evitar múltiplas instanciações
settings = Settings()
