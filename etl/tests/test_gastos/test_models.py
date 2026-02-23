"""Testes para model SQLAlchemy do domínio de Gastos."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.deputados.models import Deputado
from src.gastos.models import Gasto


class TestGastoModel:
    """Testes para o model Gasto."""

    def _create_deputado(self, db_session, deputado_id=1):
        """Helper para criar um deputado de teste."""
        deputado = Deputado(
            id=deputado_id,
            nome="Deputado Teste",
            partido="PT",
            uf="SP",
        )
        db_session.add(deputado)
        db_session.commit()
        return deputado

    def test_create_gasto_with_all_fields(self, db_session):
        """Test: Gasto pode ser criado com todos os campos do contrato."""
        deputado = self._create_deputado(db_session)
        gasto = Gasto(
            deputado_id=deputado.id,
            ano=2024,
            mes=1,
            tipo_despesa="COMBUSTÍVEL",
            tipo_documento="NOTA FISCAL",
            data_documento=date(2024, 1, 15),
            numero_documento="NF-123",
            valor_documento=Decimal("100.50"),
            valor_liquido=Decimal("95.30"),
            valor_glosa=Decimal("5.20"),
            nome_fornecedor="Posto Exemplo",
            cnpj_cpf_fornecedor="12345678000199",
            url_documento="https://example.com/doc",
            cod_documento=1001,
            cod_lote=2002,
            parcela=1,
        )
        db_session.add(gasto)
        db_session.commit()

        assert gasto.id is not None
        assert gasto.deputado_id == deputado.id
        assert gasto.tipo_despesa == "COMBUSTÍVEL"
        assert gasto.valor_documento == Decimal("100.50")
        assert gasto.valor_liquido == Decimal("95.30")
        assert gasto.valor_glosa == Decimal("5.20")

    def test_create_gasto_without_deputado_id(self, db_session):
        """Test: Gasto aceita deputado_id nulo conforme contrato."""
        gasto = Gasto(
            ano=2024,
            mes=2,
            tipo_despesa="PASSAGEM AÉREA",
            valor_documento=Decimal("1200.00"),
            valor_liquido=Decimal("1200.00"),
            valor_glosa=Decimal("0.00"),
        )
        db_session.add(gasto)
        db_session.commit()

        assert gasto.id is not None
        assert gasto.deputado_id is None

    def test_model_contract_metadata(self):
        """Test: Model possui tablename, índices e unique do contrato."""
        assert Gasto.__tablename__ == "gastos"

        constraint_names = {constraint.name for constraint in Gasto.__table__.constraints if constraint.name}
        assert "uq_gasto" in constraint_names

        index_names = {index.name for index in Gasto.__table__.indexes}
        assert "ux_gastos_dedup_normalized" in index_names
        assert "ix_gastos_deputado_id" in index_names
        assert "ix_gastos_ano_mes" in index_names
        assert "ix_gastos_tipo_despesa" in index_names
        assert "ix_gastos_fornecedor" in index_names

    def test_foreign_key_metadata(self):
        """Test: FK deputado_id referencia deputados.id com ondelete SET NULL."""
        fk = next(fk for fk in Gasto.__table__.c.deputado_id.foreign_keys)
        assert fk.target_fullname == "deputados.id"
        assert fk.ondelete == "SET NULL"

    def test_nullability_contract(self):
        """Test: Campos críticos respeitam nullability definido no contrato."""
        assert Gasto.__table__.c.deputado_id.nullable is True
        assert Gasto.__table__.c.ano.nullable is False
        assert Gasto.__table__.c.mes.nullable is False
        assert Gasto.__table__.c.tipo_despesa.nullable is False
        assert Gasto.__table__.c.valor_documento.nullable is False
        assert Gasto.__table__.c.valor_liquido.nullable is False
        assert Gasto.__table__.c.valor_glosa.nullable is False

    def test_column_defaults_contract(self):
        """Test: Defaults dos campos numéricos seguem o contrato."""
        assert Gasto.__table__.c.valor_documento.default.arg == 0
        assert Gasto.__table__.c.valor_liquido.default.arg == 0
        assert Gasto.__table__.c.valor_glosa.default.arg == 0
        assert Gasto.__table__.c.parcela.default.arg == 0

    def test_unique_constraint_rejects_duplicates(self, db_session):
        """Test: Unique constraint uq_gasto rejeita registro duplicado."""
        deputado = self._create_deputado(db_session)
        gasto_base = {
            "deputado_id": deputado.id,
            "ano": 2024,
            "mes": 3,
            "tipo_despesa": "HOSPEDAGEM",
            "cnpj_cpf_fornecedor": "11122233000144",
            "numero_documento": "DOC-001",
            "valor_documento": Decimal("500.00"),
            "valor_liquido": Decimal("500.00"),
            "valor_glosa": Decimal("0.00"),
        }

        gasto_1 = Gasto(**gasto_base)
        db_session.add(gasto_1)
        db_session.commit()

        gasto_2 = Gasto(**gasto_base)
        db_session.add(gasto_2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_normalized_dedup_rejects_duplicates_with_null_key_fields(self, db_session):
        """Test: Deduplicação também protege quando campos da chave chegam nulos."""
        gasto_base = {
            "deputado_id": None,
            "ano": 2024,
            "mes": 3,
            "tipo_despesa": "HOSPEDAGEM",
            "cnpj_cpf_fornecedor": None,
            "numero_documento": None,
            "valor_documento": Decimal("500.00"),
            "valor_liquido": Decimal("500.00"),
            "valor_glosa": Decimal("0.00"),
        }

        gasto_1 = Gasto(**gasto_base)
        db_session.add(gasto_1)
        db_session.commit()

        gasto_2 = Gasto(**gasto_base)
        db_session.add(gasto_2)
        with pytest.raises(IntegrityError):
            db_session.commit()
