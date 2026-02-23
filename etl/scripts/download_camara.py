#!/usr/bin/env python3
"""Download de arquivos CSV da API Dados Abertos da Câmara dos Deputados.

NOTA: Requer Python 3.11+ conforme pyproject.toml.
O import de annotations permite sintaxe moderna de tipos.

Este script baixa os arquivos CSV necessários para o pipeline ETL:
- deputados.csv: Lista de todos os deputados
- gastos-{ano}.csv: Gastos parlamentares (CEAP)
- proposicoes-{ano}.csv: Proposições do ano
- votacoes-{ano}.csv: Votações do ano
- votacoesVotos-{ano}.csv: Votos individuais do ano

O download respeita a sequência de dependências:
deputados → proposições → votações → votos → gastos

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
import time
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directory to path for imports
ETL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ETL_DIR))

from src.shared.config import settings  # noqa: E402
from src.shared.downloader import DownloadResult, download_file  # noqa: E402
from src.shared.webhook import send_webhook_notification  # noqa: E402

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
        total_bytes: Total de bytes baixados
        total_time: Tempo total de execução em segundos
        phase_times: Dicionário com tempo de cada fase (arquivo)
        retry_count: Número total de retries realizados
        start_time: Timestamp de início da execução
    """

    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    total_bytes: int = 0
    total_time: float = 0.0
    phase_times: dict[str, float] = field(default_factory=dict)
    retry_count: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def total_files(self) -> int:
        """Retorna o número total de arquivos processados."""
        return self.downloaded + self.skipped + self.failed

    def format_time(self, seconds: float) -> str:
        """Formata tempo em formato legível.

        Args:
            seconds: Tempo em segundos

        Returns:
            String formatada (ex: "1m 30s", "45s", "2h 15m")
        """
        if seconds >= 3600:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        elif seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        return f"{seconds:.2f}s"

    def format_bytes(self, size_bytes: int) -> str:
        """Formata tamanho em formato legível.

        Args:
            size_bytes: Tamanho em bytes

        Returns:
            String formatada (ex: "1.5 MB", "256 KB")
        """
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        return f"{size_bytes} bytes"


# Definição dos arquivos a serem baixados
FILE_CONFIGS = {
    "deputados": {
        "url_path": "deputados/csv/deputados.csv",
        "filename": "deputados.csv",
        "requires_legislatura": False,
        "requires_ano": False,
    },
    "proposicoes": {
        "url_path": "proposicoes/csv/proposicoes-{ano}.csv",
        "filename": "proposicoes-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
    "gastos": {
        "url_path": "deputadosDespesas/csv/deputadosDespesas-{ano}.csv",
        "filename": "gastos-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
    "votacoes": {
        "url_path": "votacoes/csv/votacoes-{ano}.csv",
        "filename": "votacoes-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
    "votos": {
        "url_path": "votacoesVotos/csv/votacoesVotos-{ano}.csv",
        "filename": "votacoesVotos-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
    "votacoes_proposicoes": {
        "url_path": "votacoesProposicoes/csv/votacoesProposicoes-{ano}.csv",
        "filename": "votacoesProposicoes-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
    "votacoes_orientacoes": {
        "url_path": "votacoesOrientacoes/csv/votacoesOrientacoes-{ano}.csv",
        "filename": "votacoesOrientacoes-{ano}.csv",
        "requires_legislatura": False,
        "requires_ano": True,
    },
}

# Ordem de download (respeita dependências)
DOWNLOAD_ORDER = [
    "deputados",
    "proposicoes",
    "votacoes",
    "votos",
    "gastos",
    "votacoes_proposicoes",
    "votacoes_orientacoes",
]


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
    elif config["requires_ano"]:
        url_path = url_path.format(ano=settings.CAMARA_ANO)

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
    elif config["requires_ano"]:
        filename = filename.format(ano=settings.CAMARA_ANO)

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

    phase_start = time.time()

    if dry_run:
        logger.info("  [DRY-RUN] Download simulado")
        stats.downloaded += 1
        phase_time = time.time() - phase_start
        stats.phase_times[file_key] = phase_time
        return True

    result: DownloadResult = download_file(url=url, dest_path=dest_path)

    phase_time = time.time() - phase_start
    stats.phase_times[file_key] = phase_time

    if result.success:
        if result.skipped:
            logger.warning(
                "  Arquivo não alterado, pulando: %s (tempo: %s)",
                dest_path.name,
                stats.format_time(phase_time),
            )
            stats.skipped += 1
            # Adicionar tamanho do arquivo existente para estatísticas
            if result.file_size:
                stats.total_bytes += result.file_size
        else:
            logger.info(
                "  Download concluído: %s (tamanho: %s, tempo: %s, retries: %d)",
                dest_path.name,
                stats.format_bytes(result.file_size) if result.file_size else "N/A",
                stats.format_time(phase_time),
                result.retry_attempts,
            )
            stats.downloaded += 1
            if result.file_size:
                stats.total_bytes += result.file_size
            stats.retry_count += result.retry_attempts
        return True
    else:
        error_msg = f"{file_key}: {result.error}"
        logger.error(
            "  Falha no download: %s (tempo: %s, retries: %d)",
            result.error,
            stats.format_time(phase_time),
            result.retry_attempts,
        )
        stats.failed += 1
        stats.errors.append(error_msg)
        stats.retry_count += result.retry_attempts

        # Enviar notificação via webhook (não bloqueia em caso de falha)
        send_webhook_notification(
            stage=f"download_{file_key}",
            message=result.error or "Erro desconhecido no download",
        )

        return False


def download_all_files(
    data_dir: Path,
    files: list[str] | None = None,
    dry_run: bool = False,
) -> DownloadStats:
    """Baixa todos os arquivos na ordem correta.

    Orquestra o download de todos os arquivos CSV da API da Câmara,
    respeitando a ordem de dependências e rastreando métricas detalhadas.

    Args:
        data_dir: Diretório de destino para os arquivos
        files: Lista de arquivos específicos para baixar (None = todos)
        dry_run: Se True, apenas simula os downloads

    Returns:
        Estatísticas de download com métricas de tempo e desempenho
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
    logger.info("Legislatura: %d | Ano: %d", settings.CAMARA_LEGISLATURA, settings.CAMARA_ANO)
    if dry_run:
        logger.info("Modo: DRY-RUN (simulação)")
    logger.info("=" * 60)

    for i, file_key in enumerate(ordered_files, 1):
        logger.info("")
        logger.info("[%d/%d] %s", i, len(ordered_files), file_key.upper())
        logger.info("-" * 40)
        download_single_file(file_key, data_dir, stats, dry_run)

    return stats


def print_summary(stats: DownloadStats) -> None:
    """Imprime sumário final dos downloads.

    Gera relatório completo com:
    - Contagem de arquivos (baixados, pulados, falhas)
    - Tempo total e tempo por fase
    - Volume total de dados processados
    - Lista de erros (se houver)

    Args:
        stats: Estatísticas de download
    """
    # Calcular tempo total
    stats.total_time = time.time() - stats.start_time

    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMÁRIO DE DOWNLOADS")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Estatísticas de arquivos:")
    logger.info("  Total processado: %d arquivo(s)", stats.total_files)
    logger.info("  Baixados: %d", stats.downloaded)
    logger.info("  Pulados (cache): %d", stats.skipped)
    logger.info("  Falhas: %d", stats.failed)
    logger.info("")
    logger.info("Métricas de desempenho:")
    logger.info("  Tempo total: %s", stats.format_time(stats.total_time))
    logger.info("  Dados processados: %s", stats.format_bytes(stats.total_bytes))
    if stats.retry_count > 0:
        logger.info("  Total de retries: %d", stats.retry_count)

    # Tempo por fase
    if stats.phase_times:
        logger.info("")
        logger.info("Tempo por arquivo:")
        for file_key, phase_time in stats.phase_times.items():
            logger.info("  %s: %s", file_key, stats.format_time(phase_time))

    # Erros
    if stats.errors:
        logger.info("")
        logger.info("Erros encontrados:")
        for error in stats.errors:
            logger.error("  - %s", error)

    logger.info("")
    logger.info("=" * 60)

    if stats.failed == 0:
        logger.info("✓ Download concluído com sucesso!")
    else:
        logger.error("✗ Download concluído com %d falha(s)", stats.failed)
    logger.info("=" * 60)


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
