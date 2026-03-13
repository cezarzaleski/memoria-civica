"""Testes unitários para src/enriquecimento/prompts.py.

Testa PROMPT_VERSION, SYSTEM_PROMPT e build_user_prompt.
"""

from src.enriquecimento.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt


# ---------------------------------------------------------------------------
# PROMPT_VERSION
# ---------------------------------------------------------------------------
class TestPromptVersion:
    """Testes para a constante PROMPT_VERSION."""

    def test_is_non_empty_string(self):
        """PROMPT_VERSION é uma string não vazia."""
        assert isinstance(PROMPT_VERSION, str)
        assert len(PROMPT_VERSION) > 0

    def test_max_10_characters(self):
        """PROMPT_VERSION respeita o limite de 10 caracteres (varchar(10))."""
        assert len(PROMPT_VERSION) <= 10


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT
# ---------------------------------------------------------------------------
class TestSystemPrompt:
    """Testes para o template SYSTEM_PROMPT."""

    def test_contains_portuguese_instruction(self):
        """System prompt instrui resposta em português brasileiro."""
        assert "português brasileiro" in SYSTEM_PROMPT.lower() or "português" in SYSTEM_PROMPT.lower()

    def test_contains_json_format_instruction(self):
        """System prompt instrui formato JSON."""
        assert "JSON" in SYSTEM_PROMPT or "json" in SYSTEM_PROMPT

    def test_contains_expected_fields(self):
        """System prompt menciona os campos esperados."""
        assert "headline" in SYSTEM_PROMPT
        assert "resumo_simples" in SYSTEM_PROMPT
        assert "impacto_cidadao" in SYSTEM_PROMPT
        assert "confianca" in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# build_user_prompt
# ---------------------------------------------------------------------------
class TestBuildUserPrompt:
    """Testes para a função build_user_prompt."""

    def test_formats_tipo_numero_ano(self):
        """User prompt contém tipo, número e ano formatados corretamente."""
        result = build_user_prompt("PL", 1234, 2024, "Ementa de teste")
        assert "PL 1234/2024" in result

    def test_contains_ementa(self):
        """User prompt contém a ementa fornecida."""
        ementa = "Altera disposições sobre o salário mínimo."
        result = build_user_prompt("PL", 1, 2024, ementa)
        assert ementa in result

    def test_includes_categorias_when_provided(self):
        """User prompt inclui categorias quando fornecidas."""
        result = build_user_prompt("PL", 1, 2024, "Ementa", categorias=["Saúde", "Educação"])
        assert "Saúde" in result
        assert "Educação" in result
        assert "Categorias já atribuídas" in result

    def test_omits_categorias_when_none(self):
        """User prompt omite seção de categorias quando None."""
        result = build_user_prompt("PL", 1, 2024, "Ementa", categorias=None)
        assert "Categorias já atribuídas" not in result

    def test_omits_categorias_when_empty_list(self):
        """User prompt omite seção de categorias quando lista vazia."""
        result = build_user_prompt("PL", 1, 2024, "Ementa", categorias=[])
        assert "Categorias já atribuídas" not in result

    def test_handles_empty_ementa(self):
        """User prompt lida com ementa vazia sem erro."""
        result = build_user_prompt("PL", 1, 2024, "")
        assert "PL 1/2024" in result
        assert "Ementa:" in result

    def test_returns_string(self):
        """build_user_prompt retorna uma string."""
        result = build_user_prompt("PEC", 99, 2023, "Ementa de PEC")
        assert isinstance(result, str)

    def test_contains_json_generation_instruction(self):
        """User prompt contém instrução para gerar JSON."""
        result = build_user_prompt("PL", 1, 2024, "Ementa")
        assert "JSON" in result or "json" in result
