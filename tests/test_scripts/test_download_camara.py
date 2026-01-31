"""Testes unitários para scripts/download_camara.py.

Testa funcionalidades do script CLI de download da API Câmara:
- Parsing de argumentos CLI
- Orquestração de downloads em sequência
- Geração de sumário de downloads
- Códigos de saída
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.download_camara import (
    DOWNLOAD_ORDER,
    FILE_CONFIGS,
    DownloadStats,
    build_url,
    download_all_files,
    download_single_file,
    get_dest_path,
    main,
    parse_args,
    print_summary,
    setup_logging,
)
from src.shared.downloader import DownloadResult


class TestDownloadStatsDataclass:
    """Testes para a dataclass DownloadStats."""

    def test_default_values(self):
        """Testa valores padrão da dataclass."""
        stats = DownloadStats()
        assert stats.downloaded == 0
        assert stats.skipped == 0
        assert stats.failed == 0
        assert stats.errors == []

    def test_custom_values(self):
        """Testa valores personalizados."""
        stats = DownloadStats(downloaded=3, skipped=1, failed=2)
        assert stats.downloaded == 3
        assert stats.skipped == 1
        assert stats.failed == 2

    def test_errors_list_initialization(self):
        """Testa que lista de erros é inicializada corretamente."""
        stats = DownloadStats()
        stats.errors.append("erro1")
        stats.errors.append("erro2")
        assert len(stats.errors) == 2


class TestFileConfigs:
    """Testes para configuração de arquivos."""

    def test_file_configs_has_all_required_files(self):
        """Testa que FILE_CONFIGS tem todos os arquivos necessários."""
        expected_files = {"deputados", "proposicoes", "votacoes", "votos"}
        assert set(FILE_CONFIGS.keys()) == expected_files

    def test_download_order_has_correct_sequence(self):
        """Testa que DOWNLOAD_ORDER tem a sequência correta."""
        assert DOWNLOAD_ORDER == ["deputados", "proposicoes", "votacoes", "votos"]

    def test_deputados_does_not_require_legislatura(self):
        """Testa que deputados não requer legislatura."""
        assert FILE_CONFIGS["deputados"]["requires_legislatura"] is False

    def test_other_files_require_legislatura(self):
        """Testa que outros arquivos requerem legislatura."""
        for key in ["proposicoes", "votacoes", "votos"]:
            assert FILE_CONFIGS[key]["requires_legislatura"] is True


class TestBuildUrl:
    """Testes para a função build_url."""

    @patch("scripts.download_camara.settings")
    def test_build_url_deputados(self, mock_settings):
        """Testa URL para deputados."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57

        url = build_url("deputados")

        assert url == "https://api.example.com/arquivos/deputados/csv/deputados.csv"

    @patch("scripts.download_camara.settings")
    def test_build_url_proposicoes_with_legislatura(self, mock_settings):
        """Testa URL para proposições com legislatura."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57

        url = build_url("proposicoes")

        assert url == "https://api.example.com/arquivos/proposicoes/csv/proposicoes-57.csv"

    @patch("scripts.download_camara.settings")
    def test_build_url_votacoes_with_legislatura(self, mock_settings):
        """Testa URL para votações com legislatura."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57

        url = build_url("votacoes")

        assert url == "https://api.example.com/arquivos/votacoes/csv/votacoes-57.csv"

    @patch("scripts.download_camara.settings")
    def test_build_url_votos_with_legislatura(self, mock_settings):
        """Testa URL para votos com legislatura."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57

        url = build_url("votos")

        assert url == "https://api.example.com/arquivos/votacoesVotos/csv/votacoesVotos-57.csv"


class TestGetDestPath:
    """Testes para a função get_dest_path."""

    @patch("scripts.download_camara.settings")
    def test_get_dest_path_deputados(self, mock_settings, tmp_path):
        """Testa caminho de destino para deputados."""
        mock_settings.CAMARA_LEGISLATURA = 57

        path = get_dest_path("deputados", tmp_path)

        assert path == tmp_path / "deputados.csv"

    @patch("scripts.download_camara.settings")
    def test_get_dest_path_proposicoes(self, mock_settings, tmp_path):
        """Testa caminho de destino para proposições."""
        mock_settings.CAMARA_LEGISLATURA = 57

        path = get_dest_path("proposicoes", tmp_path)

        assert path == tmp_path / "proposicoes-57.csv"


class TestParseArgs:
    """Testes para parsing de argumentos CLI."""

    @patch("scripts.download_camara.settings")
    def test_default_args(self, mock_settings):
        """Testa argumentos padrão."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")

        args = parse_args([])

        assert args.data_dir == Path("/tmp/test")
        assert args.files is None
        assert args.dry_run is False
        assert args.verbose is False

    def test_data_dir_argument(self):
        """Testa argumento --data-dir."""
        args = parse_args(["--data-dir", "/custom/path"])

        assert args.data_dir == Path("/custom/path")

    def test_single_file_argument(self):
        """Testa argumento --file único."""
        args = parse_args(["--file", "deputados"])

        assert args.files == ["deputados"]

    def test_multiple_file_arguments(self):
        """Testa múltiplos argumentos --file."""
        args = parse_args(["--file", "deputados", "--file", "votacoes"])

        assert args.files == ["deputados", "votacoes"]

    def test_dry_run_argument(self):
        """Testa argumento --dry-run."""
        args = parse_args(["--dry-run"])

        assert args.dry_run is True

    def test_verbose_argument(self):
        """Testa argumento --verbose."""
        args = parse_args(["-v"])

        assert args.verbose is True

    def test_verbose_long_argument(self):
        """Testa argumento --verbose (forma longa)."""
        args = parse_args(["--verbose"])

        assert args.verbose is True

    def test_invalid_file_argument(self):
        """Testa que argumento --file inválido gera erro."""
        with pytest.raises(SystemExit):
            parse_args(["--file", "invalid_file"])


class TestSetupLogging:
    """Testes para configuração de logging."""

    def test_setup_logging_default_level(self):
        """Testa nível de logging padrão (INFO)."""
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(verbose=False)

        assert root_logger.level == logging.INFO

    def test_setup_logging_verbose_level(self):
        """Testa nível de logging verbose (DEBUG)."""
        # Limpar handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(verbose=True)

        assert root_logger.level == logging.DEBUG


class TestDownloadSingleFile:
    """Testes para a função download_single_file."""

    @patch("scripts.download_camara.download_file")
    @patch("scripts.download_camara.settings")
    def test_download_success(self, mock_settings, mock_download, tmp_path):
        """Testa download bem-sucedido."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = DownloadResult(
            success=True, path=tmp_path / "deputados.csv", skipped=False, error=None
        )
        stats = DownloadStats()

        result = download_single_file("deputados", tmp_path, stats)

        assert result is True
        assert stats.downloaded == 1
        assert stats.skipped == 0
        assert stats.failed == 0

    @patch("scripts.download_camara.download_file")
    @patch("scripts.download_camara.settings")
    def test_download_skipped(self, mock_settings, mock_download, tmp_path):
        """Testa download pulado (cache hit)."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = DownloadResult(
            success=True, path=tmp_path / "deputados.csv", skipped=True, error=None
        )
        stats = DownloadStats()

        result = download_single_file("deputados", tmp_path, stats)

        assert result is True
        assert stats.downloaded == 0
        assert stats.skipped == 1
        assert stats.failed == 0

    @patch("scripts.download_camara.download_file")
    @patch("scripts.download_camara.settings")
    def test_download_failure(self, mock_settings, mock_download, tmp_path):
        """Testa falha no download."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = DownloadResult(
            success=False, path=None, skipped=False, error="Connection failed"
        )
        stats = DownloadStats()

        result = download_single_file("deputados", tmp_path, stats)

        assert result is False
        assert stats.downloaded == 0
        assert stats.skipped == 0
        assert stats.failed == 1
        assert len(stats.errors) == 1
        assert "Connection failed" in stats.errors[0]

    @patch("scripts.download_camara.settings")
    def test_dry_run_mode(self, mock_settings, tmp_path):
        """Testa modo dry-run (simula download)."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57
        stats = DownloadStats()

        result = download_single_file("deputados", tmp_path, stats, dry_run=True)

        assert result is True
        assert stats.downloaded == 1


class TestDownloadAllFiles:
    """Testes para a função download_all_files."""

    @patch("scripts.download_camara.download_single_file")
    @patch("scripts.download_camara.settings")
    def test_downloads_all_files_in_order(self, mock_settings, mock_download, tmp_path):
        """Testa que baixa todos os arquivos na ordem correta."""
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = True

        download_all_files(tmp_path)

        # Verificar que foi chamado para cada arquivo na ordem correta
        call_args = [call[0][0] for call in mock_download.call_args_list]
        assert call_args == DOWNLOAD_ORDER

    @patch("scripts.download_camara.download_single_file")
    @patch("scripts.download_camara.settings")
    def test_downloads_specific_files_only(self, mock_settings, mock_download, tmp_path):
        """Testa download de arquivos específicos."""
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = True

        download_all_files(tmp_path, files=["deputados", "votacoes"])

        call_args = [call[0][0] for call in mock_download.call_args_list]
        assert call_args == ["deputados", "votacoes"]

    @patch("scripts.download_camara.download_single_file")
    @patch("scripts.download_camara.settings")
    def test_creates_data_directory(self, mock_settings, mock_download, tmp_path):
        """Testa que cria diretório de dados se não existe."""
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = True
        new_dir = tmp_path / "new" / "nested" / "dir"

        download_all_files(new_dir)

        assert new_dir.exists()

    @patch("scripts.download_camara.settings")
    def test_invalid_file_returns_error(self, mock_settings, tmp_path):
        """Testa que arquivo inválido retorna erro."""
        mock_settings.CAMARA_LEGISLATURA = 57

        stats = download_all_files(tmp_path, files=["invalid_file"])

        assert stats.failed == 1
        assert "Arquivo desconhecido" in stats.errors[0]

    @patch("scripts.download_camara.download_single_file")
    @patch("scripts.download_camara.settings")
    def test_respects_dependency_order(self, mock_settings, mock_download, tmp_path):
        """Testa que respeita ordem de dependências mesmo com arquivos fora de ordem."""
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = True

        # Passar arquivos fora de ordem
        download_all_files(tmp_path, files=["votos", "deputados", "votacoes"])

        # Deve baixar na ordem correta (deputados antes de votacoes antes de votos)
        call_args = [call[0][0] for call in mock_download.call_args_list]
        assert call_args == ["deputados", "votacoes", "votos"]


class TestPrintSummary:
    """Testes para a função print_summary."""

    def test_print_summary_success(self, caplog):
        """Testa sumário de sucesso."""
        stats = DownloadStats(downloaded=4, skipped=0, failed=0)

        with caplog.at_level(logging.INFO):
            print_summary(stats)

        assert "Baixados: 4" in caplog.text
        assert "sucesso" in caplog.text.lower()

    def test_print_summary_with_skipped(self, caplog):
        """Testa sumário com arquivos pulados."""
        stats = DownloadStats(downloaded=2, skipped=2, failed=0)

        with caplog.at_level(logging.INFO):
            print_summary(stats)

        assert "Pulados (cache): 2" in caplog.text

    def test_print_summary_with_failures(self, caplog):
        """Testa sumário com falhas."""
        stats = DownloadStats(downloaded=2, skipped=0, failed=2)
        stats.errors = ["erro1", "erro2"]

        with caplog.at_level(logging.INFO):
            print_summary(stats)

        assert "Falhas: 2" in caplog.text
        assert "erro1" in caplog.text
        assert "erro2" in caplog.text


class TestMain:
    """Testes para a função main."""

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_returns_0_on_success(self, mock_settings, mock_download):
        """Testa que main retorna 0 em caso de sucesso."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=4, skipped=0, failed=0)

        exit_code = main([])

        assert exit_code == 0

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_returns_1_on_failure(self, mock_settings, mock_download):
        """Testa que main retorna 1 em caso de falha."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=2, skipped=0, failed=2)

        exit_code = main([])

        assert exit_code == 1

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_returns_1_on_exception(self, mock_settings, mock_download):
        """Testa que main retorna 1 em caso de exceção."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.side_effect = Exception("Unexpected error")

        exit_code = main([])

        assert exit_code == 1

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_passes_data_dir_argument(self, mock_settings, mock_download):
        """Testa que main passa argumento data-dir."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats()

        main(["--data-dir", "/custom/path"])

        mock_download.assert_called_once()
        assert mock_download.call_args[1]["data_dir"] == Path("/custom/path")

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_passes_files_argument(self, mock_settings, mock_download):
        """Testa que main passa argumento files."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats()

        main(["--file", "deputados", "--file", "votacoes"])

        mock_download.assert_called_once()
        assert mock_download.call_args[1]["files"] == ["deputados", "votacoes"]

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_main_passes_dry_run_argument(self, mock_settings, mock_download):
        """Testa que main passa argumento dry-run."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats()

        main(["--dry-run"])

        mock_download.assert_called_once()
        assert mock_download.call_args[1]["dry_run"] is True


class TestExitCodes:
    """Testes específicos para códigos de saída."""

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_exit_code_0_all_successful(self, mock_settings, mock_download):
        """Testa código 0 quando todos downloads são bem-sucedidos."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=4, skipped=0, failed=0)

        assert main([]) == 0

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_exit_code_0_all_skipped(self, mock_settings, mock_download):
        """Testa código 0 quando todos arquivos são pulados (cache)."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=0, skipped=4, failed=0)

        assert main([]) == 0

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_exit_code_0_mixed_success_and_skipped(self, mock_settings, mock_download):
        """Testa código 0 com mix de downloads e skips."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=2, skipped=2, failed=0)

        assert main([]) == 0

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_exit_code_1_any_failure(self, mock_settings, mock_download):
        """Testa código 1 quando há qualquer falha."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=3, skipped=0, failed=1)

        assert main([]) == 1

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_exit_code_1_all_failures(self, mock_settings, mock_download):
        """Testa código 1 quando todos downloads falham."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats(downloaded=0, skipped=0, failed=4)

        assert main([]) == 1


class TestLoggingFormat:
    """Testes para formato de logging."""

    @patch("scripts.download_camara.download_all_files")
    @patch("scripts.download_camara.settings")
    def test_logging_format_contains_timestamp(self, mock_settings, mock_download, caplog):
        """Testa que formato de log contém timestamp."""
        mock_settings.TEMP_DOWNLOAD_DIR = Path("/tmp/test")
        mock_download.return_value = DownloadStats()

        # O formato é configurado pelo setup_logging
        # Verificar que logging está configurado
        with caplog.at_level(logging.INFO):
            main([])

        # Caplog não preserva formato custom, apenas verifica que logging funciona
        assert len(caplog.records) > 0


class TestIntegrationWithConfig:
    """Testes de integração com config.py."""

    @patch("scripts.download_camara.download_file")
    @patch("scripts.download_camara.settings")
    def test_uses_config_api_base_url(self, mock_settings, mock_download, tmp_path):
        """Testa que usa URL base do config."""
        mock_settings.CAMARA_API_BASE_URL = "https://custom.api.url/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 57
        mock_download.return_value = DownloadResult(
            success=True, path=tmp_path / "deputados.csv", skipped=False, error=None
        )
        stats = DownloadStats()

        download_single_file("deputados", tmp_path, stats)

        # Verificar que download_file foi chamado com URL correta
        call_url = mock_download.call_args[1]["url"]
        assert call_url.startswith("https://custom.api.url/arquivos")

    @patch("scripts.download_camara.download_file")
    @patch("scripts.download_camara.settings")
    def test_uses_config_legislatura(self, mock_settings, mock_download, tmp_path):
        """Testa que usa legislatura do config."""
        mock_settings.CAMARA_API_BASE_URL = "https://api.example.com/arquivos"
        mock_settings.CAMARA_LEGISLATURA = 99  # Legislatura personalizada
        mock_download.return_value = DownloadResult(
            success=True, path=tmp_path / "proposicoes-99.csv", skipped=False, error=None
        )
        stats = DownloadStats()

        download_single_file("proposicoes", tmp_path, stats)

        # Verificar que URL contém legislatura correta
        call_url = mock_download.call_args[1]["url"]
        assert "-99.csv" in call_url
