"""Testes para schemas Pydantic do domínio de Proposições.

Validam a criação de instâncias de ProposicaoCreate e ProposicaoRead,
incluindo validação de constraints e campo opcionais.
"""

import pytest
from pydantic import ValidationError

from src.proposicoes.schemas import ProposicaoCreate, ProposicaoRead


class TestProposicaoCreate:
    """Testes para schema ProposicaoCreate."""

    def test_create_valid_proposicao(self):
        """Test: ProposicaoCreate aceita dados válidos."""
        proposicao = ProposicaoCreate(
            id=1,
            tipo="PL",
            numero=123,
            ano=2024,
            ementa="Lei que trata de educação",
        )
        assert proposicao.id == 1
        assert proposicao.tipo == "PL"
        assert proposicao.numero == 123
        assert proposicao.ano == 2024
        assert proposicao.ementa == "Lei que trata de educação"
        assert proposicao.autor_id is None

    def test_create_with_optional_autor_id(self):
        """Test: ProposicaoCreate aceita autor_id opcional."""
        proposicao = ProposicaoCreate(
            id=2,
            tipo="PEC",
            numero=1,
            ano=2024,
            ementa="Proposta de emenda",
            autor_id=456,
        )
        assert proposicao.autor_id == 456

    def test_create_accepts_various_tipos(self):
        """Test: ProposicaoCreate aceita diversos tipos de proposição."""
        valid_tipos = ["PL", "PEC", "MP", "PLP", "PDC", "REQ", "INC", "MSC", "RIC"]

        for tipo in valid_tipos:
            proposicao = ProposicaoCreate(
                id=100,
                tipo=tipo,
                numero=1,
                ano=2024,
                ementa="Teste",
            )
            assert proposicao.tipo == tipo

    def test_create_accepts_empty_ementa(self):
        """Test: ProposicaoCreate aceita ementa vazia (default)."""
        proposicao = ProposicaoCreate(
            id=4,
            tipo="PL",
            numero=1,
            ano=2024,
            ementa="",
        )
        assert proposicao.ementa == ""

    def test_create_accepts_numero_zero(self):
        """Test: ProposicaoCreate aceita numero >= 0."""
        proposicao = ProposicaoCreate(
            id=5,
            tipo="PL",
            numero=0,
            ano=2024,
            ementa="Teste",
        )
        assert proposicao.numero == 0

    def test_create_rejects_invalid_year(self):
        """Test: ProposicaoCreate rejeita ano fora do intervalo."""
        # Ano muito alto
        with pytest.raises(ValidationError):
            ProposicaoCreate(
                id=7,
                tipo="PL",
                numero=1,
                ano=2200,  # Deve ser <= 2100
                ementa="Teste",
            )

    def test_create_with_missing_required_fields(self):
        """Test: ProposicaoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            ProposicaoCreate(
                id=8,
                tipo="PL",
                numero=1,
                # Falta ano
                ementa="Teste",
            )

    def test_create_accepts_autor_id_as_none(self):
        """Test: ProposicaoCreate aceita autor_id como None (proposição órfã)."""
        proposicao = ProposicaoCreate(
            id=9,
            tipo="MP",
            numero=1,
            ano=2024,
            ementa="Medida provisória",
            autor_id=None,
        )
        assert proposicao.autor_id is None


class TestProposicaoRead:
    """Testes para schema ProposicaoRead."""

    def test_read_valid_proposicao(self):
        """Test: ProposicaoRead aceita dados válidos."""
        proposicao = ProposicaoRead(
            id=50,
            tipo="PL",
            numero=123,
            ano=2024,
            ementa="Lei de educação",
        )
        assert proposicao.id == 50
        assert proposicao.tipo == "PL"
        assert proposicao.numero == 123
        assert proposicao.ano == 2024
        assert proposicao.autor_id is None

    def test_read_with_author(self):
        """Test: ProposicaoRead com autor."""
        proposicao = ProposicaoRead(
            id=51,
            tipo="PEC",
            numero=1,
            ano=2024,
            ementa="Emenda constitucional",
            autor_id=456,
        )
        assert proposicao.autor_id == 456

    def test_read_from_attributes(self):
        """Test: ProposicaoRead pode ser criado de model com from_attributes."""
        # Simular um modelo ORM
        class MockProposicao:
            id = 52
            tipo = "PL"
            numero = 789
            ano = 2023
            ementa = "Lei teste"
            autor_id = None

        mock = MockProposicao()
        proposicao = ProposicaoRead.model_validate(mock)
        assert proposicao.id == 52
        assert proposicao.numero == 789
