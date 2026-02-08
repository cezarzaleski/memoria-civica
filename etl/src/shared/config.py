"""Configurações centralizadas do projeto usando Pydantic Settings.

Este módulo fornece configurações carregadas de variáveis de ambiente com
fallback para valores padrão sensatos. Usado por todos os domínios do projeto.
"""

from pathlib import Path
from typing import Literal, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação com suporte a variáveis de ambiente.

    Attributes:
        DATABASE_URL: URL de conexão do banco de dados (construída automaticamente se não definida).
        POSTGRES_USER: Usuário do PostgreSQL.
        POSTGRES_PASSWORD: Senha do PostgreSQL.
        POSTGRES_DB: Nome do banco de dados.
        POSTGRES_HOST: Host do PostgreSQL (padrão: memoria-postgres para Docker).
        POSTGRES_PORT: Porta do PostgreSQL (padrão: 5432).
        DATA_DIR: Diretório contendo arquivos CSV da Câmara dos Deputados.
        LOG_LEVEL: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        LOG_FILE: Caminho do arquivo de log (None desabilita log em arquivo).
        CAMARA_API_BASE_URL: URL base da API Dados Abertos da Câmara dos Deputados.
        CAMARA_LEGISLATURA: Número da legislatura atual (57 = 2023-2027).
        CAMARA_ANO: Ano para download de proposições (arquivos são organizados por ano).
        TEMP_DOWNLOAD_DIR: Diretório temporário para downloads de arquivos CSV.
        WEBHOOK_URL: URL do webhook para notificações de erro (None desabilita notificações).
    """

    # Configurações do PostgreSQL (usadas para construir DATABASE_URL)
    POSTGRES_USER: str = "memoria"
    POSTGRES_PASSWORD: Optional[str] = None  # noqa: UP045
    POSTGRES_DB: str = "memoria_civica"
    POSTGRES_HOST: str = "memoria-postgres"
    POSTGRES_PORT: int = 5432

    # URL de conexão (construída automaticamente se POSTGRES_PASSWORD estiver definida)
    DATABASE_URL: Optional[str] = None  # noqa: UP045

    DATA_DIR: Path = Path("./data/dados_camara")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE: Optional[Path] = None  # noqa: UP045

    # Configurações da API Câmara dos Deputados
    CAMARA_API_BASE_URL: str = "https://dadosabertos.camara.leg.br/arquivos"
    CAMARA_LEGISLATURA: int = 57
    CAMARA_ANO: int = 2025
    TEMP_DOWNLOAD_DIR: Path = Path("/tmp/camara_downloads")

    # Configuração de webhook para notificações de erro
    WEBHOOK_URL: Optional[str] = None  # noqa: UP045

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Constrói DATABASE_URL a partir das variáveis POSTGRES_* se não definida."""
        if self.DATABASE_URL is None and self.POSTGRES_PASSWORD is not None:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        elif self.DATABASE_URL is None:
            # Fallback para SQLite se não houver configuração PostgreSQL
            self.DATABASE_URL = "sqlite:///./memoria_civica.db"
        return self


# Singleton global para evitar múltiplas instanciações
settings = Settings()
