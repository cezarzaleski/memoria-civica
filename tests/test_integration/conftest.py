"""Fixtures pytest compartilhadas para testes de integração."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture que fornece o caminho para o diretório de fixtures."""
    return Path(__file__).parent.parent / "fixtures"
