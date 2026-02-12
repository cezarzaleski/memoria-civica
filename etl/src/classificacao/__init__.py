"""Módulo de classificação cívica de proposições."""

from .engine import CategoriaMatch, ClassificadorCivico
from .patterns import CIVIC_PATTERNS

__all__ = ["CIVIC_PATTERNS", "CategoriaMatch", "ClassificadorCivico"]
