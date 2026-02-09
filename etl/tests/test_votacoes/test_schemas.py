"""Testes para schemas Pydantic do domínio de Votações.

Validam a criação de instâncias de VotacaoCreate, VotacaoRead, VotoCreate e VotoRead,
incluindo validação de constraints e campos opcionais.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.votacoes.schemas import (
    VotacaoCreate,
    VotacaoRead,
    VotoCreate,
    VotoRead,
)


class TestVotacaoCreate:
    """Testes para schema VotacaoCreate."""

    def test_create_valid_votacao(self):
        """Test: VotacaoCreate aceita dados válidos."""
        votacao = VotacaoCreate(
            id=1,
            proposicao_id=123,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.id == 1
        assert votacao.proposicao_id == 123
        assert votacao.data_hora == datetime(2024, 1, 15, 14, 30, 0)
        assert votacao.resultado == "APROVADO"

    def test_create_with_rejeitado_resultado(self):
        """Test: VotacaoCreate aceita resultado REJEITADO."""
        votacao = VotacaoCreate(
            id=2,
            proposicao_id=456,
            data_hora=datetime(2024, 1, 16, 10, 15, 0),
            resultado="REJEITADO",
        )
        assert votacao.resultado == "REJEITADO"

    def test_create_accepts_various_resultados(self):
        """Test: VotacaoCreate aceita diversos resultados."""
        valid_resultados = ["APROVADO", "REJEITADO", "Aprovado", "Rejeitado"]

        for resultado in valid_resultados:
            votacao = VotacaoCreate(
                id=100,
                proposicao_id=1,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado=resultado,
            )
            assert votacao.resultado == resultado

    def test_create_rejects_invalid_proposicao_id(self):
        """Test: VotacaoCreate rejeita proposicao_id <= 0."""
        with pytest.raises(ValidationError):
            VotacaoCreate(
                id=5,
                proposicao_id=0,  # Deve ser >= 1
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            )

    def test_create_rejects_missing_required_fields(self):
        """Test: VotacaoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            VotacaoCreate(
                id=6,
                # Falta proposicao_id
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            )

    def test_create_datetime_parsing(self):
        """Test: VotacaoCreate faz parse de datetime (ISO 8601)."""
        votacao = VotacaoCreate(
            id=7,
            proposicao_id=1,
            data_hora="2024-01-15T14:30:00",  # ISO 8601 string
            resultado="APROVADO",
        )
        assert isinstance(votacao.data_hora, datetime)
        assert votacao.data_hora == datetime(2024, 1, 15, 14, 30, 0)


class TestVotacaoRead:
    """Testes para schema VotacaoRead."""

    def test_read_valid_votacao(self):
        """Test: VotacaoRead aceita dados válidos."""
        votacao = VotacaoRead(
            id=50,
            proposicao_id=123,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.id == 50
        assert votacao.proposicao_id == 123
        assert votacao.data_hora == datetime(2024, 1, 15, 14, 30, 0)
        assert votacao.resultado == "APROVADO"

    def test_read_from_attributes(self):
        """Test: VotacaoRead pode ser criado de model com from_attributes."""
        # Simular um modelo ORM
        class MockVotacao:
            id = 51
            proposicao_id = 456
            data_hora = datetime(2024, 1, 16, 10, 15, 0)
            resultado = "REJEITADO"

        mock = MockVotacao()
        votacao = VotacaoRead.model_validate(mock)
        assert votacao.id == 51
        assert votacao.proposicao_id == 456


class TestVotoCreate:
    """Testes para schema VotoCreate."""

    def test_create_valid_voto(self):
        """Test: VotoCreate aceita dados válidos."""
        voto = VotoCreate(
            id=1,
            votacao_id=123,
            deputado_id=456,
            voto="SIM",
        )
        assert voto.id == 1
        assert voto.votacao_id == 123
        assert voto.deputado_id == 456
        assert voto.voto == "SIM"

    def test_create_accepts_all_voto_types(self):
        """Test: VotoCreate aceita diversos tipos de voto."""
        valid_votos = ["SIM", "NAO", "ABSTENCAO", "OBSTRUCAO", "Sim", "Não"]

        for voto_tipo in valid_votos:
            voto = VotoCreate(
                id=100,
                votacao_id=1,
                deputado_id=1,
                voto=voto_tipo,
            )
            assert voto.voto == voto_tipo

    def test_create_rejects_invalid_votacao_id(self):
        """Test: VotoCreate rejeita votacao_id <= 0."""
        with pytest.raises(ValidationError):
            VotoCreate(
                id=4,
                votacao_id=0,  # Deve ser >= 1
                deputado_id=1,
                voto="SIM",
            )

    def test_create_rejects_invalid_deputado_id(self):
        """Test: VotoCreate rejeita deputado_id <= 0."""
        with pytest.raises(ValidationError):
            VotoCreate(
                id=5,
                votacao_id=1,
                deputado_id=0,  # Deve ser >= 1
                voto="SIM",
            )

    def test_create_rejects_missing_required_fields(self):
        """Test: VotoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            VotoCreate(
                id=6,
                # Falta votacao_id
                deputado_id=1,
                voto="SIM",
            )


class TestVotoRead:
    """Testes para schema VotoRead."""

    def test_read_valid_voto(self):
        """Test: VotoRead aceita dados válidos."""
        voto = VotoRead(
            id=50,
            votacao_id=123,
            deputado_id=456,
            voto="SIM",
        )
        assert voto.id == 50
        assert voto.votacao_id == 123
        assert voto.deputado_id == 456
        assert voto.voto == "SIM"

    def test_read_from_attributes(self):
        """Test: VotoRead pode ser criado de model com from_attributes."""
        # Simular um modelo ORM
        class MockVoto:
            id = 51
            votacao_id = 456
            deputado_id = 789
            voto = "NAO"

        mock = MockVoto()
        voto = VotoRead.model_validate(mock)
        assert voto.id == 51
        assert voto.votacao_id == 456
        assert voto.deputado_id == 789
        assert voto.voto == "NAO"
