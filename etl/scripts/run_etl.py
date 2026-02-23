#!/usr/bin/env python3
"""Orquestra ETL completo em 3 fases sequenciais.

Fase 1 — Ingestão base:
    deputados → proposições → votações + votos → gastos

Fase 2 — Ingestão relacional:
    votacoes_proposicoes (CRÍTICO) → orientacoes (NÃO-CRÍTICO)

Fase 3 — Enriquecimento:
    classificação cívica (NÃO-CRÍTICO)

Política de erros:
    - Steps de ingestão base (Fase 1) são bloqueantes.
    - votacoes_proposicoes (Fase 2) é bloqueante — pipeline para se falhar.
    - orientacoes (Fase 2) e classificacao (Fase 3) são NÃO-CRÍTICOS — pipeline
      continua com warning se falharem.

Exit codes:
    0: Sucesso — ETL completo executado (steps não-críticos podem ter falhado)
    1: Falha — erro em step crítico
"""

import logging
import sys
import time
from functools import wraps
from pathlib import Path

from src.classificacao.etl import run_classificacao_etl
from src.deputados.etl import run_deputados_etl
from src.gastos.etl import run_gastos_etl
from src.proposicoes.etl import run_proposicoes_etl
from src.shared.config import settings
from src.votacoes.etl import run_orientacoes_etl, run_votacoes_etl, run_votacoes_proposicoes_etl

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


@retry_with_backoff(max_retries=3, initial_wait=1)
def run_gastos_etl_with_retry(csv_path: str) -> int:
    """Executa ETL de gastos com retry automático.

    Args:
        csv_path: Caminho para o arquivo CSV de gastos

    Returns:
        Exit code (0 sucesso, 1 falha)
    """
    return run_gastos_etl(csv_path)


def resolve_csv_path(
    data_dir: Path,
    legacy_name: str,
    *,
    annual_name: str | None = None,
    ano: int | None = None,
) -> Path:
    """Resolve caminho de CSV aceitando convenções anual e legado.

    Regra:
    1. Se existir arquivo anual (`{annual_name}-{ano}.csv`), usa anual.
    2. Senão, usa nome legado (`{legacy_name}.csv`).
    3. Se nenhum existir, retorna o caminho anual (quando configurado) para
       manter mensagem de erro mais alinhada ao pipeline atual.
    """
    annual_path = None
    if annual_name and ano is not None:
        annual_path = data_dir / f"{annual_name}-{ano}.csv"
        if annual_path.exists():
            return annual_path

    legacy_path = data_dir / f"{legacy_name}.csv"
    if legacy_path.exists():
        return legacy_path

    return annual_path or legacy_path


def main() -> int:
    """Orquestra ETL completo em 3 fases sequenciais.

    Fase 1: Ingestão base (deputados → proposições → votações + votos → gastos)
    Fase 2: Ingestão relacional (votacoes_proposicoes → orientacoes)
    Fase 3: Enriquecimento (classificação cívica)

    Returns:
        Exit code (0 sucesso, 1 falha em step crítico)
    """
    data_dir = Path("data/dados_camara")
    ano = settings.CAMARA_ANO

    # Validar que diretório de dados existe
    if not data_dir.exists():
        logger.error(f"Diretório de dados não encontrado: {data_dir}")
        return 1

    warnings_count = 0

    try:
        logger.info("=" * 60)
        logger.info("Iniciando ETL completo de todos domínios")
        logger.info("=" * 60)

        # Registrar timestamps para medir performance
        start_time = time.time()

        # ======================================================================
        # FASE 1: Ingestão base (existente — todas são CRÍTICAS)
        # ======================================================================

        # Fase 1.1: Deputados (sem dependências)
        logger.info("")
        logger.info("FASE 1/3: Ingestão base")
        logger.info("-" * 60)
        phase_start = time.time()

        logger.info("Step 1.1: Deputados (sem dependências)")
        deputados_csv = data_dir / "deputados.csv"
        result = run_deputados_etl_with_retry(str(deputados_csv))
        if result != 0:
            logger.error("ETL de deputados falhou")
            return 1

        # Step 1.2: Proposições (depende de deputados)
        logger.info("Step 1.2: Proposições (depende de deputados)")
        proposicoes_csv = resolve_csv_path(
            data_dir,
            "proposicoes",
            annual_name="proposicoes",
            ano=ano,
        )
        result = run_proposicoes_etl_with_retry(str(proposicoes_csv))
        if result != 0:
            logger.error("ETL de proposições falhou")
            return 1

        # Step 1.3: Votações + Votos (depende de proposições e deputados)
        logger.info("Step 1.3: Votações + Votos (depende de proposições e deputados)")
        votacoes_csv = resolve_csv_path(
            data_dir,
            "votacoes",
            annual_name="votacoes",
            ano=ano,
        )
        votos_csv = resolve_csv_path(
            data_dir,
            "votos",
            annual_name="votacoesVotos",
            ano=ano,
        )
        result = run_votacoes_etl_with_retry(str(votacoes_csv), str(votos_csv))
        if result != 0:
            logger.error("ETL de votações falhou")
            return 1

        # Step 1.4: Gastos (depende de deputados)
        logger.info("Step 1.4: Gastos parlamentares CEAP (depende de deputados)")
        gastos_csv = resolve_csv_path(
            data_dir,
            "gastos",
            annual_name="gastos",
            ano=ano,
        )
        result = run_gastos_etl_with_retry(str(gastos_csv))
        if result != 0:
            logger.error("ETL de gastos falhou")
            return 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 1 concluída em {phase_time:.2f}s")

        # ======================================================================
        # FASE 2: Ingestão relacional
        # ======================================================================
        logger.info("")
        logger.info("FASE 2/3: Ingestão relacional")
        logger.info("-" * 60)
        phase_start = time.time()

        # Step 2.1: Votações-Proposições (CRÍTICO — pipeline para se falhar)
        logger.info("Step 2.1: Votações-Proposições (CRÍTICO)")
        vp_csv = resolve_csv_path(
            data_dir,
            "votacoes_proposicoes",
            annual_name="votacoesProposicoes",
            ano=ano,
        )
        try:
            run_votacoes_proposicoes_etl(str(vp_csv))
        except Exception as e:
            logger.error(f"Step crítico falhou: votacoes_proposicoes — {e}")
            raise

        # Step 2.2: Orientações (NÃO-CRÍTICO — pipeline continua com warning)
        logger.info("Step 2.2: Orientações de bancada (NÃO-CRÍTICO)")
        orientacoes_csv = resolve_csv_path(
            data_dir,
            "orientacoes",
            annual_name="votacoesOrientacoes",
            ano=ano,
        )
        try:
            run_orientacoes_etl(str(orientacoes_csv))
        except Exception as e:
            logger.warning(f"Step não-crítico falhou: orientacoes — {e}")
            warnings_count += 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 2 concluída em {phase_time:.2f}s")

        # ======================================================================
        # FASE 3: Enriquecimento
        # ======================================================================
        logger.info("")
        logger.info("FASE 3/3: Enriquecimento")
        logger.info("-" * 60)
        phase_start = time.time()

        # Step 3.1: Classificação cívica (NÃO-CRÍTICO)
        logger.info("Step 3.1: Classificação cívica (NÃO-CRÍTICO)")
        try:
            run_classificacao_etl()
        except Exception as e:
            logger.warning(f"Step não-crítico falhou: classificacao — {e}")
            warnings_count += 1

        phase_time = time.time() - phase_start
        logger.info(f"✓ Fase 3 concluída em {phase_time:.2f}s")

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
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
