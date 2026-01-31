"""Testes unitários para src/shared/downloader.py.

Testa funcionalidades de download HTTP com cache ETag e retry.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.shared.downloader import (
    CHUNK_SIZE,
    DEFAULT_TIMEOUT,
    INITIAL_WAIT,
    MAX_RETRIES,
    DownloadResult,
    _check_file_unchanged,
    _get_file_etag_path,
    _load_cached_etag,
    _save_etag,
    download_file,
    retry_with_backoff,
)


class TestDownloadResultDataclass:
    """Testes para a dataclass DownloadResult."""

    def test_download_result_has_correct_fields(self):
        """Testa que DownloadResult tem os campos corretos."""
        result = DownloadResult(
            success=True,
            path=Path("/tmp/test.csv"),
            skipped=False,
            error=None,
        )
        assert result.success is True
        assert result.path == Path("/tmp/test.csv")
        assert result.skipped is False
        assert result.error is None

    def test_download_result_success_state(self):
        """Testa estado de sucesso."""
        result = DownloadResult(success=True, path=Path("/tmp/file.csv"), skipped=False, error=None)
        assert result.success
        assert result.path is not None
        assert not result.skipped
        assert result.error is None

    def test_download_result_skipped_state(self):
        """Testa estado de skip (arquivo não alterado)."""
        result = DownloadResult(success=True, path=Path("/tmp/file.csv"), skipped=True, error=None)
        assert result.success
        assert result.skipped

    def test_download_result_error_state(self):
        """Testa estado de erro."""
        result = DownloadResult(success=False, path=None, skipped=False, error="Connection failed")
        assert not result.success
        assert result.path is None
        assert not result.skipped
        assert result.error == "Connection failed"


class TestEtagHelpers:
    """Testes para funções auxiliares de ETag."""

    def test_get_file_etag_path(self, tmp_path):
        """Testa geração do caminho do arquivo .etag."""
        dest_path = tmp_path / "test.csv"
        etag_path = _get_file_etag_path(dest_path)
        assert etag_path == tmp_path / "test.csv.etag"

    def test_save_and_load_etag(self, tmp_path):
        """Testa salvar e carregar ETag."""
        dest_path = tmp_path / "test.csv"
        etag = '"abc123"'

        _save_etag(dest_path, etag)
        loaded_etag = _load_cached_etag(dest_path)

        assert loaded_etag == etag

    def test_load_cached_etag_returns_none_if_not_exists(self, tmp_path):
        """Testa que _load_cached_etag retorna None se arquivo não existe."""
        dest_path = tmp_path / "nonexistent.csv"
        assert _load_cached_etag(dest_path) is None


class TestCheckFileUnchanged:
    """Testes para verificação de arquivo inalterado."""

    def test_returns_false_if_local_file_not_exists(self, tmp_path):
        """Testa que retorna False se arquivo local não existe."""
        dest_path = tmp_path / "nonexistent.csv"
        with patch("src.shared.downloader.requests.head") as mock_head:
            is_unchanged, _ = _check_file_unchanged("http://example.com/file.csv", dest_path, timeout=30)
            assert is_unchanged is False
            mock_head.assert_not_called()

    @patch("src.shared.downloader.requests.head")
    def test_returns_true_if_etag_matches(self, mock_head, tmp_path):
        """Testa que retorna True se ETag remoto coincide com local."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("content")
        etag = '"abc123"'
        _save_etag(dest_path, etag)

        mock_response = MagicMock()
        mock_response.headers = {"ETag": etag}
        mock_head.return_value = mock_response

        is_unchanged, returned_etag = _check_file_unchanged("http://example.com/file.csv", dest_path, timeout=30)

        assert is_unchanged is True
        assert returned_etag == etag

    @patch("src.shared.downloader.requests.head")
    def test_returns_true_if_content_length_matches(self, mock_head, tmp_path):
        """Testa que retorna True se Content-Length coincide."""
        dest_path = tmp_path / "test.csv"
        content = "test content"
        dest_path.write_text(content)

        mock_response = MagicMock()
        mock_response.headers = {"Content-Length": str(len(content))}
        mock_head.return_value = mock_response

        is_unchanged, _ = _check_file_unchanged("http://example.com/file.csv", dest_path, timeout=30)

        assert is_unchanged is True

    @patch("src.shared.downloader.requests.head")
    def test_returns_false_if_etag_differs(self, mock_head, tmp_path):
        """Testa que retorna False se ETag remoto é diferente."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("content")
        _save_etag(dest_path, '"old_etag"')

        mock_response = MagicMock()
        mock_response.headers = {"ETag": '"new_etag"'}
        mock_head.return_value = mock_response

        is_unchanged, _ = _check_file_unchanged("http://example.com/file.csv", dest_path, timeout=30)

        assert is_unchanged is False

    @patch("src.shared.downloader.requests.head")
    def test_returns_false_on_request_exception(self, mock_head, tmp_path):
        """Testa que retorna False se requisição HEAD falhar."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("content")

        mock_head.side_effect = requests.exceptions.ConnectionError()

        is_unchanged, _ = _check_file_unchanged("http://example.com/file.csv", dest_path, timeout=30)

        assert is_unchanged is False


class TestRetryWithBackoff:
    """Testes para o decorator retry_with_backoff."""

    @patch("src.shared.downloader.time.sleep")
    def test_retries_on_connection_error(self, mock_sleep):
        """Testa que retry é executado em ConnectionError."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "success"

        result = failing_function()

        assert result == "success"
        assert call_count == 3
        assert mock_sleep.call_count == 2

    @patch("src.shared.downloader.time.sleep")
    def test_retries_on_timeout_error(self, mock_sleep):
        """Testa que retry é executado em TimeoutError."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Timeout")
            return "success"

        result = failing_function()

        assert result == "success"
        assert call_count == 2

    @patch("src.shared.downloader.time.sleep")
    def test_retries_on_os_error(self, mock_sleep):
        """Testa que retry é executado em OSError."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("OS Error")
            return "success"

        result = failing_function()

        assert result == "success"

    @patch("src.shared.downloader.time.sleep")
    def test_retries_on_requests_connection_error(self, mock_sleep):
        """Testa que retry é executado em requests.exceptions.ConnectionError."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.exceptions.ConnectionError("Connection failed")
            return "success"

        result = failing_function()

        assert result == "success"

    @patch("src.shared.downloader.time.sleep")
    def test_retries_on_requests_timeout(self, mock_sleep):
        """Testa que retry é executado em requests.exceptions.Timeout."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.exceptions.Timeout("Timeout")
            return "success"

        result = failing_function()

        assert result == "success"

    @patch("src.shared.downloader.time.sleep")
    def test_exponential_backoff_timing(self, mock_sleep):
        """Testa que backoff exponencial usa tempos 2s, 4s."""
        @retry_with_backoff(max_retries=3, initial_wait=2)
        def always_fails():
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_fails()

        # Deve ter dormido com 2s e 4s (2*2=4)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2)
        mock_sleep.assert_any_call(4)

    def test_does_not_retry_on_non_transient_errors(self):
        """Testa que NÃO retenta em erros não-transientes."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Validation error")

        with pytest.raises(ValueError):
            failing_function()

        assert call_count == 1  # Apenas uma tentativa

    @patch("src.shared.downloader.time.sleep")
    def test_respects_max_retries_limit(self, mock_sleep):
        """Testa que respeita limite de max_retries."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=1)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_fails()

        assert call_count == 3  # Exatamente 3 tentativas


class TestDownloadFile:
    """Testes para a função download_file."""

    @patch("src.shared.downloader._download_file_internal")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_returns_success_when_download_succeeds(self, mock_check, mock_download, tmp_path):
        """Testa que retorna success=True quando download bem-sucedido."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)  # Arquivo mudou
        mock_download.return_value = (True, '"new_etag"')

        result = download_file("http://example.com/file.csv", dest_path)

        assert result.success is True
        assert result.path == dest_path
        assert result.skipped is False
        assert result.error is None

    @patch("src.shared.downloader._check_file_unchanged")
    def test_returns_skipped_when_etag_matches(self, mock_check, tmp_path):
        """Testa que retorna skipped=True quando ETag coincide."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("existing content")
        mock_check.return_value = (True, '"same_etag"')  # Arquivo não mudou

        result = download_file("http://example.com/file.csv", dest_path)

        assert result.success is True
        assert result.skipped is True

    @patch("src.shared.downloader._check_file_unchanged")
    def test_returns_skipped_when_content_length_matches(self, mock_check, tmp_path):
        """Testa que retorna skipped=True quando Content-Length coincide."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("existing content")
        mock_check.return_value = (True, None)  # Arquivo não mudou (via Content-Length)

        result = download_file("http://example.com/file.csv", dest_path, check_etag=True)

        assert result.success is True
        assert result.skipped is True

    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_streams_large_files_in_chunks(self, mock_check, mock_get, tmp_path):
        """Testa que arquivos são baixados em chunks de 8KB."""
        dest_path = tmp_path / "large.csv"
        mock_check.return_value = (False, None)

        # Simular resposta com chunks
        chunk_data = b"x" * CHUNK_SIZE
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [chunk_data, chunk_data, b"remaining"]
        mock_response.headers = {"ETag": '"test"'}
        mock_get.return_value = mock_response

        result = download_file("http://example.com/large.csv", dest_path)

        assert result.success is True
        mock_response.iter_content.assert_called_with(chunk_size=CHUNK_SIZE)

    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_does_not_retry_on_http_404(self, mock_check, mock_get, tmp_path):
        """Testa que NÃO retenta em erro HTTP 404."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        result = download_file("http://example.com/notfound.csv", dest_path)

        assert result.success is False
        assert "404" in result.error
        assert mock_get.call_count == 1

    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_does_not_retry_on_http_403(self, mock_check, mock_get, tmp_path):
        """Testa que NÃO retenta em erro HTTP 403."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.reason = "Forbidden"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        result = download_file("http://example.com/forbidden.csv", dest_path)

        assert result.success is False
        assert "403" in result.error

    @patch("src.shared.downloader.time.sleep")
    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_returns_error_after_max_retries_exceeded(self, mock_check, mock_get, mock_sleep, tmp_path):
        """Testa que retorna success=False após exceder max_retries."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = download_file("http://example.com/file.csv", dest_path)

        assert result.success is False
        assert result.error is not None
        assert f"{MAX_RETRIES}" in result.error

    @patch("src.shared.downloader._download_file_internal")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_respects_timeout_parameter(self, mock_check, mock_download, tmp_path):
        """Testa que respeita parâmetro timeout."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)
        mock_download.return_value = (True, None)

        custom_timeout = 60
        download_file("http://example.com/file.csv", dest_path, timeout=custom_timeout)

        # Verificar que check_file_unchanged foi chamado com timeout correto
        mock_check.assert_called_once()
        # O timeout é passado como argumento posicional, não keyword
        assert mock_check.call_args[0][2] == custom_timeout

    @patch("src.shared.downloader._download_file_internal")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_skips_etag_check_when_disabled(self, mock_check, mock_download, tmp_path):
        """Testa que pula verificação ETag quando check_etag=False."""
        dest_path = tmp_path / "test.csv"
        mock_download.return_value = (True, None)

        download_file("http://example.com/file.csv", dest_path, check_etag=False)

        mock_check.assert_not_called()

    def test_default_timeout_is_300_seconds(self):
        """Testa que timeout padrão é 300 segundos."""
        assert DEFAULT_TIMEOUT == 300

    def test_default_max_retries_is_3(self):
        """Testa que max_retries padrão é 3."""
        assert MAX_RETRIES == 3

    def test_initial_wait_is_2_seconds(self):
        """Testa que initial_wait padrão é 2 segundos."""
        assert INITIAL_WAIT == 2


class TestDownloadFileLogging:
    """Testes para logging do download_file."""

    @patch("src.shared.downloader._download_file_internal")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_logs_info_on_success(self, mock_check, mock_download, tmp_path, caplog):
        """Testa que loga INFO no sucesso."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)
        mock_download.return_value = (True, None)

        with caplog.at_level(logging.INFO):
            download_file("http://example.com/file.csv", dest_path)

        assert "Download concluído com sucesso" in caplog.text

    @patch("src.shared.downloader._check_file_unchanged")
    def test_logs_warning_on_skip(self, mock_check, tmp_path, caplog):
        """Testa que loga WARNING quando arquivo é pulado."""
        dest_path = tmp_path / "test.csv"
        dest_path.write_text("content")
        mock_check.return_value = (True, '"etag"')

        with caplog.at_level(logging.WARNING):
            download_file("http://example.com/file.csv", dest_path)

        assert "pulando download" in caplog.text.lower() or "não alterado" in caplog.text.lower()

    @patch("src.shared.downloader.time.sleep")
    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_logs_error_on_failure(self, mock_check, mock_get, mock_sleep, tmp_path, caplog):
        """Testa que loga ERROR em caso de falha."""
        dest_path = tmp_path / "test.csv"
        mock_check.return_value = (False, None)
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with caplog.at_level(logging.ERROR):
            download_file("http://example.com/file.csv", dest_path)

        assert "falha" in caplog.text.lower() or "error" in caplog.text.lower()


class TestDownloadFileCreateDirectory:
    """Testes para criação de diretório de destino."""

    @patch("src.shared.downloader.requests.get")
    @patch("src.shared.downloader._check_file_unchanged")
    def test_creates_parent_directory_if_not_exists(self, mock_check, mock_get, tmp_path):
        """Testa que cria diretório pai se não existe."""
        dest_path = tmp_path / "subdir" / "deep" / "test.csv"
        mock_check.return_value = (False, None)

        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"content"]
        mock_response.headers = {}
        mock_get.return_value = mock_response

        result = download_file("http://example.com/file.csv", dest_path)

        assert result.success is True
        assert dest_path.parent.exists()
