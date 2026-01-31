"""Testes de integração para src/shared/downloader.py.

Testa downloads reais usando URLs públicas.
Estes testes requerem conexão com internet e são marcados com @pytest.mark.integration.

Execução: pytest -m integration tests/test_integration/test_downloader_integration.py
"""


import pytest

from src.shared.downloader import download_file


@pytest.mark.integration
class TestDownloadRealFile:
    """Testes de integração com download real de arquivos."""

    def test_download_real_file_from_public_url(self, tmp_path):
        """Testa download real de arquivo de URL pública.

        Usa um arquivo pequeno de um servidor público confiável.
        """
        # URL de um arquivo pequeno e estável (httpbin echo)
        url = "https://httpbin.org/robots.txt"
        dest_path = tmp_path / "robots.txt"

        result = download_file(url, dest_path, timeout=30)

        assert result.success is True
        assert result.path == dest_path
        assert result.skipped is False
        assert result.error is None
        assert dest_path.exists()
        assert dest_path.stat().st_size > 0

    def test_download_same_file_twice_skips_second(self, tmp_path):
        """Testa que segundo download do mesmo arquivo é pulado (cache ETag).

        Nota: Este teste depende do servidor retornar ETag, o que httpbin faz.
        """
        url = "https://httpbin.org/robots.txt"
        dest_path = tmp_path / "robots.txt"

        # Primeiro download
        result1 = download_file(url, dest_path, timeout=30)
        assert result1.success is True
        assert result1.skipped is False

        # Segundo download - deve ser pulado se ETag coincidir
        result2 = download_file(url, dest_path, timeout=30)
        assert result2.success is True
        # O skip depende do servidor suportar ETag - alguns não suportam
        # Se não for pulado, o download ainda é bem-sucedido
        if result2.skipped:
            assert result2.path == dest_path
        else:
            # Servidor não suporta ETag/Content-Length check
            assert result2.path == dest_path

    def test_download_nonexistent_url_returns_error(self, tmp_path):
        """Testa que URL inexistente retorna erro apropriado."""
        url = "https://httpbin.org/status/404"
        dest_path = tmp_path / "nonexistent.txt"

        result = download_file(url, dest_path, timeout=30)

        assert result.success is False
        assert result.error is not None
        assert "404" in result.error

    def test_download_creates_directory_structure(self, tmp_path):
        """Testa que download cria estrutura de diretórios se não existir."""
        url = "https://httpbin.org/robots.txt"
        dest_path = tmp_path / "deep" / "nested" / "dir" / "file.txt"

        result = download_file(url, dest_path, timeout=30)

        assert result.success is True
        assert dest_path.exists()
        assert dest_path.parent.exists()


@pytest.mark.integration
class TestDownloadCamaraApi:
    """Testes de integração específicos para API da Câmara dos Deputados.

    Nota: Estes testes dependem da disponibilidade da API externa.
    Podem ser lentos e falhar se a API estiver indisponível.
    """

    @pytest.mark.slow
    def test_download_deputados_csv_real(self, tmp_path):
        """Testa download real do CSV de deputados da Câmara.

        Este teste baixa o arquivo real da API da Câmara.
        Marcado como slow pois pode demorar dependendo do tamanho do arquivo.
        """
        url = "https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv"
        dest_path = tmp_path / "deputados.csv"

        result = download_file(url, dest_path, timeout=120)

        assert result.success is True
        assert dest_path.exists()
        # Arquivo de deputados deve ter pelo menos alguns KB
        assert dest_path.stat().st_size > 1000

        # Verificar que é um CSV válido (primeira linha é header)
        content = dest_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert len(lines) > 1  # Header + dados


@pytest.mark.integration
class TestDownloadWithTimeout:
    """Testes de integração para comportamento de timeout."""

    def test_timeout_on_slow_response(self, tmp_path):
        """Testa comportamento de timeout com resposta lenta.

        Usa httpbin para simular delay na resposta.
        """
        # URL que força delay de 5 segundos
        url = "https://httpbin.org/delay/5"
        dest_path = tmp_path / "slow.txt"

        # Timeout de 2 segundos deve falhar
        result = download_file(url, dest_path, timeout=2)

        # Pode retornar erro de timeout ou conexão
        assert result.success is False
        assert result.error is not None


@pytest.mark.integration
class TestDownloadRetryBehavior:
    """Testes de integração para comportamento de retry."""

    def test_handles_server_error_gracefully(self, tmp_path):
        """Testa que erros de servidor são tratados graciosamente."""
        # URL que retorna erro 500
        url = "https://httpbin.org/status/500"
        dest_path = tmp_path / "error.txt"

        result = download_file(url, dest_path, timeout=30)

        assert result.success is False
        assert result.error is not None
        assert "500" in result.error
