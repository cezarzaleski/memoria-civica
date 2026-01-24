"""Fixtures pytest compartilhadas para testes de Proposições."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.proposicoes.repository import ProposicaoRepository
from src.shared.database import Base


@pytest.fixture
def temp_db():
    """Fixture que fornece um banco de dados SQLite em memória para testes.

    Cria o schema das tabelas (deputados e proposicoes) automaticamente.
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
def proposicao_repository(db_session) -> ProposicaoRepository:
    """Fixture que fornece um ProposicaoRepository com banco in-memory."""
    return ProposicaoRepository(db_session)


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture que fornece o caminho para o diretório de fixtures."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def proposicoes_csv_path(fixtures_dir) -> str:
    """Fixture que fornece o caminho para o CSV de proposições."""
    return str(fixtures_dir / "proposicoes.csv")
