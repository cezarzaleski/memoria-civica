"""Fixtures pytest compartilhadas para testes de Deputados."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.deputados.repository import DeputadoRepository
from src.shared.database import Base


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes.

    Cria o schema da tabela deputados automaticamente.
    Fornece um SessionLocal factory que pode criar sessões.
    """
    # Criar engine SQLite in-memory
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    # Criar SessionLocal factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield SessionLocal

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(temp_db):
    """Fixture que fornece uma sessão de banco de dados para cada teste.

    Garante cleanup automático entre testes (rollback).
    """
    session = temp_db()
    yield session
    session.close()


@pytest.fixture
def deputado_repository(db_session) -> DeputadoRepository:
    """Fixture que fornece um DeputadoRepository com banco in-memory."""
    return DeputadoRepository(db_session)


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture que fornece o caminho para o diretório de fixtures."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def deputados_csv_path(fixtures_dir) -> str:
    """Fixture que fornece o caminho para o CSV de deputados."""
    return str(fixtures_dir / "deputados.csv")
