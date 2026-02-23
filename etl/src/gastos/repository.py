"""Repository pattern para persistência do domínio de Gastos Parlamentares."""

from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from .models import Gasto
from .schemas import GastoCreate

NormalizedDedupKey = tuple[int, int, int, str, str, str]
ResumoCategoria = dict[str, str | int | Decimal]


class GastoRepository:
    """Repository para operações com a tabela gastos."""

    def __init__(self, db: Session) -> None:
        """Inicializa o repository com uma sessão de banco de dados."""
        self.db = db

    @staticmethod
    def _normalized_key(
        deputado_id: int | None,
        ano: int,
        mes: int,
        tipo_despesa: str,
        cnpj_cpf_fornecedor: str | None,
        numero_documento: str | None,
    ) -> NormalizedDedupKey:
        """Normaliza a chave de deduplicação para casar com índice funcional."""
        return (
            deputado_id if deputado_id is not None else -1,
            ano,
            mes,
            tipo_despesa,
            cnpj_cpf_fornecedor or "",
            numero_documento or "",
        )

    @classmethod
    def _normalized_key_from_schema(cls, gasto: GastoCreate) -> NormalizedDedupKey:
        """Extrai chave normalizada a partir do schema de entrada."""
        return cls._normalized_key(
            gasto.deputado_id,
            gasto.ano,
            gasto.mes,
            gasto.tipo_despesa,
            gasto.cnpj_cpf_fornecedor,
            gasto.numero_documento,
        )

    @classmethod
    def _normalized_key_from_model(cls, gasto: Gasto) -> NormalizedDedupKey:
        """Extrai chave normalizada a partir do model persistido."""
        return cls._normalized_key(
            gasto.deputado_id,
            gasto.ano,
            gasto.mes,
            gasto.tipo_despesa,
            gasto.cnpj_cpf_fornecedor,
            gasto.numero_documento,
        )

    def _find_existing_by_keys(self, keys: list[NormalizedDedupKey]) -> dict[NormalizedDedupKey, Gasto]:
        """Busca gastos existentes para um conjunto de chaves normalizadas."""
        if not keys:
            return {}

        predicates = [
            and_(
                func.coalesce(Gasto.deputado_id, -1) == deputado_id,
                Gasto.ano == ano,
                Gasto.mes == mes,
                Gasto.tipo_despesa == tipo_despesa,
                func.coalesce(Gasto.cnpj_cpf_fornecedor, "") == cnpj_cpf_fornecedor,
                func.coalesce(Gasto.numero_documento, "") == numero_documento,
            )
            for deputado_id, ano, mes, tipo_despesa, cnpj_cpf_fornecedor, numero_documento in keys
        ]

        stmt = select(Gasto).where(or_(*predicates))
        existing_records = self.db.execute(stmt).scalars().all()
        return {self._normalized_key_from_model(record): record for record in existing_records}

    def bulk_upsert(self, gastos: list[GastoCreate], batch_size: int = 1000) -> int:
        """Insere/atualiza múltiplos gastos com semântica idempotente.

        A deduplicação usa a chave normalizada equivalente ao índice funcional
        `ux_gastos_dedup_normalized`, o que evita duplicações em reprocessamentos
        mesmo quando campos da chave chegam nulos.
        """
        if not gastos:
            return 0
        if batch_size <= 0:
            raise ValueError("batch_size deve ser maior que zero")

        total_processed = 0

        for batch_start in range(0, len(gastos), batch_size):
            batch = gastos[batch_start : batch_start + batch_size]
            total_processed += len(batch)

            # Em caso de duplicidade no mesmo lote, o último registro prevalece.
            deduplicated_batch: dict[NormalizedDedupKey, GastoCreate] = {}
            for gasto in batch:
                deduplicated_batch[self._normalized_key_from_schema(gasto)] = gasto

            existing_by_key = self._find_existing_by_keys(list(deduplicated_batch.keys()))

            for normalized_key, gasto in deduplicated_batch.items():
                existing = existing_by_key.get(normalized_key)
                payload = gasto.model_dump()

                if existing is None:
                    self.db.add(Gasto(**payload))
                    continue

                for field_name, value in payload.items():
                    setattr(existing, field_name, value)

            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise

        return total_processed

    def get_by_deputado(self, deputado_id: int, ano: int | None = None) -> list[Gasto]:
        """Busca gastos por deputado, com filtro opcional por ano."""
        stmt = select(Gasto).where(Gasto.deputado_id == deputado_id)
        if ano is not None:
            stmt = stmt.where(Gasto.ano == ano)

        stmt = stmt.order_by(Gasto.ano, Gasto.mes, Gasto.id)
        return self.db.execute(stmt).scalars().all()

    def get_by_ano_mes(self, ano: int, mes: int) -> list[Gasto]:
        """Busca gastos de um período específico (ano/mês)."""
        stmt = (
            select(Gasto)
            .where(
                Gasto.ano == ano,
                Gasto.mes == mes,
            )
            .order_by(Gasto.deputado_id, Gasto.id)
        )
        return self.db.execute(stmt).scalars().all()

    def get_resumo_por_categoria(self, ano: int) -> list[ResumoCategoria]:
        """Retorna resumo anual agregado por categoria de despesa."""
        stmt = (
            select(
                Gasto.tipo_despesa,
                func.sum(Gasto.valor_liquido).label("total_valor_liquido"),
                func.count(Gasto.id).label("quantidade_registros"),
            )
            .where(Gasto.ano == ano)
            .group_by(Gasto.tipo_despesa)
            .order_by(Gasto.tipo_despesa)
        )

        rows = self.db.execute(stmt).all()
        return [
            {
                "tipo_despesa": row.tipo_despesa,
                "total_valor_liquido": row.total_valor_liquido,
                "quantidade_registros": row.quantidade_registros,
            }
            for row in rows
        ]
