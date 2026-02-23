"""Testes para Repository do domínio de Gastos."""

from decimal import Decimal

from src.deputados.models import Deputado
from src.gastos.models import Gasto
from src.gastos.schemas import GastoCreate


class TestGastoRepository:
    """Testes para GastoRepository."""

    def _create_deputado(self, db_session, deputado_id: int) -> Deputado:
        """Helper para garantir FK válida quando necessário."""
        deputado = Deputado(
            id=deputado_id,
            nome=f"Deputado {deputado_id}",
            partido="PT",
            uf="SP",
        )
        db_session.add(deputado)
        db_session.commit()
        return deputado

    def _build_gasto(self, **kwargs) -> GastoCreate:
        """Factory de GastoCreate com defaults úteis para os testes."""
        base = {
            "deputado_id": None,
            "ano": 2024,
            "mes": 1,
            "tipo_despesa": "COMBUSTÍVEL",
            "tipo_documento": "NOTA FISCAL",
            "numero_documento": "DOC-001",
            "valor_documento": Decimal("100.00"),
            "valor_liquido": Decimal("95.00"),
            "valor_glosa": Decimal("5.00"),
            "nome_fornecedor": "Fornecedor A",
            "cnpj_cpf_fornecedor": "11122233000144",
            "parcela": 1,
        }
        base.update(kwargs)
        return GastoCreate(**base)

    def test_bulk_upsert_inserts_multiple_and_returns_processed_count(self, gasto_repository, db_session):
        """Test: bulk_upsert() insere lote válido e retorna total processado."""
        self._create_deputado(db_session, 101)
        self._create_deputado(db_session, 102)

        gastos = [
            self._build_gasto(deputado_id=101, numero_documento="DOC-101"),
            self._build_gasto(deputado_id=102, numero_documento="DOC-102"),
        ]

        count = gasto_repository.bulk_upsert(gastos, batch_size=1)

        assert count == 2
        assert db_session.query(Gasto).count() == 2

    def test_bulk_upsert_is_idempotent_for_same_dataset(self, gasto_repository, db_session):
        """Test: reprocessar o mesmo lote não duplica registros."""
        self._create_deputado(db_session, 201)

        gastos = [
            self._build_gasto(deputado_id=201, tipo_despesa="PASSAGEM", numero_documento="DOC-201"),
            self._build_gasto(deputado_id=201, tipo_despesa="HOSPEDAGEM", numero_documento="DOC-202"),
        ]

        count_first = gasto_repository.bulk_upsert(gastos)
        count_second = gasto_repository.bulk_upsert(gastos)

        assert count_first == 2
        assert count_second == 2
        assert db_session.query(Gasto).count() == 2

    def test_bulk_upsert_handles_normalized_null_dedup_key(self, gasto_repository, db_session):
        """Test: chave com nulos segue deduplicação normalizada (NULL == string vazia)."""
        gasto_base = self._build_gasto(
            deputado_id=None,
            tipo_despesa="ALUGUEL",
            cnpj_cpf_fornecedor=None,
            numero_documento=None,
            valor_documento=Decimal("250.00"),
            valor_liquido=Decimal("240.00"),
            valor_glosa=Decimal("10.00"),
        )
        gasto_updated_same_normalized_key = self._build_gasto(
            deputado_id=None,
            tipo_despesa="ALUGUEL",
            cnpj_cpf_fornecedor="",
            numero_documento="",
            valor_documento=Decimal("300.00"),
            valor_liquido=Decimal("300.00"),
            valor_glosa=Decimal("0.00"),
        )

        count_first = gasto_repository.bulk_upsert([gasto_base])
        count_second = gasto_repository.bulk_upsert([gasto_updated_same_normalized_key])

        assert count_first == 1
        assert count_second == 1
        assert db_session.query(Gasto).count() == 1

        persisted = db_session.query(Gasto).first()
        assert persisted is not None
        assert persisted.valor_documento == Decimal("300.00")
        assert persisted.valor_liquido == Decimal("300.00")
        assert persisted.valor_glosa == Decimal("0.00")

    def test_bulk_upsert_empty_list_returns_zero(self, gasto_repository, db_session):
        """Test: bulk_upsert() com lista vazia retorna 0 sem efeitos colaterais."""
        count = gasto_repository.bulk_upsert([])
        assert count == 0
        assert db_session.query(Gasto).count() == 0

    def test_get_by_deputado_returns_only_requested_deputado(self, gasto_repository, db_session):
        """Test: get_by_deputado() filtra corretamente por deputado_id."""
        self._create_deputado(db_session, 301)
        self._create_deputado(db_session, 302)
        gasto_repository.bulk_upsert(
            [
                self._build_gasto(deputado_id=301, numero_documento="DOC-301"),
                self._build_gasto(deputado_id=301, numero_documento="DOC-302", mes=2),
                self._build_gasto(deputado_id=302, numero_documento="DOC-303"),
            ]
        )

        records = gasto_repository.get_by_deputado(301)

        assert len(records) == 2
        assert all(record.deputado_id == 301 for record in records)

    def test_get_by_deputado_with_optional_year_filter(self, gasto_repository, db_session):
        """Test: get_by_deputado() respeita filtro opcional por ano."""
        self._create_deputado(db_session, 401)
        gasto_repository.bulk_upsert(
            [
                self._build_gasto(deputado_id=401, ano=2023, numero_documento="DOC-401"),
                self._build_gasto(deputado_id=401, ano=2024, numero_documento="DOC-402"),
            ]
        )

        all_years = gasto_repository.get_by_deputado(401)
        records_2024 = gasto_repository.get_by_deputado(401, ano=2024)

        assert len(all_years) == 2
        assert len(records_2024) == 1
        assert records_2024[0].ano == 2024

    def test_get_by_ano_mes_returns_only_requested_period(self, gasto_repository, db_session):
        """Test: get_by_ano_mes() retorna somente registros do período informado."""
        self._create_deputado(db_session, 501)
        gasto_repository.bulk_upsert(
            [
                self._build_gasto(deputado_id=501, ano=2024, mes=3, numero_documento="DOC-501"),
                self._build_gasto(deputado_id=501, ano=2024, mes=3, numero_documento="DOC-502"),
                self._build_gasto(deputado_id=501, ano=2024, mes=4, numero_documento="DOC-503"),
            ]
        )

        period_records = gasto_repository.get_by_ano_mes(2024, 3)

        assert len(period_records) == 2
        assert all(record.ano == 2024 and record.mes == 3 for record in period_records)

    def test_get_resumo_por_categoria_aggregates_annual_totals(self, gasto_repository, db_session):
        """Test: get_resumo_por_categoria() agrega total por tipo_despesa no ano."""
        self._create_deputado(db_session, 601)
        gasto_repository.bulk_upsert(
            [
                self._build_gasto(
                    deputado_id=601,
                    ano=2024,
                    tipo_despesa="COMBUSTÍVEL",
                    numero_documento="DOC-601",
                    valor_liquido=Decimal("10.00"),
                ),
                self._build_gasto(
                    deputado_id=601,
                    ano=2024,
                    tipo_despesa="COMBUSTÍVEL",
                    numero_documento="DOC-602",
                    valor_liquido=Decimal("15.50"),
                ),
                self._build_gasto(
                    deputado_id=601,
                    ano=2024,
                    tipo_despesa="HOSPEDAGEM",
                    numero_documento="DOC-603",
                    valor_liquido=Decimal("30.00"),
                ),
                self._build_gasto(
                    deputado_id=601,
                    ano=2025,
                    tipo_despesa="COMBUSTÍVEL",
                    numero_documento="DOC-604",
                    valor_liquido=Decimal("999.99"),
                ),
            ]
        )

        resumo = gasto_repository.get_resumo_por_categoria(2024)
        resumo_map = {row["tipo_despesa"]: row for row in resumo}

        assert len(resumo) == 2
        assert resumo_map["COMBUSTÍVEL"]["total_valor_liquido"] == Decimal("25.50")
        assert resumo_map["COMBUSTÍVEL"]["quantidade_registros"] == 2
        assert resumo_map["HOSPEDAGEM"]["total_valor_liquido"] == Decimal("30.00")
        assert resumo_map["HOSPEDAGEM"]["quantidade_registros"] == 1

    def test_queries_return_empty_collections_when_no_results(self, gasto_repository):
        """Test: queries retornam coleção vazia em cenários sem resultados."""
        assert gasto_repository.get_by_deputado(99999) == []
        assert gasto_repository.get_by_ano_mes(2020, 1) == []
        assert gasto_repository.get_resumo_por_categoria(2020) == []
