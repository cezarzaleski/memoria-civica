"""Testes para padrões regex de classificação cívica.

Validam que todos os padrões compilam corretamente e que a estrutura
do dicionário CIVIC_PATTERNS está consistente.
"""

import re

from src.classificacao.patterns import CIVIC_PATTERNS

EXPECTED_CATEGORIES = {
    "GASTOS_PUBLICOS",
    "TRIBUTACAO_AUMENTO",
    "TRIBUTACAO_ISENCAO",
    "BENEFICIOS_CATEGORIAS",
    "DIREITOS_SOCIAIS",
    "SEGURANCA_JUSTICA",
    "MEIO_AMBIENTE",
    "REGULACAO_ECONOMICA",
    "POLITICA_INSTITUCIONAL",
}


class TestCivicPatterns:
    """Testes para a estrutura e validade dos padrões regex."""

    def test_all_9_categories_present(self):
        """Test: CIVIC_PATTERNS contém exatamente as 9 categorias esperadas."""
        assert set(CIVIC_PATTERNS.keys()) == EXPECTED_CATEGORIES

    def test_all_categories_have_patterns(self):
        """Test: cada categoria tem pelo menos 1 padrão regex."""
        for codigo, patterns in CIVIC_PATTERNS.items():
            assert len(patterns) > 0, f"Categoria {codigo} não tem padrões"

    def test_all_patterns_compile_without_error(self):
        """Test: todos os padrões compilam como regex válido."""
        for codigo, patterns in CIVIC_PATTERNS.items():
            for pattern in patterns:
                try:
                    re.compile(pattern, re.IGNORECASE)
                except re.error as e:
                    raise AssertionError(f"Padrão inválido na categoria {codigo}: {pattern!r} — {e}") from e

    def test_patterns_are_strings(self):
        """Test: todos os valores são listas de strings."""
        for codigo, patterns in CIVIC_PATTERNS.items():
            assert isinstance(patterns, list), f"{codigo}: patterns deve ser lista"
            for p in patterns:
                assert isinstance(p, str), f"{codigo}: padrão deve ser string, got {type(p)}"

    def test_no_empty_patterns(self):
        """Test: nenhum padrão é string vazia."""
        for codigo, patterns in CIVIC_PATTERNS.items():
            for p in patterns:
                assert p.strip(), f"Categoria {codigo} tem padrão vazio"

    def test_patterns_are_case_insensitive_compatible(self):
        """Test: padrões funcionam com flag IGNORECASE."""
        for codigo, patterns in CIVIC_PATTERNS.items():
            for pattern in patterns:
                compiled = re.compile(pattern, re.IGNORECASE)
                assert compiled.flags & re.IGNORECASE, f"Padrão {pattern!r} em {codigo} não aceita IGNORECASE"
