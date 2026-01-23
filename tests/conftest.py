"""Pytest configuration and fixtures"""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory path"""
    return Path(__file__).parent / "fixtures"
