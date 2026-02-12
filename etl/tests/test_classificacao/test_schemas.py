"""Testes para schemas Pydantic do domínio de Classificação Cívica.

Validam a criação e validação de ProposicaoCategoriaCreate.
"""

import pytest
from pydantic import ValidationError

from src.classificacao.schemas import ProposicaoCategoriaCreate


class TestProposicaoCategoriaCreate:
    """Testes para schema ProposicaoCategoriaCreate."""

    def test_create_valid(self):
        """Test: ProposicaoCategoriaCreate aceita dados válidos."""
        schema = ProposicaoCategoriaCreate(
            proposicao_id=1,
            categoria_id=2,
            origem="regra",
            confianca=1.0,
        )
        assert schema.proposicao_id == 1
        assert schema.categoria_id == 2
        assert schema.origem == "regra"
        assert schema.confianca == 1.0

    def test_defaults_origem_regra(self):
        """Test: ProposicaoCategoriaCreate tem default origem='regra'."""
        schema = ProposicaoCategoriaCreate(
            proposicao_id=1,
            categoria_id=2,
        )
        assert schema.origem == "regra"

    def test_defaults_confianca_1(self):
        """Test: ProposicaoCategoriaCreate tem default confianca=1.0."""
        schema = ProposicaoCategoriaCreate(
            proposicao_id=1,
            categoria_id=2,
        )
        assert schema.confianca == 1.0

    def test_accepts_llm_origem(self):
        """Test: ProposicaoCategoriaCreate aceita origem='llm'."""
        schema = ProposicaoCategoriaCreate(
            proposicao_id=1,
            categoria_id=2,
            origem="llm",
            confianca=0.75,
        )
        assert schema.origem == "llm"
        assert schema.confianca == 0.75

    def test_rejects_missing_proposicao_id(self):
        """Test: ProposicaoCategoriaCreate rejeita falta de proposicao_id."""
        with pytest.raises(ValidationError):
            ProposicaoCategoriaCreate(
                categoria_id=2,
            )

    def test_rejects_missing_categoria_id(self):
        """Test: ProposicaoCategoriaCreate rejeita falta de categoria_id."""
        with pytest.raises(ValidationError):
            ProposicaoCategoriaCreate(
                proposicao_id=1,
            )
