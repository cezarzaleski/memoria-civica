#!/usr/bin/env python3
"""Pipeline completo: Migrations + Download + ETL (3 fases).

Este script é o ponto de entrada principal para o container Docker.
Executa o pipeline completo:
0. Migrations do banco de dados (Alembic)
1. Download dos CSVs da Câmara dos Deputados
2. ETL Fase 1: deputados → proposições → votações + votos
   2.4 ETL de gastos (CRÍTICO, depende de deputados)
3. ETL Fase 2: votacoes_proposicoes (CRÍTICO) → orientacoes (NÃO-CRÍTICO)
4. ETL Fase 3: classificação cívica (NÃO-CRÍTICO)

Example:
    python scripts/run_full_etl.py

Exit codes:
    0: Sucesso - pipeline completo executado sem erros em steps críticos
    1: Falha - erro em migrations, download ou ETL crítico
"""

import logging
import subprocess
import sys
import time
from functools import wraps
from pathlib import Path

# Add parent directory to path for imports
ETL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ETL_DIR))

from scripts.download_camara import download_all_files, print_summary  # noqa: E402
from src.classificacao.etl import run_classificacao_etl  # noqa: E402
from src.deputados.etl import run_deputados_etl  # noqa: E402
from src.gastos.etl import run_gastos_etl  # noqa: E402
from src.proposicoes.etl import run_proposicoes_etl  # noqa: E402
from src.shared.config import settings  # noqa: E402
from src.votacoes.etl import run_orientacoes_etl, run_votacoes_etl, run_votacoes_proposicoes_etl  # noqa: E402

# Configurar logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configura logging para stdout."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stdout_handler)


def retry_with_backoff(
    max_retries: int = 3,
    initial_wait: int = 1,
) -> callable:
    """Decorator que implementa retry com backoff exponencial."""

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> int:
            wait_time = initial_wait
            last_exception = None

            for attempt in range(max_retries):
                try:
                    logger.debug(f"Tentativa {attempt + 1}/{max_retries} de {func.__name__}")
                    return func(*args, **kwargs)

                except (ConnectionError, TimeoutError, OSError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Erro transiente em {func.__name__}: {e}. "
                            f"Retry em {wait_time}s (tentativa {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        wait_time *= 2
                    else:
                        logger.error(f"Erro transiente após {max_retries} tentativas: {e}")

                except Exception as e:
                    logger.error(f"Erro não-transiente em {func.__name__}: {e}")
                    raise

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_deputados_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de deputados com retry automático."""
    return run_deputados_etl(csv_path)


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_proposicoes_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de proposições com retry automático."""
    return run_proposicoes_etl(csv_path)


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_votacoes_etl_with_retry(votacoes_csv: str, votos_csv: str) -> int:
    """Executa ETL de votações com retry automático."""
    return run_votacoes_etl(votacoes_csv, votos_csv)


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_gastos_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de gastos com retry automático."""
    return run_gastos_etl(csv_path)


def run_migrations() -> int:
    """Executa migrations do banco de dados via Alembic.

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("FASE 0: Migrations do banco de dados")
    logger.info("=" * 60)

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=ETL_DIR,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                logger.info(f"  {line}")

        if result.returncode != 0:
            logger.error(f"Migrations falharam: {result.stderr}")
            return 1

        logger.info("✓ Migrations executadas com sucesso")
        return 0

    except Exception as e:
        logger.error(f"Erro ao executar migrations: {e}")
        return 1


def run_download() -> int:
    """Executa download dos arquivos da Câmara.

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("FASE 1: Download dos arquivos da Câmara")
    logger.info("=" * 60)

    stats = download_all_files(data_dir=settings.TEMP_DOWNLOAD_DIR)
    print_summary(stats)

    if stats.failed > 0:
        logger.error("Download falhou")
        return 1

    return 0


def run_etl(data_dir: Path) -> int:
    """Executa ETL completo em 3 fases.

    Fase 1: Ingestão base (deputados → proposições → votações + votos)
    Fase 2: Ingestão relacional (votacoes_proposicoes → orientacoes)
    Fase 3: Enriquecimento (classificação cívica)

    Args:
        data_dir: Diretório com os arquivos CSV

    Returns:
        Exit code (0 sucesso, 1 falha em step crítico)
    """
    warnings_count = 0

    try:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Iniciando ETL completo de todos domínios")
        logger.info("=" * 60)

        start_time = time.time()

        # ==================================================================
        # FASE 1 (FASE 2 do pipeline completo): Ingestão base
        # ==================================================================
        logger.info("")
        logger.info("FASE 2/4: Ingestão base")
        logger.info("-" * 60)
        phase_start = time.time()

        # Step: Deputados
        logger.info("Step 2.1: Deputados (sem dependências)")
        deputados_csv = data_dir / "deputados.csv"
        if not deputados_csv.exists():
            logger.error(f"Arquivo não encontrado: {deputados_csv}")
            return 1
        result = run_deputados_etl_with_retry(str(deputados_csv))
        if result != 0:
            logger.error("ETL de deputados falhou")
            return 1

        # Step: Proposições
        logger.info("Step 2.2: Proposições (depende de deputados)")
        proposicoes_csv = data_dir / f"proposicoes-{settings.CAMARA_ANO}.csv"
        if not proposicoes_csv.exists():
            logger.error(f"Arquivo não encontrado: {proposicoes_csv}")
            return 1
        result = run_proposicoes_etl_with_retry(str(proposicoes_csv))
        if result != 0:
            logger.error("ETL de proposições falhou")
            return 1

        # Step: Votações + Votos
        logger.info("Step 2.3: Votações + Votos (depende de proposições e deputados)")
        votacoes_csv = data_dir / f"votacoes-{settings.CAMARA_ANO}.csv"
        votos_csv = data_dir / f"votacoesVotos-{settings.CAMARA_ANO}.csv"
        if not votacoes_csv.exists():
            logger.error(f"Arquivo não encontrado: {votacoes_csv}")
            return 1
        if not votos_csv.exists():
            logger.error(f"Arquivo não encontrado: {votos_csv}")
            return 1
        result = run_votacoes_etl_with_retry(str(votacoes_csv), str(votos_csv))
        if result != 0:
            logger.error("ETL de votações falhou")
            return 1

        # Step: Gastos (CRÍTICO)
        logger.info("Step 2.4: Gastos parlamentares CEAP (depende de deputados)")
        gastos_csv = data_dir / f"gastos-{settings.CAMARA_ANO}.csv"
        if not gastos_csv.exists():
            logger.error(f"Arquivo não encontrado: {gastos_csv}")
            return 1
        result = run_gastos_etl_with_retry(str(gastos_csv))
        if result != 0:
            logger.error("ETL de gastos falhou")
            return 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 2 concluída em {phase_time:.2f}s")

        # ==================================================================
        # FASE 2 (FASE 3 do pipeline completo): Ingestão relacional
        # ==================================================================
        logger.info("")
        logger.info("FASE 3/4: Ingestão relacional")
        logger.info("-" * 60)
        phase_start = time.time()

        # Step: Votações-Proposições (CRÍTICO)
        logger.info("Step 3.1: Votações-Proposições (CRÍTICO)")
        vp_csv = data_dir / f"votacoesProposicoes-{settings.CAMARA_ANO}.csv"
        if not vp_csv.exists():
            logger.error(f"Arquivo não encontrado: {vp_csv}")
            return 1
        try:
            run_votacoes_proposicoes_etl(str(vp_csv))
        except Exception as e:
            logger.error(f"Step crítico falhou: votacoes_proposicoes — {e}")
            raise

        # Step: Orientações (NÃO-CRÍTICO)
        logger.info("Step 3.2: Orientações de bancada (NÃO-CRÍTICO)")
        orientacoes_csv = data_dir / f"votacoesOrientacoes-{settings.CAMARA_ANO}.csv"
        if not orientacoes_csv.exists():
            logger.warning(f"Arquivo não encontrado: {orientacoes_csv} — continuando sem orientações")
            warnings_count += 1
        else:
            try:
                run_orientacoes_etl(str(orientacoes_csv))
            except Exception as e:
                logger.warning(f"Step não-crítico falhou: orientacoes — {e}")
                warnings_count += 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 3 concluída em {phase_time:.2f}s")

        # ==================================================================
        # FASE 3 (FASE 4 do pipeline completo): Enriquecimento
        # ==================================================================
        logger.info("")
        logger.info("FASE 4/4: Enriquecimento")
        logger.info("-" * 60)
        phase_start = time.time()

        # Step: Classificação cívica (NÃO-CRÍTICO)
        logger.info("Step 4.1: Classificação cívica (NÃO-CRÍTICO)")
        try:
            run_classificacao_etl()
        except Exception as e:
            logger.warning(f"Step não-crítico falhou: classificacao — {e}")
            warnings_count += 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 4 concluída em {phase_time:.2f}s")

        # Resumo final
        total_time = time.time() - start_time
        logger.info("")
        logger.info("=" * 60)
        if warnings_count > 0:
            logger.info(f"✓ ETL COMPLETO EXECUTADO COM {warnings_count} WARNING(S)")
        else:
            logger.info("✓ ETL COMPLETO EXECUTADO COM SUCESSO!")
        logger.info(f"Tempo total: {total_time:.2f}s ({total_time / 60:.2f}m)")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Erro no ETL: {e}", exc_info=True)
        return 1


def main() -> int:
    """Função principal: Migrations + Download + ETL.

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    logger.info("=" * 60)
    logger.info("MEMÓRIA CÍVICA - PIPELINE COMPLETO")
    logger.info("=" * 60)
    logger.info(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    logger.info(f"Legislatura: {settings.CAMARA_LEGISLATURA}")
    logger.info(f"Ano: {settings.CAMARA_ANO}")
    logger.info(f"Diretório de dados: {settings.TEMP_DOWNLOAD_DIR}")
    logger.info("=" * 60)

    start_time = time.time()

    # Fase 0: Migrations
    result = run_migrations()
    if result != 0:
        return 1

    # Fase 1: Download
    result = run_download()
    if result != 0:
        return 1

    # Fases 2-4: ETL
    result = run_etl(settings.TEMP_DOWNLOAD_DIR)
    if result != 0:
        return 1

    # Resumo final
    total_time = time.time() - start_time
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
    logger.info(f"Tempo total (download + ETL): {total_time:.2f}s ({total_time / 60:.2f}m)")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
