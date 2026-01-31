#!/usr/bin/env python3
"""Download de arquivos CSV da API Dados Abertos da Câmara dos Deputados.

NOTA: Requer Python 3.11+ conforme pyproject.toml.
O import de annotations permite sintaxe moderna de tipos.

Este script baixa os arquivos CSV necessários para o pipeline ETL:
- deputados.csv: Lista de todos os deputados
- proposicoes-{legislatura}.csv: Proposições da legislatura
- votacoes-{legislatura}.csv: Votações da legislatura
- votacoesVotos-{legislatura}.csv: Votos individuais

O download respeita a sequência de dependências:
deputados → proposições → votações → votos

Example:
    # Baixar todos os arquivos para diretório padrão
    python scripts/download_camara.py

    # Especificar diretório de destino
    python scripts/download_camara.py --data-dir /path/to/data

    # Baixar arquivo específico
    python scripts/download_camara.py --file deputados

Exit codes:
    0: Sucesso - todos os downloads concluídos
    1: Falha - pelo menos um download falhou
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from src.shared.config import settings
from src.shared.downloader import DownloadResult, download_file

# Configurar logger
logger = logging.getLogger(__name__)


@dataclass
class DownloadStats:
    """Estatísticas de download.

    Attributes:
        downloaded: Número de arquivos baixados com sucesso
        skipped: Número de arquivos pulados (cache hit)
        failed: Número de arquivos que falharam
        errors: Lista de mensagens de erro
    """

    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Inicializa a lista de erros."""
        if self.errors is None:
            self.errors = []


# Definição dos arquivos a serem baixados
FILE_CONFIGS = {
    "deputados": {
        "url_path": "deputados/csv/deputados.csv",
        "filename": "deputados.csv",
        "requires_legislatura": False,
    },
    "proposicoes": {
        "url_path": "proposicoes/csv/proposicoes-{legislatura}.csv",
        "filename": "proposicoes-{legislatura}.csv",
        "requires_legislatura": True,
    },
    "votacoes": {
        "url_path": "votacoes/csv/votacoes-{legislatura}.csv",
        "filename": "votacoes-{legislatura}.csv",
        "requires_legislatura": True,
    },
    "votos": {
        "url_path": "votacoesVotos/csv/votacoesVotos-{legislatura}.csv",
        "filename": "votacoesVotos-{legislatura}.csv",
        "requires_legislatura": True,
    },
}

# Ordem de download (respeita dependências)
DOWNLOAD_ORDER = ["deputados", "proposicoes", "votacoes", "votos"]


def setup_logging(verbose: bool = False) -> None:
    """Configura logging para stdout.

    Args:
        verbose: Se True, usa nível DEBUG. Se False, usa INFO.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    root_logger.addHandler(stdout_handler)


def build_url(file_key: str) -> str:
    """Constrói URL completa para download.

    Args:
        file_key: Chave do arquivo (deputados, proposicoes, votacoes, votos)

    Returns:
        URL completa para download
    """
    config = FILE_CONFIGS[file_key]
    url_path = config["url_path"]

    if config["requires_legislatura"]:
        url_path = url_path.format(legislatura=settings.CAMARA_LEGISLATURA)

    return f"{settings.CAMARA_API_BASE_URL}/{url_path}"


def get_dest_path(file_key: str, data_dir: Path) -> Path:
    """Retorna o caminho de destino para um arquivo.

    Args:
        file_key: Chave do arquivo (deputados, proposicoes, votacoes, votos)
        data_dir: Diretório de destino

    Returns:
        Caminho completo do arquivo de destino
    """
    config = FILE_CONFIGS[file_key]
    filename = config["filename"]

    if config["requires_legislatura"]:
        filename = filename.format(legislatura=settings.CAMARA_LEGISLATURA)

    return data_dir / filename


def download_single_file(
    file_key: str,
    data_dir: Path,
    stats: DownloadStats,
    dry_run: bool = False,
) -> bool:
    """Baixa um único arquivo.

    Args:
        file_key: Chave do arquivo (deputados, proposicoes, votacoes, votos)
        data_dir: Diretório de destino
        stats: Estatísticas de download para atualização
        dry_run: Se True, apenas simula o download

    Returns:
        True se o download foi bem-sucedido ou pulado, False se falhou
    """
    url = build_url(file_key)
    dest_path = get_dest_path(file_key, data_dir)

    logger.info("Processando: %s", file_key)
    logger.info("  URL: %s", url)
    logger.info("  Destino: %s", dest_path)

    if dry_run:
        logger.info("  [DRY-RUN] Download simulado")
        stats.downloaded += 1
        return True

    result: DownloadResult = download_file(url=url, dest_path=dest_path)

    if result.success:
        if result.skipped:
            logger.warning("  Arquivo não alterado, pulando: %s", dest_path.name)
            stats.skipped += 1
        else:
            logger.info("  Download concluído: %s", dest_path.name)
            stats.downloaded += 1
        return True
    else:
        error_msg = f"{file_key}: {result.error}"
        logger.error("  Falha no download: %s", result.error)
        stats.failed += 1
        stats.errors.append(error_msg)
        return False


def download_all_files(
    data_dir: Path,
    files: list[str] | None = None,
    dry_run: bool = False,
) -> DownloadStats:
    """Baixa todos os arquivos na ordem correta.

    Args:
        data_dir: Diretório de destino para os arquivos
        files: Lista de arquivos específicos para baixar (None = todos)
        dry_run: Se True, apenas simula os downloads

    Returns:
        Estatísticas de download
    """
    stats = DownloadStats()

    # Criar diretório se não existir
    data_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Diretório de dados: %s", data_dir)

    # Determinar quais arquivos baixar
    files_to_download = files if files else DOWNLOAD_ORDER

    # Validar arquivos solicitados
    for file_key in files_to_download:
        if file_key not in FILE_CONFIGS:
            logger.error("Arquivo desconhecido: %s", file_key)
            logger.error("Arquivos válidos: %s", ", ".join(FILE_CONFIGS.keys()))
            stats.failed += 1
            stats.errors.append(f"Arquivo desconhecido: {file_key}")
            return stats

    # Reordenar para respeitar dependências
    ordered_files = [f for f in DOWNLOAD_ORDER if f in files_to_download]

    logger.info("=" * 60)
    logger.info("Iniciando download de %d arquivo(s) da Câmara dos Deputados", len(ordered_files))
    logger.info("Legislatura: %d", settings.CAMARA_LEGISLATURA)
    logger.info("=" * 60)

    for i, file_key in enumerate(ordered_files, 1):
        logger.info("")
        logger.info("[%d/%d] %s", i, len(ordered_files), file_key.upper())
        logger.info("-" * 40)
        download_single_file(file_key, data_dir, stats, dry_run)

    return stats


def print_summary(stats: DownloadStats) -> None:
    """Imprime sumário final dos downloads.

    Args:
        stats: Estatísticas de download
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMÁRIO DE DOWNLOADS")
    logger.info("=" * 60)
    logger.info("  Baixados: %d", stats.downloaded)
    logger.info("  Pulados (cache): %d", stats.skipped)
    logger.info("  Falhas: %d", stats.failed)

    if stats.errors:
        logger.info("")
        logger.info("Erros encontrados:")
        for error in stats.errors:
            logger.error("  - %s", error)

    logger.info("=" * 60)

    if stats.failed == 0:
        logger.info("✓ Download concluído com sucesso!")
    else:
        logger.error("✗ Download concluído com %d falha(s)", stats.failed)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Processa argumentos de linha de comando.

    Args:
        args: Lista de argumentos (None = sys.argv)

    Returns:
        Namespace com argumentos processados
    """
    parser = argparse.ArgumentParser(
        description="Download de arquivos CSV da API Dados Abertos da Câmara dos Deputados",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                           Baixa todos os arquivos
  %(prog)s --data-dir /tmp/camara    Especifica diretório de destino
  %(prog)s --file deputados          Baixa apenas deputados.csv
  %(prog)s --file votacoes --file votos  Baixa múltiplos arquivos
  %(prog)s --dry-run                 Simula downloads sem executar
        """,
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=settings.TEMP_DOWNLOAD_DIR,
        help=f"Diretório de destino para os arquivos (padrão: {settings.TEMP_DOWNLOAD_DIR})",
    )

    parser.add_argument(
        "--file",
        dest="files",
        action="append",
        choices=list(FILE_CONFIGS.keys()),
        help="Arquivo específico para baixar (pode ser usado múltiplas vezes)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula downloads sem executar (útil para testar)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Habilita logging detalhado (DEBUG)",
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Função principal do script.

    Args:
        args: Lista de argumentos de linha de comando (None = sys.argv)

    Returns:
        Exit code (0 = sucesso, 1 = falha)
    """
    parsed_args = parse_args(args)

    # Configurar logging
    setup_logging(verbose=parsed_args.verbose)

    try:
        # Executar downloads
        stats = download_all_files(
            data_dir=parsed_args.data_dir,
            files=parsed_args.files,
            dry_run=parsed_args.dry_run,
        )

        # Imprimir sumário
        print_summary(stats)

        # Retornar código de saída
        return 0 if stats.failed == 0 else 1

    except KeyboardInterrupt:
        logger.warning("Download interrompido pelo usuário")
        return 1

    except Exception as e:
        logger.error("Erro inesperado: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
