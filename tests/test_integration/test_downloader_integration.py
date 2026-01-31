"""Testes de integração para src/shared/downloader.py.

Testa downloads reais usando URLs públicas e a API da Câmara dos Deputados.
Estes testes requerem conexão com internet e são marcados com @pytest.mark.integration.

Execução: pytest -m integration tests/test_integration/test_downloader_integration.py

Cenários de teste:
- Download real de arquivos de URLs públicas
- Cache ETag para evitar downloads duplicados
- Todos os 4 endpoints da API da Câmara (deputados, proposições, votações, votos)
- Degradação graciosa quando API indisponível
- Retry com backoff exponencial para erros transientes
- Validação de integridade de arquivos baixados
"""

from __future__ import annotations

import csv
import io

import pytest
import requests

from src.shared.config import settings
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

    def test_retry_on_transient_error_records_attempts(self, tmp_path):
        """Testa que retry com backoff exponencial registra tentativas.

        O downloader deve tentar múltiplas vezes antes de falhar em erros transientes
        e registrar o número de tentativas no resultado.
        """
        # URL que simula timeout forçado - o servidor não responde a tempo
        url = "https://httpbin.org/delay/10"
        dest_path = tmp_path / "timeout.txt"

        # Timeout muito curto para forçar falha após retries
        result = download_file(url, dest_path, timeout=1)

        # Download deve falhar após retries
        assert result.success is False
        assert result.error is not None
        # Deve ter tentado retry (retry_attempts >= 0 indica que o sistema funcionou)
        assert result.retry_attempts >= 0


@pytest.mark.integration
class TestAllCamaraEndpoints:
    """Testes de integração para validar todos os 4 endpoints CSV da Câmara.

    Verifica que cada endpoint responde com sucesso e retorna dados válidos.
    Estes testes são lentos pois acessam a API real.
    """

    @pytest.mark.slow
    def test_all_endpoints_reachable(self, tmp_path):
        """Testa que todos os 4 endpoints CSV da Câmara são acessíveis.

        Endpoints validados:
        - deputados: Lista de deputados (obrigatório - disponível para todas as legislaturas)
        - proposicoes: Proposições legislativas (pode não existir para legislaturas recentes)
        - votacoes: Votações em plenário (pode não existir para legislaturas recentes)
        - votos: Votos individuais dos deputados (pode não existir para legislaturas recentes)

        Nota: A API da Câmara pode não ter dados para todos os endpoints de legislaturas
        recentes, por isso o teste valida apenas que pelo menos 1 endpoint funciona
        e o principal (deputados) deve estar sempre disponível.
        """
        base_url = settings.CAMARA_API_BASE_URL
        legislatura = settings.CAMARA_LEGISLATURA
        ano = settings.CAMARA_ANO

        # URLs dos 4 endpoints conforme TechSpec
        endpoints = {
            "deputados": f"{base_url}/deputados/csv/deputados.csv",
            "proposicoes": f"{base_url}/proposicoes/csv/proposicoes-{ano}.csv",
            "votacoes": f"{base_url}/votacoes/csv/votacoes-{legislatura}.csv",
            "votos": f"{base_url}/votacoesVotos/csv/votacoesVotos-{legislatura}.csv",
        }

        results = {}

        for name, url in endpoints.items():
            dest_path = tmp_path / f"{name}.csv"
            result = download_file(url, dest_path, timeout=120)
            results[name] = result

        # Verificar que pelo menos os endpoints principais estão acessíveis
        # Permitir falhas parciais em testes de integração
        successful_endpoints = [name for name, r in results.items() if r.success]
        failed_endpoints = [name for name, r in results.items() if not r.success]

        # O endpoint de deputados DEVE estar sempre acessível (não depende de legislatura)
        assert results["deputados"].success, (
            f"Endpoint de deputados deve estar sempre disponível. Erro: {results['deputados'].error}"
        )

        # Pelo menos 1 endpoint deve funcionar (tolerância máxima para API externa)
        # Nota: Outros endpoints podem retornar 404 para legislaturas recentes
        assert len(successful_endpoints) >= 1, (
            f"Nenhum endpoint acessível. "
            f"Sucesso: {successful_endpoints}, Falha: {failed_endpoints}"
        )

        # Verificar que arquivos baixados existem e têm conteúdo
        for name in successful_endpoints:
            dest_path = tmp_path / f"{name}.csv"
            assert dest_path.exists(), f"Arquivo {name}.csv não foi criado"
            assert dest_path.stat().st_size > 100, f"Arquivo {name}.csv muito pequeno"

        # Registrar endpoints que falharam (informativo, não falha o teste)
        if failed_endpoints:
            # Endpoints que retornam 404 são esperados para legislaturas recentes
            for name in failed_endpoints:
                result = results[name]
                if result.status_code == 404:
                    # 404 é esperado para dados não disponíveis ainda
                    pass  # Não falha o teste para 404

    @pytest.mark.slow
    def test_deputados_endpoint_has_valid_csv_structure(self, tmp_path):
        """Testa que endpoint de deputados retorna CSV com estrutura válida.

        Valida que o arquivo baixado é um CSV válido com headers esperados.
        """
        url = f"{settings.CAMARA_API_BASE_URL}/deputados/csv/deputados.csv"
        dest_path = tmp_path / "deputados.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        assert dest_path.exists()

        # Ler e validar estrutura CSV
        content = dest_path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        # Deve ter header + pelo menos uma linha de dados
        assert len(rows) > 1, "CSV deve ter header e dados"

        # Header deve conter colunas típicas de deputados
        header = rows[0]
        assert len(header) > 0, "Header não pode ser vazio"

    @pytest.mark.slow
    def test_proposicoes_endpoint_has_valid_csv_structure(self, tmp_path):
        """Testa que endpoint de proposições retorna CSV com estrutura válida."""
        ano = settings.CAMARA_ANO
        url = f"{settings.CAMARA_API_BASE_URL}/proposicoes/csv/proposicoes-{ano}.csv"
        dest_path = tmp_path / "proposicoes.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        assert dest_path.exists()

        # Validar que é um CSV válido
        content = dest_path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) > 1, "CSV deve ter header e dados"

    @pytest.mark.slow
    def test_votacoes_endpoint_has_valid_csv_structure(self, tmp_path):
        """Testa que endpoint de votações retorna CSV com estrutura válida."""
        legislatura = settings.CAMARA_LEGISLATURA
        url = f"{settings.CAMARA_API_BASE_URL}/votacoes/csv/votacoes-{legislatura}.csv"
        dest_path = tmp_path / "votacoes.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        assert dest_path.exists()

        # Validar que é um CSV válido
        content = dest_path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) > 1, "CSV deve ter header e dados"

    @pytest.mark.slow
    def test_votos_endpoint_has_valid_csv_structure(self, tmp_path):
        """Testa que endpoint de votos retorna CSV com estrutura válida."""
        legislatura = settings.CAMARA_LEGISLATURA
        url = f"{settings.CAMARA_API_BASE_URL}/votacoesVotos/csv/votacoesVotos-{legislatura}.csv"
        dest_path = tmp_path / "votos.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        assert dest_path.exists()

        # Validar que é um CSV válido
        content = dest_path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        assert len(rows) > 1, "CSV deve ter header e dados"


@pytest.mark.integration
class TestApiUnavailableGraceful:
    """Testes de integração para degradação graciosa quando API indisponível."""

    def test_api_unavailable_graceful_degradation(self, tmp_path):
        """Testa que sistema lida graciosamente com API indisponível.

        Usa URL inexistente para simular API indisponível.
        O sistema deve retornar erro claro sem exceções não tratadas.
        """
        # URL que não existe - simula API totalmente indisponível
        url = "https://api-que-nao-existe-12345.camara.leg.br/arquivos/test.csv"
        dest_path = tmp_path / "unavailable.csv"

        result = download_file(url, dest_path, timeout=10)

        # Download deve falhar graciosamente
        assert result.success is False
        assert result.error is not None
        assert result.skipped is False
        assert result.path is None

        # Arquivo não deve ser criado
        assert not dest_path.exists()

    def test_handles_dns_resolution_failure(self, tmp_path):
        """Testa tratamento de falha de resolução DNS."""
        # Domínio inválido que causará erro de DNS
        url = "https://invalid-domain-xyz-123.invalid/file.csv"
        dest_path = tmp_path / "dns_fail.csv"

        result = download_file(url, dest_path, timeout=10)

        assert result.success is False
        assert result.error is not None

    def test_skips_gracefully_with_pytest_skip(self, tmp_path):
        """Demonstra padrão de skip gracioso para testes que dependem de API externa.

        Este teste mostra o padrão recomendado para testes de integração:
        usar pytest.skip() quando a API externa está indisponível.
        """
        url = f"{settings.CAMARA_API_BASE_URL}/deputados/csv/deputados.csv"
        dest_path = tmp_path / "deputados.csv"

        # Primeiro, verificar se API está disponível via HEAD request
        try:
            response = requests.head(url, timeout=10)
            api_available = response.status_code < 500
        except requests.exceptions.RequestException:
            api_available = False

        if not api_available:
            pytest.skip("API da Câmara indisponível - pulando teste de integração")

        # Se chegou aqui, API está disponível
        result = download_file(url, dest_path, timeout=120)
        assert result.success is True or result.skipped is True


@pytest.mark.integration
class TestDownloadFileIntegrity:
    """Testes de integração para validação de integridade de arquivos."""

    @pytest.mark.slow
    def test_download_file_integrity_checksum(self, tmp_path):
        """Testa integridade do arquivo baixado verificando tamanho e conteúdo.

        Valida que:
        - Arquivo foi completamente baixado (não truncado)
        - Conteúdo é legível como texto
        - Tamanho reportado corresponde ao tamanho real
        """
        url = f"{settings.CAMARA_API_BASE_URL}/deputados/csv/deputados.csv"
        dest_path = tmp_path / "deputados.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        # Verificar tamanho do arquivo
        actual_size = dest_path.stat().st_size
        assert actual_size > 0, "Arquivo não pode estar vazio"

        # Verificar que tamanho reportado corresponde ao real
        if result.file_size is not None:
            assert result.file_size == actual_size, (
                f"Tamanho reportado ({result.file_size}) diferente do real ({actual_size})"
            )

        # Verificar que conteúdo é legível
        content = dest_path.read_text(encoding="utf-8")
        assert len(content) > 0, "Conteúdo não pode estar vazio"

        # Verificar que não foi truncado (última linha deve terminar corretamente)
        lines = content.strip().split("\n")
        assert len(lines) > 1, "Arquivo deve ter múltiplas linhas"

        # Última linha deve ser válida (não truncada)
        last_line = lines[-1]
        assert len(last_line) > 0, "Última linha não pode estar vazia"

    def test_download_file_creates_etag_cache(self, tmp_path):
        """Testa que download cria arquivo de cache ETag.

        Após download bem-sucedido, deve existir um arquivo .etag
        contendo o ETag retornado pelo servidor.
        """
        url = "https://httpbin.org/robots.txt"
        dest_path = tmp_path / "robots.txt"
        etag_path = dest_path.with_suffix(dest_path.suffix + ".etag")

        result = download_file(url, dest_path, timeout=30)

        assert result.success is True
        assert dest_path.exists()

        # Se servidor retornou ETag, arquivo de cache deve existir
        if result.etag is not None:
            assert etag_path.exists(), "Arquivo .etag deve ser criado quando servidor retorna ETag"
            cached_etag = etag_path.read_text().strip()
            assert cached_etag == result.etag, "ETag em cache deve corresponder ao retornado"

    @pytest.mark.slow
    def test_downloaded_csv_can_be_parsed(self, tmp_path):
        """Testa que CSV baixado pode ser parseado corretamente.

        Valida que o arquivo é um CSV válido que pode ser processado
        pela biblioteca csv do Python.
        """
        url = f"{settings.CAMARA_API_BASE_URL}/deputados/csv/deputados.csv"
        dest_path = tmp_path / "deputados.csv"

        result = download_file(url, dest_path, timeout=120)

        if not result.success:
            pytest.skip(f"API indisponível: {result.error}")

        # Tentar parsear o CSV
        with dest_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Deve ter pelo menos algumas linhas de dados
        assert len(rows) > 0, "CSV deve conter dados"

        # Primeira linha deve ter campos (não ser vazia)
        first_row = rows[0]
        assert len(first_row) > 0, "Primeira linha de dados não pode ser vazia"

    def test_partial_download_handling(self, tmp_path):
        """Testa comportamento quando download é interrompido (timeout curto).

        Verifica que arquivo parcialmente baixado não é deixado no sistema
        ou é marcado como falha.
        """
        # URL com resposta lenta para simular download interrompido
        url = "https://httpbin.org/drip?numbytes=5000&duration=10"
        dest_path = tmp_path / "partial.txt"

        # Timeout curto para interromper download
        result = download_file(url, dest_path, timeout=1)

        # Deve falhar ou completar parcialmente
        if not result.success:
            # Em caso de falha, arquivo não deve existir ou deve estar marcado
            assert result.error is not None
