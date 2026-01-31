"""Configurações centralizadas do projeto usando Pydantic Settings.

Este módulo fornece configurações carregadas de variáveis de ambiente com
fallback para valores padrão sensatos. Usado por todos os domínios do projeto.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação com suporte a variáveis de ambiente.

    Attributes:
        DATABASE_URL: URL de conexão do banco de dados (SQLite por padrão).
        DATA_DIR: Diretório contendo arquivos CSV da Câmara dos Deputados.
        LOG_LEVEL: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        LOG_FILE: Caminho do arquivo de log (None desabilita log em arquivo).
        CAMARA_API_BASE_URL: URL base da API Dados Abertos da Câmara dos Deputados.
        CAMARA_LEGISLATURA: Número da legislatura atual (57 = 2023-2027).
        TEMP_DOWNLOAD_DIR: Diretório temporário para downloads de arquivos CSV.
        WEBHOOK_URL: URL do webhook para notificações de erro (None desabilita notificações).
    """

    DATABASE_URL: str = "sqlite:///./memoria_civica.db"
    DATA_DIR: Path = Path("./data/dados_camara")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE: Optional[Path] = None  # noqa: UP045

    # Configurações da API Câmara dos Deputados
    CAMARA_API_BASE_URL: str = "https://dadosabertos.camara.leg.br/arquivos"
    CAMARA_LEGISLATURA: int = 57
    TEMP_DOWNLOAD_DIR: Path = Path("/tmp/camara_downloads")

    # Configuração de webhook para notificações de erro
    WEBHOOK_URL: Optional[str] = None  # noqa: UP045

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Singleton global para evitar múltiplas instanciações
settings = Settings()
