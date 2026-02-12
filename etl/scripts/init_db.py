#!/usr/bin/env python3
"""Inicializa o banco de dados executando migrations Alembic.

Este script cria todas as tabelas necessárias no banco de dados
executando as migrações Alembic. Deve ser executado antes de rodar o ETL.

Exemplo:
    python scripts/init_db.py

Exit codes:
    0: Sucesso - banco inicializado com sucesso
    1: Falha - erro ao inicializar o banco
"""

import logging
import sys
from pathlib import Path

from alembic.config import Config

from alembic import command

# Add parent (etl) to path so imports work
ETL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ETL_DIR))

# Configurar logger
logger = logging.getLogger(__name__)


def setup_logging(log_dir: Path | None = None) -> None:
    """Configura logging para stdout e arquivo.

    Args:
        log_dir: Diretório para armazenar logs (padrão: logs/)
    """
    if log_dir is None:
        log_dir = Path("logs")

    # Criar diretório de logs se não existir
    log_dir.mkdir(exist_ok=True)

    # Formato de log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Handler para arquivo
    file_handler = logging.FileHandler(log_dir / "etl.log")
    file_handler.setFormatter(formatter)

    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)


def main() -> int:
    """Inicializa o banco de dados com Alembic.

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    try:
        logger.info("=" * 60)
        logger.info("Inicializando banco de dados...")
        logger.info("=" * 60)

        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")

        # Executar upgrade para HEAD (última migration)
        logger.info("Executando migrations Alembic...")
        command.upgrade(alembic_cfg, "head")

        logger.info("=" * 60)
        logger.info("Banco de dados inicializado com sucesso!")
        logger.info("=" * 60)
        return 0

    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}", exc_info=True)
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
