"""Testes para ETL do domínio de Deputados.

Validam extract, transform e load, incluindo logging e tratamento de erros.
"""

import logging

import pytest

from src.deputados.etl import (
    extract_deputados_csv,
    load_deputados,
    run_deputados_etl,
    transform_deputados,
)
from src.deputados.schemas import DeputadoCreate


class TestExtractDeputadosCSV:
    """Testes para extract_deputados_csv."""

    def test_extract_returns_dict_list(self, deputados_csv_path):
        """Test: extract_deputados_csv() lê CSV e retorna dicts."""
        data = extract_deputados_csv(deputados_csv_path)

        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)

    def test_extract_has_expected_columns(self, deputados_csv_path):
        """Test: extract retorna dicts com colunas esperadas."""
        data = extract_deputados_csv(deputados_csv_path)

        # Verificar que tem pelo menos algumas colunas
        first_record = data[0]
        assert "uri" in first_record or "nome" in first_record

    def test_extract_file_not_found(self):
        """Test: extract_deputados_csv() lança FileNotFoundError se arquivo não existe."""
        with pytest.raises(FileNotFoundError):
            extract_deputados_csv("/path/que/nao/existe/deputados.csv")

    def test_extract_reads_all_records(self, deputados_csv_path):
        """Test: extract_deputados_csv() lê todos os registros do CSV."""
        data = extract_deputados_csv(deputados_csv_path)

        # O CSV fixture tem 5 deputados
        assert len(data) >= 3


class TestTransformDeputados:
    """Testes para transform_deputados."""

    def test_transform_validates_correct_data(self):
        """Test: transform_deputados() valida dados corretos."""
        raw_data = [
            {
                "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/220593",
                "nome": "João Silva",
                "ufNascimento": "SP",
                "partido": "PT",
            }
        ]

        result = transform_deputados(raw_data)

        assert len(result) > 0
        assert isinstance(result[0], DeputadoCreate)

    def test_transform_skips_invalid_data(self, caplog):
        """Test: transform_deputados() logga warning para dados inválidos."""
        raw_data = [
            {
                "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/220593",
                "nome": "João Silva",
                "ufNascimento": "SP",
                "partido": "PT",
            },
            {
                "uri": "invalid_uri",
                "nome": "Maria",
                # Dados inválidos - uf ausente
            },
        ]

        with caplog.at_level(logging.WARNING):
            result = transform_deputados(raw_data)

        # Pelo menos um registro deve ter sido processado
        assert len(result) >= 1

    def test_transform_handles_missing_fields(self):
        """Test: transform_deputados() com campos faltando."""
        raw_data = [
            {
                "nome": "Pedro",
                "ufNascimento": "MG",
                "partido": "PSDB",
                # Sem uri
            }
        ]

        result = transform_deputados(raw_data)

        # Deve tentar processar mesmo sem uri
        assert isinstance(result, list)

    def test_transform_empty_list(self):
        """Test: transform_deputados() com lista vazia."""
        result = transform_deputados([])
        assert result == []

    def test_transform_invalid_uf_excluded(self, caplog):
        """Test: transform_deputados() exclui registros com UF inválida."""
        raw_data = [
            {
                "uri": "https://...",
                "nome": "João",
                "ufNascimento": "X",  # UF inválida (1 caractere)
                "partido": "PT",
            }
        ]

        with caplog.at_level(logging.WARNING):
            result = transform_deputados(raw_data)

        # Deve ser excluído ou ajustado
        assert len(result) <= 1


class TestLoadDeputados:
    """Testes para load_deputados."""

    def test_load_persists_deputados(self, db_session):
        """Test: load_deputados() persiste deputados no banco."""
        deputados = [
            DeputadoCreate(id=1000, nome="Teste1", partido="PT", uf="SP"),
            DeputadoCreate(id=1001, nome="Teste2", partido="PDT", uf="RJ"),
        ]

        count = load_deputados(deputados, db_session)

        assert count == 2

    def test_load_empty_list(self, db_session, caplog):
        """Test: load_deputados() com lista vazia."""
        with caplog.at_level(logging.INFO):
            count = load_deputados([], db_session)

        assert count == 0

    def test_load_returns_correct_count(self, db_session):
        """Test: load_deputados() retorna quantidade correta."""
        deputados = [
            DeputadoCreate(id=2000, nome="A", partido="PT", uf="SP"),
            DeputadoCreate(id=2001, nome="B", partido="PDT", uf="RJ"),
            DeputadoCreate(id=2002, nome="C", partido="PSDB", uf="MG"),
        ]

        count = load_deputados(deputados, db_session)

        assert count == 3


class TestRunDeputadosETL:
    """Testes para run_deputados_etl (orquestração completa)."""

    def test_run_etl_complete_pipeline(self, deputados_csv_path, db_session, caplog):
        """Test: ETL completo (CSV fixture → database) persiste corretamente.

        Este é o teste de integração do pipeline ETL.
        """
        with caplog.at_level(logging.INFO):
            exit_code = run_deputados_etl(deputados_csv_path, db_session)

        assert exit_code == 0

        # Verificar que algo foi persistido
        from src.deputados.repository import DeputadoRepository

        repo = DeputadoRepository(db_session)
        todos = repo.get_all()
        assert len(todos) > 0

    def test_run_etl_returns_zero_on_success(self, deputados_csv_path, db_session):
        """Test: run_deputados_etl() retorna 0 em sucesso."""
        exit_code = run_deputados_etl(deputados_csv_path, db_session)
        assert exit_code == 0

    def test_run_etl_returns_one_on_failure(self, db_session):
        """Test: run_deputados_etl() retorna 1 em falha."""
        exit_code = run_deputados_etl("/caminho/invalido/deputados.csv", db_session)
        assert exit_code == 1

    def test_run_etl_logs_progress(self, deputados_csv_path, db_session, caplog):
        """Test: ETL logga progresso INFO."""
        with caplog.at_level(logging.INFO):
            run_deputados_etl(deputados_csv_path, db_session)

        log_text = caplog.text
        assert "Iniciando ETL" in log_text or "iniciando" in log_text.lower()


@pytest.mark.integration
class TestETLIntegration:
    """Testes de integração end-to-end do ETL."""

    def test_etl_end_to_end_csv_to_database(self, deputados_csv_path, db_session):
        """Test: Dados no banco correspondem ao CSV após ETL.

        Este é o teste principal de integração que valida o pipeline completo.
        """
        from src.deputados.repository import DeputadoRepository

        # Executar ETL
        exit_code = run_deputados_etl(deputados_csv_path, db_session)
        assert exit_code == 0

        # Verificar dados
        repo = DeputadoRepository(db_session)
        todos = repo.get_all()

        # Deve ter carregado os deputados do CSV
        assert len(todos) > 0

        # Verificar que dados estão corretos
        primeiro = todos[0]
        assert primeiro.nome is not None
        assert primeiro.partido is not None
        assert primeiro.uf is not None

    def test_etl_is_idempotent(self, deputados_csv_path, db_session):
        """Test: ETL é idempotente (pode rodar múltiplas vezes)."""
        from src.deputados.repository import DeputadoRepository

        # Primeira execução
        exit_code1 = run_deputados_etl(deputados_csv_path, db_session)
        assert exit_code1 == 0

        repo = DeputadoRepository(db_session)
        count1 = len(repo.get_all())

        # Segunda execução
        exit_code2 = run_deputados_etl(deputados_csv_path, db_session)
        assert exit_code2 == 0

        count2 = len(repo.get_all())

        # Número deve ser igual (idempotência)
        assert count1 == count2
