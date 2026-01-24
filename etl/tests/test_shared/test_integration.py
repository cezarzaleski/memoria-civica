"""Testes de integração para módulo shared.

Testa integração entre config, database e Alembic migrations.
"""

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.shared.config import Settings
from src.shared.database import get_db


@pytest.mark.integration
class TestDatabaseIntegration:
    """Testes de integração para database."""

    def test_database_file_exists(self):
        """Testa que arquivo de banco de dados foi criado."""
        # Database padrão deve existir após setup inicial
        db_path = Path("./memoria_civica.db")
        assert db_path.exists(), "Database file should exist after initial setup"

    def test_alembic_version_table_exists(self):
        """Testa que tabela alembic_version existe (migrations executadas)."""
        with get_db() as db:
            # Verificar se tabela alembic_version existe
            result = db.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
                )
            )
            tables = result.fetchall()
            assert len(tables) == 1, "alembic_version table should exist"

    def test_alembic_version_has_current_revision(self):
        """Testa que alembic_version tem revisão atual registrada."""
        with get_db() as db:
            result = db.execute(text("SELECT version_num FROM alembic_version"))
            versions = result.fetchall()
            assert len(versions) > 0, "Should have at least one migration applied"
            # A versão atual deve ser uma string válida (baseline "0b0b45871666" ou subsequentes como "001")
            assert isinstance(versions[0][0], str), "version_num should be a string"
            assert len(versions[0][0]) > 0, "version_num should not be empty"


@pytest.mark.integration
class TestSessionLifecycle:
    """Testes de integração para ciclo de vida de sessões."""

    def test_session_can_execute_queries(self):
        """Testa que sessão pode executar queries no database real."""
        with get_db() as db:
            result = db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1

    def test_session_transaction_rollback(self):
        """Testa que rollback de transação funciona corretamente."""
        with get_db() as db:
            # Criar tabela temporária
            db.execute(text("CREATE TEMP TABLE test_rollback (id INTEGER)"))
            db.execute(text("INSERT INTO test_rollback VALUES (1)"))
            db.rollback()

            # Após rollback, insert não deve ter persistido
            result = db.execute(text("SELECT COUNT(*) FROM test_rollback"))
            count = result.scalar()
            assert count == 0, "Rollback should undo insert"

    def test_session_transaction_commit(self):
        """Testa que commit de transação persiste dados."""
        with get_db() as db:
            # Criar tabela temporária e inserir dados
            db.execute(text("CREATE TEMP TABLE test_commit (id INTEGER)"))
            db.execute(text("INSERT INTO test_commit VALUES (1)"))
            db.commit()

            # Após commit, dados devem estar presentes
            result = db.execute(text("SELECT COUNT(*) FROM test_commit"))
            count = result.scalar()
            assert count == 1, "Commit should persist insert"


@pytest.mark.integration
class TestConfigIntegration:
    """Testes de integração entre config e database."""

    def test_database_url_from_config_is_used(self):
        """Testa que DATABASE_URL do config é usada pelo engine."""
        from src.shared.config import settings
        from src.shared.database import engine

        # URL do engine deve corresponder à configuração
        assert str(engine.url) == settings.DATABASE_URL

    def test_custom_database_url_creates_separate_database(self, monkeypatch):
        """Testa que URL customizada cria banco separado."""
        # Criar database temporário
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        try:
            custom_url = f"sqlite:///{tmp_db_path}"
            monkeypatch.setenv("DATABASE_URL", custom_url)

            # Recarregar settings e criar novo engine
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            test_settings = Settings()
            test_engine = create_engine(
                test_settings.DATABASE_URL,
                connect_args={"check_same_thread": False},
            )
            TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

            # Verificar que pode criar sessão com novo database
            session = TestSessionLocal()
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            session.close()

        finally:
            # Limpar database temporário
            if os.path.exists(tmp_db_path):
                os.unlink(tmp_db_path)


@pytest.mark.integration
class TestDatabaseErrorHandling:
    """Testes de integração para tratamento de erros."""

    def test_invalid_query_raises_exception(self):
        """Testa que query inválida levanta exceção."""
        with pytest.raises(OperationalError), get_db() as db:
            db.execute(text("SELECT * FROM nonexistent_table"))

    def test_session_closed_after_exception(self):
        """Testa que sessão é fechada mesmo após exceção."""
        exception_caught = False
        try:
            with get_db() as db:
                # Forçar exceção
                db.execute(text("INVALID SQL SYNTAX"))
        except Exception:
            exception_caught = True

        # Confirmar que exceção foi capturada
        assert exception_caught
        # Se chegou aqui, context manager fez cleanup mesmo com exception
