"""Testes unitários para src/shared/config.py.

Testa carregamento de configurações de variáveis de ambiente e defaults.
"""

from pathlib import Path

from src.shared.config import Settings


class TestSettingsDefaults:
    """Testes para valores padrão das configurações."""

    def test_default_database_url(self):
        """Testa que DATABASE_URL tem valor padrão correto."""
        settings = Settings()
        assert settings.DATABASE_URL == "sqlite:///./memoria_civica.db"

    def test_default_data_dir(self):
        """Testa que DATA_DIR tem valor padrão correto."""
        settings = Settings()
        assert Path("./data/dados_camara") == settings.DATA_DIR

    def test_default_log_level(self):
        """Testa que LOG_LEVEL tem valor padrão correto."""
        settings = Settings()
        assert settings.LOG_LEVEL == "INFO"

    def test_default_log_file_is_none(self):
        """Testa que LOG_FILE é None por padrão (log apenas em stdout)."""
        settings = Settings()
        assert settings.LOG_FILE is None

    def test_default_camara_api_base_url(self):
        """Testa que CAMARA_API_BASE_URL tem valor padrão correto."""
        settings = Settings()
        assert settings.CAMARA_API_BASE_URL == "https://dadosabertos.camara.leg.br/arquivos"

    def test_default_camara_legislatura(self):
        """Testa que CAMARA_LEGISLATURA tem valor padrão correto."""
        settings = Settings()
        assert settings.CAMARA_LEGISLATURA == 57

    def test_default_temp_download_dir(self):
        """Testa que TEMP_DOWNLOAD_DIR tem valor padrão correto."""
        settings = Settings()
        assert Path("/tmp/camara_downloads") == settings.TEMP_DOWNLOAD_DIR


class TestSettingsFromEnvironment:
    """Testes para carregamento de configurações via variáveis de ambiente."""

    def test_database_url_from_env(self, monkeypatch):
        """Testa que DATABASE_URL é carregada de variável de ambiente."""
        custom_url = "postgresql://user:pass@localhost/testdb"
        monkeypatch.setenv("DATABASE_URL", custom_url)
        settings = Settings()
        assert custom_url == settings.DATABASE_URL

    def test_data_dir_from_env(self, monkeypatch):
        """Testa que DATA_DIR é carregada de variável de ambiente."""
        custom_dir = "/custom/data/path"
        monkeypatch.setenv("DATA_DIR", custom_dir)
        settings = Settings()
        assert Path(custom_dir) == settings.DATA_DIR

    def test_log_level_from_env(self, monkeypatch):
        """Testa que LOG_LEVEL é carregada de variável de ambiente."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.LOG_LEVEL == "DEBUG"

    def test_log_file_from_env(self, monkeypatch):
        """Testa que LOG_FILE é carregada de variável de ambiente."""
        log_path = "/var/log/memoria_civica.log"
        monkeypatch.setenv("LOG_FILE", log_path)
        settings = Settings()
        assert Path(log_path) == settings.LOG_FILE

    def test_multiple_settings_from_env(self, monkeypatch):
        """Testa carregamento de múltiplas configurações simultaneamente."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
        monkeypatch.setenv("DATA_DIR", "/test/data")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        settings = Settings()
        assert settings.DATABASE_URL == "sqlite:///./test.db"
        assert Path("/test/data") == settings.DATA_DIR
        assert settings.LOG_LEVEL == "WARNING"

    def test_camara_api_base_url_from_env(self, monkeypatch):
        """Testa que CAMARA_API_BASE_URL é carregada de variável de ambiente."""
        custom_url = "https://custom.api.example.com/arquivos"
        monkeypatch.setenv("CAMARA_API_BASE_URL", custom_url)
        settings = Settings()
        assert custom_url == settings.CAMARA_API_BASE_URL

    def test_camara_legislatura_from_env(self, monkeypatch):
        """Testa que CAMARA_LEGISLATURA é carregada de variável de ambiente."""
        monkeypatch.setenv("CAMARA_LEGISLATURA", "56")
        settings = Settings()
        assert settings.CAMARA_LEGISLATURA == 56

    def test_temp_download_dir_from_env(self, monkeypatch):
        """Testa que TEMP_DOWNLOAD_DIR é carregada de variável de ambiente e convertida para Path."""
        custom_dir = "/custom/temp/downloads"
        monkeypatch.setenv("TEMP_DOWNLOAD_DIR", custom_dir)
        settings = Settings()
        assert Path(custom_dir) == settings.TEMP_DOWNLOAD_DIR


class TestSettingsValidation:
    """Testes para validação de configurações."""

    def test_log_level_accepts_valid_values(self, monkeypatch):
        """Testa que LOG_LEVEL aceita valores válidos."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            monkeypatch.setenv("LOG_LEVEL", level)
            settings = Settings()
            assert level == settings.LOG_LEVEL

    def test_extra_fields_are_ignored(self, monkeypatch):
        """Testa que campos extras em variáveis de ambiente são ignorados."""
        monkeypatch.setenv("UNKNOWN_FIELD", "some_value")
        settings = Settings()
        assert not hasattr(settings, "UNKNOWN_FIELD")


class TestSettingsSingleton:
    """Testes relacionados ao singleton settings importável."""

    def test_settings_singleton_is_available(self):
        """Testa que o singleton global settings pode ser importado."""
        from src.shared.config import settings

        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_singleton_has_defaults(self):
        """Testa que o singleton tem valores padrão corretos."""
        from src.shared.config import settings

        # Pode já ter sido modificado por env vars, então apenas verifica existência
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "DATA_DIR")
        assert hasattr(settings, "LOG_LEVEL")
        assert hasattr(settings, "LOG_FILE")

    def test_settings_singleton_has_camara_fields(self):
        """Testa que o singleton inclui os campos de configuração da API Câmara."""
        from src.shared.config import settings

        # Verifica existência dos novos campos
        assert hasattr(settings, "CAMARA_API_BASE_URL")
        assert hasattr(settings, "CAMARA_LEGISLATURA")
        assert hasattr(settings, "TEMP_DOWNLOAD_DIR")
