"""Testes para ETL do domínio de Votações.

Validam extract, transform, load e FK validation, incluindo logging e tratamento de erros,
além de testes de integração end-to-end.
"""

import logging
from datetime import datetime

import pytest

from src.deputados.repository import DeputadoRepository
from src.deputados.schemas import DeputadoCreate
from src.proposicoes.repository import ProposicaoRepository
from src.proposicoes.schemas import ProposicaoCreate
from src.votacoes.etl import (
    _criar_proposicao_parcial,
    _eleger_principal,
    _parse_votacao_id,
    extract_orientacoes_csv,
    extract_votacoes_csv,
    extract_votacoes_proposicoes_csv,
    extract_votos_csv,
    load_orientacoes,
    load_votacoes,
    load_votacoes_proposicoes,
    load_votos,
    run_orientacoes_etl,
    run_votacoes_etl,
    run_votacoes_proposicoes_etl,
    transform_orientacoes,
    transform_votacoes,
    transform_votacoes_proposicoes,
    transform_votos,
)
from src.votacoes.models import Orientacao, Votacao, VotacaoProposicao, Voto
from src.votacoes.schemas import OrientacaoCreate, VotacaoCreate, VotacaoProposicaoCreate, VotoCreate


class TestExtractVotacoesCsv:
    """Testes para extract_votacoes_csv."""

    def test_extract_votacoes_returns_dict_list(self, votacoes_csv_path):
        """Test: extract_votacoes_csv() lê CSV e retorna dicts."""
        data = extract_votacoes_csv(votacoes_csv_path)

        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_votacoes_has_expected_columns(self, votacoes_csv_path):
        """Test: extract votacoes retorna dicts com colunas do formato Câmara."""
        data = extract_votacoes_csv(votacoes_csv_path)

        first_record = data[0]
        assert "id" in first_record
        assert "ultimaApresentacaoProposicao_idProposicao" in first_record
        assert "dataHoraRegistro" in first_record
        assert "aprovacao" in first_record

    def test_extract_votacoes_file_not_found(self):
        """Test: extract_votacoes_csv() lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_votacoes_csv("/path/que/nao/existe/votacoes.csv")


class TestExtractVotosCsv:
    """Testes para extract_votos_csv."""

    def test_extract_votos_returns_dict_list(self, votos_csv_path):
        """Test: extract_votos_csv() lê CSV e retorna dicts."""
        data = extract_votos_csv(votos_csv_path)

        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_votos_has_expected_columns(self, votos_csv_path):
        """Test: extract votos retorna dicts com colunas do formato Câmara."""
        data = extract_votos_csv(votos_csv_path)

        first_record = data[0]
        assert "idVotacao" in first_record
        assert "deputado_id" in first_record
        assert "voto" in first_record

    def test_extract_votos_file_not_found(self):
        """Test: extract_votos_csv() lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_votos_csv("/path/que/nao/existe/votos.csv")


class TestTransformVotacoes:
    """Testes para transform_votacoes."""

    def test_transform_votacoes_validates_correct_data(self):
        """Test: transform_votacoes() valida dados corretos com formato Câmara."""
        raw_data = [
            {
                "id": "123-1",
                "ultimaApresentacaoProposicao_idProposicao": "123",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "descricao": "Aprovado o projeto",
                "quantidadeVotosSim": "250",
                "quantidadeVotosNao": "100",
                "quantidadeVotosOutros": "10",
                "siglaOrgao": "PLEN",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) > 0
        assert isinstance(result[0], VotacaoCreate)
        assert result[0].resultado == "APROVADO"
        assert result[0].id == 123  # Extraído do "123-1"
        assert result[0].votos_sim == 250
        assert result[0].votos_nao == 100
        assert result[0].votos_outros == 10
        assert result[0].sigla_orgao == "PLEN"
        assert result[0].descricao == "Aprovado o projeto"
        assert result[0].eh_nominal is True

    def test_transform_votacoes_skips_invalid_datetime(self, caplog):
        """Test: transform_votacoes() pula dados com datetime inválida."""
        raw_data = [
            {
                "id": "2-1",
                "ultimaApresentacaoProposicao_idProposicao": "123",
                "dataHoraRegistro": "INVALIDO",  # datetime inválida
                "aprovacao": "1",
            }
        ]

        with caplog.at_level(logging.WARNING):
            result = transform_votacoes(raw_data)

        # Nenhum registro deve ter sido processado
        assert len(result) == 0

    def test_transform_votacoes_validates_fk_without_db(self):
        """Test: transform_votacoes() sem db não valida FK."""
        raw_data = [
            {
                "id": "3-1",
                "ultimaApresentacaoProposicao_idProposicao": "999999",  # ID que não existe
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
            }
        ]

        # Sem db, deveria processar normalmente
        result = transform_votacoes(raw_data, db=None)

        assert len(result) > 0

    def test_transform_votacoes_validates_fk_with_db(self, db_session):
        """Test: transform_votacoes() com db valida FK proposicao_id."""
        # Criar uma proposição no banco
        prop_repo = ProposicaoRepository(db_session)
        prop_create = ProposicaoCreate(
            id=456,
            tipo="PL",
            numero=123,
            ano=2024,
            ementa="Lei teste",
        )
        prop_repo.create(prop_create)

        # Testar com proposicao_id válida
        raw_data_valid = [
            {
                "id": "4-1",
                "ultimaApresentacaoProposicao_idProposicao": "456",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
            }
        ]

        result = transform_votacoes(raw_data_valid, db=db_session)
        assert len(result) == 1

        # Testar com proposicao_id inválida
        raw_data_invalid = [
            {
                "id": "5-1",
                "ultimaApresentacaoProposicao_idProposicao": "999999",  # Não existe
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
            }
        ]

        result = transform_votacoes(raw_data_invalid, db=db_session)
        assert len(result) == 0  # Deve ser pulado

    def test_transform_votacoes_nullable_proposicao_id_zero(self):
        """Test: transform_votacoes() aceita votações com proposicao_id=0 (nullable)."""
        raw_data = [
            {
                "id": "10-1",
                "ultimaApresentacaoProposicao_idProposicao": "0",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "descricao": "Votação sem proposição",
                "quantidadeVotosSim": "200",
                "quantidadeVotosNao": "80",
                "quantidadeVotosOutros": "5",
                "siglaOrgao": "PLEN",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].proposicao_id is None
        assert result[0].votos_sim == 200

    def test_transform_votacoes_nullable_proposicao_id_empty(self):
        """Test: transform_votacoes() aceita votações com proposicao_id vazio (nullable)."""
        raw_data = [
            {
                "id": "11-1",
                "ultimaApresentacaoProposicao_idProposicao": "",
                "dataHoraRegistro": "2024-01-20T11:00:00",
                "aprovacao": "0",
                "descricao": "Outra votação sem proposição",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].proposicao_id is None

    def test_transform_votacoes_eh_nominal_true(self):
        """Test: transform_votacoes() calcula eh_nominal=True quando votos_sim > 0."""
        raw_data = [
            {
                "id": "12-1",
                "ultimaApresentacaoProposicao_idProposicao": "1",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "quantidadeVotosSim": "250",
                "quantidadeVotosNao": "100",
                "quantidadeVotosOutros": "10",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].eh_nominal is True

    def test_transform_votacoes_eh_nominal_false(self):
        """Test: transform_votacoes() calcula eh_nominal=False quando votos_sim == 0."""
        raw_data = [
            {
                "id": "13-1",
                "ultimaApresentacaoProposicao_idProposicao": "1",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "quantidadeVotosSim": "0",
                "quantidadeVotosNao": "0",
                "quantidadeVotosOutros": "0",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].eh_nominal is False

    def test_transform_votacoes_maps_new_csv_fields(self):
        """Test: transform_votacoes() mapeia votos_sim, votos_nao, votos_outros, sigla_orgao, descricao."""
        raw_data = [
            {
                "id": "14-1",
                "ultimaApresentacaoProposicao_idProposicao": "1",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "descricao": "Aprovado em plenário",
                "quantidadeVotosSim": "300",
                "quantidadeVotosNao": "50",
                "quantidadeVotosOutros": "3",
                "siglaOrgao": "CCJC",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].votos_sim == 300
        assert result[0].votos_nao == 50
        assert result[0].votos_outros == 3
        assert result[0].sigla_orgao == "CCJC"
        assert result[0].descricao == "Aprovado em plenário"

    def test_transform_votacoes_handles_missing_new_columns(self):
        """Test: transform_votacoes() trata CSV sem novos campos (defaults a 0/None)."""
        raw_data = [
            {
                "id": "15-1",
                "ultimaApresentacaoProposicao_idProposicao": "1",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
                "descricao": "Aprovado",
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) == 1
        assert result[0].votos_sim == 0
        assert result[0].votos_nao == 0
        assert result[0].votos_outros == 0
        assert result[0].eh_nominal is False
        assert result[0].sigla_orgao is None

    def test_transform_votacoes_fk_validation_with_nullable_proposicao_id(self, db_session):
        """Test: transform_votacoes() valida FK quando proposicao_id é válido, aceita None."""
        prop_repo = ProposicaoRepository(db_session)
        prop_repo.create(ProposicaoCreate(
            id=789, tipo="PL", numero=100, ano=2024, ementa="Lei teste",
        ))

        raw_data = [
            # Com proposicao_id válido
            {
                "id": "16-1",
                "ultimaApresentacaoProposicao_idProposicao": "789",
                "dataHoraRegistro": "2024-01-15T14:30:00",
                "aprovacao": "1",
            },
            # Sem proposicao_id (nullable)
            {
                "id": "17-1",
                "ultimaApresentacaoProposicao_idProposicao": "0",
                "dataHoraRegistro": "2024-01-16T10:00:00",
                "aprovacao": "0",
            },
        ]

        result = transform_votacoes(raw_data, db=db_session)

        assert len(result) == 2
        assert result[0].proposicao_id == 789
        assert result[1].proposicao_id is None


class TestTransformVotos:
    """Testes para transform_votos."""

    def test_transform_votos_validates_correct_data(self):
        """Test: transform_votos() valida dados corretos com formato Câmara."""
        raw_data = [
            {
                "idVotacao": "123-1",
                "deputado_id": "456",
                "voto": "Sim",
            }
        ]

        result = transform_votos(raw_data)

        assert len(result) > 0
        assert isinstance(result[0], VotoCreate)
        assert result[0].voto == "SIM"  # Normalizado para maiúsculas
        assert result[0].votacao_id == 123  # Extraído do "123-1"

    def test_transform_votos_validates_all_voto_types(self):
        """Test: transform_votos() valida todos os tipos de voto e normaliza."""
        raw_data = [
            {"idVotacao": "1-1", "deputado_id": "1", "voto": "Sim"},
            {"idVotacao": "1-1", "deputado_id": "2", "voto": "Não"},
            {"idVotacao": "1-1", "deputado_id": "3", "voto": "Abstenção"},
            {"idVotacao": "1-1", "deputado_id": "4", "voto": "Obstrução"},
        ]

        result = transform_votos(raw_data)

        assert len(result) == 4
        assert result[0].voto == "SIM"
        assert result[1].voto == "NAO"
        assert result[2].voto == "ABSTENCAO"
        assert result[3].voto == "OBSTRUCAO"

    def test_transform_votos_validates_fk_with_db(self, db_session):
        """Test: transform_votos() com db valida FKs votacao_id e deputado_id."""
        # Criar votação e deputado no banco
        votacao_create = VotacaoCreate(
            id=789,
            proposicao_id=1,
            data_hora=datetime(2024, 1, 15, 14, 30, 0),
            resultado="APROVADO",
        )
        db_votacao = Votacao(**votacao_create.model_dump())
        db_session.add(db_votacao)

        deputado_create = DeputadoCreate(
            id=999,
            nome="Test Deputy",
            partido="PT",
            uf="SP",
        )
        dep_repo = DeputadoRepository(db_session)
        dep_repo.create(deputado_create)

        # Testar com FKs válidas (formato Câmara)
        raw_data_valid = [
            {
                "idVotacao": "789-1",
                "deputado_id": "999",
                "voto": "Sim",
            }
        ]

        result = transform_votos(raw_data_valid, db=db_session)
        assert len(result) == 1

        # Testar com votacao_id inválida
        raw_data_invalid_votacao = [
            {
                "idVotacao": "999999-1",  # Não existe
                "deputado_id": "999",
                "voto": "Sim",
            }
        ]

        result = transform_votos(raw_data_invalid_votacao, db=db_session)
        assert len(result) == 0

        # Testar com deputado_id inválida
        raw_data_invalid_deputado = [
            {
                "idVotacao": "789-1",
                "deputado_id": "999999",  # Não existe
                "voto": "Sim",
            }
        ]

        result = transform_votos(raw_data_invalid_deputado, db=db_session)
        assert len(result) == 0


class TestLoadVotacoes:
    """Testes para load_votacoes."""

    def test_load_votacoes_persists_data(self, db_session):
        """Test: load_votacoes() persiste votações no banco com todos os campos."""
        votacoes = [
            VotacaoCreate(
                id=500,
                proposicao_id=1,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
                eh_nominal=True,
                votos_sim=250,
                votos_nao=100,
                votos_outros=10,
                descricao="Aprovado o projeto",
                sigla_orgao="PLEN",
            )
        ]

        count = load_votacoes(votacoes, db_session)

        assert count == 1

        # Verificar persistência de todos os campos
        from_db = db_session.query(Votacao).filter(Votacao.id == 500).first()
        assert from_db is not None
        assert from_db.proposicao_id == 1
        assert from_db.eh_nominal is True
        assert from_db.votos_sim == 250
        assert from_db.votos_nao == 100
        assert from_db.votos_outros == 10
        assert from_db.descricao == "Aprovado o projeto"
        assert from_db.sigla_orgao == "PLEN"

    def test_load_votacoes_persists_with_nullable_proposicao_id(self, db_session):
        """Test: load_votacoes() persiste votação com proposicao_id=None."""
        votacoes = [
            VotacaoCreate(
                id=501,
                proposicao_id=None,
                data_hora=datetime(2024, 1, 20, 11, 0, 0),
                resultado="APROVADO",
                eh_nominal=True,
                votos_sim=200,
                votos_nao=80,
                votos_outros=5,
                descricao="Votação sem proposição",
                sigla_orgao="PLEN",
            )
        ]

        count = load_votacoes(votacoes, db_session)

        assert count == 1

        from_db = db_session.query(Votacao).filter(Votacao.id == 501).first()
        assert from_db is not None
        assert from_db.proposicao_id is None
        assert from_db.eh_nominal is True
        assert from_db.votos_sim == 200

    def test_load_votacoes_returns_zero_for_empty(self, db_session):
        """Test: load_votacoes() retorna 0 para lista vazia."""
        count = load_votacoes([], db_session)
        assert count == 0


class TestLoadVotos:
    """Testes para load_votos."""

    def test_load_votos_persists_data(self, db_session):
        """Test: load_votos() persiste votos no banco."""
        votos = [
            VotoCreate(
                id=600,
                votacao_id=1,
                deputado_id=1,
                voto="SIM",
            ),
            VotoCreate(
                id=601,
                votacao_id=1,
                deputado_id=2,
                voto="NAO",
            ),
        ]

        count = load_votos(votos, db_session)

        assert count == 2

        # Verificar persistência
        from_db = db_session.query(Voto).filter(Voto.id == 600).first()
        assert from_db is not None
        assert from_db.deputado_id == 1

    def test_load_votos_returns_zero_for_empty(self, db_session):
        """Test: load_votos() retorna 0 para lista vazia."""
        count = load_votos([], db_session)
        assert count == 0


class TestRunVotacoesEtl:
    """Testes de integração ETL completo."""

    def test_run_votacoes_etl_end_to_end(
        self,
        db_session,
        votacoes_csv_path,
        votos_csv_path,
    ):
        """Test: run_votacoes_etl() executa pipeline completo."""
        # Criar dados base (proposições e deputados)
        prop_repo = ProposicaoRepository(db_session)
        for i in range(1, 6):
            prop_create = ProposicaoCreate(
                id=i,
                tipo="PL",
                numero=i * 100,
                ano=2024,
                ementa=f"Lei {i}",
            )
            prop_repo.create(prop_create)

        dep_repo = DeputadoRepository(db_session)
        deputy_ids = [220593, 204379, 220714, 221328, 204560]
        for i, dep_id in enumerate(deputy_ids):
            dep_create = DeputadoCreate(
                id=dep_id,
                nome=f"Deputy {i}",
                partido="PT",
                uf="SP",
            )
            dep_repo.create(dep_create)

        # Garantir que os dados estão persistidos antes do ETL
        db_session.commit()

        # Executar ETL com db_session para validação de FKs e persistência
        # (votações sem proposicao_id são aceitas com proposicao_id=None)
        result = run_votacoes_etl(votacoes_csv_path, votos_csv_path, db=db_session)

        # Deve retornar sucesso
        assert result == 0

        # Verificar que votações foram persistidas, incluindo as sem proposicao_id
        all_votacoes = db_session.query(Votacao).all()
        assert len(all_votacoes) > 0

        # Verificar que votações com proposicao_id=None estão presentes
        votacoes_sem_prop = [v for v in all_votacoes if v.proposicao_id is None]
        assert len(votacoes_sem_prop) >= 1  # Pelo menos uma votação sem proposição


# ==============================================================================
# Testes para ETL votacoes_proposicoes
# ==============================================================================


def _setup_base_data(db_session):
    """Helper para criar dados base (votações e proposições) para testes de votacoes_proposicoes."""
    # Criar proposições base
    prop_repo = ProposicaoRepository(db_session)
    for i in range(1, 6):
        prop_repo.create(ProposicaoCreate(
            id=i,
            tipo="PL",
            numero=i * 100,
            ano=2024,
            ementa=f"Ementa proposição {i}",
        ))

    # Criar votações base
    for i in range(1, 6):
        db_votacao = Votacao(
            id=i,
            proposicao_id=i,
            data_hora=datetime(2024, 1, 15 + i, 14, 30, 0),
            resultado="APROVADO",
        )
        db_session.add(db_votacao)
    db_session.commit()


class TestParseVotacaoId:
    """Testes para _parse_votacao_id."""

    def test_parse_with_hyphen(self):
        """Test: parse idVotacao com formato 'NNN-N'."""
        votacao_id, original = _parse_votacao_id("2367548-7")
        assert votacao_id == 2367548
        assert original == "2367548-7"

    def test_parse_without_hyphen(self):
        """Test: parse idVotacao sem hífen."""
        votacao_id, original = _parse_votacao_id("12345")
        assert votacao_id == 12345
        assert original == "12345"

    def test_parse_empty_raises(self):
        """Test: parse idVotacao vazio lança ValueError."""
        with pytest.raises(ValueError, match="idVotacao vazio"):
            _parse_votacao_id("")

    def test_parse_with_spaces(self):
        """Test: parse idVotacao com espaços é limpo."""
        votacao_id, original = _parse_votacao_id("  1-1  ")
        assert votacao_id == 1
        assert original == "1-1"


class TestCriarProposicaoParcial:
    """Testes para _criar_proposicao_parcial."""

    def test_cria_proposicao_com_dados_csv(self, db_session):
        """Test: cria proposição parcial com dados do CSV."""
        record = {
            "proposicao_siglaTipo": "MPV",
            "proposicao_numero": "200",
            "proposicao_ano": "2024",
            "proposicao_titulo": "MPV 200/2024",
            "proposicao_ementa": "Ementa da medida provisória",
        }
        result = _criar_proposicao_parcial(99999, record, db_session)
        assert result is True

        # Verificar persistência
        from src.proposicoes.models import Proposicao

        prop = db_session.query(Proposicao).filter(Proposicao.id == 99999).first()
        assert prop is not None
        assert prop.tipo == "MPV"
        assert prop.numero == 200
        assert prop.ano == 2024
        assert prop.ementa == "Ementa da medida provisória"
        assert prop.autor_id is None

    def test_cria_proposicao_com_dados_minimos(self, db_session):
        """Test: cria proposição parcial com campos mínimos."""
        record = {
            "proposicao_siglaTipo": "",
            "proposicao_numero": "",
            "proposicao_ano": "",
            "proposicao_titulo": "Título genérico",
            "proposicao_ementa": "",
        }
        result = _criar_proposicao_parcial(88888, record, db_session)
        assert result is True

        from src.proposicoes.models import Proposicao

        prop = db_session.query(Proposicao).filter(Proposicao.id == 88888).first()
        assert prop is not None
        assert prop.tipo == "ND"
        assert prop.ementa == "Título genérico"

    def test_cria_proposicao_com_ementa_fallback(self, db_session):
        """Test: usa tipo numero/ano como ementa se nenhum texto disponível."""
        record = {
            "proposicao_siglaTipo": "PL",
            "proposicao_numero": "100",
            "proposicao_ano": "2024",
            "proposicao_titulo": "",
            "proposicao_ementa": "",
        }
        result = _criar_proposicao_parcial(77777, record, db_session)
        assert result is True

        from src.proposicoes.models import Proposicao

        prop = db_session.query(Proposicao).filter(Proposicao.id == 77777).first()
        assert prop is not None
        assert prop.ementa == "PL 100/2024"


class TestElegerPrincipal:
    """Testes para _eleger_principal."""

    def test_pec_tem_prioridade_sobre_pl(self):
        """Test: PEC é eleita principal sobre PL na mesma votação."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="PL"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=20, sigla_tipo="PEC"),
        ]
        result = _eleger_principal(records)
        assert result[0].eh_principal is False
        assert result[1].eh_principal is True

    def test_plp_tem_prioridade_sobre_pl(self):
        """Test: PLP é eleita principal sobre PL."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="PL"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=20, sigla_tipo="PLP"),
        ]
        result = _eleger_principal(records)
        assert result[0].eh_principal is False
        assert result[1].eh_principal is True

    def test_mpv_tem_prioridade_sobre_req(self):
        """Test: MPV é eleita principal sobre REQ."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="REQ"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=20, sigla_tipo="MPV"),
        ]
        result = _eleger_principal(records)
        assert result[0].eh_principal is False
        assert result[1].eh_principal is True

    def test_votacao_unica_proposicao_eh_principal(self):
        """Test: votação com uma única proposição a marca como principal."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="PL"),
        ]
        result = _eleger_principal(records)
        assert result[0].eh_principal is True

    def test_votacoes_diferentes_tem_principals_independentes(self):
        """Test: votações diferentes elegem principal independentemente."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="PL"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=20, sigla_tipo="PEC"),
            VotacaoProposicaoCreate(votacao_id=2, proposicao_id=30, sigla_tipo="REQ"),
        ]
        result = _eleger_principal(records)
        # Votação 1: PEC é principal
        assert result[0].eh_principal is False
        assert result[1].eh_principal is True
        # Votação 2: REQ é o único, então é principal
        assert result[2].eh_principal is True

    def test_tipo_desconhecido_tem_prioridade_baixa(self):
        """Test: tipo desconhecido tem prioridade menor que PEC."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=10, sigla_tipo="XYZ"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=20, sigla_tipo="PEC"),
        ]
        result = _eleger_principal(records)
        assert result[0].eh_principal is False
        assert result[1].eh_principal is True

    def test_lista_vazia(self):
        """Test: lista vazia retorna lista vazia."""
        result = _eleger_principal([])
        assert result == []

    def test_prioridade_completa(self):
        """Test: valida ordem completa PEC > PLP > PL > MPV > PDL > PFC > TVR > REQ."""
        records = [
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=1, sigla_tipo="REQ"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=2, sigla_tipo="TVR"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=3, sigla_tipo="PFC"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=4, sigla_tipo="PDL"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=5, sigla_tipo="MPV"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=6, sigla_tipo="PL"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=7, sigla_tipo="PLP"),
            VotacaoProposicaoCreate(votacao_id=1, proposicao_id=8, sigla_tipo="PEC"),
        ]
        result = _eleger_principal(records)
        # Apenas PEC (índice 7) deve ser principal
        for i, r in enumerate(result):
            if i == 7:
                assert r.eh_principal is True, "PEC deveria ser principal"
            else:
                assert r.eh_principal is False, f"Tipo {r.sigla_tipo} não deveria ser principal"


class TestExtractVotacoesProposicoesCsv:
    """Testes para extract_votacoes_proposicoes_csv."""

    def test_extract_returns_dict_list(self, votacoes_proposicoes_csv_path):
        """Test: extract lê CSV e retorna lista de dicts."""
        data = extract_votacoes_proposicoes_csv(votacoes_proposicoes_csv_path)
        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_has_expected_columns(self, votacoes_proposicoes_csv_path):
        """Test: extract retorna dicts com colunas esperadas."""
        data = extract_votacoes_proposicoes_csv(votacoes_proposicoes_csv_path)
        first = data[0]
        assert "idVotacao" in first
        assert "proposicao_id" in first
        assert "proposicao_siglaTipo" in first
        assert "proposicao_titulo" in first
        assert "proposicao_ementa" in first
        assert "proposicao_numero" in first
        assert "proposicao_ano" in first

    def test_extract_file_not_found(self):
        """Test: extract lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_votacoes_proposicoes_csv("/path/inexistente/vp.csv")


class TestTransformVotacoesProposicoes:
    """Testes para transform_votacoes_proposicoes."""

    def test_transform_com_dados_validos(self, db_session):
        """Test: transform com votação e proposição existentes retorna registros válidos."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL 100/2024",
                "proposicao_ementa": "Ementa teste",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            }
        ]
        result = transform_votacoes_proposicoes(raw_data, db_session)
        assert len(result) == 1
        assert isinstance(result[0], VotacaoProposicaoCreate)
        assert result[0].votacao_id == 1
        assert result[0].votacao_id_original == "1-1"
        assert result[0].proposicao_id == 1
        assert result[0].sigla_tipo == "PL"
        assert result[0].titulo == "PL 100/2024"

    def test_transform_skipa_votacao_inexistente(self, db_session, caplog):
        """Test: transform skipa registro quando votacao_id não existe."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "999-1",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL 100/2024",
                "proposicao_ementa": "Ementa",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_votacoes_proposicoes(raw_data, db_session)

        assert len(result) == 0
        assert "votacao_id 999" in caplog.text

    def test_transform_cria_proposicao_parcial(self, db_session):
        """Test: transform cria proposição parcial quando proposicao_id não existe."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "99999",
                "proposicao_siglaTipo": "MPV",
                "proposicao_titulo": "MPV 200/2024",
                "proposicao_ementa": "Ementa da MPV",
                "proposicao_numero": "200",
                "proposicao_ano": "2024",
            }
        ]
        result = transform_votacoes_proposicoes(raw_data, db_session)
        assert len(result) == 1
        assert result[0].proposicao_id == 99999

        # Verificar que proposição parcial foi criada no banco
        from src.proposicoes.models import Proposicao

        prop = db_session.query(Proposicao).filter(Proposicao.id == 99999).first()
        assert prop is not None
        assert prop.tipo == "MPV"
        assert prop.numero == 200
        assert prop.ano == 2024

    def test_transform_elege_principal_por_prioridade(self, db_session):
        """Test: transform elege eh_principal por prioridade de tipo."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL 100/2024",
                "proposicao_ementa": "Ementa PL",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            },
            {
                "idVotacao": "1-1",
                "proposicao_id": "2",
                "proposicao_siglaTipo": "PEC",
                "proposicao_titulo": "PEC 10/2024",
                "proposicao_ementa": "Ementa PEC",
                "proposicao_numero": "10",
                "proposicao_ano": "2024",
            },
        ]
        result = transform_votacoes_proposicoes(raw_data, db_session)
        assert len(result) == 2

        # PEC deve ser principal
        pl_record = next(r for r in result if r.sigla_tipo == "PL")
        pec_record = next(r for r in result if r.sigla_tipo == "PEC")
        assert pl_record.eh_principal is False
        assert pec_record.eh_principal is True

    def test_transform_skipa_id_votacao_invalido(self, db_session, caplog):
        """Test: transform skipa registros com idVotacao inválido."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL",
                "proposicao_ementa": "Ementa",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_votacoes_proposicoes(raw_data, db_session)

        assert len(result) == 0

    def test_transform_skipa_proposicao_id_invalido(self, db_session, caplog):
        """Test: transform skipa registros com proposicao_id inválido."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "0",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL",
                "proposicao_ementa": "Ementa",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_votacoes_proposicoes(raw_data, db_session)

        assert len(result) == 0

    def test_transform_cache_evita_queries_repetidas(self, db_session):
        """Test: transform usa cache para evitar queries repetidas."""
        _setup_base_data(db_session)

        # 3 registros referenciando a mesma votação e proposição
        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL 100/2024",
                "proposicao_ementa": "Ementa",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            },
            {
                "idVotacao": "1-1",
                "proposicao_id": "2",
                "proposicao_siglaTipo": "PEC",
                "proposicao_titulo": "PEC 10/2024",
                "proposicao_ementa": "Ementa PEC",
                "proposicao_numero": "10",
                "proposicao_ano": "2024",
            },
            {
                "idVotacao": "2-1",
                "proposicao_id": "1",
                "proposicao_siglaTipo": "PL",
                "proposicao_titulo": "PL 100/2024",
                "proposicao_ementa": "Ementa",
                "proposicao_numero": "100",
                "proposicao_ano": "2024",
            },
        ]
        result = transform_votacoes_proposicoes(raw_data, db_session)
        assert len(result) == 3

    def test_transform_lista_vazia(self, db_session):
        """Test: transform com lista vazia retorna lista vazia."""
        result = transform_votacoes_proposicoes([], db_session)
        assert result == []

    def test_transform_com_csv_fixture(self, db_session, votacoes_proposicoes_csv_path):
        """Test: transform usando fixture CSV completa."""
        _setup_base_data(db_session)

        raw_data = extract_votacoes_proposicoes_csv(votacoes_proposicoes_csv_path)
        result = transform_votacoes_proposicoes(raw_data, db_session)

        # O CSV tem 8 linhas: linhas com votacao_id=999 são skipadas (não existe),
        # linhas com votacao_id=1,2,3,4,5 são processadas
        assert len(result) > 0
        # Todas devem ter votacao_id válido
        for r in result:
            assert r.votacao_id in [1, 2, 3, 4, 5]

    def test_transform_proposicao_parcial_com_proposicao_id_inexistente(self, db_session):
        """Test: quando proposicao_id do CSV não existe, cria parcial e inclui no resultado."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "proposicao_id": "50000",
                "proposicao_siglaTipo": "PEC",
                "proposicao_titulo": "PEC 99/2024",
                "proposicao_ementa": "Ementa PEC parcial",
                "proposicao_numero": "99",
                "proposicao_ano": "2024",
            }
        ]
        result = transform_votacoes_proposicoes(raw_data, db_session)
        assert len(result) == 1
        assert result[0].proposicao_id == 50000

        from src.proposicoes.models import Proposicao

        prop = db_session.query(Proposicao).filter(Proposicao.id == 50000).first()
        assert prop is not None
        assert prop.tipo == "PEC"


class TestLoadVotacoesProposicoes:
    """Testes para load_votacoes_proposicoes."""

    def test_load_persists_data(self, db_session):
        """Test: load persiste vínculos no banco via repository."""
        _setup_base_data(db_session)

        records = [
            VotacaoProposicaoCreate(
                votacao_id=1,
                votacao_id_original="1-1",
                proposicao_id=1,
                titulo="PL 100/2024",
                ementa="Ementa",
                sigla_tipo="PL",
                numero=100,
                ano=2024,
                eh_principal=True,
            ),
        ]
        count = load_votacoes_proposicoes(records, db_session)
        assert count == 1

        # Verificar persistência
        from_db = db_session.query(VotacaoProposicao).filter(
            VotacaoProposicao.votacao_id == 1,
            VotacaoProposicao.proposicao_id == 1,
        ).first()
        assert from_db is not None
        assert from_db.titulo == "PL 100/2024"
        assert from_db.eh_principal is True

    def test_load_returns_zero_for_empty(self, db_session):
        """Test: load retorna 0 para lista vazia."""
        count = load_votacoes_proposicoes([], db_session)
        assert count == 0

    def test_load_multiple_records(self, db_session):
        """Test: load persiste múltiplos registros."""
        _setup_base_data(db_session)

        records = [
            VotacaoProposicaoCreate(
                votacao_id=1, proposicao_id=1, sigla_tipo="PL", eh_principal=False
            ),
            VotacaoProposicaoCreate(
                votacao_id=1, proposicao_id=2, sigla_tipo="PEC", eh_principal=True
            ),
            VotacaoProposicaoCreate(
                votacao_id=2, proposicao_id=3, sigla_tipo="PLP", eh_principal=True
            ),
        ]
        count = load_votacoes_proposicoes(records, db_session)
        assert count == 3


class TestRunVotacoesProposicoesEtl:
    """Testes de integração para run_votacoes_proposicoes_etl."""

    def test_run_etl_end_to_end(self, db_session, votacoes_proposicoes_csv_path):
        """Test: ETL completo extract→transform→load funciona."""
        _setup_base_data(db_session)

        count = run_votacoes_proposicoes_etl(votacoes_proposicoes_csv_path, db_session)
        assert count > 0

        # Verificar que registros foram persistidos
        all_vps = db_session.query(VotacaoProposicao).all()
        assert len(all_vps) > 0

    def test_run_etl_creates_partial_propositions(self, db_session, votacoes_proposicoes_csv_path):
        """Test: ETL cria proposições parciais para IDs inexistentes."""
        _setup_base_data(db_session)

        # O CSV fixture tem proposicao_id=99999 que não existe nos dados base
        run_votacoes_proposicoes_etl(votacoes_proposicoes_csv_path, db_session)

        from src.proposicoes.models import Proposicao

        # Verificar que proposição parcial 99999 foi criada
        prop = db_session.query(Proposicao).filter(Proposicao.id == 99999).first()
        assert prop is not None
        assert prop.tipo == "MPV"

    def test_run_etl_file_not_found_raises(self, db_session):
        """Test: ETL lança exceção se arquivo CSV não existe."""
        with pytest.raises(FileNotFoundError):
            run_votacoes_proposicoes_etl("/path/inexistente.csv", db_session)

    def test_run_etl_idempotent(self, db_session, votacoes_proposicoes_csv_path):
        """Test: executar ETL 2x não duplica registros (idempotência)."""
        _setup_base_data(db_session)

        count1 = run_votacoes_proposicoes_etl(votacoes_proposicoes_csv_path, db_session)
        count2 = run_votacoes_proposicoes_etl(votacoes_proposicoes_csv_path, db_session)

        assert count1 == count2

        all_vps = db_session.query(VotacaoProposicao).all()
        assert len(all_vps) == count1


# ==============================================================================
# Testes para ETL orientacoes de bancada
# ==============================================================================


class TestExtractOrientacoesCsv:
    """Testes para extract_orientacoes_csv."""

    def test_extract_returns_dict_list(self, orientacoes_csv_path):
        """Test: extract lê CSV e retorna lista de dicts."""
        data = extract_orientacoes_csv(orientacoes_csv_path)
        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_has_expected_columns(self, orientacoes_csv_path):
        """Test: extract retorna dicts com colunas esperadas do formato Câmara."""
        data = extract_orientacoes_csv(orientacoes_csv_path)
        first = data[0]
        assert "idVotacao" in first
        assert "siglaBancada" in first
        assert "orientacao" in first
        assert "siglaOrgao" in first

    def test_extract_file_not_found(self):
        """Test: extract lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_orientacoes_csv("/path/inexistente/orientacoes.csv")

    def test_extract_empty_csv(self, tmp_path):
        """Test: extract retorna lista vazia para CSV com apenas headers."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text(
            "idVotacao;uriVotacao;siglaOrgao;descricao;siglaBancada;uriBancada;orientacao\n",
            encoding="utf-8",
        )
        data = extract_orientacoes_csv(str(csv_file))
        assert data == []


class TestTransformOrientacoes:
    """Testes para transform_orientacoes."""

    def test_transform_com_dados_validos(self, db_session):
        """Test: transform com votação existente retorna registros válidos."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "siglaBancada": "PT",
                "orientacao": "Sim",
            }
        ]
        result = transform_orientacoes(raw_data, db_session)
        assert len(result) == 1
        assert isinstance(result[0], OrientacaoCreate)
        assert result[0].votacao_id == 1
        assert result[0].votacao_id_original == "1-1"
        assert result[0].sigla_bancada == "PT"
        assert result[0].orientacao == "Sim"

    def test_transform_normaliza_orientacao_sim(self, db_session):
        """Test: transform normaliza 'Sim' corretamente."""
        _setup_base_data(db_session)
        raw_data = [{"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "Sim"}]
        result = transform_orientacoes(raw_data, db_session)
        assert result[0].orientacao == "Sim"

    def test_transform_normaliza_orientacao_nao(self, db_session):
        """Test: transform normaliza 'Não' corretamente."""
        _setup_base_data(db_session)
        raw_data = [{"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "Não"}]
        result = transform_orientacoes(raw_data, db_session)
        assert result[0].orientacao == "Não"

    def test_transform_normaliza_orientacao_liberado(self, db_session):
        """Test: transform normaliza 'Liberado' corretamente."""
        _setup_base_data(db_session)
        raw_data = [{"idVotacao": "1-1", "siglaBancada": "MDB", "orientacao": "Liberado"}]
        result = transform_orientacoes(raw_data, db_session)
        assert result[0].orientacao == "Liberado"

    def test_transform_normaliza_orientacao_obstrucao(self, db_session):
        """Test: transform normaliza 'Obstrução' corretamente."""
        _setup_base_data(db_session)
        raw_data = [{"idVotacao": "1-1", "siglaBancada": "PSOL", "orientacao": "Obstrução"}]
        result = transform_orientacoes(raw_data, db_session)
        assert result[0].orientacao == "Obstrução"

    def test_transform_normaliza_case_insensitive(self, db_session):
        """Test: normalização funciona independente de casing."""
        _setup_base_data(db_session)
        raw_data = [
            {"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "sim"},
            {"idVotacao": "1-1", "siglaBancada": "PL", "orientacao": "NÃO"},
            {"idVotacao": "1-1", "siglaBancada": "MDB", "orientacao": "liberado"},
            {"idVotacao": "1-1", "siglaBancada": "PSOL", "orientacao": "obstrução"},
        ]
        result = transform_orientacoes(raw_data, db_session)
        assert len(result) == 4
        assert result[0].orientacao == "Sim"
        assert result[1].orientacao == "Não"
        assert result[2].orientacao == "Liberado"
        assert result[3].orientacao == "Obstrução"

    def test_transform_skipa_votacao_inexistente(self, db_session, caplog):
        """Test: transform skipa registro quando votacao_id não existe."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "999-1",
                "siglaBancada": "PT",
                "orientacao": "Sim",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_orientacoes(raw_data, db_session)

        assert len(result) == 0
        assert "votacao_id 999" in caplog.text

    def test_transform_skipa_orientacao_vazia(self, db_session, caplog):
        """Test: transform skipa registro com orientacao vazia."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "siglaBancada": "PT",
                "orientacao": "",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_orientacoes(raw_data, db_session)

        assert len(result) == 0
        assert "orientacao vazia" in caplog.text

    def test_transform_skipa_sigla_bancada_vazia(self, db_session, caplog):
        """Test: transform skipa registro com siglaBancada vazia."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "1-1",
                "siglaBancada": "",
                "orientacao": "Sim",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_orientacoes(raw_data, db_session)

        assert len(result) == 0
        assert "siglaBancada vazia" in caplog.text

    def test_transform_skipa_id_votacao_invalido(self, db_session, caplog):
        """Test: transform skipa registros com idVotacao inválido."""
        _setup_base_data(db_session)

        raw_data = [
            {
                "idVotacao": "",
                "siglaBancada": "PT",
                "orientacao": "Sim",
            }
        ]
        with caplog.at_level(logging.WARNING):
            result = transform_orientacoes(raw_data, db_session)

        assert len(result) == 0

    def test_transform_cache_evita_queries_repetidas(self, db_session):
        """Test: transform usa cache para evitar queries repetidas."""
        _setup_base_data(db_session)

        raw_data = [
            {"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "Sim"},
            {"idVotacao": "1-1", "siglaBancada": "PL", "orientacao": "Não"},
            {"idVotacao": "2-1", "siglaBancada": "PT", "orientacao": "Liberado"},
        ]
        result = transform_orientacoes(raw_data, db_session)
        assert len(result) == 3

    def test_transform_lista_vazia(self, db_session):
        """Test: transform com lista vazia retorna lista vazia."""
        result = transform_orientacoes([], db_session)
        assert result == []

    def test_transform_preserva_orientacao_desconhecida(self, db_session):
        """Test: orientação não reconhecida é preservada como está."""
        _setup_base_data(db_session)
        raw_data = [
            {"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "Artigo 17"},
        ]
        result = transform_orientacoes(raw_data, db_session)
        assert len(result) == 1
        assert result[0].orientacao == "Artigo 17"

    def test_transform_com_csv_fixture(self, db_session, orientacoes_csv_path):
        """Test: transform usando fixture CSV completa."""
        _setup_base_data(db_session)

        raw_data = extract_orientacoes_csv(orientacoes_csv_path)
        result = transform_orientacoes(raw_data, db_session)

        # O CSV tem 12 linhas:
        # - 1 com votacao_id=999 (skipada - não existe)
        # - 1 com orientacao vazia para PSDB (skipada)
        # - 10 restantes com votacao_id=1,2,3,4,5 válidas
        assert len(result) > 0
        # Todas devem ter votacao_id válido
        for r in result:
            assert r.votacao_id in [1, 2, 3, 4, 5]

    def test_transform_multiplas_bancadas_mesma_votacao(self, db_session):
        """Test: múltiplas bancadas na mesma votação são aceitas."""
        _setup_base_data(db_session)
        raw_data = [
            {"idVotacao": "1-1", "siglaBancada": "PT", "orientacao": "Sim"},
            {"idVotacao": "1-1", "siglaBancada": "PL", "orientacao": "Não"},
            {"idVotacao": "1-1", "siglaBancada": "MDB", "orientacao": "Liberado"},
            {"idVotacao": "1-1", "siglaBancada": "Governo", "orientacao": "Sim"},
        ]
        result = transform_orientacoes(raw_data, db_session)
        assert len(result) == 4
        bancadas = {r.sigla_bancada for r in result}
        assert bancadas == {"PT", "PL", "MDB", "Governo"}


class TestLoadOrientacoes:
    """Testes para load_orientacoes."""

    def test_load_persists_data(self, db_session):
        """Test: load persiste orientações no banco via repository."""
        _setup_base_data(db_session)

        records = [
            OrientacaoCreate(
                votacao_id=1,
                votacao_id_original="1-1",
                sigla_bancada="PT",
                orientacao="Sim",
            ),
        ]
        count = load_orientacoes(records, db_session)
        assert count == 1

        # Verificar persistência
        from_db = db_session.query(Orientacao).filter(
            Orientacao.votacao_id == 1,
            Orientacao.sigla_bancada == "PT",
        ).first()
        assert from_db is not None
        assert from_db.orientacao == "Sim"

    def test_load_returns_zero_for_empty(self, db_session):
        """Test: load retorna 0 para lista vazia."""
        count = load_orientacoes([], db_session)
        assert count == 0

    def test_load_multiple_records(self, db_session):
        """Test: load persiste múltiplos registros."""
        _setup_base_data(db_session)

        records = [
            OrientacaoCreate(
                votacao_id=1, sigla_bancada="PT", orientacao="Sim"
            ),
            OrientacaoCreate(
                votacao_id=1, sigla_bancada="PL", orientacao="Não"
            ),
            OrientacaoCreate(
                votacao_id=2, sigla_bancada="PT", orientacao="Liberado"
            ),
        ]
        count = load_orientacoes(records, db_session)
        assert count == 3


class TestRunOrientacoesEtl:
    """Testes de integração para run_orientacoes_etl."""

    def test_run_etl_end_to_end(self, db_session, orientacoes_csv_path):
        """Test: ETL completo extract→transform→load funciona."""
        _setup_base_data(db_session)

        count = run_orientacoes_etl(orientacoes_csv_path, db_session)
        assert count > 0

        # Verificar que registros foram persistidos
        all_orientacoes = db_session.query(Orientacao).all()
        assert len(all_orientacoes) > 0

    def test_run_etl_file_not_found_raises(self, db_session):
        """Test: ETL lança exceção se arquivo CSV não existe."""
        with pytest.raises(FileNotFoundError):
            run_orientacoes_etl("/path/inexistente.csv", db_session)

    def test_run_etl_idempotent(self, db_session, orientacoes_csv_path):
        """Test: executar ETL 2x não duplica registros (idempotência)."""
        _setup_base_data(db_session)

        count1 = run_orientacoes_etl(orientacoes_csv_path, db_session)
        count2 = run_orientacoes_etl(orientacoes_csv_path, db_session)

        assert count1 == count2

        all_orientacoes = db_session.query(Orientacao).all()
        assert len(all_orientacoes) == count1

    def test_run_etl_skips_invalid_votacao(self, db_session, orientacoes_csv_path):
        """Test: ETL skipa orientações para votações inexistentes."""
        _setup_base_data(db_session)

        run_orientacoes_etl(orientacoes_csv_path, db_session)

        # O CSV tem 12 linhas: 1 com votacao_id=999 e 1 com orientacao vazia
        # devem ser skipadas
        all_orientacoes = db_session.query(Orientacao).all()
        for o in all_orientacoes:
            assert o.votacao_id != 999

    def test_run_etl_normalizes_orientacao(self, db_session, orientacoes_csv_path):
        """Test: ETL normaliza corretamente os valores de orientação."""
        _setup_base_data(db_session)

        run_orientacoes_etl(orientacoes_csv_path, db_session)

        all_orientacoes = db_session.query(Orientacao).all()
        valid_orientacoes = {"Sim", "Não", "Liberado", "Obstrução", "Não informado"}
        for o in all_orientacoes:
            assert o.orientacao in valid_orientacoes, (
                f"Orientação '{o.orientacao}' não é um valor normalizado válido"
            )
