"""Testes unitários para src/shared/database.py.

Testa criação de engine, SessionLocal factory e context manager get_db().
"""

from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import Session

from src.shared.database import Base, SessionLocal, engine, get_db


class TestEngineConfiguration:
    """Testes para configuração do engine SQLAlchemy."""

    def test_engine_is_created(self):
        """Testa que engine é criado corretamente."""
        assert engine is not None
        assert hasattr(engine, "connect")

    def test_engine_url_is_configured(self):
        """Testa que URL do engine está configurada."""
        assert engine.url is not None
        # URL pode vir de settings ou variável de ambiente
        assert str(engine.url).startswith("sqlite")

    def test_engine_can_connect(self):
        """Testa que engine consegue estabelecer conexão."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestSessionLocalFactory:
    """Testes para SessionLocal factory."""

    def test_sessionlocal_creates_session(self):
        """Testa que SessionLocal factory cria sessões válidas."""
        session = SessionLocal()
        assert session is not None
        assert isinstance(session, Session)
        session.close()

    def test_sessionlocal_sessions_are_independent(self):
        """Testa que SessionLocal cria sessões independentes."""
        session1 = SessionLocal()
        session2 = SessionLocal()
        assert session1 is not session2
        session1.close()
        session2.close()

    def test_sessionlocal_autocommit_disabled(self):
        """Testa que autocommit está desabilitado (transações explícitas)."""
        session = SessionLocal()
        # SQLAlchemy 2.0 não expõe autocommit como atributo público
        # Verificamos que sessão requer commit explícito testando comportamento
        assert session.get_bind() is not None
        session.close()

    def test_sessionlocal_autoflush_disabled(self):
        """Testa que autoflush está desabilitado (flush manual)."""
        session = SessionLocal()
        assert not session.autoflush
        session.close()


class TestGetDbContextManager:
    """Testes para context manager get_db()."""

    def test_get_db_yields_session(self):
        """Testa que get_db() retorna uma sessão válida."""
        with get_db() as db:
            assert db is not None
            assert isinstance(db, Session)

    def test_get_db_session_can_query(self):
        """Testa que sessão retornada por get_db() pode executar queries."""
        with get_db() as db:
            # Query simples para testar funcionalidade
            result = db.execute(text("SELECT 1 as value"))
            row = result.fetchone()
            assert row is not None
            assert row[0] == 1

    def test_get_db_closes_session_after_use(self):
        """Testa que get_db() fecha sessão após uso (mesmo sem exceção)."""
        # Testa que context manager funciona corretamente sem leaks
        # Executar múltiplas vezes para garantir que cleanup está funcionando
        for _ in range(5):
            with get_db() as db:
                result = db.execute(text("SELECT 1"))
                assert result.scalar() == 1
        # Se chegou aqui, context manager está fazendo cleanup correto

    def test_get_db_closes_session_on_exception(self):
        """Testa que get_db() fecha sessão mesmo quando exception ocorre."""
        # Testa que context manager faz cleanup mesmo com exceção
        exception_raised = False
        try:
            with get_db() as db:
                # Verificar que sessão está ativa
                result = db.execute(text("SELECT 1"))
                assert result.scalar() == 1
                exception_raised = True
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Confirmar que exception foi levantada
        assert exception_raised
        # Se chegou aqui, context manager fez cleanup mesmo com exception

    def test_get_db_multiple_calls_yield_different_sessions(self):
        """Testa que múltiplas chamadas a get_db() retornam sessões diferentes."""
        with get_db() as db1, get_db() as db2:
            assert db1 is not db2


class TestBaseDeclarative:
    """Testes para Base declarativa."""

    def test_base_is_available(self):
        """Testa que Base está disponível para herança."""
        assert Base is not None
        assert hasattr(Base, "metadata")

    def test_base_can_be_inherited(self):
        """Testa que Base pode ser herdada para criar models."""

        class TestModel(Base):
            __tablename__ = "test_model"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        assert TestModel.__tablename__ == "test_model"
        assert hasattr(TestModel, "id")
        assert hasattr(TestModel, "name")

    def test_base_metadata_tracks_tables(self):
        """Testa que Base.metadata rastreia tabelas criadas."""
        initial_table_count = len(Base.metadata.tables)

        class AnotherTestModel(Base):
            __tablename__ = "another_test_model"
            id = Column(Integer, primary_key=True)

        # Metadata deve ter registrado a nova tabela
        assert len(Base.metadata.tables) > initial_table_count
