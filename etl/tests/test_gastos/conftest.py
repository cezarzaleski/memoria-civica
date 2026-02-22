"""Fixtures pytest compartilhadas para testes de Gastos."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa models com FK para garantir criação correta do schema em memória
import src.deputados.models
import src.gastos.models  # noqa: F401
from src.gastos.repository import GastoRepository
from src.shared.database import Base


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield session_local

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(temp_db):
    """Fixture que fornece uma sessão de banco para cada teste."""
    session = temp_db()
    yield session
    session.close()


@pytest.fixture
def gasto_repository(db_session) -> GastoRepository:
    """Fixture que fornece um GastoRepository com banco in-memory."""
    return GastoRepository(db_session)
