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


# ---------------------------------------------------------------------------
# LLM Settings Defaults
# ---------------------------------------------------------------------------
class TestLLMSettingsDefaults:
    """Testes para valores padrão dos campos LLM no Settings."""

    def test_llm_enabled_defaults_to_false(self):
        """LLM_ENABLED é False por padrão."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_ENABLED is False

    def test_llm_api_key_defaults_to_none(self):
        """LLM_API_KEY é None por padrão."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_API_KEY is None

    def test_llm_model_defaults_to_gpt4o_mini(self):
        """LLM_MODEL é 'gpt-4o-mini' por padrão."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_MODEL == "gpt-4o-mini"

    def test_llm_batch_size_defaults_to_10(self):
        """LLM_BATCH_SIZE é 10 por padrão."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_BATCH_SIZE == 10

    def test_llm_confidence_threshold_defaults_to_0_5(self):
        """LLM_CONFIDENCE_THRESHOLD é 0.5 por padrão."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_CONFIDENCE_THRESHOLD == 0.5


# ---------------------------------------------------------------------------
# LLM Settings Override via Env
# ---------------------------------------------------------------------------
class TestLLMSettingsEnvOverride:
    """Testes para override de campos LLM via variáveis de ambiente."""

    def test_llm_enabled_override(self, monkeypatch):
        """LLM_ENABLED pode ser ativado via variável de ambiente."""
        monkeypatch.setenv("LLM_ENABLED", "true")
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_ENABLED is True

    def test_llm_api_key_override(self, monkeypatch):
        """LLM_API_KEY pode ser definida via variável de ambiente."""
        monkeypatch.setenv("LLM_API_KEY", "sk-test-12345")
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_API_KEY == "sk-test-12345"

    def test_llm_model_override(self, monkeypatch):
        """LLM_MODEL pode ser alterado via variável de ambiente."""
        monkeypatch.setenv("LLM_MODEL", "gpt-4o")
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_MODEL == "gpt-4o"

    def test_llm_batch_size_override(self, monkeypatch):
        """LLM_BATCH_SIZE pode ser alterado via variável de ambiente."""
        monkeypatch.setenv("LLM_BATCH_SIZE", "25")
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_BATCH_SIZE == 25

    def test_llm_confidence_threshold_override(self, monkeypatch):
        """LLM_CONFIDENCE_THRESHOLD pode ser alterado via variável de ambiente."""
        monkeypatch.setenv("LLM_CONFIDENCE_THRESHOLD", "0.7")
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LLM_CONFIDENCE_THRESHOLD == 0.7


# ---------------------------------------------------------------------------
# Existing settings not broken by LLM additions
# ---------------------------------------------------------------------------
class TestExistingSettingsNotBrokenByLLM:
    """Verifica que campos existentes continuam com valores padrão corretos após adição dos campos LLM."""

    def test_postgres_user_default_unchanged(self):
        """POSTGRES_USER mantém padrão original."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.POSTGRES_USER == "memoria"

    def test_log_level_default_unchanged(self):
        """LOG_LEVEL mantém padrão original."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.LOG_LEVEL == "INFO"

    def test_camara_legislatura_default_unchanged(self):
        """CAMARA_LEGISLATURA mantém padrão original."""
        s = Settings(POSTGRES_PASSWORD="test")
        assert s.CAMARA_LEGISLATURA == 57
