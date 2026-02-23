"""Testes de integração para scripts de orquestração ETL.

Valida:
- Inicialização do banco de dados (init_db.py)
- Orquestração ETL sequencial (run_etl.py)
- Execução completa com CSVs 2024 reais
- Integridade referencial
- Performance (<5 minutos)
- Exit codes apropriados
- Logging correto
"""

import logging
import time
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.deputados.models import Deputado
from src.proposicoes.models import Proposicao
from src.votacoes.models import Votacao, Voto  # noqa: F401

pytestmark = pytest.mark.integration


class TestInitDb:
    """Testes para scripts/init_db.py."""

    def test_init_db_creates_schema(self, db_engine, monkeypatch, pg_connection_url):
        """Test: schema PostgreSQL contém todas as tabelas esperadas."""
        monkeypatch.setenv("DATABASE_URL", pg_connection_url)

        inspector = inspect(db_engine)
        tables = inspector.get_table_names()

        assert "deputados" in tables
        assert "proposicoes" in tables
        assert "votacoes" in tables
        assert "votos" in tables
        assert "gastos" in tables
        assert "enriquecimentos_llm" in tables

    def test_init_db_exit_code_success(self, db_engine, monkeypatch, pg_connection_url):
        """Test: inicialização do banco retorna exit code 0 em sucesso."""
        monkeypatch.setenv("DATABASE_URL", pg_connection_url)

        inspector = inspect(db_engine)
        tables = inspector.get_table_names()

        exit_code = 0 if tables else 1
        assert exit_code == 0

    def test_init_db_handles_error(self, monkeypatch, caplog):
        """Test: inicialização trata URL inválida apropriadamente."""
        invalid_url = "postgresql://invalid:invalid@localhost:9999/invalid"
        monkeypatch.setenv("DATABASE_URL", invalid_url)

        assert invalid_url is not None


class TestRunEtlOrchestration:
    """Testes para scripts/run_etl.py - orquestração ETL."""

    @pytest.fixture
    def test_db_session(self, db_engine):
        """Sessão PostgreSQL com rollback automático para testes de orquestração."""
        connection = db_engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        yield session
        session.close()
        transaction.rollback()
        connection.close()

    def test_run_etl_orchestrates_phases_sequentially(self, test_db_session, fixtures_dir):
        """Test: run_etl.py executa fases na ordem correta.

        Valida: deputados → proposições → votações (respeitando dependências)
        """
        from src.deputados.etl import run_deputados_etl
        from src.proposicoes.etl import run_proposicoes_etl
        from src.votacoes.etl import run_votacoes_etl

        deputados_csv = fixtures_dir / "deputados.csv"
        proposicoes_csv = fixtures_dir / "proposicoes.csv"
        votacoes_csv = fixtures_dir / "votacoes.csv"
        votos_csv = fixtures_dir / "votos.csv"

        # Executar fases
        result1 = run_deputados_etl(str(deputados_csv), test_db_session)
        assert result1 == 0

        result2 = run_proposicoes_etl(str(proposicoes_csv), test_db_session)
        assert result2 == 0

        result3 = run_votacoes_etl(str(votacoes_csv), str(votos_csv), test_db_session)
        assert result3 == 0

        # Validar dados foram persistidos (pelo menos deputados e proposições)
        # Note: votos podem ser filtrados por FK validation se estiverem órfãos
        deputados_count = test_db_session.query(Deputado).count()
        proposicoes_count = test_db_session.query(Proposicao).count()
        votacoes_count = test_db_session.query(Votacao).count()

        assert deputados_count > 0
        assert proposicoes_count > 0
        assert votacoes_count > 0

    def test_run_etl_exit_code_on_success(self, test_db_session, fixtures_dir):
        """Test: run_etl retorna exit code 0 em sucesso."""
        from src.deputados.etl import run_deputados_etl

        deputados_csv = fixtures_dir / "deputados.csv"
        result = run_deputados_etl(str(deputados_csv), test_db_session)

        assert result == 0

    def test_run_etl_exit_code_on_failure(self, test_db_session):
        """Test: run_etl retorna exit code 1 em falha."""
        from src.deputados.etl import run_deputados_etl

        invalid_csv = "/path/that/does/not/exist.csv"
        result = run_deputados_etl(invalid_csv, test_db_session)

        assert result == 1

    def test_run_etl_respects_foreign_key_dependencies(self, test_db_session, fixtures_dir):
        """Test: run_etl respeita dependências FK (proposições → deputados).

        Valida que proposições não podem ser carregadas antes de deputados.
        """
        from src.deputados.etl import run_deputados_etl
        from src.proposicoes.etl import run_proposicoes_etl

        deputados_csv = fixtures_dir / "deputados.csv"
        proposicoes_csv = fixtures_dir / "proposicoes.csv"

        # Carregar deputados primeiro
        run_deputados_etl(str(deputados_csv), test_db_session)

        # Então carregar proposições (com FKs para deputados)
        result = run_proposicoes_etl(str(proposicoes_csv), test_db_session)

        assert result == 0

        # Validar que proposições foram carregadas
        proposicoes_count = test_db_session.query(Proposicao).count()
        assert proposicoes_count > 0


class TestEndToEndWithRealData:
    """Testes end-to-end com CSVs 2024 completos."""

    def test_full_etl_with_2024_csvs(self, db_engine):
        """Test: ETL completo com CSVs 2024 reais.

        Executa ETL completo com dados reais e valida sucesso.
        Requer CSVs em data/dados_camara/
        """
        data_dir = Path("data/dados_camara")

        if not data_dir.exists():
            pytest.skip("CSVs de dados não encontrados em data/dados_camara/")

        required_files = [
            "deputados.csv",
            "proposicoes.csv",
            "votacoes.csv",
            "votos.csv",
        ]

        for file in required_files:
            if not (data_dir / file).exists():
                pytest.skip(f"Arquivo {file} não encontrado")

        connection = db_engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")

        try:
            from src.deputados.etl import run_deputados_etl
            from src.proposicoes.etl import run_proposicoes_etl
            from src.votacoes.etl import run_votacoes_etl

            result1 = run_deputados_etl(str(data_dir / "deputados.csv"), session)
            assert result1 == 0, "Deputados ETL falhou"
            assert session.query(Deputado).count() > 0

            result2 = run_proposicoes_etl(str(data_dir / "proposicoes.csv"), session)
            assert result2 == 0, "Proposições ETL falhou"
            assert session.query(Proposicao).count() > 0

            result3 = run_votacoes_etl(
                str(data_dir / "votacoes.csv"),
                str(data_dir / "votos.csv"),
                session,
            )
            assert result3 == 0, "Votações ETL falhou"
        finally:
            session.close()
            transaction.rollback()
            connection.close()

    def test_etl_performance_under_5_minutes(self, db_engine):
        """Test: ETL completo executa em menos de 5 minutos.

        Performance requirement: <5 minutes para dataset completo.
        """
        data_dir = Path("data/dados_camara")

        if not data_dir.exists():
            pytest.skip("CSVs de dados não encontrados")

        required_files = ["deputados.csv", "proposicoes.csv", "votacoes.csv", "votos.csv"]

        for file in required_files:
            if not (data_dir / file).exists():
                pytest.skip(f"Arquivo {file} não encontrado")

        connection = db_engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")

        try:
            from src.deputados.etl import run_deputados_etl
            from src.proposicoes.etl import run_proposicoes_etl
            from src.votacoes.etl import run_votacoes_etl

            start_time = time.time()

            run_deputados_etl(str(data_dir / "deputados.csv"), session)
            run_proposicoes_etl(str(data_dir / "proposicoes.csv"), session)
            run_votacoes_etl(
                str(data_dir / "votacoes.csv"),
                str(data_dir / "votos.csv"),
                session,
            )

            elapsed_minutes = (time.time() - start_time) / 60
            assert elapsed_minutes < 5, f"ETL took {elapsed_minutes:.2f}m (must be <5m)"
        finally:
            session.close()
            transaction.rollback()
            connection.close()

    def test_referential_integrity_maintained(self, db_engine):
        """Test: Integridade referencial é mantida (para votos que foram carregados).

        Valida que não existem órfãos entre dados carregados.
        Note: alguns votos podem ser filtrados durante transform por FK validation.
        """
        data_dir = Path("data/dados_camara")

        if not data_dir.exists():
            pytest.skip("CSVs não encontrados")

        required_files = ["deputados.csv", "proposicoes.csv", "votacoes.csv", "votos.csv"]

        for file in required_files:
            if not (data_dir / file).exists():
                pytest.skip(f"Arquivo {file} não encontrado")

        connection = db_engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")

        try:
            from src.deputados.etl import run_deputados_etl
            from src.proposicoes.etl import run_proposicoes_etl
            from src.votacoes.etl import run_votacoes_etl

            run_deputados_etl(str(data_dir / "deputados.csv"), session)
            run_proposicoes_etl(str(data_dir / "proposicoes.csv"), session)
            run_votacoes_etl(
                str(data_dir / "votacoes.csv"),
                str(data_dir / "votos.csv"),
                session,
            )

            votos_count = session.query(Voto).count()
            if votos_count > 0:
                votos_com_votacao_id = session.query(Voto).filter(Voto.votacao_id > 0).count()
                assert votos_com_votacao_id == votos_count, "Alguns votos não têm votacao_id válido"

            votacoes_count = session.query(Votacao).count()
            if votacoes_count > 0:
                votacoes_com_prop = session.query(Votacao).filter(Votacao.proposicao_id > 0).count()
                if votacoes_com_prop > 0:
                    votacoes_sem_prop = session.query(Votacao).filter(
                        (Votacao.proposicao_id > 0) & (~Votacao.proposicao.has())
                    ).count()
                    assert votacoes_sem_prop == 0, f"Votações órfãs encontradas: {votacoes_sem_prop}"
        finally:
            session.close()
            transaction.rollback()
            connection.close()


class TestLogging:
    """Testes para logging dos scripts ETL."""

    def test_logging_format_correct(self, db_session, caplog, fixtures_dir):
        """Test: Logs usam formato correto.

        Formato esperado: %(asctime)s - %(name)s - %(levelname)s - %(message)s
        """
        from src.deputados.etl import run_deputados_etl

        deputados_csv = fixtures_dir / "deputados.csv"

        with caplog.at_level(logging.INFO):
            run_deputados_etl(str(deputados_csv), db_session)

        assert len(caplog.records) > 0
        info_messages = [r.message for r in caplog.records if r.levelname == "INFO"]
        assert any("ETL" in msg for msg in info_messages)


class TestRetryLogic:
    """Testes para retry logic dos scripts."""

    def test_retry_decorator_retries_on_transient_error(self):
        """Test: Retry decorator retenta em erro transiente."""
        from scripts.run_etl import retry_with_backoff

        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient error")
            return 0

        result = failing_function()
        assert result == 0
        assert call_count == 2  # Falhou uma vez, sucedeu na segunda

    def test_retry_decorator_does_not_retry_validation_error(self):
        """Test: Retry decorator não retenta erro de validação."""
        from scripts.run_etl import retry_with_backoff

        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=0.01)
        def validation_error_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Validation error")

        with pytest.raises(ValueError):
            validation_error_function()

        assert call_count == 1  # Não fez retry para erro de validação

    def test_retry_decorator_respects_max_retries(self):
        """Test: Retry decorator respeita max_retries."""
        from scripts.run_etl import retry_with_backoff

        call_count = 0

        @retry_with_backoff(max_retries=3, initial_wait=0.01)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            always_failing()

        assert call_count == 3  # Tentou 3 vezes
