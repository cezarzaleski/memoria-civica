"""Testes para schemas Pydantic do domínio de Votações.

Validam a criação de instâncias de VotacaoCreate, VotacaoRead, VotoCreate, VotoRead,
VotacaoProposicaoCreate e OrientacaoCreate, incluindo validação de constraints.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.votacoes.schemas import (
    OrientacaoCreate,
    VotacaoCreate,
    VotacaoProposicaoCreate,
    VotacaoRead,
    VotoCreate,
    VotoRead,
)


class TestVotacaoCreate:
    """Testes para schema VotacaoCreate."""

    def test_create_valid_votacao(self):
        """Test: VotacaoCreate aceita dados válidos com todos os campos."""
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

    def test_create_accepts_none_proposicao_id(self):
        """Test: VotacaoCreate aceita proposicao_id=None (nullable)."""
        votacao = VotacaoCreate(
            id=5,
            proposicao_id=None,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.proposicao_id is None

    def test_create_defaults_proposicao_id_none(self):
        """Test: VotacaoCreate tem proposicao_id=None como default."""
        votacao = VotacaoCreate(
            id=6,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.proposicao_id is None

    def test_create_accepts_new_optional_fields(self):
        """Test: VotacaoCreate aceita novos campos opcionais."""
        votacao = VotacaoCreate(
            id=7,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
            eh_nominal=True,
            votos_sim=250,
            votos_nao=150,
            votos_outros=10,
            descricao="Votação do PL 1234/2024",
            sigla_orgao="PLEN",
        )
        assert votacao.eh_nominal is True
        assert votacao.votos_sim == 250
        assert votacao.votos_nao == 150
        assert votacao.votos_outros == 10
        assert votacao.descricao == "Votação do PL 1234/2024"
        assert votacao.sigla_orgao == "PLEN"

    def test_create_new_fields_defaults(self):
        """Test: VotacaoCreate novos campos têm defaults corretos."""
        votacao = VotacaoCreate(
            id=8,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.eh_nominal is False
        assert votacao.votos_sim == 0
        assert votacao.votos_nao == 0
        assert votacao.votos_outros == 0
        assert votacao.descricao is None
        assert votacao.sigla_orgao is None

    def test_create_rejects_negative_votos(self):
        """Test: VotacaoCreate rejeita votos_sim/nao/outros negativos."""
        with pytest.raises(ValidationError):
            VotacaoCreate(
                id=9,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
                votos_sim=-1,
            )

    def test_create_datetime_parsing(self):
        """Test: VotacaoCreate faz parse de datetime (ISO 8601)."""
        votacao = VotacaoCreate(
            id=10,
            proposicao_id=1,
            data_hora="2024-01-15T14:30:00",
            resultado="APROVADO",
        )
        assert isinstance(votacao.data_hora, datetime)
        assert votacao.data_hora == datetime(2024, 1, 15, 14, 30, 0)

    def test_backward_compatibility_with_original_fields(self):
        """Test: VotacaoCreate ainda funciona com campos originais (backward compatibility)."""
        votacao = VotacaoCreate(
            id=11,
            proposicao_id=123,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        assert votacao.id == 11
        assert votacao.proposicao_id == 123
        assert votacao.data_hora == datetime(2024, 1, 15, 14, 30, 0)
        assert votacao.resultado == "APROVADO"
        # Novos campos com defaults
        assert votacao.eh_nominal is False
        assert votacao.votos_sim == 0


class TestVotacaoRead:
    """Testes para schema VotacaoRead."""

    def test_read_valid_votacao(self):
        """Test: VotacaoRead aceita dados válidos com novos campos."""
        votacao = VotacaoRead(
            id=50,
            proposicao_id=123,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
            eh_nominal=True,
            votos_sim=250,
            votos_nao=150,
            votos_outros=10,
            descricao="Teste",
            sigla_orgao="PLEN",
        )
        assert votacao.id == 50
        assert votacao.proposicao_id == 123
        assert votacao.eh_nominal is True

    def test_read_accepts_null_proposicao_id(self):
        """Test: VotacaoRead aceita proposicao_id=None."""
        votacao = VotacaoRead(
            id=51,
            proposicao_id=None,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
            eh_nominal=False,
            votos_sim=0,
            votos_nao=0,
            votos_outros=0,
            descricao=None,
            sigla_orgao=None,
        )
        assert votacao.proposicao_id is None

    def test_read_from_attributes(self):
        """Test: VotacaoRead pode ser criado de model com from_attributes."""

        class MockVotacao:
            id = 51
            proposicao_id = 456
            data_hora = datetime(2024, 1, 16, 10, 15, 0)
            resultado = "REJEITADO"
            eh_nominal = True
            votos_sim = 200
            votos_nao = 100
            votos_outros = 5
            descricao = "Teste"
            sigla_orgao = "PLEN"

        mock = MockVotacao()
        votacao = VotacaoRead.model_validate(mock)
        assert votacao.id == 51
        assert votacao.proposicao_id == 456
        assert votacao.eh_nominal is True


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
                votacao_id=0,
                deputado_id=1,
                voto="SIM",
            )

    def test_create_rejects_invalid_deputado_id(self):
        """Test: VotoCreate rejeita deputado_id <= 0."""
        with pytest.raises(ValidationError):
            VotoCreate(
                id=5,
                votacao_id=1,
                deputado_id=0,
                voto="SIM",
            )

    def test_create_rejects_missing_required_fields(self):
        """Test: VotoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            VotoCreate(
                id=6,
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


class TestVotacaoProposicaoCreate:
    """Testes para schema VotacaoProposicaoCreate."""

    def test_create_valid(self):
        """Test: VotacaoProposicaoCreate aceita dados válidos com todos os campos."""
        schema = VotacaoProposicaoCreate(
            votacao_id=1,
            votacao_id_original="2367548-7",
            proposicao_id=100,
            titulo="PL 10106/2018",
            ementa="Ementa da proposição",
            sigla_tipo="PL",
            numero=10106,
            ano=2018,
            eh_principal=True,
        )
        assert schema.votacao_id == 1
        assert schema.votacao_id_original == "2367548-7"
        assert schema.proposicao_id == 100
        assert schema.titulo == "PL 10106/2018"
        assert schema.eh_principal is True

    def test_optional_fields_default_none(self):
        """Test: VotacaoProposicaoCreate campos opcionais têm default None."""
        schema = VotacaoProposicaoCreate(
            votacao_id=1,
            proposicao_id=100,
        )
        assert schema.votacao_id_original is None
        assert schema.titulo is None
        assert schema.ementa is None
        assert schema.sigla_tipo is None
        assert schema.numero is None
        assert schema.ano is None

    def test_eh_principal_defaults_false(self):
        """Test: VotacaoProposicaoCreate eh_principal default é False."""
        schema = VotacaoProposicaoCreate(
            votacao_id=1,
            proposicao_id=100,
        )
        assert schema.eh_principal is False

    def test_rejects_missing_votacao_id(self):
        """Test: VotacaoProposicaoCreate rejeita falta de votacao_id."""
        with pytest.raises(ValidationError):
            VotacaoProposicaoCreate(proposicao_id=100)

    def test_rejects_missing_proposicao_id(self):
        """Test: VotacaoProposicaoCreate rejeita falta de proposicao_id."""
        with pytest.raises(ValidationError):
            VotacaoProposicaoCreate(votacao_id=1)


class TestOrientacaoCreate:
    """Testes para schema OrientacaoCreate."""

    def test_create_valid(self):
        """Test: OrientacaoCreate aceita dados válidos."""
        schema = OrientacaoCreate(
            votacao_id=1,
            votacao_id_original="2367548-7",
            sigla_bancada="PT",
            orientacao="Sim",
        )
        assert schema.votacao_id == 1
        assert schema.votacao_id_original == "2367548-7"
        assert schema.sigla_bancada == "PT"
        assert schema.orientacao == "Sim"

    def test_optional_votacao_id_original(self):
        """Test: OrientacaoCreate votacao_id_original é opcional."""
        schema = OrientacaoCreate(
            votacao_id=1,
            sigla_bancada="PT",
            orientacao="Sim",
        )
        assert schema.votacao_id_original is None

    def test_rejects_missing_votacao_id(self):
        """Test: OrientacaoCreate rejeita falta de votacao_id."""
        with pytest.raises(ValidationError):
            OrientacaoCreate(
                sigla_bancada="PT",
                orientacao="Sim",
            )

    def test_rejects_missing_sigla_bancada(self):
        """Test: OrientacaoCreate rejeita falta de sigla_bancada."""
        with pytest.raises(ValidationError):
            OrientacaoCreate(
                votacao_id=1,
                orientacao="Sim",
            )

    def test_rejects_missing_orientacao(self):
        """Test: OrientacaoCreate rejeita falta de orientacao."""
        with pytest.raises(ValidationError):
            OrientacaoCreate(
                votacao_id=1,
                sigla_bancada="PT",
            )
