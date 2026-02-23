"""Fixtures pytest para testes de integração com PostgreSQL via testcontainers."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

# Importar models de todos os domínios para garantir que Base.metadata.create_all()
# consiga criar todas as tabelas necessárias
import src.classificacao.models
import src.deputados.models
import src.enriquecimento.models
import src.gastos.models
import src.proposicoes.models
import src.votacoes.models  # noqa: F401
from src.shared.database import Base


@pytest.fixture(scope="session")
def postgres_container():
    """Container PostgreSQL iniciado uma vez para toda a sessão de testes."""
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def pg_connection_url(postgres_container) -> str:
    """URL de conexão SQLAlchemy ao container PostgreSQL."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """Engine SQLAlchemy com schema completo, compartilhada na sessão de testes."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def temp_db(db_engine):
    """SessionFactory — mantém compatibilidade com testes que usam temp_db."""
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture
def db_session(db_engine):
    """Sessão com rollback automático para isolamento entre testes."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def fixtures_dir() -> Path:
    """Diretório de fixtures de testes."""
    return Path(__file__).parent.parent / "fixtures"
