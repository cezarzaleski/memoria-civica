"""Fixtures pytest compartilhadas para testes de Classificação."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar models com FK cruzada para garantir que Base.metadata.create_all()
# consiga criar todas as tabelas necessárias (proposicoes, deputados, votacoes)
import src.deputados.models
import src.proposicoes.models
import src.votacoes.models  # noqa: F401
from src.classificacao.repository import CategoriaCivicaRepository, ProposicaoCategoriaRepository
from src.shared.database import Base


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes.

    Cria o schema das tabelas automaticamente.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield SessionLocal
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(temp_db):
    """Fixture que fornece uma sessão de banco de dados para cada teste."""
    session = temp_db()
    yield session
    session.close()


@pytest.fixture
def categoria_civica_repository(db_session) -> CategoriaCivicaRepository:
    """Fixture que fornece um CategoriaCivicaRepository com banco in-memory."""
    return CategoriaCivicaRepository(db_session)


@pytest.fixture
def proposicao_categoria_repository(db_session) -> ProposicaoCategoriaRepository:
    """Fixture que fornece um ProposicaoCategoriaRepository com banco in-memory."""
    return ProposicaoCategoriaRepository(db_session)
