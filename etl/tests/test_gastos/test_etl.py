"""Testes para ETL do domínio de Gastos."""

from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

import pytest

from src.deputados.models import Deputado
from src.gastos.etl import (
    extract_gastos_csv,
    load_gastos,
    parse_data_documento,
    parse_valor_brasileiro,
    run_gastos_etl,
    transform_gastos,
)
from src.gastos.models import Gasto
from src.gastos.schemas import GastoCreate


def _seed_deputados(db_session) -> None:
    """Cria deputados de apoio para validação de FK nos testes."""
    db_session.add_all(
        [
            Deputado(id=1001, nome="Deputada 1001", partido="PT", uf="SP"),
            Deputado(id=1002, nome="Deputado 1002", partido="PSB", uf="RJ"),
        ]
    )
    db_session.commit()


class TestHelpers:
    """Testes para helpers internos de parsing."""

    def test_parse_valor_brasileiro_with_thousand_separator(self):
        """Test: converte valor brasileiro com milhar e vírgula decimal."""
        assert parse_valor_brasileiro("1.234,56") == Decimal("1234.56")

    def test_parse_valor_brasileiro_with_empty_and_invalid_values(self):
        """Test: converte vazio/inválido para zero sem quebrar pipeline."""
        assert parse_valor_brasileiro("") == Decimal("0")
        assert parse_valor_brasileiro(None) == Decimal("0")
        assert parse_valor_brasileiro("valor_invalido") == Decimal("0")

    def test_parse_data_documento_supports_multiple_formats(self):
        """Test: converte datas no formato ISO e dd/mm/yyyy."""
        assert str(parse_data_documento("2024-01-31")) == "2024-01-31"
        assert str(parse_data_documento("31/01/2024")) == "2024-01-31"
        assert parse_data_documento("data-invalida") is None


class TestExtractGastosCsv:
    """Testes para extract_gastos_csv."""

    def test_extract_returns_dict_list(self, gastos_csv_path):
        """Test: extract lê CSV fixture e retorna lista de dicts."""
        data = extract_gastos_csv(gastos_csv_path)

        assert isinstance(data, list)
        assert len(data) == 6
        assert isinstance(data[0], dict)

    def test_extract_has_expected_columns(self, gastos_csv_path):
        """Test: extract preserva colunas contratuais do CSV CEAP."""
        data = extract_gastos_csv(gastos_csv_path)
        first_record = data[0]

        assert "idDeputado" in first_record
        assert "tipoDespesa" in first_record
        assert "valorDocumento" in first_record

    def test_extract_file_not_found(self):
        """Test: extract lança FileNotFoundError para arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            extract_gastos_csv("/path/que/nao/existe/gastos.csv")

    def test_extract_raises_error_when_required_columns_are_missing(self, tmp_path: Path):
        """Test: extract falha quando colunas obrigatórias não existem no CSV."""
        invalid_csv = tmp_path / "gastos_invalidos.csv"
        invalid_csv.write_text("ano;mes\n2024;1\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
            extract_gastos_csv(str(invalid_csv))


class TestTransformGastos:
    """Testes para transform_gastos."""

    def test_transform_maps_and_normalizes_values(self, gastos_csv_path, db_session):
        """Test: transform aplica contrato CSV→schema e normalizações."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)

        result = transform_gastos(raw_data, db_session)

        assert len(result) == 6
        assert isinstance(result[0], GastoCreate)

        first = next(g for g in result if g.numero_documento == "DOC-001")
        assert first.deputado_id == 1001
        assert first.valor_documento == Decimal("1234.56")
        assert first.valor_liquido == Decimal("1200.00")
        assert first.valor_glosa == Decimal("34.56")

    def test_transform_sets_null_for_nonexistent_deputado(self, gastos_csv_path, db_session):
        """Test: FK inexistente em deputado vira NULL (None) na transformação."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)

        result = transform_gastos(raw_data, db_session)

        unknown_deputy_record = next(g for g in result if g.numero_documento == "DOC-003")
        assert unknown_deputy_record.deputado_id is None

    def test_transform_handles_optional_empty_fields(self, gastos_csv_path, db_session):
        """Test: campos opcionais vazios não quebram o pipeline."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)

        result = transform_gastos(raw_data, db_session)

        optional_empty = next(g for g in result if g.tipo_despesa == "ALIMENTACAO")
        assert optional_empty.tipo_documento is None
        assert optional_empty.data_documento is None
        assert optional_empty.numero_documento is None
        assert optional_empty.valor_documento == Decimal("0")
        assert optional_empty.valor_liquido == Decimal("0")
        assert optional_empty.valor_glosa == Decimal("0")

    def test_transform_converts_invalid_monetary_values_to_zero(self, gastos_csv_path, db_session):
        """Test: valores monetários inválidos são tratados como zero."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)

        result = transform_gastos(raw_data, db_session)

        invalid_monetary = next(g for g in result if g.numero_documento == "DOC-005")
        assert invalid_monetary.valor_documento == Decimal("0")
        assert invalid_monetary.valor_glosa == Decimal("0")
        assert invalid_monetary.valor_liquido == Decimal("120.50")


class TestLoadGastos:
    """Testes para load_gastos."""

    def test_load_persists_batch_and_returns_processed_count(self, gastos_csv_path, db_session):
        """Test: load persiste lote transformado e retorna contagem correta."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)
        gastos = transform_gastos(raw_data, db_session)

        count = load_gastos(gastos, db_session)

        assert count == 6
        assert db_session.query(Gasto).count() == 6

    def test_load_with_empty_list_returns_zero(self, db_session):
        """Test: load com lista vazia retorna zero."""
        assert load_gastos([], db_session) == 0

    def test_load_uses_get_db_when_session_is_none(self, gastos_csv_path, db_session, monkeypatch):
        """Test: load usa get_db quando `db=None`."""
        _seed_deputados(db_session)
        raw_data = extract_gastos_csv(gastos_csv_path)
        gastos = transform_gastos(raw_data, db_session)
        called = {"used_get_db": False}

        @contextmanager
        def fake_get_db():
            called["used_get_db"] = True
            yield db_session

        monkeypatch.setattr("src.gastos.etl.get_db", fake_get_db)

        count = load_gastos(gastos, db=None)

        assert called["used_get_db"] is True
        assert count == 6


class TestRunGastosEtl:
    """Testes de integração para run_gastos_etl."""

    def test_run_returns_zero_on_success(self, gastos_csv_path, db_session):
        """Test: run_gastos_etl retorna 0 e persiste dados em cenário válido."""
        _seed_deputados(db_session)

        exit_code = run_gastos_etl(gastos_csv_path, db_session)

        assert exit_code == 0
        assert db_session.query(Gasto).count() == 6

    def test_run_returns_one_on_failure(self, db_session):
        """Test: run_gastos_etl retorna 1 quando falha."""
        assert run_gastos_etl("/path/inexistente/gastos.csv", db_session) == 1

    def test_run_uses_get_db_when_session_is_none(self, gastos_csv_path, db_session, monkeypatch):
        """Test: run usa get_db quando `db=None`."""
        _seed_deputados(db_session)
        called = {"used_get_db": False}

        @contextmanager
        def fake_get_db():
            called["used_get_db"] = True
            yield db_session

        monkeypatch.setattr("src.gastos.etl.get_db", fake_get_db)

        exit_code = run_gastos_etl(gastos_csv_path, db=None)

        assert called["used_get_db"] is True
        assert exit_code == 0

    def test_run_missing_file_fails_before_opening_db(self, monkeypatch):
        """Test: run falha rápido para arquivo inexistente sem abrir sessão."""
        called = {"used_get_db": False}

        @contextmanager
        def fake_get_db():
            called["used_get_db"] = True
            yield None

        monkeypatch.setattr("src.gastos.etl.get_db", fake_get_db)

        exit_code = run_gastos_etl("/path/inexistente/gastos.csv", db=None)

        assert exit_code == 1
        assert called["used_get_db"] is False

    def test_run_is_idempotent_for_same_dataset(self, gastos_csv_path, db_session):
        """Test: reprocessar o mesmo CSV não duplica registros."""
        _seed_deputados(db_session)

        exit_code_first = run_gastos_etl(gastos_csv_path, db_session)
        count_first = db_session.query(Gasto).count()

        exit_code_second = run_gastos_etl(gastos_csv_path, db_session)
        count_second = db_session.query(Gasto).count()

        assert exit_code_first == 0
        assert exit_code_second == 0
        assert count_first == 6
        assert count_second == 6
