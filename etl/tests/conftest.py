"""Pytest configuration and fixtures"""

import sys
from pathlib import Path

import pytest

# Add etl/src to path so 'from src.*' imports work when running pytest from root
ETL_SRC_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(ETL_SRC_PATH))


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory path"""
    return Path(__file__).parent / "fixtures"
