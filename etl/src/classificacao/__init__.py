"""Módulo de classificação cívica de proposições."""

from .engine import CategoriaMatch, ClassificadorCivico
from .etl import run_classificacao_etl
from .patterns import CIVIC_PATTERNS

__all__ = ["CIVIC_PATTERNS", "CategoriaMatch", "ClassificadorCivico", "run_classificacao_etl"]
