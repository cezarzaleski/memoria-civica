#!/usr/bin/env python3
"""Orquestra ETL completo: deputados → proposições → votações.

Este script é o ponto de entrada principal para executar o pipeline ETL
de todos os domínios na ordem correta respeitando as dependências.

Ordem de execução:
    1. Deputados (sem dependências)
    2. Proposições (depende de deputados para autores)
    3. Votações (depende de proposições e deputados)

Exemplo:
    python scripts/run_etl.py

Exit codes:
    0: Sucesso - ETL completo executado sem erros
    1: Falha - erro em qualquer fase do ETL
"""

import logging
import sys
import time
from functools import wraps
from pathlib import Path

from src.deputados.etl import run_deputados_etl
from src.proposicoes.etl import run_proposicoes_etl
from src.votacoes.etl import run_votacoes_etl

# Add src to path so imports work when script is run from anywhere
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


def retry_with_backoff(
    max_retries: int = 3,
    initial_wait: int = 1,
) -> callable:
    """Decorator que implementa retry com backoff exponencial.

    Retry é aplicado apenas para erros transientes (conexão, timeout).
    Erros de validação não são retentados.

    Args:
        max_retries: Número máximo de tentativas (padrão: 3)
        initial_wait: Tempo inicial de espera em segundos (padrão: 1)

    Returns:
        Função decoradora
    """

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> int:
            """Wrapper que implementa lógica de retry."""
            wait_time = initial_wait
            last_exception = None

            for attempt in range(max_retries):
                try:
                    logger.debug(f"Tentativa {attempt + 1}/{max_retries} de {func.__name__}")
                    return func(*args, **kwargs)

                except (ConnectionError, TimeoutError, OSError) as e:
                    # Erros transientes - retry
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Erro transiente em {func.__name__}: {e}. "
                            f"Retry em {wait_time}s (tentativa {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        wait_time *= 2  # Backoff exponencial
                    else:
                        logger.error(f"Erro transiente após {max_retries} tentativas: {e}")

                except Exception as e:
                    # Erros não-transientes (validação, etc) - não retry
                    logger.error(f"Erro não-transiente em {func.__name__}: {e}")
                    raise

            # Se todas tentativas falharam com erro transiente
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_deputados_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de deputados com retry automático.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    return run_deputados_etl(csv_path)


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_proposicoes_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de proposições com retry automático.

    Args:
        csv_path: Caminho para o arquivo CSV

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    return run_proposicoes_etl(csv_path)


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_votacoes_etl_with_retry(votacoes_csv: str, votos_csv: str) -> int:
    """Executa ETL de votações com retry automático.

    Args:
        votacoes_csv: Caminho para o arquivo CSV de votações
        votos_csv: Caminho para o arquivo CSV de votos

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    return run_votacoes_etl(votacoes_csv, votos_csv)


def main() -> int:
    """Orquestra ETL completo para todos domínios.

    Executa na ordem: deputados → proposições → votações,
    respeitando dependências entre domínios.

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    data_dir = Path("data/dados_camara")

    # Validar que diretório de dados existe
    if not data_dir.exists():
        logger.error(f"Diretório de dados não encontrado: {data_dir}")
        return 1

    try:
        logger.info("=" * 60)
        logger.info("Iniciando ETL completo de todos domínios")
        logger.info("=" * 60)

        # Registrar timestamps para medir performance
        start_time = time.time()

        # Fase 1: Deputados (sem dependências)
        logger.info("")
        logger.info("FASE 1/3: Deputados (sem dependências)")
        logger.info("-" * 60)
        phase_start = time.time()

        deputados_csv = data_dir / "deputados.csv"
        result = run_deputados_etl_with_retry(str(deputados_csv))

        if result != 0:
            logger.error("ETL de deputados falhou")
            return 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 1 concluída em {phase_time:.2f}s")

        # Fase 2: Proposições (depende de deputados)
        logger.info("")
        logger.info("FASE 2/3: Proposições (depende de deputados)")
        logger.info("-" * 60)
        phase_start = time.time()

        proposicoes_csv = data_dir / "proposicoes.csv"
        result = run_proposicoes_etl_with_retry(str(proposicoes_csv))

        if result != 0:
            logger.error("ETL de proposições falhou")
            return 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 2 concluída em {phase_time:.2f}s")

        # Fase 3: Votações (depende de proposições e deputados)
        logger.info("")
        logger.info("FASE 3/3: Votações (depende de proposições e deputados)")
        logger.info("-" * 60)
        phase_start = time.time()

        votacoes_csv = data_dir / "votacoes.csv"
        votos_csv = data_dir / "votos.csv"
        result = run_votacoes_etl_with_retry(str(votacoes_csv), str(votos_csv))

        if result != 0:
            logger.error("ETL de votações falhou")
            return 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 3 concluída em {phase_time:.2f}s")

        # Resumo final
        total_time = time.time() - start_time
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ ETL COMPLETO EXECUTADO COM SUCESSO!")
        logger.info(f"Tempo total: {total_time:.2f}s ({total_time / 60:.2f}m)")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Erro no ETL: {e}", exc_info=True)
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
