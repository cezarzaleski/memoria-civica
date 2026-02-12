"""Fixtures pytest compartilhadas para testes de Votações."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.shared.database import Base
from src.votacoes.repository import VotacaoRepository, VotoRepository


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
    """Fixture que fornece uma sessão de banco de dados para cada teste.

    Garante cleanup automático entre testes (rollback).
    """
    session = temp_db()
    yield session
    session.close()


@pytest.fixture
def votacao_repository(db_session) -> VotacaoRepository:
    """Fixture que fornece um VotacaoRepository com banco in-memory."""
    return VotacaoRepository(db_session)


@pytest.fixture
def voto_repository(db_session) -> VotoRepository:
    """Fixture que fornece um VotoRepository com banco in-memory."""
    return VotoRepository(db_session)


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture que fornece o caminho para o diretório de fixtures."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def votacoes_csv_path(fixtures_dir) -> str:
    """Fixture que fornece o caminho para o CSV de votações."""
    return str(fixtures_dir / "votacoes.csv")


@pytest.fixture
def votos_csv_path(fixtures_dir) -> str:
    """Fixture que fornece o caminho para o CSV de votos."""
    return str(fixtures_dir / "votos.csv")
