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
    extract_votacoes_csv,
    extract_votos_csv,
    load_votacoes,
    load_votos,
    run_votacoes_etl,
    transform_votacoes,
    transform_votos,
)
from src.votacoes.models import Votacao, Voto
from src.votacoes.schemas import VotacaoCreate, VotoCreate


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
            }
        ]

        result = transform_votacoes(raw_data)

        assert len(result) > 0
        assert isinstance(result[0], VotacaoCreate)
        assert result[0].resultado == "APROVADO"
        assert result[0].id == 123  # Extraído do "123-1"

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
        """Test: load_votacoes() persiste votações no banco."""
        votacoes = [
            VotacaoCreate(
                id=500,
                proposicao_id=1,
                data_hora=datetime(2024, 1, 15, 14, 30, 0),
                resultado="APROVADO",
            )
        ]

        count = load_votacoes(votacoes, db_session)

        assert count == 1

        # Verificar persistência
        from_db = db_session.query(Votacao).filter(Votacao.id == 500).first()
        assert from_db is not None
        assert from_db.proposicao_id == 1

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

        # Executar ETL (sem db para não validar FKs - FKs já foram criados acima)
        result = run_votacoes_etl(votacoes_csv_path, votos_csv_path, db=None)

        # Deve retornar sucesso
        assert result == 0
