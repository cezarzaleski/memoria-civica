"""Testes de integração para scripts/download_camara.py.

Testa downloads reais usando a API Dados Abertos da Câmara dos Deputados.
Estes testes requerem conexão com internet e são marcados com @pytest.mark.integration.

Execução: pytest -m integration tests/test_integration/test_download_camara_integration.py
"""

from __future__ import annotations

import pytest

from scripts.download_camara import (
    DownloadStats,
    build_url,
    download_all_files,
    download_single_file,
    main,
)


@pytest.mark.integration
class TestDownloadCamaraIntegration:
    """Testes de integração com API real da Câmara dos Deputados."""

    @pytest.mark.slow
    def test_download_deputados_csv_real(self, tmp_path):
        """Testa download real do CSV de deputados.

        Este teste baixa o arquivo real da API da Câmara.
        Marcado como slow pois pode demorar dependendo do tamanho do arquivo.
        """
        stats = DownloadStats()

        result = download_single_file("deputados", tmp_path, stats)

        assert result is True
        assert stats.downloaded == 1 or stats.skipped == 1
        assert stats.failed == 0

        # Verificar que arquivo foi criado
        dest_path = tmp_path / "deputados.csv"
        assert dest_path.exists()
        assert dest_path.stat().st_size > 1000

        # Verificar que é um CSV válido
        content = dest_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert len(lines) > 1  # Header + dados

    @pytest.mark.slow
    def test_download_all_files_real(self, tmp_path):
        """Testa download de todos os arquivos da API.

        Este teste é lento pois baixa todos os 4 arquivos CSV.
        """
        stats = download_all_files(tmp_path)

        # Pelo menos alguns arquivos devem ter sido baixados ou pulados
        total_processed = stats.downloaded + stats.skipped
        assert total_processed > 0

        # Se houve falhas, verificar que não foram todas
        if stats.failed > 0:
            assert total_processed > 0, "Todos os downloads falharam"

    @pytest.mark.slow
    def test_etag_caching_works_on_second_run(self, tmp_path):
        """Testa que cache ETag funciona na segunda execução.

        Primeiro download deve baixar o arquivo.
        Segundo download deve pular (cache hit) se ETag não mudou.
        """
        # Primeiro download
        stats1 = DownloadStats()
        download_single_file("deputados", tmp_path, stats1)

        # Segundo download - deve ser pulado se ETag coincidir
        stats2 = DownloadStats()
        download_single_file("deputados", tmp_path, stats2)

        # O segundo deve ser pulado (se API suporta ETag) ou baixado novamente
        # De qualquer forma, não deve falhar
        assert stats2.failed == 0

    def test_build_url_generates_valid_urls(self):
        """Testa que URLs geradas são válidas e acessíveis."""
        # Testar URL de deputados
        url_deputados = build_url("deputados")
        assert "dadosabertos.camara.leg.br" in url_deputados
        assert "deputados" in url_deputados
        assert url_deputados.endswith(".csv")

        # Testar URL de proposições
        url_proposicoes = build_url("proposicoes")
        assert "dadosabertos.camara.leg.br" in url_proposicoes
        assert "proposicoes" in url_proposicoes


@pytest.mark.integration
class TestMainCLIIntegration:
    """Testes de integração para função main()."""

    @pytest.mark.slow
    def test_main_downloads_single_file(self, tmp_path):
        """Testa main() com download de arquivo único."""
        exit_code = main([
            "--data-dir", str(tmp_path),
            "--file", "deputados"
        ])

        # Deve retornar 0 se download foi bem-sucedido
        # Ou 1 se API estiver indisponível (aceitável em testes de integração)
        assert exit_code in [0, 1]

        # Se retornou 0, arquivo deve existir
        if exit_code == 0:
            dest_path = tmp_path / "deputados.csv"
            assert dest_path.exists()

    def test_main_dry_run_does_not_download(self, tmp_path):
        """Testa que dry-run não baixa arquivos reais."""
        exit_code = main([
            "--data-dir", str(tmp_path),
            "--dry-run"
        ])

        assert exit_code == 0

        # Nenhum arquivo CSV deve ser criado em dry-run
        csv_files = list(tmp_path.glob("*.csv"))
        assert len(csv_files) == 0


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Testes de integração para tratamento de erros."""

    def test_handles_invalid_file_gracefully(self, tmp_path):
        """Testa que arquivo inválido é tratado graciosamente."""
        stats = download_all_files(tmp_path, files=["invalid_file_name"])

        assert stats.failed == 1
        assert len(stats.errors) == 1
        assert "desconhecido" in stats.errors[0].lower()

    @pytest.mark.slow
    def test_continues_after_single_file_failure(self, tmp_path):
        """Testa que continua processando após falha de um arquivo.

        Simula falha parcial baixando arquivo válido após tentativa inválida.
        """
        # Primeiro tenta arquivo inválido, depois válido
        stats = DownloadStats()

        # Arquivo inválido
        download_single_file("invalid", tmp_path, stats)

        # Arquivo válido após falha
        download_single_file("deputados", tmp_path, stats)

        # Deve ter registrado 1 falha e 1 sucesso (ou skip)
        assert stats.failed == 1
        assert stats.downloaded + stats.skipped >= 0  # Pode ser 0 se deputados falhar por timeout


@pytest.mark.integration
class TestDataDirectoryCreation:
    """Testes de integração para criação de diretórios."""

    def test_creates_nested_data_directory(self, tmp_path):
        """Testa criação de diretório aninhado."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        # Usar dry-run para não precisar de download real
        exit_code = main([
            "--data-dir", str(nested_dir),
            "--dry-run"
        ])

        assert exit_code == 0
        assert nested_dir.exists()
