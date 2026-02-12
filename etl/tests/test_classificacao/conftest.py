"""Fixtures pytest compartilhadas para testes de Classificação."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
