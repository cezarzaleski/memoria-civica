"""Fixtures pytest compartilhadas para testes de Enriquecimento LLM."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar todos os models que participam de FKs para que Base.metadata.create_all funcione
from src.classificacao.models import CategoriaCivica, ProposicaoCategoria  # noqa: F401
from src.deputados.models import Deputado  # noqa: F401
from src.enriquecimento.models import EnriquecimentoLLM  # noqa: F401
from src.proposicoes.models import Proposicao  # noqa: F401
from src.shared.database import Base


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes.

    Cria o schema das tabelas automaticamente.
    Fornece um SessionLocal factory que pode criar sessões.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield SessionLocal
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(temp_db):
    """Fixture que fornece uma sessão de banco de dados para cada teste.

    Garante cleanup automático entre testes.
    """
    session = temp_db()
    yield session
    session.close()
