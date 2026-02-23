"""Fixtures pytest compartilhadas para testes de integração."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar models de todos os domínios para garantir que Base.metadata.create_all()
# consiga criar todas as tabelas necessárias
import src.classificacao.models
import src.deputados.models
import src.enriquecimento.models
import src.gastos.models
import src.proposicoes.models
import src.votacoes.models  # noqa: F401
from src.shared.database import Base


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture que fornece o caminho para o diretório de fixtures."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes."""
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
