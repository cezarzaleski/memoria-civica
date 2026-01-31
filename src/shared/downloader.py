"""Módulo de download reutilizável com suporte a cache ETag e retry.

Este módulo fornece funcionalidades de download HTTP com:
- Verificação de cache via ETag ou Content-Length
- Streaming de arquivos grandes em chunks de 8KB
- Retry com backoff exponencial para erros transientes

Example:
    from pathlib import Path
    from src.shared.downloader import download_file, DownloadResult

    result = download_file(
        url="https://example.com/file.csv",
        dest_path=Path("/tmp/file.csv")
    )
    if result.success:
        print(f"Arquivo salvo em: {result.path}")
    elif result.skipped:
        print("Arquivo não foi alterado, download ignorado")
    else:
        print(f"Erro: {result.error}")
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Optional, TypeVar

import requests

logger = logging.getLogger(__name__)

# Constantes
CHUNK_SIZE = 8192  # 8KB
DEFAULT_TIMEOUT = 300  # 5 minutos
MAX_RETRIES = 3
INITIAL_WAIT = 2  # segundos

T = TypeVar("T")


@dataclass
class DownloadResult:
    """Resultado de uma operação de download.

    Attributes:
        success: True se o download foi bem-sucedido
        path: Caminho do arquivo baixado (None se falhou)
        skipped: True se o arquivo não foi alterado (cache hit)
        error: Mensagem de erro (None se sucesso ou skipped)
    """

    success: bool
    path: Optional[Path]  # noqa: UP045
    skipped: bool
    error: Optional[str]  # noqa: UP045


def retry_with_backoff(
    max_retries: int = MAX_RETRIES,
    initial_wait: int = INITIAL_WAIT,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator que implementa retry com backoff exponencial.

    Retry é aplicado apenas para erros transientes (conexão, timeout).
    Erros HTTP 4xx/5xx NÃO são retentados automaticamente.

    Args:
        max_retries: Número máximo de tentativas (padrão: 3)
        initial_wait: Tempo inicial de espera em segundos (padrão: 2)

    Returns:
        Função decoradora

    Example:
        @retry_with_backoff(max_retries=3, initial_wait=2)
        def fetch_data(url: str) -> dict:
            return requests.get(url).json()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            """Wrapper que implementa lógica de retry."""
            wait_time = initial_wait
            last_exception: Optional[Exception] = None  # noqa: UP045

            for attempt in range(max_retries):
                try:
                    logger.debug("Tentativa %d/%d de %s", attempt + 1, max_retries, func.__name__)
                    return func(*args, **kwargs)

                except (ConnectionError, TimeoutError, OSError, requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout) as e:
                    # HTTPError é subclasse de OSError, mas NÃO é transiente
                    if isinstance(e, requests.exceptions.HTTPError):
                        logger.error("Erro HTTP em %s: %s", func.__name__, e)
                        raise

                    # Erros transientes - retry
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            "Erro transiente em %s: %s. Retry em %ds (tentativa %d/%d)",
                            func.__name__,
                            e,
                            wait_time,
                            attempt + 1,
                            max_retries,
                        )
                        time.sleep(wait_time)
                        wait_time *= 2  # Backoff exponencial
                    else:
                        logger.error("Erro transiente após %d tentativas: %s", max_retries, e)

                except Exception as e:
                    # Erros não-transientes - não retry
                    logger.error("Erro não-transiente em %s: %s", func.__name__, e)
                    raise

            # Se todas tentativas falharam com erro transiente
            if last_exception:
                raise last_exception

            # Nunca deveria chegar aqui, mas satisfaz o type checker
            raise RuntimeError("Retry exausted without result")

        return wrapper

    return decorator


def _get_file_etag_path(dest_path: Path) -> Path:
    """Retorna o caminho do arquivo que armazena o ETag.

    Args:
        dest_path: Caminho do arquivo de destino

    Returns:
        Caminho do arquivo .etag
    """
    return dest_path.with_suffix(dest_path.suffix + ".etag")


def _load_cached_etag(dest_path: Path) -> Optional[str]:  # noqa: UP045
    """Carrega o ETag salvo em cache para um arquivo.

    Args:
        dest_path: Caminho do arquivo de destino

    Returns:
        ETag salvo ou None se não existir
    """
    etag_path = _get_file_etag_path(dest_path)
    if etag_path.exists():
        return etag_path.read_text().strip()
    return None


def _save_etag(dest_path: Path, etag: str) -> None:
    """Salva o ETag de um arquivo baixado.

    Args:
        dest_path: Caminho do arquivo de destino
        etag: ETag a ser salvo
    """
    etag_path = _get_file_etag_path(dest_path)
    etag_path.write_text(etag)


def _check_file_unchanged(
    url: str,
    dest_path: Path,
    timeout: int,
) -> tuple[bool, Optional[str]]:  # noqa: UP045
    """Verifica se o arquivo remoto foi alterado usando ETag ou Content-Length.

    Args:
        url: URL do arquivo remoto
        dest_path: Caminho do arquivo local
        timeout: Timeout para a requisição HEAD

    Returns:
        Tupla (arquivo_inalterado, etag_remoto)
    """
    if not dest_path.exists():
        return False, None

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        remote_etag = response.headers.get("ETag")
        remote_length = response.headers.get("Content-Length")

        # Verificar ETag primeiro (mais confiável)
        if remote_etag:
            cached_etag = _load_cached_etag(dest_path)
            if cached_etag and cached_etag == remote_etag:
                logger.debug("ETag match: %s", remote_etag)
                return True, remote_etag

        # Fallback para Content-Length
        if remote_length:
            local_size = dest_path.stat().st_size
            if str(local_size) == remote_length:
                logger.debug("Content-Length match: %s bytes", remote_length)
                return True, remote_etag

        return False, remote_etag

    except requests.exceptions.RequestException as e:
        logger.warning("Não foi possível verificar cache: %s", e)
        return False, None


@retry_with_backoff(max_retries=MAX_RETRIES, initial_wait=INITIAL_WAIT)
def _download_file_internal(
    url: str,
    dest_path: Path,
    timeout: int,
) -> tuple[bool, Optional[str]]:  # noqa: UP045
    """Baixa um arquivo usando streaming.

    Args:
        url: URL do arquivo
        dest_path: Caminho de destino
        timeout: Timeout da requisição

    Returns:
        Tupla (sucesso, etag)

    Raises:
        requests.exceptions.HTTPError: Se o servidor retornar erro HTTP
    """
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    # Garantir que o diretório pai existe
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Baixar em chunks para evitar carregar arquivo inteiro em memória
    with dest_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:  # Filtrar keep-alive chunks vazios
                f.write(chunk)

    etag = response.headers.get("ETag")
    return True, etag


def download_file(
    url: str,
    dest_path: Path,
    check_etag: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> DownloadResult:
    """Baixa arquivo com verificação de cache ETag e retry com backoff.

    Implementa download resiliente com:
    - Verificação de cache via ETag ou Content-Length (se check_etag=True)
    - Streaming em chunks de 8KB para arquivos grandes
    - Retry com backoff exponencial (2s, 4s, 8s) para erros transientes

    Args:
        url: URL do arquivo para download
        dest_path: Caminho de destino para salvar o arquivo
        check_etag: Se True, verifica ETag/Content-Length antes de baixar
        timeout: Timeout em segundos para a requisição (padrão: 300)

    Returns:
        DownloadResult com status do download

    Example:
        result = download_file(
            url="https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv",
            dest_path=Path("/tmp/deputados.csv")
        )
        if result.success:
            print(f"Baixado: {result.path}")
        elif result.skipped:
            print("Arquivo não mudou")
        else:
            print(f"Erro: {result.error}")
    """
    logger.info("Iniciando download: %s -> %s", url, dest_path)

    try:
        # Verificar cache se habilitado
        if check_etag:
            is_unchanged, _ = _check_file_unchanged(url, dest_path, timeout)
            if is_unchanged:
                logger.warning("Arquivo não alterado, pulando download: %s", dest_path)
                return DownloadResult(
                    success=True,
                    path=dest_path,
                    skipped=True,
                    error=None,
                )

        # Baixar arquivo
        success, etag = _download_file_internal(url, dest_path, timeout)

        if success:
            # Salvar ETag para verificação futura
            if etag:
                _save_etag(dest_path, etag)

            logger.info("Download concluído com sucesso: %s", dest_path)
            return DownloadResult(
                success=True,
                path=dest_path,
                skipped=False,
                error=None,
            )

        # Não deveria chegar aqui, mas por segurança
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error="Download falhou sem erro específico",
        )

    except requests.exceptions.HTTPError as e:
        error_msg = f"Erro HTTP: {e.response.status_code} - {e.response.reason}"
        logger.error("Falha no download de %s: %s", url, error_msg)
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
        )

    except (ConnectionError, TimeoutError, OSError, requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        error_msg = f"Erro de conexão após {MAX_RETRIES} tentativas: {e}"
        logger.error("Falha no download de %s: %s", url, error_msg)
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
        )

    except Exception as e:
        error_msg = f"Erro inesperado: {e}"
        logger.error("Falha no download de %s: %s", url, error_msg)
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
        )
