"""Testes para schemas Pydantic do domínio de Enriquecimento LLM.

Validam a criação de instâncias de EnriquecimentoCreate e EnriquecimentoRead,
incluindo validação de constraints e campos opcionais.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.enriquecimento.schemas import EnriquecimentoCreate, EnriquecimentoRead


class TestEnriquecimentoCreate:
    """Testes para schema EnriquecimentoCreate."""

    def test_create_valid_with_all_fields(self):
        """Test: EnriquecimentoCreate aceita dados válidos com todos os campos."""
        enriquecimento = EnriquecimentoCreate(
            proposicao_id=123,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            headline="Nova lei facilita acesso à educação básica",
            resumo_simples="Esta proposição visa ampliar o acesso à educação.",
            impacto_cidadao=["Mais vagas em escolas públicas", "Redução de mensalidades"],
            confianca=0.85,
            tokens_input=150,
            tokens_output=200,
        )
        assert enriquecimento.proposicao_id == 123
        assert enriquecimento.modelo == "gpt-4o-mini"
        assert enriquecimento.versao_prompt == "v1.0"
        assert enriquecimento.headline == "Nova lei facilita acesso à educação básica"
        assert enriquecimento.resumo_simples == "Esta proposição visa ampliar o acesso à educação."
        assert enriquecimento.impacto_cidadao == ["Mais vagas em escolas públicas", "Redução de mensalidades"]
        assert enriquecimento.confianca == 0.85
        assert enriquecimento.tokens_input == 150
        assert enriquecimento.tokens_output == 200

    def test_create_valid_with_optional_fields_none(self):
        """Test: EnriquecimentoCreate aceita campos opcionais como None."""
        enriquecimento = EnriquecimentoCreate(
            proposicao_id=456,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=0.7,
        )
        assert enriquecimento.headline is None
        assert enriquecimento.resumo_simples is None
        assert enriquecimento.impacto_cidadao is None
        assert enriquecimento.tokens_input is None
        assert enriquecimento.tokens_output is None

    def test_create_validates_confianca_between_0_and_1(self):
        """Test: EnriquecimentoCreate valida confianca entre 0.0 e 1.0."""
        # Confianca acima de 1.0
        with pytest.raises(ValidationError):
            EnriquecimentoCreate(
                proposicao_id=1,
                modelo="gpt-4o-mini",
                versao_prompt="v1.0",
                confianca=1.5,
            )

        # Confianca abaixo de 0.0
        with pytest.raises(ValidationError):
            EnriquecimentoCreate(
                proposicao_id=1,
                modelo="gpt-4o-mini",
                versao_prompt="v1.0",
                confianca=-0.1,
            )

    def test_create_accepts_confianca_boundaries(self):
        """Test: EnriquecimentoCreate aceita confianca nos limites (0.0 e 1.0)."""
        zero = EnriquecimentoCreate(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=0.0,
        )
        assert zero.confianca == 0.0

        one = EnriquecimentoCreate(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=1.0,
        )
        assert one.confianca == 1.0

    def test_create_validates_impacto_cidadao_is_list_of_strings(self):
        """Test: EnriquecimentoCreate valida impacto_cidadao como lista de strings."""
        enriquecimento = EnriquecimentoCreate(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            impacto_cidadao=["Impacto 1", "Impacto 2"],
        )
        assert enriquecimento.impacto_cidadao == ["Impacto 1", "Impacto 2"]

    def test_create_accepts_empty_impacto_cidadao_list(self):
        """Test: EnriquecimentoCreate aceita lista vazia de impactos."""
        enriquecimento = EnriquecimentoCreate(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            impacto_cidadao=[],
        )
        assert enriquecimento.impacto_cidadao == []

    def test_create_rejects_missing_required_fields(self):
        """Test: EnriquecimentoCreate rejeita quando faltam campos obrigatórios."""
        # Falta proposicao_id
        with pytest.raises(ValidationError):
            EnriquecimentoCreate(
                modelo="gpt-4o-mini",
                versao_prompt="v1.0",
            )

        # Falta modelo
        with pytest.raises(ValidationError):
            EnriquecimentoCreate(
                proposicao_id=1,
                versao_prompt="v1.0",
            )

        # Falta versao_prompt
        with pytest.raises(ValidationError):
            EnriquecimentoCreate(
                proposicao_id=1,
                modelo="gpt-4o-mini",
            )

    def test_create_default_confianca(self):
        """Test: EnriquecimentoCreate usa default 1.0 para confianca."""
        enriquecimento = EnriquecimentoCreate(
            proposicao_id=1,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
        )
        assert enriquecimento.confianca == 1.0


class TestEnriquecimentoRead:
    """Testes para schema EnriquecimentoRead."""

    def test_read_valid_with_all_fields(self):
        """Test: EnriquecimentoRead aceita dados válidos com todos os campos."""
        now = datetime.utcnow()
        enriquecimento = EnriquecimentoRead(
            id=1,
            proposicao_id=123,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            headline="Nova lei de educação",
            resumo_simples="Resumo da proposição.",
            impacto_cidadao=["Impacto 1"],
            confianca=0.9,
            necessita_revisao=False,
            tokens_input=100,
            tokens_output=200,
            gerado_em=now,
        )
        assert enriquecimento.id == 1
        assert enriquecimento.proposicao_id == 123
        assert enriquecimento.necessita_revisao is False
        assert enriquecimento.gerado_em == now

    def test_read_from_attributes(self):
        """Test: EnriquecimentoRead pode ser criado de model com from_attributes."""

        class MockEnriquecimento:
            id = 10
            proposicao_id = 99
            modelo = "gpt-4o-mini"
            versao_prompt = "v1.0"
            headline = "Headline teste"
            resumo_simples = "Resumo teste"
            impacto_cidadao = ["Impacto A"]  # noqa: RUF012
            confianca = 0.75
            necessita_revisao = False
            tokens_input = 50
            tokens_output = 100
            gerado_em = datetime(2026, 1, 1, 12, 0, 0)

        mock = MockEnriquecimento()
        enriquecimento = EnriquecimentoRead.model_validate(mock)
        assert enriquecimento.id == 10
        assert enriquecimento.proposicao_id == 99
        assert enriquecimento.modelo == "gpt-4o-mini"

    def test_read_includes_computed_fields(self):
        """Test: EnriquecimentoRead inclui campos computados/default."""
        now = datetime.utcnow()
        enriquecimento = EnriquecimentoRead(
            id=5,
            proposicao_id=50,
            modelo="gpt-4o-mini",
            versao_prompt="v1.0",
            confianca=0.3,
            necessita_revisao=True,
            gerado_em=now,
        )
        assert enriquecimento.necessita_revisao is True
        assert enriquecimento.gerado_em == now
        assert enriquecimento.headline is None
        assert enriquecimento.resumo_simples is None
        assert enriquecimento.impacto_cidadao is None
