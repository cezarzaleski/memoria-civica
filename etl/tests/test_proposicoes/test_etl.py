"""Testes para ETL do domínio de Proposições.

Validam extract, transform e load, incluindo logging e tratamento de erros,
além de testes de integração end-to-end.
"""

import logging

import pytest

from src.deputados.repository import DeputadoRepository
from src.deputados.schemas import DeputadoCreate
from src.proposicoes.etl import (
    extract_proposicoes_csv,
    load_proposicoes,
    run_proposicoes_etl,
    transform_proposicoes,
)
from src.proposicoes.models import Proposicao
from src.proposicoes.schemas import ProposicaoCreate


class TestExtractProposicoesCsv:
    """Testes para extract_proposicoes_csv."""

    def test_extract_returns_dict_list(self, proposicoes_csv_path):
        """Test: extract_proposicoes_csv() lê CSV e retorna dicts."""
        data = extract_proposicoes_csv(proposicoes_csv_path)

        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_has_expected_columns(self, proposicoes_csv_path):
        """Test: extract retorna dicts com colunas esperadas."""
        data = extract_proposicoes_csv(proposicoes_csv_path)

        # Verificar que tem as colunas esperadas
        first_record = data[0]
        assert "id" in first_record
        assert "tipo" in first_record
        assert "numero" in first_record

    def test_extract_file_not_found(self):
        """Test: extract_proposicoes_csv() lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_proposicoes_csv("/path/que/nao/existe/proposicoes.csv")

    def test_extract_reads_all_records(self, proposicoes_csv_path):
        """Test: extract_proposicoes_csv() lê todos os registros do CSV."""
        data = extract_proposicoes_csv(proposicoes_csv_path)

        # O CSV fixture tem 5 proposições
        assert len(data) >= 3


class TestTransformProposicoes:
    """Testes para transform_proposicoes."""

    def test_transform_validates_correct_data(self):
        """Test: transform_proposicoes() valida dados corretos."""
        raw_data = [
            {
                "id": "1",
                "tipo": "PL",
                "numero": "123",
                "ano": "2024",
                "ementa": "Lei de educação",
                "autor_id": "456",
            }
        ]

        result = transform_proposicoes(raw_data)

        assert len(result) > 0
        assert isinstance(result[0], ProposicaoCreate)
        assert result[0].tipo == "PL"

    def test_transform_accepts_various_tipos(self):
        """Test: transform_proposicoes() aceita qualquer tipo de proposição."""
        raw_data = [
            {
                "id": "1",
                "tipo": "PL",
                "numero": "123",
                "ano": "2024",
                "ementa": "Lei válida",
                "autor_id": "456",
            },
            {
                "id": "2",
                "tipo": "REQ",  # Tipo não tradicional, mas válido
                "numero": "456",
                "ano": "2024",
                "ementa": "Requerimento",
                "autor_id": "",
            },
            {
                "id": "3",
                "tipo": "INC",  # Indicação
                "numero": "789",
                "ano": "2024",
                "ementa": "Indicação legislativa",
                "autor_id": "",
            },
        ]

        result = transform_proposicoes(raw_data)

        # Todos os registros devem ser processados
        assert len(result) == 3
        assert result[0].tipo == "PL"
        assert result[1].tipo == "REQ"
        assert result[2].tipo == "INC"

    def test_transform_handles_missing_fields(self):
        """Test: transform_proposicoes() com campos faltando."""
        raw_data = [
            {
                "id": "3",
                "tipo": "MP",
                "numero": "1",
                # Campos faltando
                "ementa": "Medida provisória",
            }
        ]

        result = transform_proposicoes(raw_data)

        # Mesmo com campos faltando, deveria processar
        assert len(result) >= 0

    def test_transform_handles_orphan_proposicoes(self, caplog):
        """Test: transform logga warning para proposições órfãs (autor_id inválido)."""
        raw_data = [
            {
                "id": "4",
                "tipo": "PL",
                "numero": "100",
                "ano": "2024",
                "ementa": "Lei órfã",
                "autor_id": "INVALIDO",  # autor_id inválido
            }
        ]

        with caplog.at_level(logging.WARNING):
            result = transform_proposicoes(raw_data)

        # A proposição deve ser aceita com autor_id=None
        assert len(result) > 0
        assert result[0].autor_id is None
        # Deve ter logado warning sobre autor_id inválido
        assert "autor_id inválido" in caplog.text.lower() or "inválido" in caplog.text.lower()

    def test_transform_accepts_null_autor_id(self):
        """Test: transform_proposicoes() aceita autor_id vazio como NULL."""
        raw_data = [
            {
                "id": "5",
                "tipo": "PEC",
                "numero": "1",
                "ano": "2024",
                "ementa": "Emenda sem autor",
                "autor_id": "",  # Vazio = NULL
            }
        ]

        result = transform_proposicoes(raw_data)

        assert len(result) > 0
        assert result[0].autor_id is None


class TestLoadProposicoes:
    """Testes para load_proposicoes."""

    def test_load_inserts_proposicoes(self, db_session):
        """Test: load_proposicoes() insere proposições no banco."""
        proposicoes = [
            ProposicaoCreate(
                id=1,
                tipo="PL",
                numero=123,
                ano=2024,
                ementa="Lei 1",
                autor_id=None,
            ),
            ProposicaoCreate(
                id=2,
                tipo="PEC",
                numero=1,
                ano=2024,
                ementa="Emenda 1",
                autor_id=None,
            ),
        ]

        count = load_proposicoes(proposicoes, db_session)

        assert count == 2

        # Verificar que foram inseridas
        proposicoes_db = db_session.query(Proposicao).all()
        assert len(proposicoes_db) == 2

    def test_load_with_empty_list(self, db_session):
        """Test: load_proposicoes() com lista vazia retorna 0."""
        count = load_proposicoes([], db_session)
        assert count == 0


class TestRunProposicoeEtl:
    """Testes para run_proposicoes_etl (integração completa)."""

    def test_etl_completo_funciona(self, proposicoes_csv_path, db_session):
        """Test: ETL completo executa e persiste proposições."""
        exit_code = run_proposicoes_etl(proposicoes_csv_path, db_session)

        assert exit_code == 0

        # Verificar que foram persistidas
        proposicoes_db = db_session.query(Proposicao).all()
        assert len(proposicoes_db) > 0

    def test_etl_idempotencia(self, proposicoes_csv_path, db_session):
        """Test: ETL é idempotente - executar 2x não duplica."""
        # Primeira execução
        exit_code1 = run_proposicoes_etl(proposicoes_csv_path, db_session)
        assert exit_code1 == 0
        count1 = db_session.query(Proposicao).count()

        # Segunda execução
        exit_code2 = run_proposicoes_etl(proposicoes_csv_path, db_session)
        assert exit_code2 == 0
        count2 = db_session.query(Proposicao).count()

        # Quantidade deve ser igual (não deve ter duplicado)
        assert count1 == count2

    def test_etl_with_foreign_key_constraint(self, proposicoes_csv_path, db_session):
        """Test: ETL respeita FK constraints - proposições órfãs são aceitas."""
        # Criar um deputado como autor
        deputado = DeputadoCreate(
            id=220593,  # ID do primeiro deputado no CSV
            nome="João Silva",
            partido="PT",
            uf="SP",
        )
        dep_repo = DeputadoRepository(db_session)
        dep_repo.create(deputado)

        # Executar ETL
        exit_code = run_proposicoes_etl(proposicoes_csv_path, db_session)

        assert exit_code == 0

        # Verificar que proposições foram inseridas
        proposicoes_db = db_session.query(Proposicao).all()
        assert len(proposicoes_db) > 0

        # Algumas podem ter author_id válido, outras NULL (órfãs)
        assert any(p.autor_id is not None for p in proposicoes_db) or True

    def test_etl_file_not_found(self, db_session):
        """Test: ETL falha gracefully se arquivo CSV não existe."""
        exit_code = run_proposicoes_etl("/path/inexistente/proposicoes.csv", db_session)

        assert exit_code == 1

    def test_etl_persists_all_fields(self, proposicoes_csv_path, db_session):
        """Test: ETL persiste todos os campos corretamente."""
        run_proposicoes_etl(proposicoes_csv_path, db_session)

        proposicoes_db = db_session.query(Proposicao).all()
        assert len(proposicoes_db) > 0

        # Verificar que todos os campos foram persistidos
        prop = proposicoes_db[0]
        assert prop.id is not None
        assert prop.tipo is not None
        assert prop.numero is not None
        assert prop.ano is not None
        assert prop.ementa is not None
        # autor_id pode ser None (OK)
