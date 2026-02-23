"""Models SQLAlchemy para o domínio de Gastos Parlamentares (CEAP)."""

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)

from src.shared.database import Base


class Gasto(Base):
    """Model SQLAlchemy para representar um gasto parlamentar."""

    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deputado_id = Column(
        Integer,
        ForeignKey("deputados.id", ondelete="SET NULL"),
        nullable=True,
    )
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    tipo_despesa = Column(String(255), nullable=False)
    tipo_documento = Column(String(50), nullable=True)
    data_documento = Column(Date, nullable=True)
    numero_documento = Column(String(100), nullable=True)
    valor_documento = Column(Numeric(12, 2), nullable=False, default=0)
    valor_liquido = Column(Numeric(12, 2), nullable=False, default=0)
    valor_glosa = Column(Numeric(12, 2), nullable=False, default=0)
    nome_fornecedor = Column(String(255), nullable=True)
    cnpj_cpf_fornecedor = Column(String(20), nullable=True)
    url_documento = Column(Text, nullable=True)
    cod_documento = Column(Integer, nullable=True)
    cod_lote = Column(Integer, nullable=True)
    parcela = Column(Integer, nullable=True, default=0)

    __table_args__ = (
        UniqueConstraint(
            "deputado_id",
            "ano",
            "mes",
            "tipo_despesa",
            "cnpj_cpf_fornecedor",
            "numero_documento",
            name="uq_gasto",
        ),
        # Chave normalizada para preservar idempotência mesmo quando campos da
        # uq_gasto chegam nulos (sem quebrar o contrato original da constraint).
        Index(
            "ux_gastos_dedup_normalized",
            func.coalesce(deputado_id, -1),
            ano,
            mes,
            tipo_despesa,
            func.coalesce(cnpj_cpf_fornecedor, ""),
            func.coalesce(numero_documento, ""),
            unique=True,
        ),
        Index("ix_gastos_deputado_id", "deputado_id"),
        Index("ix_gastos_ano_mes", "ano", "mes"),
        Index("ix_gastos_tipo_despesa", "tipo_despesa"),
        Index("ix_gastos_fornecedor", "cnpj_cpf_fornecedor"),
    )

    def __repr__(self) -> str:
        """Representação string do model."""
        return (
            f"<Gasto(id={self.id}, deputado_id={self.deputado_id}, "
            f"ano={self.ano}, mes={self.mes}, tipo_despesa='{self.tipo_despesa}')>"
        )
