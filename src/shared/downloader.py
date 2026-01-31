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
        file_size: Tamanho do arquivo em bytes (None se falhou ou skipped)
        etag: ETag do arquivo (None se não disponível)
        status_code: Código HTTP da resposta (None se falhou antes da requisição)
        retry_attempts: Número de tentativas de retry realizadas
    """

    success: bool
    path: Optional[Path]  # noqa: UP045
    skipped: bool
    error: Optional[str]  # noqa: UP045
    file_size: Optional[int] = None  # noqa: UP045
    etag: Optional[str] = None  # noqa: UP045
    status_code: Optional[int] = None  # noqa: UP045
    retry_attempts: int = 0


class RetryContext:
    """Contexto para rastrear informações de retry entre chamadas.

    Attributes:
        attempts: Número de tentativas realizadas (começa em 0)
    """

    def __init__(self) -> None:
        """Inicializa contexto de retry."""
        self.attempts: int = 0


# Contexto global para rastrear tentativas de retry
_retry_context: Optional[RetryContext] = None  # noqa: UP045


def get_retry_attempts() -> int:
    """Retorna o número de tentativas de retry da última operação.

    Returns:
        Número de tentativas (0 se nenhum retry ocorreu ou não há contexto)
    """
    return _retry_context.attempts if _retry_context else 0


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
            global _retry_context
            _retry_context = RetryContext()

            wait_time = initial_wait
            last_exception: Optional[Exception] = None  # noqa: UP045

            for attempt in range(max_retries):
                _retry_context.attempts = attempt
                try:
                    logger.debug("Tentativa %d/%d de %s", attempt + 1, max_retries, func.__name__)
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(
                            "Sucesso após %d tentativa(s) de retry em %s",
                            attempt,
                            func.__name__,
                        )
                    return result

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
                            "Erro transiente em %s: %s. Retry em %ds com backoff exponencial (tentativa %d/%d)",
                            func.__name__,
                            e,
                            wait_time,
                            attempt + 1,
                            max_retries,
                        )
                        time.sleep(wait_time)
                        wait_time *= 2  # Backoff exponencial
                    else:
                        logger.error(
                            "Erro transiente após %d tentativas em %s: %s",
                            max_retries,
                            func.__name__,
                            e,
                        )

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


@dataclass
class DownloadMetadata:
    """Metadados de uma operação de download.

    Attributes:
        success: Se o download foi bem-sucedido
        etag: ETag do arquivo (None se não disponível)
        status_code: Código HTTP da resposta
        file_size: Tamanho do arquivo em bytes
    """

    success: bool
    etag: Optional[str]  # noqa: UP045
    status_code: int
    file_size: int


@retry_with_backoff(max_retries=MAX_RETRIES, initial_wait=INITIAL_WAIT)
def _download_file_internal(
    url: str,
    dest_path: Path,
    timeout: int,
) -> DownloadMetadata:
    """Baixa um arquivo usando streaming.

    Args:
        url: URL do arquivo
        dest_path: Caminho de destino
        timeout: Timeout da requisição

    Returns:
        DownloadMetadata com informações do download

    Raises:
        requests.exceptions.HTTPError: Se o servidor retornar erro HTTP
    """
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    # Garantir que o diretório pai existe
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Baixar em chunks para evitar carregar arquivo inteiro em memória
    file_size = 0
    with dest_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:  # Filtrar keep-alive chunks vazios
                f.write(chunk)
                file_size += len(chunk)

    etag = response.headers.get("ETag")
    return DownloadMetadata(
        success=True,
        etag=etag,
        status_code=response.status_code,
        file_size=file_size,
    )


def _format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo em formato legível.

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
    - Logging estruturado com metadados (file size, ETag, status code, retry attempts)

    Args:
        url: URL do arquivo para download
        dest_path: Caminho de destino para salvar o arquivo
        check_etag: Se True, verifica ETag/Content-Length antes de baixar
        timeout: Timeout em segundos para a requisição (padrão: 300)

    Returns:
        DownloadResult com status do download e metadados

    Example:
        result = download_file(
            url="https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv",
            dest_path=Path("/tmp/deputados.csv")
        )
        if result.success:
            print(f"Baixado: {result.path} ({result.file_size} bytes)")
        elif result.skipped:
            print("Arquivo não mudou")
        else:
            print(f"Erro: {result.error}")
    """
    logger.info("Iniciando download: %s -> %s", url, dest_path)

    try:
        # Verificar cache se habilitado
        if check_etag:
            is_unchanged, cached_etag = _check_file_unchanged(url, dest_path, timeout)
            if is_unchanged:
                file_size = dest_path.stat().st_size if dest_path.exists() else None
                logger.warning(
                    "Arquivo não alterado, pulando download: %s (ETag: %s, tamanho: %s)",
                    dest_path,
                    cached_etag or "N/A",
                    _format_file_size(file_size) if file_size else "N/A",
                )
                return DownloadResult(
                    success=True,
                    path=dest_path,
                    skipped=True,
                    error=None,
                    file_size=file_size,
                    etag=cached_etag,
                    status_code=304,  # Not Modified (implícito)
                    retry_attempts=0,
                )

        # Baixar arquivo
        metadata = _download_file_internal(url, dest_path, timeout)
        retry_attempts = get_retry_attempts()

        if metadata.success:
            # Salvar ETag para verificação futura
            if metadata.etag:
                _save_etag(dest_path, metadata.etag)

            logger.info(
                "Download concluído com sucesso: %s (status: %d, tamanho: %s, ETag: %s, retries: %d)",
                dest_path,
                metadata.status_code,
                _format_file_size(metadata.file_size),
                metadata.etag or "N/A",
                retry_attempts,
            )
            return DownloadResult(
                success=True,
                path=dest_path,
                skipped=False,
                error=None,
                file_size=metadata.file_size,
                etag=metadata.etag,
                status_code=metadata.status_code,
                retry_attempts=retry_attempts,
            )

        # Não deveria chegar aqui, mas por segurança
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error="Download falhou sem erro específico",
            retry_attempts=retry_attempts,
        )

    except requests.exceptions.HTTPError as e:
        error_msg = f"Erro HTTP: {e.response.status_code} - {e.response.reason}"
        retry_attempts = get_retry_attempts()
        logger.error(
            "Falha no download de %s: %s (status: %d, retries: %d)",
            url,
            error_msg,
            e.response.status_code,
            retry_attempts,
        )
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
            status_code=e.response.status_code,
            retry_attempts=retry_attempts,
        )

    except (ConnectionError, TimeoutError, OSError, requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        retry_attempts = get_retry_attempts()
        error_msg = f"Erro de conexão após {retry_attempts + 1} tentativa(s): {e}"
        logger.error(
            "Falha no download de %s: %s (retries: %d)",
            url,
            error_msg,
            retry_attempts,
        )
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
            retry_attempts=retry_attempts,
        )

    except Exception as e:
        retry_attempts = get_retry_attempts()
        error_msg = f"Erro inesperado: {e}"
        logger.error(
            "Falha no download de %s: %s (retries: %d)",
            url,
            error_msg,
            retry_attempts,
        )
        return DownloadResult(
            success=False,
            path=None,
            skipped=False,
            error=error_msg,
            retry_attempts=retry_attempts,
        )
