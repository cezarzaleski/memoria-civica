"""Testes para schemas Pydantic do domínio de Gastos."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.gastos.schemas import GastoCreate, GastoRead


class TestGastoCreate:
    """Testes para schema GastoCreate."""

    def test_create_valid_gasto(self):
        """Test: GastoCreate aceita payload válido com campos obrigatórios."""
        gasto = GastoCreate(
            deputado_id=10,
            ano=2024,
            mes=4,
            tipo_despesa="DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR",
            valor_documento=Decimal("2500.40"),
            valor_liquido=Decimal("2500.40"),
            valor_glosa=Decimal("0.00"),
        )

        assert gasto.deputado_id == 10
        assert gasto.ano == 2024
        assert gasto.mes == 4
        assert gasto.tipo_despesa == "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR"
        assert gasto.valor_documento == Decimal("2500.40")

    def test_defaults_and_optional_fields(self):
        """Test: Campos opcionais/defaults seguem contrato."""
        gasto = GastoCreate(
            ano=2024,
            mes=5,
            tipo_despesa="PASSAGENS",
        )

        assert gasto.deputado_id is None
        assert gasto.tipo_documento is None
        assert gasto.data_documento is None
        assert gasto.numero_documento is None
        assert gasto.valor_documento == Decimal("0")
        assert gasto.valor_liquido == Decimal("0")
        assert gasto.valor_glosa == Decimal("0")
        assert gasto.parcela == 0

    def test_decimal_and_date_parsing(self):
        """Test: GastoCreate faz parsing de Decimal e date a partir de string."""
        gasto = GastoCreate(
            ano=2024,
            mes=6,
            tipo_despesa="COMBUSTÍVEL",
            data_documento="2024-06-12",
            valor_documento="123.45",
            valor_liquido="120.00",
            valor_glosa="3.45",
        )

        assert isinstance(gasto.data_documento, date)
        assert gasto.data_documento == date(2024, 6, 12)
        assert gasto.valor_documento == Decimal("123.45")
        assert gasto.valor_liquido == Decimal("120.00")
        assert gasto.valor_glosa == Decimal("3.45")

    def test_create_rejects_missing_required_fields(self):
        """Test: GastoCreate rejeita quando faltam campos obrigatórios."""
        with pytest.raises(ValidationError):
            GastoCreate(
                ano=2024,
                mes=7,
                # Falta tipo_despesa
            )

    def test_create_rejects_invalid_mes(self):
        """Test: GastoCreate rejeita mês inválido fora de 1..12."""
        with pytest.raises(ValidationError):
            GastoCreate(
                ano=2024,
                mes=13,
                tipo_despesa="HOSPEDAGEM",
            )


class TestGastoRead:
    """Testes para schema GastoRead."""

    def test_read_from_attributes(self):
        """Test: GastoRead suporta model_validate com from_attributes."""

        class MockGasto:
            id = 100
            deputado_id = 1
            ano = 2024
            mes = 8
            tipo_despesa = "ALUGUEL DE VEÍCULOS"
            tipo_documento = "RECIBO"
            data_documento = date(2024, 8, 20)
            numero_documento = "R-999"
            valor_documento = Decimal("980.55")
            valor_liquido = Decimal("980.55")
            valor_glosa = Decimal("0.00")
            nome_fornecedor = "Fornecedor X"
            cnpj_cpf_fornecedor = "99888777000166"
            url_documento = "https://example.com/recibo"
            cod_documento = 321
            cod_lote = 654
            parcela = 2

        gasto = GastoRead.model_validate(MockGasto())
        assert gasto.id == 100
        assert gasto.deputado_id == 1
        assert gasto.ano == 2024
        assert gasto.mes == 8
        assert gasto.tipo_despesa == "ALUGUEL DE VEÍCULOS"
        assert gasto.valor_documento == Decimal("980.55")
